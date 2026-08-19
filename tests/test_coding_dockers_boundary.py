import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INSTALL = ROOT / "scripts" / "pop_install_unirepo.py"


def run(*args, cwd=None):
    return subprocess.run(args, cwd=cwd, text=True, capture_output=True)


def load_installer():
    spec = importlib.util.spec_from_file_location("unirepo_installer", INSTALL)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CodingDockersBoundaryTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.target = Path(self.tmp.name) / "unirepo"
        self.target.mkdir()
        (self.target / "AGENTS.md").write_text("# Fixture\n- **Type:** uni-repo\n")

    def install(self):
        result = run("python3", str(INSTALL), str(self.target))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_feature_does_not_enter_the_fixture_harness(self):
        data = json.loads(
            (ROOT / "_templates/unirepo-manifest.json").read_text())
        self.assertNotIn("coding-sandbox", data["skills"])

        self.install()

        self.assertFalse((self.target / "pop/scripts/pop_sandbox.py").exists())
        self.assertFalse((self.target / "pop/_templates/coding-dockers").exists())
        self.assertFalse((self.target / "coding-dockers").exists())
        self.assertFalse((self.target / ".agents/skills/coding-sandbox").exists())

        marker = json.loads(
            (self.target / "pop/.unirepo-harness.json").read_text())
        installed = marker["installed"]
        self.assertFalse(any("coding-dockers" in path for path in installed))
        self.assertFalse(any("coding-sandbox" in path for path in installed))
        self.assertNotIn("pop/scripts/pop_sandbox.py", installed)

        forbidden = (b"coding-dockers", b"coding docker", b"coding-sandbox",
                     b"coding sandbox", b"pop_sandbox.py")
        for path in sorted(item for item in self.target.rglob("*")
                           if item.is_file()):
            content = path.read_bytes().lower()
            for token in forbidden:
                self.assertNotIn(token, content, f"{path}: {token!r}")

        for args in (("--audit-boundary",),
                     ("--check-fresh", str(self.target))):
            result = run("python3", str(INSTALL), *args)
            self.assertEqual(result.returncode, 0,
                             result.stdout + result.stderr)
        result = run("python3", "pop/scripts/pop_validate.py", "--standalone",
                     cwd=self.target)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_exclusion_covers_subtree_hash_and_pruning(self):
        installer = load_installer()
        labels = {label for label, _ in
                  installer.managed_sources(installer.manifest())}
        self.assertNotIn("scripts/pop_sandbox.py", labels)
        self.assertFalse(any(label.startswith("skills/coding-sandbox/")
                             for label in labels))
        self.assertFalse(any(label.startswith("_templates/coding-dockers/")
                             for label in labels))

        self.install()
        stale_files = (
            "pop/scripts/pop_sandbox.py",
            "pop/_templates/coding-dockers/catalog.json",
            "pop/_templates/coding-dockers/recipes/future.json",
            ".agents/skills/coding-sandbox/SKILL.md",
            "coding-dockers/INDEX.md",
        )
        marker_path = self.target / "pop/.unirepo-harness.json"
        marker = json.loads(marker_path.read_text())
        for relative in stale_files:
            path = self.target / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("stale\n")
            marker["installed"].append(relative)
        marker_path.write_text(json.dumps(marker))

        self.install()
        for relative in stale_files:
            self.assertFalse((self.target / relative).exists(), relative)

    def test_excluded_content_does_not_change_the_harness_hash(self):
        installer = load_installer()
        source = Path(self.tmp.name) / "source"
        (source / "_templates/coding-dockers").mkdir(parents=True)
        (source / "scripts").mkdir()
        (source / ".agents/skills/coding-sandbox").mkdir(parents=True)
        (source / ".agents/skills/managed").mkdir(parents=True)
        excluded_template = source / "_templates/coding-dockers/future.json"
        excluded_script = source / "scripts/pop_sandbox.py"
        excluded_skill = source / ".agents/skills/coding-sandbox/SKILL.md"
        managed_skill = source / ".agents/skills/managed/SKILL.md"
        managed_script = source / "scripts/managed.py"
        excluded_template.write_text("one")
        excluded_script.write_text("one")
        excluded_skill.write_text("one")
        managed_skill.write_text("one")
        managed_script.write_text("one")
        data = {
            "files": [],
            "directories": ["_templates", "scripts"],
            "skills": ["managed"],
            "exclude_prefixes": [
                "_templates/coding-dockers", "scripts/pop_sandbox.py"
            ],
        }
        manifest_path = source / "manifest.json"
        manifest_path.write_text(json.dumps(data))
        installer.SOURCE = source
        installer.MANIFEST = manifest_path
        installer.SKILLS_SOURCE = source / ".agents/skills"

        original = installer.content_sha(data)
        excluded_template.write_text("two")
        excluded_script.write_text("two")
        excluded_skill.write_text("two")
        self.assertEqual(installer.content_sha(data), original)
        managed_skill.write_text("two")
        self.assertNotEqual(installer.content_sha(data), original)
        original = installer.content_sha(data)
        managed_script.write_text("two")
        self.assertNotEqual(installer.content_sha(data), original)


if __name__ == "__main__":
    unittest.main()
