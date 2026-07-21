#!/usr/bin/env python3

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import poplib

SCRIPTS = Path(__file__).resolve().parent.parent


class RoadmapLifecycleTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "vault"
        self.task = "0.1.1-completed-fix"
        self.epoch = self.root / "roadmap/0-maintenance.md"
        self.card = self.root / "kanban/006_done" / self.task / f"{self.task}.md"
        self.memory = self.root / "memory" / f"{self.task}.md"
        self.card.parent.mkdir(parents=True)
        self.memory.parent.mkdir(parents=True)
        self.epoch.parent.mkdir(parents=True)
        self.card.write_text(
            f"---\nid: 0.1.1\nproject: pop\nstage: 006_done\n"
            "created: 2026-07-21\nupdated: 2026-07-21\n---\n",
            encoding="utf-8")
        self.epoch.write_text(
            "# Epoch 0\n\n## Phase 0.1 — maintenance\n\n"
            "| Task | Description | Status |\n|---|---|---|\n"
            f"| [[{self.task}]] | fix | completed |\n"
            "| `0.1.2-open` | next | not started |\n",
            encoding="utf-8")

    def run_cli(self, script, *args):
        return subprocess.run(
            [sys.executable, str(SCRIPTS / script), *args, "--vault", str(self.root)],
            capture_output=True, text=True)

    def write_memory(self, *, task=None, commit="abc123", include_pr=True):
        task = task or self.task
        pr = "pr:\n" if include_pr else ""
        self.memory.write_text(
            "---\n"
            f"task: {task}\nproject: pop\nstarted: 2026-07-20\n"
            f"finished: 2026-07-21\ncommit: {commit}\n{pr}---\n\n# Memory\n",
            encoding="utf-8")

    def test_close_removes_only_task_and_preserves_epoch_phase_and_open_task(self):
        self.write_memory()
        result = self.run_cli("pop_roadmap.py", "close", self.task)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        text = self.epoch.read_text(encoding="utf-8")
        self.assertNotIn(self.task, text)
        self.assertIn("# Epoch 0", text)
        self.assertIn("## Phase 0.1", text)
        self.assertIn("0.1.2-open", text)

    def test_close_aborts_without_valid_memory_and_preserves_row(self):
        self.write_memory(task="0.1.9-other")
        result = self.run_cli("pop_roadmap.py", "close", self.task)
        self.assertEqual(result.returncode, 1)
        self.assertIn(self.task, self.epoch.read_text(encoding="utf-8"))

    def test_close_aborts_without_pr_key_but_accepts_empty_pr(self):
        self.write_memory(include_pr=False)
        result = self.run_cli("pop_roadmap.py", "close", self.task)
        self.assertEqual(result.returncode, 1)
        self.assertIn(self.task, self.epoch.read_text(encoding="utf-8"))
        self.write_memory(include_pr=True)
        result = self.run_cli("pop_roadmap.py", "close", self.task)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_duplicate_close_aborts_without_writing_any_epoch(self):
        self.write_memory()
        duplicate = self.root / "roadmap/1-other.md"
        duplicate.write_text(
            f"# Epoch 1\n\n## Phase 1.1\n\n| Task | Description | Status |\n"
            f"|---|---|---|\n| [[{self.task}]] | duplicate | completed |\n",
            encoding="utf-8")
        before_epoch = self.epoch.read_bytes()
        before_duplicate = duplicate.read_bytes()
        result = self.run_cli("pop_roadmap.py", "close", self.task)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(self.epoch.read_bytes(), before_epoch)
        self.assertEqual(duplicate.read_bytes(), before_duplicate)

    def test_validator_reports_residual_task_with_memory(self):
        self.write_memory()
        result = self.run_cli("pop_validate.py")
        self.assertEqual(result.returncode, 1)
        self.assertIn("completed task left in roadmap", result.stdout)

    def test_validator_ignores_open_task_without_memory(self):
        result = self.run_cli("pop_validate.py")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_pop_worktree_rejects_meta_pop_and_reports_main(self):
        route = self.run_cli("pop_worktree.py", "route", self.task)
        self.assertEqual(route.returncode, 0, route.stdout + route.stderr)
        self.assertIn("worktree=no", route.stdout)
        self.assertIn("integration_branch=main", route.stdout)
        add = self.run_cli("pop_worktree.py", "add", self.task)
        self.assertEqual(add.returncode, 1)
        self.assertIn("directly on main", add.stdout)
        self.assertFalse((self.root / "worktrees").exists())

    def test_pop_worktree_reports_external_yolo_develop_to_main(self):
        project = self.root / "categories/applications/example"
        task = "1.1.1-external-yolo"
        card = project / "pop/kanban/004_processing" / task / f"{task}.md"
        card.parent.mkdir(parents=True)
        card.write_text(
            "---\nid: 1.1.1\nproject: applications/example\n"
            "stage: 004_processing\nyolo: true\ncreated: 2026-07-21\n"
            "updated: 2026-07-21\n---\n", encoding="utf-8")
        route = self.run_cli("pop_worktree.py", "route", task)
        self.assertEqual(route.returncode, 0, route.stdout + route.stderr)
        self.assertIn("worktree=yes", route.stdout)
        self.assertIn("integration_branch=develop", route.stdout)
        self.assertIn("target_branch=main", route.stdout)
        self.assertIn("merge_owner=user", route.stdout)


if __name__ == "__main__":
    unittest.main()
