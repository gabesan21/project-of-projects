import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INSTALL = ROOT / "scripts" / "pop_install_included.py"


def run(*args, cwd=None):
    return subprocess.run(args, cwd=cwd, text=True, capture_output=True)


class IncludedFlowsTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.target = Path(self.tmp.name) / "included"
        self.target.mkdir()
        (self.target / "AGENTS.md").write_text("# Fixture\n- **Type:** included\n")

    def tearDown(self): self.tmp.cleanup()

    def install(self):
        result = run("python3", str(INSTALL), str(self.target))
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_new_project(self):
        self.install()
        result = run("python3", "pop/scripts/pop_validate.py", "--standalone", cwd=self.target)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("standalone valid", result.stdout)

    def test_import_project(self):
        self.install(); self.install()
        self.assertTrue((self.target / "pop/.included-harness.json").is_file())

    def test_full_multi_repo(self):
        other = Path(self.tmp.name) / "second"; other.mkdir()
        (other / "AGENTS.md").write_text("# Second\n")
        self.install()
        result = run("python3", str(INSTALL), str(other))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((self.target / "pop/.included-harness.json").read_bytes(),
                         (other / "pop/.included-harness.json").read_bytes())

    def test_real_git_clone_keeps_standalone_anatomy(self):
        self.install()
        self.assertEqual(run("git", "init", cwd=self.target).returncode, 0)
        self.assertEqual(run("git", "add", ".", cwd=self.target).returncode, 0)
        self.assertEqual(run("git", "-c", "user.name=Fixture", "-c",
                             "user.email=fixture@example.test", "commit", "-m", "fixture",
                             cwd=self.target).returncode, 0)
        clone = Path(self.tmp.name) / "clone"
        self.assertEqual(run("git", "clone", "--no-local", str(self.target), str(clone)).returncode, 0)
        result = run("python3", "pop/scripts/pop_validate.py", "--standalone", cwd=clone)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


class StandaloneNegativeTest(unittest.TestCase):
    def test_missing_skill_and_external_link_fail(self):
        with tempfile.TemporaryDirectory() as raw:
            target = Path(raw) / "included"; target.mkdir()
            (target / "AGENTS.md").write_text("# Fixture\n")
            self.assertEqual(run("python3", str(INSTALL), str(target)).returncode, 0)
            (target / ".agents/skills/yolo-critic/SKILL.md").unlink()
            self.assertNotEqual(run("python3", "pop/scripts/pop_validate.py", "--standalone", cwd=target).returncode, 0)
            shutil.copy2(ROOT / ".agents/skills/yolo-critic/SKILL.md", target / ".agents/skills/yolo-critic/SKILL.md")
            (target / "pop/PROJECT.md").write_text("[[categories/applications/outside/PROJECT]]")
            self.assertNotEqual(run("python3", "pop/scripts/pop_validate.py", "--standalone", cwd=target).returncode, 0)


class MaterializerContractTest(unittest.TestCase):
    def test_manifest_and_skills_name_one_command(self):
        self.assertEqual(run("python3", str(INSTALL), "--audit-manifest").returncode, 0)
        for skill in ("new-project", "import-project"):
            text = (ROOT / ".agents/skills" / skill / "SKILL.md").read_text()
            self.assertIn("pop_install_included.py", text)


class LocalCliTest(unittest.TestCase):
    def test_local_operations(self):
        with tempfile.TemporaryDirectory() as raw:
            target = Path(raw) / "included"; target.mkdir()
            (target / "AGENTS.md").write_text("# Fixture\n")
            self.assertEqual(run("python3", str(INSTALL), str(target)).returncode, 0)
            for name in ("pop_status.py", "pop_move.py", "pop_task.py", "pop_claim.py", "pop_worktree.py"):
                result = run("python3", "pop/scripts/" + name, "--help", cwd=target)
                self.assertEqual(result.returncode, 0, name + result.stderr)
            task = "1.1.1-fixture-task"
            self.assertEqual(run("python3", "pop/scripts/pop_task.py", "pop", task,
                                 "--title", "Fixture", cwd=target).returncode, 0)
            self.assertEqual(run("python3", "pop/scripts/pop_claim.py", task,
                                 "--by", "fixture", cwd=target).returncode, 0)
            self.assertEqual(run("python3", "pop/scripts/pop_claim.py", task,
                                 "--release", "--by", "fixture", cwd=target).returncode, 0)
            card = target / "pop/kanban/001_initial_task" / task / f"{task}.md"
            card.write_text(card.read_text().replace("- [ ] Ready to plan",
                                                     "- [x] Ready to plan"))
            self.assertEqual(run("python3", "pop/scripts/pop_move.py", task,
                                 "002_planning", "--reason", "fixture", cwd=target).returncode, 0)
            self.assertEqual(run("python3", "pop/scripts/pop_status.py", "--project", "pop",
                                 cwd=target).returncode, 0)
