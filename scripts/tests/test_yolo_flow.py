#!/usr/bin/env python3

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent
STAGES = ("001_initial_task", "002_planning", "003_human_approval",
          "004_processing", "005_closing")


class YoloFlowTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "vault"
        for stage in STAGES:
            (self.root / "kanban" / stage).mkdir(parents=True)

    def run_cli(self, script, *args):
        return subprocess.run(
            [sys.executable, str(SCRIPTS / script), *args,
             "--vault", str(self.root)], capture_output=True, text=True)

    def card(self, task, stage="003_human_approval", project="pop", **fields):
        folder = self.root / "kanban" / stage / task
        folder.mkdir(parents=True)
        data = {"id": task.split("-", 1)[0], "project": project,
                "stage": stage, "critical": "false", "yolo": "true",
                "blocked": "false", "depends_on": "[]",
                "created": "2026-07-21", "updated": "2026-07-21",
                **fields}
        text = "---\n" + "\n".join(f"{k}: {v}" for k, v in data.items())
        text += "\n---\n\n# Task\n\n## Log\n"
        path = folder / f"{task}.md"
        path.write_text(text, encoding="utf-8")
        return path

    def verify(self, task, stage, *markers):
        """Writes the task's `.verify.md` with the given machine markers."""
        folder = self.root / "kanban" / stage / task
        path = folder / f"{task}.verify.md"
        path.write_text("# Judgment\n\n" + "\n".join(markers) + "\n",
                        encoding="utf-8")
        return path

    @staticmethod
    def verdict(rnd, decision):
        return f"<!-- pop-verdict round={rnd} decision={decision} -->"

    @staticmethod
    def delta(rnd, kind, pontual="false", paths=""):
        extra = f" paths={paths}" if paths else ""
        return (f"<!-- pop-delta round={rnd} kind={kind} "
                f"pontual={pontual}{extra} -->")

    def test_two_returns_and_third_triggers_circuit_breaker(self):
        task = "1.1.1-loop-yolo"
        self.card(task)
        for attempt in (1, 2):
            result = self.run_cli("pop_move.py", task, "002_planning",
                                  "--context", f"critic-{attempt}")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            card = self.root / "kanban/002_planning" / task / f"{task}.md"
            self.assertIn(f"yolo_003_returns: {attempt}", card.read_text())
            self.assertEqual(self.run_cli("pop_move.py", task,
                                          "003_human_approval").returncode, 0)
        result = self.run_cli("pop_move.py", task, "002_planning",
                              "--context", "critic-3")
        self.assertEqual(result.returncode, 1)
        card = self.root / "kanban/003_human_approval" / task / f"{task}.md"
        text = card.read_text()
        self.assertIn("circuit_breaker: true", text)
        self.assertIn("blocked: true", text)
        self.assertTrue((card.parent / f"{task}.telemetry.json").is_file())

    def test_plan_defect_counts_as_a_plan_return(self):
        # 005_closing → 002 is a plan defect: it burns the plan counter, not
        # the execution one (the executor delivered what it was given).
        task = "1.1.3-plan-defect"
        self.card(task, stage="005_closing")
        self.verify(task, "005_closing", self.verdict(1, "lacuna"),
                    self.delta(1, "lacuna"))
        result = self.run_cli("pop_move.py", task, "002_planning",
                              "--reason", "plan defect",
                              "--return-kind", "lacuna")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        text = (self.root / "kanban/002_planning" / task
                / f"{task}.md").read_text()
        self.assertIn("yolo_003_returns: 1", text)
        self.assertNotIn("yolo_005_returns: 1", text)
        self.assertIn("return_kind: lacuna", text)

    def test_plan_defect_without_classification_does_not_move_the_folder(self):
        # Without lacuna|premissa, 002 does not know whether to amend or replan.
        task = "1.1.5-no-classification"
        self.card(task, stage="005_closing")
        result = self.run_cli("pop_move.py", task, "002_planning")
        self.assertEqual(result.returncode, 1)
        self.assertIn("CLASSIFY THE RETURN", result.stdout)
        self.assertTrue((self.root / "kanban/005_closing" / task).is_dir())
        self.assertFalse((self.root / "kanban/002_planning" / task).exists())

    def test_plan_classification_does_not_serve_the_execution_route(self):
        task = "1.1.6-incompatible-route"
        self.card(task, stage="005_closing")
        result = self.run_cli("pop_move.py", task, "004_processing",
                              "--return-kind", "premissa")
        self.assertEqual(result.returncode, 1)
        self.assertIn("INCOMPATIBLE RETURN", result.stdout)
        self.assertTrue((self.root / "kanban/005_closing" / task).is_dir())

    def test_execution_return_counts_in_the_execution_counter(self):
        task = "1.1.4-returns-execution"
        self.card(task, stage="005_closing")
        self.verify(task, "005_closing", self.verdict(1, "execucao"),
                    self.delta(1, "execucao"))
        result = self.run_cli("pop_move.py", task, "004_processing",
                              "--reason", "blocking execution issue")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        text = (self.root / "kanban/004_processing" / task
                / f"{task}.md").read_text()
        self.assertIn("yolo_005_returns: 1", text)
        self.assertNotIn("yolo_003_returns: 1", text)
        self.assertIn("return_kind: execucao", text)

    def test_return_from_005_without_verify_is_refused(self):
        # A judge that rejects without an artifact does not return.
        task = "1.1.8-no-verify"
        self.card(task, stage="005_closing")
        result = self.run_cli("pop_move.py", task, "004_processing")
        self.assertEqual(result.returncode, 1)
        self.assertIn("NO JUDGMENT", result.stdout)
        self.assertTrue((self.root / "kanban/005_closing" / task).is_dir())

    def test_approval_is_terminal_no_re_judgment(self):
        # The field bug: re-judging an approval verdict.
        task = "1.1.9-approved-terminal"
        self.card(task, stage="005_closing")
        self.verify(task, "005_closing", self.verdict(1, "aprovada"))
        result = self.run_cli("pop_move.py", task, "004_processing")
        self.assertEqual(result.returncode, 1)
        self.assertIn("APPROVAL IS TERMINAL", result.stdout)
        self.assertTrue((self.root / "kanban/005_closing" / task).is_dir())

    def test_pinpoint_delta_does_not_pay_the_full_route(self):
        task = "1.1.10-pinpoint-delta"
        self.card(task, stage="005_closing")
        self.verify(task, "005_closing", self.verdict(1, "execucao"),
                    self.delta(1, "execucao", pontual="true"))
        result = self.run_cli("pop_move.py", task, "004_processing")
        self.assertEqual(result.returncode, 1)
        self.assertIn("PINPOINT DELTA", result.stdout)

    def test_verdict_incompatible_with_the_route_is_refused(self):
        task = "1.1.11-incompatible-verdict"
        self.card(task, stage="005_closing")
        self.verify(task, "005_closing", self.verdict(1, "execucao"),
                    self.delta(1, "execucao"))
        result = self.run_cli("pop_move.py", task, "002_planning",
                              "--return-kind", "lacuna")
        self.assertEqual(result.returncode, 1)
        self.assertIn("INCOMPATIBLE VERDICT", result.stdout)

    def test_return_without_delta_is_refused(self):
        task = "1.1.12-no-delta"
        self.card(task, stage="005_closing")
        self.verify(task, "005_closing", self.verdict(1, "execucao"))
        result = self.run_cli("pop_move.py", task, "004_processing")
        self.assertEqual(result.returncode, 1)
        self.assertIn("RETURN WITHOUT DELTA", result.stdout)

    def test_telemetry_records_the_cause_of_the_return(self):
        task = "1.1.7-cause-telemetry"
        self.card(task, stage="005_closing")
        self.verify(task, "005_closing", self.verdict(1, "premissa"),
                    self.delta(1, "premissa"))
        self.assertEqual(self.run_cli(
            "pop_move.py", task, "002_planning",
            "--return-kind", "premissa").returncode, 0)
        result = self.run_cli("pop_yolo.py", "telemetry", task, "--json")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        data = json.loads(result.stdout)
        self.assertEqual(data["returns_premissa"], 1)
        self.assertEqual(data["returns_lacuna"], 0)
        self.assertEqual(data["returns_execucao"], 0)

    def test_verify_mode_is_full_for_critical_or_wrong_premise(self):
        # Only a wrong premise invalidates what has already been verified; a
        # gap and an execution failure only review the delta.
        task = "1.1.2-verify-mode"
        card = self.card(task, stage="005_closing")
        result = self.run_cli("pop_yolo.py", "verify-mode", task)
        self.assertTrue(result.stdout.startswith("differential"))

        for kind in ("lacuna", "execucao"):
            card.write_text(card.read_text().replace(
                "critical: false", f"return_kind: {kind}\ncritical: false"))
            result = self.run_cli("pop_yolo.py", "verify-mode", task)
            self.assertTrue(result.stdout.startswith("differential"),
                            f"{kind}: {result.stdout}")
            self.assertIn("delta", result.stdout)
            card.write_text(card.read_text().replace(
                f"return_kind: {kind}\n", ""))

        card.write_text(card.read_text().replace(
            "critical: false", "return_kind: premissa\ncritical: false"))
        self.assertTrue(self.run_cli(
            "pop_yolo.py", "verify-mode", task).stdout.startswith("full"))

        card.write_text(card.read_text().replace("critical: false", "critical: true"))
        result = self.run_cli("pop_yolo.py", "verify-mode", task)
        self.assertTrue(result.stdout.startswith("full"))

    def test_wave_limits_three_tasks_and_one_per_project(self):
        self.card("1.1.1-meta")
        for index in range(3):
            project = self.root / f"categories/a/p{index}"
            for stage in STAGES:
                (project / "pop/kanban" / stage).mkdir(parents=True)
            folder = project / "pop/kanban/002_planning" / f"2.1.{index + 1}-task"
            folder.mkdir(parents=True)
            (folder / f"2.1.{index + 1}-task.md").write_text(
                "---\nproject: a/p%d\nstage: 002_planning\nyolo: true\n"
                "blocked: false\ndepends_on: []\n---\n" % index, encoding="utf-8")
        result = self.run_cli("pop_yolo.py", "wave", "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(len(json.loads(result.stdout)), 3)

    def test_telemetry_summarizes_contexts_returns_and_tests(self):
        task = "1.1.3-telemetry"
        self.card(task)
        self.assertEqual(self.run_cli(
            "pop_move.py", task, "002_planning", "--context", "critic",
            "--test-seconds", "12.5").returncode, 0)
        result = self.run_cli("pop_yolo.py", "telemetry", task, "--json")
        data = json.loads(result.stdout)
        self.assertEqual(data["contexts"], 1)
        self.assertEqual(data["returns_003"], 1)
        self.assertEqual(data["test_seconds"], 12.5)

    def test_non_critical_yolo_transits_002_to_004_directly(self):
        task = "1.1.4-single-gate"
        self.card(task, stage="002_planning")
        result = self.run_cli("pop_move.py", task, "004_processing")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue(
            (self.root / "kanban/004_processing" / task).is_dir())
        self.assertFalse(
            (self.root / "kanban/002_planning" / task).exists())

    def test_critical_yolo_does_not_skip_003(self):
        task = "1.1.5-critical-gate"
        self.card(task, stage="002_planning", critical="true")
        result = self.run_cli("pop_move.py", task, "004_processing")
        self.assertEqual(result.returncode, 1)
        self.assertTrue(
            (self.root / "kanban/002_planning" / task).is_dir())
        result = self.run_cli("pop_move.py", task, "003_human_approval")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_non_yolo_does_not_skip_003(self):
        task = "1.1.6-no-single-gate"
        self.card(task, stage="002_planning", yolo="false")
        result = self.run_cli("pop_move.py", task, "004_processing")
        self.assertEqual(result.returncode, 1)
        self.assertTrue(
            (self.root / "kanban/002_planning" / task).is_dir())


class YoloReentryTest(unittest.TestCase):
    """Pre-flight of the 004→005 reentry: the diff since `return_base` must
    touch some delta path — re-presenting the same problem is refused."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "vault"
        for stage in STAGES:
            (self.root / "kanban" / stage).mkdir(parents=True)
        self.git("init", "-b", "main")
        self.git("config", "user.email", "test@example.com")
        self.git("config", "user.name", "Test")
        (self.root / "src").mkdir()
        (self.root / "src/target.ts").write_text("v1\n")
        self.task = "1.1.1-reentry"
        folder = self.root / "kanban/005_closing" / self.task
        folder.mkdir(parents=True)
        (folder / f"{self.task}.md").write_text(
            "---\nid: 1.1.1\nproject: pop\nstage: 005_closing\n"
            "critical: false\nyolo: true\nblocked: false\ndepends_on: []\n"
            "created: 2026-08-05\nupdated: 2026-08-05\n---\n\n# Task\n\n"
            "## Log\n", encoding="utf-8")
        (folder / f"{self.task}.verify.md").write_text(
            "# Judgment\n\n"
            "<!-- pop-verdict round=1 decision=execucao -->\n"
            "<!-- pop-delta round=1 kind=execucao pontual=false "
            "paths=src/target.ts -->\n", encoding="utf-8")
        self.git("add", ".")
        self.git("commit", "-m", "base")

    def git(self, *args):
        result = subprocess.run(["git", "-C", str(self.root), *args],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return result

    def run_cli(self, script, *args):
        return subprocess.run(
            [sys.executable, str(SCRIPTS / script), *args,
             "--vault", str(self.root)], capture_output=True, text=True)

    def test_reentry_without_work_on_the_delta_is_refused(self):
        result = self.run_cli("pop_move.py", self.task, "004_processing")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        card = (self.root / "kanban/004_processing" / self.task
                / f"{self.task}.md").read_text()
        self.assertIn("return_base:", card)

        result = self.run_cli("pop_move.py", self.task, "005_closing")
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("REENTRY WITHOUT WORK ON THE DELTA", result.stdout)

        (self.root / "src/target.ts").write_text("v2\n")
        result = self.run_cli("pop_move.py", self.task, "005_closing")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


class YoloDeliveryTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.repo = Path(self.tmp.name) / "repo"
        self.repo.mkdir()
        self.git("init", "-b", "develop")
        self.git("config", "user.email", "test@example.com")
        self.git("config", "user.name", "Test")
        (self.repo / "base.txt").write_text("base\n")
        self.git("add", ".")
        self.git("commit", "-m", "base")
        self.git("branch", "main")
        self.git("switch", "-c", "task/1.1.1-delivery")
        (self.repo / "feature.txt").write_text("ok\n")
        self.git("add", ".")
        self.git("commit", "-m", "feature")
        self.git("switch", "develop")
        for stage in STAGES:
            (self.repo / "pop/kanban" / stage).mkdir(parents=True)
        task = "1.1.1-delivery"
        folder = self.repo / "pop/kanban/005_closing" / task
        folder.mkdir(parents=True)
        (folder / f"{task}.md").write_text(
            "---\nproject: app/repo\nstage: 005_closing\nyolo: true\n---\n")
        self.git("add", "pop")
        self.git("commit", "-m", "harness")

    def git(self, *args):
        result = subprocess.run(["git", "-C", str(self.repo), *args],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return result

    def test_delivery_integrates_into_develop_without_touching_main(self):
        main_before = self.git("rev-parse", "main").stdout.strip()
        result = subprocess.run(
            [sys.executable, str(SCRIPTS / "pop_delivery.py"), "integrate",
             "1.1.1-delivery", "--repo", str(self.repo), "--vault", str(self.repo)],
            capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(self.git("rev-parse", "main").stdout.strip(), main_before)
        self.assertEqual(self.git("merge-base", "--is-ancestor",
                                  "task/1.1.1-delivery", "develop").returncode, 0)


if __name__ == "__main__":
    unittest.main()
