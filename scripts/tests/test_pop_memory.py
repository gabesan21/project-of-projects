#!/usr/bin/env python3
"""Regressions of the granular `memory/` layout: one folder per completion
date, a ledger `<id>.md` (≤1200 chars) indexing entries `<id>.<nn>-<slug>.md`
(≤800 chars, with an evidence wikilink), and the tolerance for flat legacy."""

import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS))

import pop_roadmap  # noqa: E402
import pop_validate  # noqa: E402

TASK = "1.1.1-test-task"
DAY = "2026-07-28"


def ledger_text(task=TASK, finished=DAY, entries=("01-did-the-thing",)):
    index = "".join(f"- [[{task}.{e}]] — what was done.\n" for e in entries)
    return (f"---\ntask: {task}\nproject: pop\nstarted: 2026-07-27\n"
            f"finished: {finished}\ncommit: abc123\npr:\n---\n\n"
            f"# {task} — test\n\n- **Delivery:** something.\n\n"
            f"## Entries\n\n{index}")


def entry_text(task=TASK, entry="01-did-the-thing", evidence=True):
    link = "- [[scripts/pop_validate.py]] — *where it lives*.\n" if evidence else "- no link.\n"
    return (f"---\ntask: {task}\nentry: {entry}\n---\n\n"
            f"# The thing done\n\nIt was done this way.\n\n## Evidence\n\n{link}")


class MemoryLayoutTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "vault"
        self.memory = self.root / "memory"
        (self.root / "kanban/005_closing").mkdir(parents=True)
        self.memory.mkdir(parents=True)
        self.day = self.memory / DAY
        self.day.mkdir()

    def write(self, name, text):
        (self.day / name).write_text(text, encoding="utf-8")

    def valid_pair(self):
        self.write(f"{TASK}.md", ledger_text())
        self.write(f"{TASK}.01-did-the-thing.md", entry_text())

    def violations(self):
        found = []
        pop_validate.check_memory(self.root, [self.root], found)
        return found

    # --- accepted layout -------------------------------------------------

    def test_valid_pair_does_not_violate(self):
        self.valid_pair()
        self.assertEqual(self.violations(), [])

    def test_ledger_without_entries_is_valid(self):
        self.write(f"{TASK}.md", ledger_text(entries=()))
        self.assertEqual(self.violations(), [])

    def test_two_digit_id_does_not_become_an_entry(self):
        """`1.1.10-x` is a whole ledger, not `1.1` + entry `10-x`."""
        task = "1.1.10-task-ten"
        self.write(f"{task}.md", ledger_text(task=task, entries=()))
        self.assertEqual(self.violations(), [])

    # --- ledger rules ----------------------------------------------------

    def test_folder_different_from_finished(self):
        self.write(f"{TASK}.md", ledger_text(finished="2026-07-01", entries=()))
        self.assertIn("differs from the folder", "\n".join(self.violations()))

    def test_ledger_above_the_cap(self):
        fat = ledger_text(entries=()) + "x" * pop_validate.MAX_MEMORY_LEDGER
        self.write(f"{TASK}.md", fat)
        self.assertIn("move content into entries", "\n".join(self.violations()))

    def test_folder_that_is_not_a_date(self):
        (self.memory / "archived").mkdir()
        self.assertIn("must be a", "\n".join(self.violations()))

    def test_subfolder_inside_the_date_folder(self):
        self.valid_pair()
        (self.day / TASK).mkdir()
        self.assertIn("has no subfolder", "\n".join(self.violations()))

    # --- entry rules -----------------------------------------------------

    def test_entry_above_the_cap(self):
        self.write(f"{TASK}.md", ledger_text())
        self.write(f"{TASK}.01-did-the-thing.md",
                   entry_text() + "x" * pop_validate.MAX_MEMORY_ENTRY)
        self.assertIn("it is almost always two entries",
                      "\n".join(self.violations()))

    def test_entry_without_evidence(self):
        self.write(f"{TASK}.md", ledger_text())
        self.write(f"{TASK}.01-did-the-thing.md", entry_text(evidence=False))
        self.assertIn("without an evidence wikilink",
                      "\n".join(self.violations()))

    def test_orphaned_entry_not_indexed(self):
        self.write(f"{TASK}.md", ledger_text(entries=()))
        self.write(f"{TASK}.01-did-the-thing.md", entry_text())
        self.assertIn("orphaned entry", "\n".join(self.violations()))

    def test_entry_without_a_ledger(self):
        self.write(f"{TASK}.01-did-the-thing.md", entry_text())
        self.assertIn("name outside the memory layout",
                      "\n".join(self.violations()))

    def test_entry_with_a_divergent_entry_field(self):
        self.write(f"{TASK}.md", ledger_text())
        self.write(f"{TASK}.01-did-the-thing.md", entry_text(entry="02-other"))
        self.assertIn("differs from the file name",
                      "\n".join(self.violations()))

    # --- legacy ----------------------------------------------------------

    def test_old_flat_memory_is_tolerated(self):
        (self.memory / "1.1.2-old.md").write_text(
            "---\ntask: 1.1.2-old\nproject: pop\nstarted: 2026-07-19\n"
            "finished: 2026-07-20\ncommit: abc\npr:\n---\n", encoding="utf-8")
        self.assertEqual(self.violations(), [])

    def test_new_flat_memory_is_a_violation(self):
        (self.memory / "1.1.3-new.md").write_text(
            "---\ntask: 1.1.3-new\nproject: pop\nstarted: 2026-07-27\n"
            f"finished: {DAY}\ncommit: abc\npr:\n---\n", encoding="utf-8")
        self.assertIn("memory loose in", "\n".join(self.violations()))


class MemoryResolutionTest(unittest.TestCase):
    """`pop_roadmap` finds the ledger in both layouts and refuses ambiguity."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "vault"
        self.memory = self.root / "memory"
        (self.memory / DAY).mkdir(parents=True)

    def valid(self):
        return pop_roadmap.memory_valid(self.root, self.root, TASK,
                                        canonical=True)

    def test_resolves_in_the_date_folder(self):
        (self.memory / DAY / f"{TASK}.md").write_text(
            ledger_text(entries=()), encoding="utf-8")
        self.assertTrue(self.valid())
        self.assertEqual(
            pop_roadmap.memory_path(self.root, self.root, TASK).parent.name, DAY)

    def test_resolves_in_the_legacy_flat_path(self):
        (self.memory / f"{TASK}.md").write_text(
            ledger_text(entries=()), encoding="utf-8")
        self.assertTrue(self.valid())

    def test_folder_diverging_from_finished_is_invalid(self):
        other = self.memory / "2026-07-01"
        other.mkdir()
        (other / f"{TASK}.md").write_text(ledger_text(entries=()),
                                          encoding="utf-8")
        self.assertFalse(self.valid())

    def test_two_ledgers_for_the_same_task_is_ambiguity(self):
        (self.memory / DAY / f"{TASK}.md").write_text(
            ledger_text(entries=()), encoding="utf-8")
        (self.memory / f"{TASK}.md").write_text(
            ledger_text(entries=()), encoding="utf-8")
        self.assertFalse(self.valid())
        self.assertFalse(pop_roadmap.memory_valid(self.root, self.root, TASK,
                                                  canonical=False))

    def test_absent_returns_the_canonical_path_for_the_message(self):
        self.assertFalse(self.valid())
        self.assertEqual(
            pop_roadmap.memory_path(self.root, self.root, TASK),
            self.memory / f"{TASK}.md")


if __name__ == "__main__":
    unittest.main()
