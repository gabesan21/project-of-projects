#!/usr/bin/env python3
"""Tests of the adversarial-gate rules in `pop_validate`.

Covers the caps of the three artifacts (defense 30, accusation 50, judgment 40)
and the exclusivity between the two configurations of act 1 of `005_closing`.
Fixture: a mini-vault in a TemporaryDirectory with the root kanban. Stdlib only.

Usage:
    python3 -m unittest discover -s scripts/tests -v   (from the vault root)
"""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent
# The PoP poplib shadows the stdlib one: make sure we import the right one.
sys.modules.pop("poplib", None)
sys.path.insert(0, str(SCRIPTS))
import poplib  # noqa: E402
import pop_validate  # noqa: E402

assert hasattr(poplib, "discover_projects"), "imported the wrong poplib (stdlib)"

CARD = """---
id: {id}
project: pop
origin: roadmap
epoch: 1
phase: "1.1"
stage: {stage}
yolo: {yolo}
size: {size}
critical: {critical}
created: {created}
updated: 2026-07-27
---

# {id}

- [x] Ready to plan
"""


class GateAdversarialTest(unittest.TestCase):
    """Mini-vault with the root kanban and one card per configuration."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name) / "vault"
        for stage in poplib.STAGES:
            (self.root / "kanban" / stage).mkdir(parents=True)

    def make_task(self, task_id, stage="005_closing", yolo="true",
                  size="L", critical="false",
                  created=pop_validate.GATE_ADVERSARIAL_SINCE):
        """Creates the task folder with the card and returns the folder."""
        folder = self.root / "kanban" / stage / task_id
        folder.mkdir(parents=True, exist_ok=True)
        (folder / f"{task_id}.md").write_text(
            CARD.format(id=task_id, stage=stage, yolo=yolo, size=size,
                        critical=critical, created=created), encoding="utf-8")
        return folder

    def validate(self):
        return subprocess.run(
            [sys.executable, str(SCRIPTS / "pop_validate.py"),
             "--vault", str(self.root)], capture_output=True, text=True)

    def assert_valid(self):
        result = self.validate()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return result

    def assert_invalid(self, needle):
        result = self.validate()
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(needle, result.stdout)
        return result

    # --- caps ---------------------------------------------------------

    def check_cap(self, suffix, limit, stage):
        folder = self.make_task(f"1.1.1-cap{suffix.replace('.', '-')}",
                                stage=stage)
        artifact = folder / f"{folder.name}{suffix}"
        artifact.write_text("line\n" * limit, encoding="utf-8")
        self.assert_valid()

        artifact.write_text("line\n" * (limit + 1), encoding="utf-8")
        self.assert_invalid(f"{limit + 1} lines (max. {limit})")

    def test_defense_cap_is_30_lines(self):
        self.check_cap(".defense.md", 30, "002_planning")

    def test_accusation_cap_is_50_lines(self):
        self.check_cap(".accusation.md", 50, "005_closing")

    def test_judgment_cap_is_40_lines(self):
        self.check_cap(".judgment.md", 40, "005_closing")

    def test_cap_applies_per_round(self):
        """The `.r<n>` infix sits before the suffix, so each artifact's cap
        reaches every round — the second accusation also fits in 50 lines."""
        folder = self.make_task("1.1.10-cap-per-round")
        artifact = folder / f"{folder.name}.r2.accusation.md"
        artifact.write_text("line\n" * 50, encoding="utf-8")
        self.assertEqual(pop_validate.note_limit(artifact), 50)
        self.assert_valid()

        artifact.write_text("line\n" * 51, encoding="utf-8")
        self.assert_invalid("51 lines (max. 50)")

    def test_defense_template_stays_under_the_ordinary_note_cap(self):
        """Negative case: the ruler matches the task artifact's suffix, never a
        template name — a false positive in `_templates/` is a defect."""
        template = self.root / "_templates" / "TASK-DEFENSE.md"
        self.assertEqual(pop_validate.note_limit(template), 150)
        template.parent.mkdir(parents=True)
        template.write_text("line\n" * 150, encoding="utf-8")
        self.assert_valid()

    # --- exclusivity --------------------------------------------------

    def test_absence_of_the_three_artifacts_is_never_a_violation(self):
        self.make_task("1.1.2-no-artifact")                     # trigger on
        self.make_task("1.1.3-no-artifact-simple", size="S")    # trigger off
        self.assert_valid()

    def test_verify_does_not_coexist_with_judgment(self):
        folder = self.make_task("1.1.4-coexistence")
        for suffix in (".verify.md", ".judgment.md"):
            (folder / f"{folder.name}{suffix}").write_text(
                "verdict\n", encoding="utf-8")
        self.assert_invalid("1.1.4-coexistence.verify.md:1: `.verify.md` "
                            "outside this task's act-1 configuration")

    def test_pair_artifact_in_a_card_without_the_trigger_is_a_violation(self):
        for suffix in (".accusation.md", ".judgment.md"):
            with self.subTest(suffix=suffix):
                task_id = f"1.1.5-no-trigger{suffix.replace('.', '-')}"
                folder = self.make_task(task_id, yolo="true", size="M",
                                        critical="false")
                artifact = folder / f"{task_id}{suffix}"
                artifact.write_text("objection\n", encoding="utf-8")
                self.assert_invalid(f"{task_id}{suffix}:1: `{suffix}` outside "
                                    "this task's act-1 configuration")
                artifact.unlink()

    def test_verify_in_a_card_with_the_trigger_is_a_violation(self):
        for yolo, size, critical in (("true", "L", "false"),
                                     ("true", "S", "true")):
            with self.subTest(size=size, critical=critical):
                task_id = f"1.1.6-trigger-{size}-{critical}"
                folder = self.make_task(task_id, yolo=yolo, size=size,
                                        critical=critical)
                (folder / f"{task_id}.verify.md").write_text(
                    "verdict\n", encoding="utf-8")
                self.assert_invalid(f"{task_id}.verify.md:1: `.verify.md` "
                                    "outside this task's act-1 configuration")
                (folder / f"{task_id}.verify.md").unlink()

    # --- transition clause ---------------------------------------------

    def test_verify_in_a_card_older_than_the_cut_off_is_not_a_violation(self):
        """This side of the cut-off: the card went through 002 when the defense
        did not exist, runs in configuration B and its `.verify.md` is what is
        expected."""
        folder = self.make_task("1.1.8-in-flight", yolo="true", size="L",
                                critical="true", created="2026-07-23")
        (folder / f"{folder.name}.verify.md").write_text(
            "verdict\n", encoding="utf-8")
        self.assert_valid()

    def test_verify_in_a_card_from_the_cut_off_on_is_a_violation(self):
        """The other side: from the effective date on, the clause does not reach."""
        folder = self.make_task("1.1.9-post-cut-off", yolo="true", size="L",
                                critical="true",
                                created=pop_validate.GATE_ADVERSARIAL_SINCE)
        (folder / f"{folder.name}.verify.md").write_text(
            "verdict\n", encoding="utf-8")
        self.assert_invalid("1.1.9-post-cut-off.verify.md:1: `.verify.md` "
                            "outside this task's act-1 configuration")

    def test_pair_in_a_card_older_than_the_cut_off_is_a_violation(self):
        """The mixed case a wholesale exemption used to hide: the pre-cut-off
        card runs in configuration B, so the `.verify.md` passes, but the pair's
        artifact next to it is still outside any valid configuration."""
        for suffix in (".accusation.md", ".judgment.md"):
            with self.subTest(suffix=suffix):
                task_id = f"1.1.11-mixed{suffix.replace('.', '-')}"
                folder = self.make_task(task_id, yolo="true", size="L",
                                        critical="true", created="2026-07-23")
                (folder / f"{task_id}.verify.md").write_text(
                    "verdict\n", encoding="utf-8")
                artifact = folder / f"{task_id}{suffix}"
                artifact.write_text("objection\n", encoding="utf-8")
                self.assert_invalid(f"{task_id}{suffix}:1: `{suffix}` outside "
                                    "this task's act-1 configuration")
                artifact.unlink()

    def test_verify_per_round_in_a_card_with_the_trigger_is_a_violation(self):
        """The sweep is per family: the round infix does not hide an artifact
        of the wrong configuration."""
        folder = self.make_task("1.1.12-verify-r2")
        (folder / f"{folder.name}.r2.verify.md").write_text(
            "verdict\n", encoding="utf-8")
        self.assert_invalid("1.1.12-verify-r2.r2.verify.md:1: `.verify.md` "
                            "outside this task's act-1 configuration")

    def test_pair_per_round_in_a_card_without_the_trigger_is_a_violation(self):
        folder = self.make_task("1.1.13-pair-r1", size="M")
        (folder / f"{folder.name}.r1.accusation.md").write_text(
            "objection\n", encoding="utf-8")
        self.assert_invalid("1.1.13-pair-r1.r1.accusation.md:1: "
                            "`.accusation.md` outside this task's act-1")

    def test_pair_per_round_in_a_card_with_the_trigger_is_expected(self):
        folder = self.make_task("1.1.14-pair-expected")
        for suffix in (".r1.accusation.md", ".r1.judgment.md",
                       ".r2.accusation.md", ".r2.judgment.md"):
            (folder / f"{folder.name}{suffix}").write_text(
                "line\n", encoding="utf-8")
        self.assert_valid()

    def test_verify_in_a_card_without_the_trigger_is_the_expected_configuration(self):
        for yolo, size, critical in (("true", "M", "false"),
                                     ("false", "L", "false")):
            with self.subTest(yolo=yolo, size=size):
                task_id = f"1.1.7-reviewer-{yolo}-{size}"
                folder = self.make_task(task_id, yolo=yolo, size=size,
                                        critical=critical)
                (folder / f"{task_id}.verify.md").write_text(
                    "verdict\n", encoding="utf-8")
        self.assert_valid()


if __name__ == "__main__":
    unittest.main()
