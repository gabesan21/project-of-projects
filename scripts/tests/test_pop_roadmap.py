#!/usr/bin/env python3
"""Regressions of the safe cleanup of completed tasks from the roadmap and
modifications: `pop_roadmap.py close` removes the task's row in
`roadmap/*.md` or `modifications/*.md` and, for a single-task modification,
removes only the wikilink from the `MODIFICATIONS.md` row."""

import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent

TASK_R = "1.1.1-completed-fix"        # roadmap task (epoch 1, phase 1.1)
TASK_M = "M-1.1-completed-tweak"      # multi-task modification task (M-1)
TASK_S = "M-2.1-completed-hotfix"     # single-task modification (index only)

NUMERIC = re.compile(r"(?:\d+\.\d+\.\d+|M-\d+\.\d+)")


class CloseLifecycleTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "vault"
        (self.root / "kanban/006_done").mkdir(parents=True)
        (self.root / "memory").mkdir(parents=True)
        (self.root / "roadmap").mkdir(parents=True)
        (self.root / "modifications").mkdir(parents=True)

    def run_cli(self, script, *args):
        return subprocess.run(
            [sys.executable, str(SCRIPTS / script), *args, "--vault", str(self.root)],
            capture_output=True, text=True)

    def write_card(self, task, stage="006_done"):
        numeric = NUMERIC.match(task).group(0)
        fields = {"id": numeric, "project": "pop", "stage": stage,
                  "created": "2026-07-20", "updated": "2026-07-21"}
        if numeric.startswith("M-"):
            fields.update(origin="modifications",
                          modification=numeric.rsplit(".", 1)[0])
        else:
            fields.update(origin="roadmap", epoch=numeric.split(".")[0],
                          phase=f'"{numeric.rsplit(".", 1)[0]}"')
        folder = self.root / "kanban" / stage / task
        folder.mkdir(parents=True)
        card = folder / f"{task}.md"
        card.write_text(
            "---\n" + "\n".join(f"{k}: {v}" for k, v in fields.items())
            + "\n---\n", encoding="utf-8")
        return card

    def write_memory(self, task, *, memory_task=None, commit="abc123",
                     include_pr=True):
        pr = "pr:\n" if include_pr else ""
        (self.root / "memory" / f"{task}.md").write_text(
            "---\n"
            f"task: {memory_task or task}\nproject: pop\nstarted: 2026-07-20\n"
            f"finished: 2026-07-21\ncommit: {commit}\n{pr}---\n\n# Memory\n",
            encoding="utf-8")

    def write_epoch(self):
        epoch = self.root / "roadmap/1-core.md"
        epoch.write_text(
            "# Epoch 1\n\n## Phase 1.1 — base\n\n"
            "| Task | Description | Status |\n|---|---|---|\n"
            f"| [[{TASK_R}]] | fix | completed |\n"
            "| `1.1.2-open` | next | not started |\n",
            encoding="utf-8")
        return epoch

    def write_modification(self):
        mod = self.root / "modifications/m-1-tweaks.md"
        mod.write_text(
            "# M-1 — tweaks\n\n"
            "| Task | Description | Status |\n|---|---|---|\n"
            f"| [[{TASK_M}]] | tweak | completed |\n"
            "| `M-1.2-open` | next | not started |\n",
            encoding="utf-8")
        return mod

    def write_index(self):
        index = self.root / "MODIFICATIONS.md"
        index.write_text(
            "# Modifications\n\n"
            "| # | Modification | Description | Status |\n|---|---|---|---|\n"
            "| M-1 | [[modifications/m-1-tweaks\\|tweaks]] | tweaks "
            "| in progress |\n"
            f"| M-2 | hotfix [[{TASK_S}]] | one-off hotfix | in progress |\n",
            encoding="utf-8")
        return index


class CloseRoadmapTest(CloseLifecycleTest):
    def test_close_removes_only_task_and_preserves_epoch_phase_and_open_task(self):
        self.write_card(TASK_R)
        self.write_memory(TASK_R)
        epoch = self.write_epoch()
        result = self.run_cli("pop_roadmap.py", "close", TASK_R)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        text = epoch.read_text(encoding="utf-8")
        self.assertNotIn(TASK_R, text)
        self.assertIn("# Epoch 1", text)
        self.assertIn("## Phase 1.1", text)
        self.assertIn("1.1.2-open", text)

    def test_close_aborts_without_pr_key_but_accepts_empty_pr(self):
        self.write_card(TASK_R)
        epoch = self.write_epoch()
        self.write_memory(TASK_R, include_pr=False)
        result = self.run_cli("pop_roadmap.py", "close", TASK_R)
        self.assertEqual(result.returncode, 1)
        self.assertIn(TASK_R, epoch.read_text(encoding="utf-8"))
        self.write_memory(TASK_R, include_pr=True)
        result = self.run_cli("pop_roadmap.py", "close", TASK_R)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


