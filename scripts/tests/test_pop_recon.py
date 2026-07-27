#!/usr/bin/env python3
"""Tests for the deterministic recon report (pop_recon.py)."""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parent.parent / "pop_recon.py"


def run_recon(target: Path, *extra: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(target), *extra],
        capture_output=True, text=True,
    )


class PopReconCodeFixtureTest(unittest.TestCase):
    """Code base with manifests, entry point, config and CI."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name) / "proj"
        self.root.mkdir()
        (self.root / "src").mkdir()
        (self.root / "src/main.py").write_text(
            "def main():\n    pass\n\n\nif __name__ == '__main__':\n    main()\n",
            encoding="utf-8",
        )
        (self.root / "src/util.py").write_text("VALUE = 1\n", encoding="utf-8")
        (self.root / "package.json").write_text(
            '{"dependencies": {"react": "^18.0.0"}, '
            '"devDependencies": {"eslint": "^9.0.0"}}\n',
            encoding="utf-8",
        )
        (self.root / "go.mod").write_text(
            "module example.com/proj\n\ngo 1.21\n\nrequire (\n"
            "\tgithub.com/foo/bar v1.2.3\n)\n",
            encoding="utf-8",
        )
        (self.root / "pyproject.toml").write_text(
            "[project]\nname = \"proj\"\n"
            "dependencies = [\"requests>=2.0\", \"click\"]\n",
            encoding="utf-8",
        )
        (self.root / "Cargo.toml").write_text(
            "[package]\nname = \"proj\"\n\n[dependencies]\nserde = \"1.0\"\n",
            encoding="utf-8",
        )
        (self.root / "Dockerfile").write_text("FROM python:3.12\n", encoding="utf-8")
        (self.root / ".github").mkdir()
        (self.root / ".github/workflows").mkdir()
        (self.root / ".github/workflows/ci.yml").write_text(
            "name: CI\non: [push]\n", encoding="utf-8"
        )
        (self.root / "node_modules").mkdir()
        (self.root / "node_modules/ignored.js").write_text("IGNORED\n", encoding="utf-8")

    def test_tree_ignores_build_and_vcs_folders(self):
        result = run_recon(self.root)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("ignored.js", result.stdout)
        self.assertIn("main.py", result.stdout)

    def test_languages_loc_present(self):
        result = run_recon(self.root)

        self.assertIn("Languages/LOC", result.stdout)
        self.assertIn(".py", result.stdout)

    def test_manifests_parsed(self):
        result = run_recon(self.root)

        self.assertIn("react", result.stdout)
        self.assertIn("eslint", result.stdout)
        self.assertIn("github.com/foo/bar", result.stdout)
        self.assertIn("requests", result.stdout)
        self.assertIn("click", result.stdout)
        self.assertIn("serde", result.stdout)

    def test_entry_points_configs_ci_detected(self):
        result = run_recon(self.root)

        self.assertIn("src/main.py", result.stdout)
        self.assertIn("Dockerfile", result.stdout)
        self.assertIn(".github/workflows/ci.yml", result.stdout)

    def test_no_writing_mode_in_a_code_base(self):
        result = run_recon(self.root)

        self.assertNotIn("Writing mode", result.stdout)


class PopReconWritingFixtureTest(unittest.TestCase):
    """Mostly-markdown base: writing mode enabled."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name) / "notes"
        self.root.mkdir()
        (self.root / "a.md").write_text(
            "---\ntitle: A\nauthor: user\n---\n\n"
            "# Chapter 1\n\nSample text with a few words here.\n\n"
            "## Section 1.1\n\nMore text.\n",
            encoding="utf-8",
        )
        (self.root / "b.md").write_text(
            "# Chapter 2\n\nAnother text with no frontmatter.\n", encoding="utf-8"
        )
        (self.root / "c.txt").write_text("loose note\n", encoding="utf-8")

    def test_writing_mode_with_headings_wordcount_and_frontmatter(self):
        result = run_recon(self.root)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Writing mode", result.stdout)
        self.assertIn("Chapter 1", result.stdout)
        self.assertIn("Section 1.1", result.stdout)
        self.assertIn("a.md", result.stdout)
        self.assertIn("author, title", result.stdout)
        self.assertIn("b.md", result.stdout)


class PopReconWithoutGitTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name) / "no_git"
        self.root.mkdir()
        (self.root / "file.txt").write_text("content\n", encoding="utf-8")

    def test_degrades_gracefully_without_git(self):
        result = run_recon(self.root)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Hotspots", result.stdout)
        self.assertIn("no git repository", result.stdout)
        # the remaining sections are still there
        self.assertIn("Languages/LOC", result.stdout)
        self.assertIn("Entry points/configs/CI", result.stdout)


class PopReconWithGitTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name) / "with_git"
        self.root.mkdir()
        self.git("init", "-q")
        self.git("config", "user.email", "test@example.com")
        self.git("config", "user.name", "PoP Test")
        (self.root / "file.py").write_text("X = 1\n", encoding="utf-8")
        self.git("add", ".")
        self.git("commit", "-qm", "initial")
        (self.root / "file.py").write_text("X = 2\n", encoding="utf-8")
        self.git("add", ".")
        self.git("commit", "-qm", "change file")

    def git(self, *args: str) -> None:
        subprocess.run(
            ["git", "-C", str(self.root), *args],
            check=True, capture_output=True, text=True,
        )

    def test_hotspots_by_git_churn(self):
        result = run_recon(self.root)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Hotspots by git churn", result.stdout)
        self.assertIn("file.py", result.stdout)
        self.assertIn("2 commit(s)", result.stdout)


class PopReconDeterminismTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name) / "det"
        self.root.mkdir()
        (self.root / "src").mkdir()
        (self.root / "src/a.py").write_text("A = 1\n", encoding="utf-8")
        (self.root / "src/b.py").write_text("B = 2\n", encoding="utf-8")

    def test_two_runs_produce_identical_output(self):
        first = run_recon(self.root)
        second = run_recon(self.root)

        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertEqual(first.stdout, second.stdout)


class PopReconOutputFlagTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name) / "proj"
        self.root.mkdir()
        (self.root / "readme.md").write_text("# Title\n", encoding="utf-8")

    def test_output_writes_file_with_default_name(self):
        workdir = Path(self._tmp.name) / "workdir"
        workdir.mkdir()
        result = subprocess.run(
            [sys.executable, str(SCRIPT), str(self.root), "--output"],
            capture_output=True, text=True, cwd=str(workdir),
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "")
        output_file = workdir / "RECON.md"
        self.assertTrue(output_file.is_file())
        self.assertIn("Recon of", output_file.read_text(encoding="utf-8"))

    def test_missing_directory_fails(self):
        result = run_recon(self.root / "does_not_exist")

        self.assertEqual(result.returncode, 2)
        self.assertIn("error", result.stderr)


if __name__ == "__main__":
    unittest.main()
