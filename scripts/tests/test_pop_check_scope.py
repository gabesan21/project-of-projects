#!/usr/bin/env python3
"""Tests for the execution-front ownership gate."""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "pop_check_scope.py"


class PopCheckScopeTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.repo = Path(self._tmp.name) / "repo"
        self.repo.mkdir()
        self.git("init", "-q")
        self.git("config", "user.email", "test@example.com")
        self.git("config", "user.name", "PoP Test")
        (self.repo / "src").mkdir()
        (self.repo / "src/model.py").write_text("MODEL = 1\n", encoding="utf-8")
        (self.repo / "README.md").write_text("base\n", encoding="utf-8")
        self.git("add", ".")
        self.git("commit", "-qm", "base")
        self.base = self.git("rev-parse", "HEAD").stdout.strip()

    def git(self, *args):
        return subprocess.run(["git", "-C", str(self.repo), *args], check=True,
                              capture_output=True, text=True)

    def check_scope(self, *allowed, denied=()):
        command = [sys.executable, str(SCRIPT), "--repo", str(self.repo), "--base", self.base]
        for pattern in allowed:
            command.extend(["--allow", pattern])
        for pattern in denied:
            command.extend(["--deny", pattern])
        return subprocess.run(command, capture_output=True, text=True)

    def test_accepts_owned_modified_and_new_files(self):
        (self.repo / "src/model.py").write_text("MODEL = 2\n", encoding="utf-8")
        (self.repo / "src/new.py").write_text("NEW = True\n", encoding="utf-8")
        result = self.check_scope("src")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("2 changed path(s)", result.stdout)

    def test_rejects_change_outside_ownership(self):
        (self.repo / "README.md").write_text("changed\n", encoding="utf-8")
        result = self.check_scope("src/**")
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("README.md", result.stdout)

    def test_accepts_file_glob(self):
        (self.repo / "src/model.py").write_text("MODEL = 3\n", encoding="utf-8")
        self.assertEqual(self.check_scope("src/*.py").returncode, 0)

    def test_single_glob_does_not_cross_directory(self):
        (self.repo / "src/deep").mkdir()
        (self.repo / "src/deep/secret.py").write_text("SECRET = 1\n", encoding="utf-8")
        result = self.check_scope("src/*.py")
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("src/deep/secret.py", result.stdout)

    def test_double_glob_crosses_directories(self):
        (self.repo / "src/a/b").mkdir(parents=True)
        (self.repo / "src/a/b/model.py").write_text("MODEL = 4\n", encoding="utf-8")
        self.assertEqual(self.check_scope("src/**/*.py").returncode, 0)

    def test_deny_overrides_allow(self):
        (self.repo / "src/generated").mkdir()
        (self.repo / "src/generated/model.py").write_text("AUTO = 1\n", encoding="utf-8")
        result = self.check_scope("src", denied=("src/generated",))
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)

    def test_checks_committed_diff_since_base(self):
        (self.repo / "README.md").write_text("committed outside\n", encoding="utf-8")
        self.git("add", "README.md")
        self.git("commit", "-qm", "outside ownership")
        self.assertEqual(self.check_scope("src").returncode, 1)

    def test_rejects_scope_escaping_repo(self):
        result = self.check_scope("../other")
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("invalid scope", result.stderr)

    def test_rename_checks_source_and_destination(self):
        self.git("mv", "README.md", "src/README.md")
        result = self.check_scope("src")
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("README.md", result.stdout)

    def test_rejects_option_shaped_base(self):
        result = subprocess.run([sys.executable, str(SCRIPT), "--repo", str(self.repo),
                                 "--base=-p", "--allow", "src"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("invalid base ref", result.stderr)


if __name__ == "__main__":
    unittest.main()
