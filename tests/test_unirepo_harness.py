import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INSTALL = ROOT / "scripts" / "pop_install_unirepo.py"


def run(*args, cwd=None):
    return subprocess.run(args, cwd=cwd, text=True, capture_output=True)


class UnirepoFlowsTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.target = Path(self.tmp.name) / "unirepo"
        self.target.mkdir()
        (self.target / "AGENTS.md").write_text("# Fixture\n- **Type:** uni-repo\n")

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
        self.assertTrue((self.target / "pop/.unirepo-harness.json").is_file())

    def test_multi_repo(self):
        other = Path(self.tmp.name) / "second"; other.mkdir()
        (other / "AGENTS.md").write_text("# Second\n")
        self.install()
        result = run("python3", str(INSTALL), str(other))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((self.target / "pop/.unirepo-harness.json").read_bytes(),
                         (other / "pop/.unirepo-harness.json").read_bytes())

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
            target = Path(raw) / "unirepo"; target.mkdir()
            (target / "AGENTS.md").write_text("# Fixture\n")
            self.assertEqual(run("python3", str(INSTALL), str(target)).returncode, 0)
            (target / ".agents/skills/judge-dredd/SKILL.md").unlink()
            self.assertNotEqual(run("python3", "pop/scripts/pop_validate.py", "--standalone", cwd=target).returncode, 0)
            shutil.copy2(ROOT / ".agents/skills/judge-dredd/SKILL.md", target / ".agents/skills/judge-dredd/SKILL.md")
            # The negative's external link uses `projects/`: in the new layout,
            # a link to `projects/<proj>/...` points outside the scope.
            (target / "pop/PROJECT.md").write_text("[[projects/applications/outside/PROJECT]]")
            self.assertNotEqual(run("python3", "pop/scripts/pop_validate.py", "--standalone", cwd=target).returncode, 0)


class MaterializerContractTest(unittest.TestCase):
    def test_manifest_and_skills_name_one_command(self):
        self.assertEqual(run("python3", str(INSTALL), "--audit-manifest").returncode, 0)
        for skill in ("new-project", "import-project"):
            text = (ROOT / ".agents/skills" / skill / "SKILL.md").read_text()
            self.assertIn("pop_install_unirepo.py", text)


class LocalCliTest(unittest.TestCase):
    def test_local_operations(self):
        with tempfile.TemporaryDirectory() as raw:
            target = Path(raw) / "unirepo"; target.mkdir()
            (target / "AGENTS.md").write_text("# Fixture\n")
            self.assertEqual(run("python3", str(INSTALL), str(target)).returncode, 0)
            for name in ("pop_status.py", "pop_move.py", "pop_task.py", "pop_claim.py", "pop_worktree.py"):
                result = run("python3", "pop/scripts/" + name, "--help", cwd=target)
                self.assertEqual(result.returncode, 0, name + result.stderr)
            task = "1.1.1-fixture-task"
            # An installed scope is named after its own root. Calling itself
            # `pop` would make the card inherit the host's delivery route.
            self.assertEqual(run("python3", "pop/scripts/pop_task.py", target.name,
                                 task, "--title", "Fixture", cwd=target).returncode, 0)
            self.assertEqual(run("python3", "pop/scripts/pop_claim.py", task,
                                 "--by", "fixture", cwd=target).returncode, 0)
            self.assertEqual(run("python3", "pop/scripts/pop_claim.py", task,
                                 "--release", "--by", "fixture", cwd=target).returncode, 0)
            card = target / "pop/kanban/001_initial_task" / task / f"{task}.md"
            card.write_text(card.read_text().replace("- [ ] Ready to plan",
                                                     "- [x] Ready to plan"))
            self.assertEqual(run("python3", "pop/scripts/pop_move.py", task,
                                 "002_planning", "--reason", "fixture", cwd=target).returncode, 0)
            self.assertEqual(run("python3", "pop/scripts/pop_status.py", "--project", target.name,
                                 cwd=target).returncode, 0)


class BoundaryTest(unittest.TestCase):
    """An installed harness is a complete world: nothing resolves above its root.

    The real case behind these tests: a project installed **inside** the tree
    of whoever installed it. The tool loads the ancestor's `AGENTS.md` on its
    own, and from then on every "vault" becomes the one above. The harness does
    not control the tool — it controls what it says and what the scripts
    resolve.
    """

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        # A complete, plausible ancestor: its own AGENTS.md, kanban and index.
        self.host = Path(self.tmp.name) / "host"
        (self.host / "kanban" / "001_initial_task").mkdir(parents=True)
        (self.host / "AGENTS.md").write_text("# Host\nNot the scope.\n")
        (self.host / "INDEX.md").write_text("# Host index\n")
        self.target = self.host / "projects" / "child"
        self.target.mkdir(parents=True)
        (self.target / "AGENTS.md").write_text("# Child\n")
        self.assertEqual(run("python3", str(INSTALL), str(self.target)).returncode, 0)

    def tearDown(self): self.tmp.cleanup()

    def test_scripts_stop_at_the_installed_scope_root(self):
        module = self.target / "pop" / "scripts" / "poplib.py"
        # Import by path: the name `poplib` collides with the stdlib POP3 module.
        probe = ("import importlib.util as u; "
                 f"s = u.spec_from_file_location('pl', r'{module}'); "
                 "m = u.module_from_spec(s); s.loader.exec_module(m); "
                 "print(m.vault_root())")
        for cwd in (self.target, self.target / "pop" / "kanban"):
            result = run("python3", "-c", probe, cwd=cwd)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout.strip(), str(self.target.resolve()))

    def test_no_installed_file_points_outside(self):
        for path in sorted(self.target.rglob("*.md")):
            text = path.read_text(encoding="utf-8").lower()
            for token in ("[[projects/", "root pop", "parent pop",
                          "parent vault", "meta-project", str(self.host).lower()):
                self.assertNotIn(token, text, f"{path}: {token}")

    def test_full_flow_without_the_origin_on_disk(self):
        """The cut-dependency criterion: it works cloned on its own."""
        alone = Path(self.tmp.name) / "alone"
        shutil.copytree(self.target, alone)
        task = "1.1.1-fixture-task"
        self.assertEqual(run("python3", "pop/scripts/pop_task.py", alone.name,
                             task, "--title", "Fixture", cwd=alone).returncode, 0)
        card = alone / "pop/kanban/001_initial_task" / task / f"{task}.md"
        card.write_text(card.read_text().replace("size: S | M | L", "size: S"))
        for args in (("pop/scripts/pop_validate.py", "--standalone"),
                     ("pop/scripts/pop_status.py",),
                     ("pop/scripts/pop_install_unirepo.py", "--check-fresh", ".")):
            result = run("python3", *args, cwd=alone)
            self.assertEqual(result.returncode, 0,
                             " ".join(args) + result.stdout + result.stderr)