class CloseModificationTest(CloseLifecycleTest):
    def test_close_multitask_removes_row_and_preserves_modification_and_open(self):
        self.write_card(TASK_M)
        self.write_memory(TASK_M)
        mod = self.write_modification()
        index = self.write_index()
        before_index = index.read_bytes()
        result = self.run_cli("pop_roadmap.py", "close", TASK_M)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        text = mod.read_text(encoding="utf-8")
        self.assertNotIn(TASK_M, text)
        self.assertIn("# M-1 — tweaks", text)
        self.assertIn("M-1.2-open", text)
        # the modification's row in the index is never touched
        self.assertEqual(index.read_bytes(), before_index)

    def test_close_single_task_removes_only_the_index_wikilink(self):
        self.write_card(TASK_S)
        self.write_memory(TASK_S)
        index = self.write_index()
        result = self.run_cli("pop_roadmap.py", "close", TASK_S)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        text = index.read_text(encoding="utf-8")
        self.assertNotIn(f"[[{TASK_S}]]", text)
        self.assertIn(f"`{TASK_S}`", text)
        # the modification's row stays
        self.assertIn("| M-2 |", text)
        self.assertIn("in progress", text)

    def test_close_aborts_without_valid_memory_and_preserves_row(self):
        self.write_card(TASK_M)
        self.write_memory(TASK_M, memory_task="M-1.9-other")
        mod = self.write_modification()
        result = self.run_cli("pop_roadmap.py", "close", TASK_M)
        self.assertEqual(result.returncode, 1)
        self.assertIn(TASK_M, mod.read_text(encoding="utf-8"))

    def test_close_duplicate_aborts_without_writing_any_file(self):
        self.write_card(TASK_M)
        self.write_memory(TASK_M)
        mod = self.write_modification()
        duplicate = self.root / "modifications/m-9-other.md"
        duplicate.write_text(
            "# M-9\n\n| Task | Description | Status |\n|---|---|---|\n"
            f"| [[{TASK_M}]] | duplicate | completed |\n",
            encoding="utf-8")
        before_mod = mod.read_bytes()
        before_duplicate = duplicate.read_bytes()
        result = self.run_cli("pop_roadmap.py", "close", TASK_M)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(mod.read_bytes(), before_mod)
        self.assertEqual(duplicate.read_bytes(), before_duplicate)


class ResidualValidationTest(CloseLifecycleTest):
    def test_validator_reports_residual_in_roadmap(self):
        self.write_card(TASK_R)
        self.write_memory(TASK_R)
        self.write_epoch()
        result = self.run_cli("pop_validate.py")
        self.assertEqual(result.returncode, 1)
        self.assertIn("residual completed task", result.stdout)

    def test_validator_reports_residual_in_modifications(self):
        self.write_card(TASK_M)
        self.write_memory(TASK_M)
        self.write_modification()
        result = self.run_cli("pop_validate.py")
        self.assertEqual(result.returncode, 1)
        self.assertIn(TASK_M, result.stdout)

    def test_validator_reports_residual_wikilink_in_index(self):
        self.write_card(TASK_S)
        self.write_memory(TASK_S)
        self.write_index()
        result = self.run_cli("pop_validate.py")
        self.assertEqual(result.returncode, 1)
        self.assertIn(TASK_S, result.stdout)

    def test_validator_ignores_open_task_without_memory(self):
        self.write_card(TASK_R)
        self.write_epoch()
        self.write_modification()
        self.write_index()
        result = self.run_cli("pop_validate.py")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


class WorktreeConsumerTest(CloseLifecycleTest):
    def test_pop_worktree_consumer_rejects_meta_pop_and_reports_main(self):
        self.write_card(TASK_R)
        route = self.run_cli("pop_worktree.py", "route", TASK_R)
        self.assertEqual(route.returncode, 0, route.stdout + route.stderr)
        self.assertIn("worktree=no", route.stdout)
        self.assertIn("integration_branch=main", route.stdout)
        add = self.run_cli("pop_worktree.py", "add", TASK_R)
        self.assertEqual(add.returncode, 1)
        self.assertIn("directly on main", add.stdout)
        self.assertFalse((self.root / "worktrees").exists())

    def test_pop_worktree_consumer_reports_external_yolo_develop_to_main(self):
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
