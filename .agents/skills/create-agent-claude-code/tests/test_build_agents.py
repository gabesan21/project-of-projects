from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest import mock

SKILL_DIR = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("build_agents", SKILL_DIR / "scripts" / "build_agents.py")
assert SPEC and SPEC.loader
build_agents = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(build_agents)


class BuildAgentsTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.sources = self.root / "sources"
        self.sources.mkdir()
        for role in build_agents.ROLES:
            sections = "\n\n".join(f"## {name}\n\nConteúdo de {name}." for name in build_agents.REQUIRED_SECTIONS)
            (self.sources / f"{role}.md").write_text(f"# {role}\n\n{sections}\n", encoding="utf-8")
        fixture = json.loads((SKILL_DIR / "fixtures" / "profiles.valid.json").read_text(encoding="utf-8"))
        self.profiles = self.root / "profiles.json"
        self.profiles.write_text(json.dumps(fixture), encoding="utf-8")
        self.runtime_document = {
            "maxSpawnDepth": 3,
            "nesting": {
                role: {
                    "executionMode": "main",
                    "currentDepth": 0,
                    "allowedChildren": list(build_agents.CHILD_AGENTS[role]),
                }
                for role in build_agents.DELEGATING_ROLES
            },
        }
        self.runtime = self.root / "runtime.json"
        self.write_runtime(self.runtime_document)
        self.destination = self.root / ".claude" / "agents"

    def tearDown(self) -> None:
        self.temp.cleanup()

    def rendered(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            return build_agents.render_all(self.sources, self.profiles, self.runtime)

    def write_runtime(self, document) -> None:
        self.runtime.write_text(json.dumps(document), encoding="utf-8")

    def test_generates_six_agents_and_is_idempotent(self) -> None:
        rendered, manifest = self.rendered()
        build_agents.generate(self.destination, rendered, manifest)
        first = {path.name: path.read_bytes() for path in self.destination.iterdir()}
        build_agents.generate(self.destination, rendered, manifest)
        second = {path.name: path.read_bytes() for path in self.destination.iterdir()}
        self.assertEqual(first, second)
        self.assertEqual(set(rendered), {f"{role}.md" for role in build_agents.ROLES})
        for role in build_agents.ROLES:
            source = (self.sources / f"{role}.md").read_text(encoding="utf-8")
            self.assertTrue(rendered[f"{role}.md"].endswith(source))
            self.assertNotIn("thinking:", rendered[f"{role}.md"].split("---", 2)[1])
        build_agents.validate_destination(self.destination, rendered, manifest)

    def test_preserves_body_and_denies_agent_without_nesting(self) -> None:
        rendered, _ = self.rendered()
        executor = rendered["pop-executor.md"]
        source = (self.sources / "pop-executor.md").read_text(encoding="utf-8")
        self.assertTrue(executor.endswith(source))
        frontmatter = executor.split("---", 2)[1]
        self.assertIn('disallowedTools: ["WebFetch", "WebSearch", "Agent"]', frontmatter)
        for content in rendered.values():
            self.assertNotIn("Agent(", content.split("---", 2)[1])

    def test_unknown_field_fails_before_mutation(self) -> None:
        self.destination.mkdir(parents=True)
        sentinel = self.destination / "sentinel.txt"
        sentinel.write_text("intacto", encoding="utf-8")
        profile = json.loads(self.profiles.read_text(encoding="utf-8"))
        profile["roles"]["pop-executor"]["thinking"] = True
        self.profiles.write_text(json.dumps(profile), encoding="utf-8")
        with self.assertRaises(build_agents.BuildError):
            self.rendered()
        self.assertEqual(sentinel.read_text(encoding="utf-8"), "intacto")

    def test_inherit_model_and_unknown_effort_fail_closed(self) -> None:
        original = json.loads(self.profiles.read_text(encoding="utf-8"))
        try:
            for field, value in (("model", "inherit"), ("model", " inherit "), ("effort", "extreme")):
                with self.subTest(field=field):
                    profile = json.loads(json.dumps(original))
                    profile["roles"]["pop-executor"][field] = value
                    self.profiles.write_text(json.dumps(profile), encoding="utf-8")
                    with self.assertRaises(build_agents.BuildError):
                        self.rendered()
        finally:
            self.profiles.write_text(json.dumps(original), encoding="utf-8")

    def test_known_model_override_fails_closed(self) -> None:
        with mock.patch.dict(os.environ, {"CLAUDE_CODE_SUBAGENT_MODEL": "haiku"}, clear=True):
            with self.assertRaises(build_agents.BuildError):
                build_agents.render_all(self.sources, self.profiles, None)

    def test_missing_source_fails_closed(self) -> None:
        (self.sources / "pop-recon.md").unlink()
        with self.assertRaises(build_agents.BuildError):
            self.rendered()

    def test_extra_role_source_fails_closed(self) -> None:
        (self.sources / "pop-intruder.md").write_text("# pop-intruder\n", encoding="utf-8")
        with self.assertRaises(build_agents.BuildError):
            self.rendered()

    def test_nesting_must_remain_empty_for_all_specialists(self) -> None:
        invalid = json.loads(json.dumps(self.runtime_document))
        invalid["nesting"]["pop-planner"] = {"executionMode": "subagent", "currentDepth": 1, "allowedChildren": []}
        self.write_runtime(invalid)
        with self.assertRaises(build_agents.BuildError):
            self.rendered()
        self.write_runtime(self.runtime_document)

    def test_environment_spawn_depth_does_not_create_specialist_nesting(self) -> None:
        with mock.patch.dict(os.environ, {"CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH": "1"}, clear=True):
            build_agents.render_all(self.sources, self.profiles, self.runtime)

    def test_unmanaged_collision_is_not_overwritten(self) -> None:
        self.destination.mkdir(parents=True)
        collision = self.destination / "pop-executor.md"
        collision.write_text("do usuário", encoding="utf-8")
        rendered, manifest = self.rendered()
        with self.assertRaises(build_agents.BuildError):
            build_agents.generate(self.destination, rendered, manifest)
        self.assertEqual(collision.read_text(encoding="utf-8"), "do usuário")

    def test_manifest_path_escape_is_rejected_before_staging_mutation(self) -> None:
        rendered, manifest = self.rendered()
        build_agents.generate(self.destination, rendered, manifest)
        outside = self.destination.parent / "outside.txt"
        outside.write_text("intacto", encoding="utf-8")
        manifest_path = self.destination / build_agents.MANIFEST
        malicious = json.loads(manifest_path.read_text(encoding="utf-8"))
        digest = next(iter(malicious["files"].values()))
        malicious["files"]["../outside.txt"] = digest
        manifest_path.write_text(json.dumps(malicious), encoding="utf-8")
        with self.assertRaises(build_agents.BuildError):
            build_agents.generate(self.destination, rendered, manifest)
        self.assertEqual(outside.read_text(encoding="utf-8"), "intacto")

    def test_manifest_schema_and_hash_are_rejected_before_mutation(self) -> None:
        rendered, manifest = self.rendered()
        build_agents.generate(self.destination, rendered, manifest)
        manifest_path = self.destination / build_agents.MANIFEST
        valid = json.loads(manifest_path.read_text(encoding="utf-8"))
        sentinel = self.destination / "sentinel.txt"
        sentinel.write_text("intacto", encoding="utf-8")
        invalid_documents = []
        unknown_field = json.loads(json.dumps(valid))
        unknown_field["unknown"] = True
        invalid_documents.append(unknown_field)
        invalid_hash = json.loads(json.dumps(valid))
        invalid_hash["files"]["pop-executor.md"] = "not-a-sha256"
        invalid_documents.append(invalid_hash)
        for document in invalid_documents:
            with self.subTest(document=document):
                manifest_path.write_text(json.dumps(document), encoding="utf-8")
                with self.assertRaises(build_agents.BuildError):
                    build_agents.generate(self.destination, rendered, manifest)
                self.assertEqual(sentinel.read_text(encoding="utf-8"), "intacto")
        manifest_path.write_text(json.dumps(valid), encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
