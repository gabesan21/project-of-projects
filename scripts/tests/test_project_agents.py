#!/usr/bin/env python3
"""The project AGENTS.md ruler: it always measures, discounting the DOX block.

The old exemption was a `continue` — an application simply was not measured,
and the file grew with nobody complaining. The contract here is: discount the
DOX block and report the rest's excess (a warning in an application, a
violation outside one).

Usage:
    python3 -m unittest discover -s scripts/tests -v   (from the vault root)
"""
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS))

import pop_validate  # noqa: E402

CAP = pop_validate.MAX_PROJECT_AGENTS


class ProjectAgentsRulerTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name) / "vault"
        self.project = self.root / "projects" / "app"
        self.project.mkdir(parents=True)

    def write(self, body):
        (self.project / "AGENTS.md").write_text(body, encoding="utf-8")

    def run_check(self):
        violations, warnings = [], []
        pop_validate.check_project_agents(self.root, [self.root, self.project],
                                          violations, warnings)
        return violations, warnings

    def dox_block(self, lines, level="## "):
        return f"{level}DOX process — hierarchical context\n" + "x\n" * (lines - 1)

    # --- no DOX: the cap is a violation, as before -----------------------

    def test_no_dox_within_cap_is_clean(self):
        self.write("line\n" * CAP)
        self.assertEqual(self.run_check(), ([], []))

    def test_no_dox_above_cap_is_a_violation(self):
        self.write("line\n" * (CAP + 1))
        violations, warnings = self.run_check()
        self.assertEqual(warnings, [])
        self.assertIn(f"{CAP + 1} lines", violations[0])
        self.assertNotIn("discounted", violations[0])

    # --- with DOX: measure the rest and warn -----------------------------

    def test_dox_block_is_discounted(self):
        """It fits the cap after the discount: nothing to report — what used to
        be a blind exemption is now a measurement that passes."""
        self.write("line\n" * CAP + self.dox_block(40))
        self.assertEqual(self.run_check(), ([], []))

    def test_excess_outside_the_dox_block_is_a_warning(self):
        self.write("line\n" * (CAP + 5) + self.dox_block(40))
        violations, warnings = self.run_check()
        self.assertEqual(violations, [])
        self.assertIn(f"{CAP + 5} lines", warnings[0])
        self.assertIn("DOX block of 40 already discounted", warnings[0])

    def test_level_one_dox_heading_is_discounted_too(self):
        """In a multi-repo repository the block arrives as `# DOX process`."""
        self.write("line\n" * (CAP + 3) + self.dox_block(12, level="# "))
        _, warnings = self.run_check()
        self.assertIn("DOX block of 12 already discounted", warnings[0])

    def test_dox_block_ends_at_the_next_heading_of_same_level(self):
        """The block runs from the marker to the next heading of equal or
        higher level — whatever comes after counts again."""
        self.write("line\n" * CAP + self.dox_block(10)
                   + "## Essential rules\n" + "y\n" * 4)
        _, warnings = self.run_check()
        self.assertIn(f"{CAP + 5} lines", warnings[0])
        self.assertIn("DOX block of 10 already discounted", warnings[0])

    # --- boundaries ------------------------------------------------------

    def test_marker_outside_a_heading_does_not_discount(self):
        """Mentioning "DOX process" in a sentence creates no block to discount."""
        self.write("line\n" * CAP + "see the DOX process below\n")
        violations, warnings = self.run_check()
        self.assertEqual(warnings, [])
        self.assertIn(f"{CAP + 1} lines", violations[0])

    def test_root_agents_is_out_of_reach(self):
        (self.root / "AGENTS.md").write_text("line\n" * 400, encoding="utf-8")
        self.assertEqual(self.run_check(), ([], []))


if __name__ == "__main__":
    unittest.main()
