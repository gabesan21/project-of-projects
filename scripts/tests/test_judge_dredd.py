#!/usr/bin/env python3
"""Tests of the Judge Dredd gate rules in `pop_validate`.

Covers the `.verify.md` cap (80), the historical caps of the retired
adversarial-gate artifacts (defense 30, accusation 50, judgment 40) and the
prohibition of those artifacts in a card created on or after
`JUDGE_DREDD_SINCE`. Fixture: a mini-vault in a TemporaryDirectory with the
root kanban. Stdlib only.

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

PRE_CUT = "2026-08-01"  # earlier than JUDGE_DREDD_SINCE: tolerated history

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
updated: 2026-08-04
---

# {id}

- [x] Ready to plan
"""


class JudgeDreddTest(unittest.TestCase):
    """Mini-vault with the root kanban and one card per case."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name) / "vault"
        for stage in poplib.STAGES:
            (self.root / "kanban" / stage).mkdir(parents=True)

    def make_task(self, task_id, stage="005_closing", yolo="true",
                  size="L", critical="false",
                  created=pop_validate.JUDGE_DREDD_SINCE):
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

    def check_cap(self, suffix, limit, stage, created):
        folder = self.make_task(f"1.1.1-cap{suffix.replace('.', '-')}",
                                stage=stage, created=created)
        artifact = folder / f"{folder.name}{suffix}"
        artifact.write_text("line\n" * limit, encoding="utf-8")
        self.assert_valid()

        artifact.write_text("line\n" * (limit + 1), encoding="utf-8")
        self.assert_invalid(f"{limit + 1} lines (max. {limit})")

    def test_verify_cap_is_80_lines(self):
        self.check_cap(".verify.md", 80, "005_closing",
                       pop_validate.JUDGE_DREDD_SINCE)

    def test_historical_defense_cap_is_30_lines(self):
        self.check_cap(".defense.md", 30, "002_planning", PRE_CUT)

    def test_historical_accusation_cap_is_50_lines(self):
        self.check_cap(".accusation.md", 50, "005_closing", PRE_CUT)

    def test_historical_judgment_cap_is_40_lines(self):
        self.check_cap(".judgment.md", 40, "005_closing", PRE_CUT)

    def test_historical_cap_applies_per_round(self):
        """The `.r<n>` infix sits before the suffix, so each artifact's cap
        reaches every round — the second accusation also fits in 50 lines."""
        folder = self.make_task("1.1.10-cap-per-round", created=PRE_CUT)
        artifact = folder / f"{folder.name}.r2.accusation.md"
        artifact.write_text("line\n" * 50, encoding="utf-8")
        self.assertEqual(pop_validate.note_limit(artifact), 50)
        self.assert_valid()

        artifact.write_text("line\n" * 51, encoding="utf-8")
        self.assert_invalid("51 lines (max. 50)")

    def test_verify_template_stays_under_the_ordinary_note_cap(self):
        """Negative case: the ruler matches by the task artifact's suffix,
        never by a template name — a false positive in `_templates/` is a
        defect."""
        template = self.root / "_templates" / "TASK-VERIFY.md"
        self.assertEqual(pop_validate.note_limit(template), 150)
        template.parent.mkdir(parents=True)
        template.write_text("line\n" * 150, encoding="utf-8")
        self.assert_valid()

    # --- verdict markers ----------------------------------------------

    def write_verify(self, folder, *markers):
        (folder / f"{folder.name}.verify.md").write_text(
            "# Judgment\n\n" + "\n".join(markers) + "\n", encoding="utf-8")

    def test_verify_without_markers_is_tolerated_legacy(self):
        folder = self.make_task("1.1.20-verify-legacy")
        self.write_verify(folder, "## Round 1", "- **Decision:** approved.")
        self.assert_valid()

    def test_verify_with_coherent_markers_is_valid(self):
        folder = self.make_task("1.1.21-verify-coherent")
        self.write_verify(
            folder,
            "<!-- pop-verdict round=1 decision=execucao -->",
            "<!-- pop-delta round=1 kind=execucao pontual=false "
            "paths=src/a.ts -->",
            "<!-- pop-verdict round=2 decision=aprovada -->")
        self.assert_valid()

    def test_duplicated_round_is_a_violation(self):
        # One judge per round: re-judging the same round is the bug that
        # inflated the counters in the field.
        folder = self.make_task("1.1.22-duplicated-round")
        self.write_verify(
            folder,
            "<!-- pop-verdict round=1 decision=execucao -->",
            "<!-- pop-delta round=1 kind=execucao pontual=false -->",
            "<!-- pop-verdict round=1 decision=execucao -->")
        self.assert_invalid("one judge per round")

    def test_verdict_after_approval_is_a_violation(self):
        folder = self.make_task("1.1.23-after-approval")
        self.write_verify(
            folder,
            "<!-- pop-verdict round=1 decision=aprovada -->",
            "<!-- pop-verdict round=2 decision=execucao -->",
            "<!-- pop-delta round=2 kind=execucao pontual=false -->")
        self.assert_invalid("approval is terminal")

    def test_return_without_the_rounds_delta_is_a_violation(self):
        folder = self.make_task("1.1.24-no-delta")
        self.write_verify(
            folder, "<!-- pop-verdict round=1 decision=execucao -->")
        self.assert_invalid("without `pop-delta round=1`")

    def test_invalid_decision_and_kind_are_violations(self):
        folder = self.make_task("1.1.25-enums")
        self.write_verify(
            folder,
            "<!-- pop-verdict round=1 decision=rejected -->",
            "<!-- pop-delta round=1 kind=defect pontual=maybe -->")
        result = self.assert_invalid("invalid decision")
        self.assertIn("invalid kind", result.stdout)
        self.assertIn("invalid pontual", result.stdout)

    # --- retired artifacts --------------------------------------------

    def test_absence_of_artifacts_is_never_a_violation(self):
        self.make_task("1.1.2-no-artifact")
        self.make_task("1.1.3-no-artifact-simple", size="S")
        self.assert_valid()

    def test_verify_is_expected_in_any_yolo_task(self):
        for yolo, size, critical in (("true", "M", "false"),
                                     ("true", "L", "false"),
                                     ("true", "S", "true")):
            with self.subTest(size=size, critical=critical):
                task_id = f"1.1.4-verify-{size}-{critical}"
                folder = self.make_task(task_id, yolo=yolo, size=size,
                                        critical=critical)
                (folder / f"{task_id}.verify.md").write_text(
                    "verdict\n", encoding="utf-8")
        self.assert_valid()

    def test_retired_artifact_in_a_new_card_is_a_violation(self):
        for suffix in pop_validate.RETIRED_GATE_ARTIFACTS:
            with self.subTest(suffix=suffix):
                task_id = f"1.1.5-retired{suffix.replace('.', '-')}"
                folder = self.make_task(task_id)
                artifact = folder / f"{task_id}{suffix}"
                artifact.write_text("objection\n", encoding="utf-8")
                self.assert_invalid(f"{task_id}{suffix}:1: `{suffix}` "
                                    "retired")
                artifact.unlink()

    def test_retired_artifact_per_round_in_a_new_card_is_a_violation(self):
        """The scan is per family: the round infix does not hide the retired
        artifact."""
        folder = self.make_task("1.1.6-retired-r1")
        (folder / f"{folder.name}.r1.accusation.md").write_text(
            "objection\n", encoding="utf-8")
        self.assert_invalid("1.1.6-retired-r1.r1.accusation.md:1: "
                            "`.accusation.md` retired")

    def test_history_in_a_pre_cutoff_card_is_tolerated(self):
        """A card older than the cutoff may carry the whole adversarial gate —
        including coexisting with the `.verify.md` of its pending judgment."""
        folder = self.make_task("1.1.7-history", created=PRE_CUT)
        for suffix in (".defense.md", ".r1.accusation.md", ".r1.judgment.md",
                       ".r2.accusation.md", ".r2.judgment.md", ".verify.md"):
            (folder / f"{folder.name}{suffix}").write_text(
                "line\n", encoding="utf-8")
        self.assert_valid()


if __name__ == "__main__":
    unittest.main()
