from __future__ import annotations

from contextlib import redirect_stderr
import importlib.util
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest import mock

SKILL = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("build_agents", SKILL / "scripts" / "build_agents.py")
assert SPEC and SPEC.loader
builder = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(builder)


class BuildAgentsTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.sources = self.root / "sources"
        self.sources.mkdir()
        for role in builder.ROLES:
            sections = "\n\n".join(f"## {section}\n\nConteúdo {section}." for section in builder.REQUIRED_SECTIONS)
            (self.sources / f"{role}.md").write_text(f"# {role}\n\n{sections}\n", encoding="utf-8")
        self.profiles = self.root / "profiles.json"
        self.profiles.write_bytes((SKILL / "fixtures" / "profiles.valid.json").read_bytes())
        self.destination = self.root / "candidate"

    def tearDown(self) -> None:
        self.temp.cleanup()

    def render(self):
        return builder.render_all(self.sources, self.profiles)

    def test_build_is_idempotent_and_preserves_sources(self) -> None:
        rendered, manifest = self.render()
        builder.write_bundle(self.destination, rendered, manifest)
        first = {p.relative_to(self.destination): p.read_bytes() for p in self.destination.rglob("*") if p.is_file()}
        builder.write_bundle(self.destination, rendered, manifest)
        second = {p.relative_to(self.destination): p.read_bytes() for p in self.destination.rglob("*") if p.is_file()}
        self.assertEqual(first, second)
        builder.validate_bundle(self.destination, rendered, manifest)
        for role in builder.ROLES:
            generated = rendered[f".opencode/agents/{role}.md"]
            self.assertTrue(generated.endswith((self.sources / f"{role}.md").read_text(encoding="utf-8")))
            self.assertNotIn("\ntools:", generated.split("---", 2)[1])

    def test_profile_rejects_inheritance_unknown_tuple_tools_and_depth(self) -> None:
        original = json.loads(self.profiles.read_text(encoding="utf-8"))
        mutations = []
        inherited = json.loads(json.dumps(original)); inherited["roles"]["pop-executor"]["model"] = "inherit"; mutations.append(inherited)
        variant = json.loads(json.dumps(original)); variant["roles"]["pop-executor"]["variant"] = "xhigh"; mutations.append(variant)
        deprecated = json.loads(json.dumps(original)); deprecated["roles"]["pop-executor"]["tools"] = []; mutations.append(deprecated)
        depth = json.loads(json.dumps(original)); depth["subagent_depth"] = 1; mutations.append(depth)
        weakened = json.loads(json.dumps(original)); weakened["roles"]["pop-recon"]["permissions"].remove("edit"); mutations.append(weakened)
        for document in mutations:
            with self.subTest(document=document):
                self.profiles.write_text(json.dumps(document), encoding="utf-8")
                with self.assertRaises(builder.BuildError):
                    self.render()

    def test_task_skill_and_web_policy_is_fail_closed(self) -> None:
        rendered, _ = self.render()
        planner = rendered[".opencode/agents/pop-planner.md"]
        executor = rendered[".opencode/agents/pop-executor.md"]
        for content in (planner, executor):
            frontmatter = content.split("---", 2)[1]
            self.assertIn('"webfetch": "deny"', frontmatter)
            self.assertIn('"websearch": "deny"', frontmatter)
            self.assertIn('"skill": {"*": "deny"', frontmatter)
        self.assertIn('"pop-recon": "allow"', planner)
        self.assertIn('"task": {"*": "deny"}', executor)

    def test_unmanaged_collision_survives(self) -> None:
        collision = self.destination / ".opencode" / "agents" / "pop-executor.md"
        collision.parent.mkdir(parents=True)
        collision.write_text("user", encoding="utf-8")
        rendered, manifest = self.render()
        with self.assertRaises(builder.BuildError):
            builder.write_bundle(self.destination, rendered, manifest)
        self.assertEqual(collision.read_text(encoding="utf-8"), "user")

    def test_modified_managed_file_is_not_overwritten(self) -> None:
        rendered, manifest = self.render()
        builder.write_bundle(self.destination, rendered, manifest)
        agent = self.destination / ".opencode" / "agents" / "pop-executor.md"
        agent.write_text("manual", encoding="utf-8")
        with self.assertRaises(builder.BuildError):
            builder.write_bundle(self.destination, rendered, manifest)
        self.assertEqual(agent.read_text(encoding="utf-8"), "manual")

    def test_backup_cleanup_failure_keeps_committed_destination(self) -> None:
        rendered, manifest = self.render()
        builder.write_bundle(self.destination, rendered, manifest)
        old_agent = self.destination / ".opencode" / "agents" / "pop-executor.md"
        old_content = old_agent.read_text(encoding="utf-8")
        source = self.sources / "pop-executor.md"
        source.write_text(source.read_text(encoding="utf-8") + "\nAtualização.\n", encoding="utf-8")
        updated, updated_manifest = self.render()
        backup = self.destination.parent / f".{self.destination.name}.backup-{os.getpid()}"
        real_rmtree = builder.shutil.rmtree

        def fail_backup_cleanup(path, *args, **kwargs):
            if Path(path) == backup:
                raise OSError("cleanup fault")
            return real_rmtree(path, *args, **kwargs)

        stderr = io.StringIO()
        with mock.patch.object(builder.shutil, "rmtree", side_effect=fail_backup_cleanup):
            with redirect_stderr(stderr):
                builder.write_bundle(self.destination, updated, updated_manifest)

        self.assertIn("WARNING", stderr.getvalue())
        self.assertNotEqual(old_content, old_agent.read_text(encoding="utf-8"))
        builder.validate_bundle(self.destination, updated, updated_manifest)
        self.assertTrue(backup.is_dir())

    def test_builder_has_no_coding_agent_execution_path(self) -> None:
        source = (SKILL / "scripts" / "build_agents.py").read_text(encoding="utf-8")
        self.assertNotIn("subprocess", source)
        self.assertNotIn("validate-discovery", source)
        self.assertNotIn("agent list", source)


if __name__ == "__main__":
    unittest.main()
