#!/usr/bin/env python3

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent


class SpecValidationTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name) / "vault"
        (self.root / "kanban").mkdir(parents=True)
        self.specs = self.root / "specs"
        self.specs.mkdir()

    def run_validator(self):
        return subprocess.run(
            [sys.executable, str(SCRIPTS / "pop_validate.py"),
             "--vault", str(self.root)],
            capture_output=True, text=True)

    def write_spec(self, rel="contract.md", **changes):
        values = {
            "id": Path(rel).stem,
            "project": "pop",
            "domain": Path(rel).parts[0] if len(Path(rel).parts) == 2 else "core",
            "kind": "contract",
            "status": "active",
            "implementation": "implemented",
            "origin": '"1.1"',
            "created": "2026-07-20",
            "updated": "2026-07-20",
            "supersedes": "[]",
            "superseded_by": "",
        }
        values.update(changes)
        frontmatter = "\n".join(f"{key}: {value}" for key, value in values.items())
        path = self.specs / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"---\n{frontmatter}\n---\n\n# Spec\n", encoding="utf-8")
        return path

    def adopt(self, *targets):
        links = "\n".join(f"- [[{target}]] — *follow to validate*." for target in targets)
        (self.specs / "INDEX.md").write_text(
            f"# Specs\n\n{links}\n", encoding="utf-8")

    def assert_invalid(self, expected):
        result = self.run_validator()
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(expected, result.stdout)

    def test_accepts_valid_collection_with_direct_contract(self):
        self.write_spec()
        self.adopt("specs/contract")
        result = self.run_validator()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_accepts_contract_reachable_through_domain_overview(self):
        overview = self.write_spec("payments/overview.md", id="payments",
                                   kind="overview")
        self.write_spec("payments/quotes.md")
        overview.write_text(
            overview.read_text(encoding="utf-8")
            + "\n- [[payments/quotes]] — *follow to quote*.\n",
            encoding="utf-8")
        self.adopt("specs/payments/overview")
        result = self.run_validator()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_collection_without_index_remains_legacy(self):
        (self.specs / "legacy.md").write_text("# No frontmatter\n", encoding="utf-8")
        result = self.run_validator()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_rejects_invalid_fields_enums_id_and_dates(self):
        self.write_spec(id="bad ID", status="published", created="20-07-2026",
                        updated="2026-07-19")
        self.adopt("specs/contract")
        result = self.run_validator()
        self.assertEqual(result.returncode, 1)
        for expected in ("`id` invalid", "`status` invalid", "`created` invalid"):
            self.assertIn(expected, result.stdout)

    def test_rejects_missing_required_field(self):
        path = self.write_spec()
        path.write_text(path.read_text(encoding="utf-8").replace(
            "origin: \"1.1\"\n", ""), encoding="utf-8")
        self.adopt("specs/contract")
        self.assert_invalid("frontmatter missing `origin`")

    def test_rejects_empty_required_field_and_earlier_updated_date(self):
        self.write_spec(origin="", created="2026-07-20", updated="2026-07-19")
        self.adopt("specs/contract")
        result = self.run_validator()
        self.assertEqual(result.returncode, 1)
        self.assertIn("frontmatter has empty `origin`", result.stdout)
        self.assertIn("`updated` precedes `created`", result.stdout)

    def test_rejects_duplicate_id(self):
        self.write_spec("one.md", id="duplicate")
        self.write_spec("two.md", id="duplicate")
        self.adopt("specs/one", "specs/two")
        self.assert_invalid("duplicate `id` `duplicate`")

    def test_rejects_mismatched_project(self):
        self.write_spec(project="other")
        self.adopt("specs/contract")
        self.assert_invalid("differs from scope label `pop`")

    def test_accepts_project_equal_to_full_scope_label(self):
        project = self.root / "categories/agents/gandalf-harness"
        (project / "pop/kanban").mkdir(parents=True)
        self.specs = project / "pop/specs"
        self.specs.mkdir()
        self.write_spec(project="agents/gandalf-harness")
        self.adopt("contract")
        result = self.run_validator()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_rejects_domain_mismatched_with_subfolder(self):
        self.write_spec("payments/contract.md", domain="other")
        self.adopt("specs/payments/contract")
        self.assert_invalid("`domain` `other` differs from folder `payments`")

    def test_rejects_deep_folder(self):
        self.write_spec("payments/api/contract.md", domain="payments")
        self.adopt("specs/payments/api/contract")
        result = self.run_validator()
        self.assertEqual(result.returncode, 1)
        self.assertIn("spec nesting is invalid", result.stdout)

    def test_rejects_unreachable_current_spec(self):
        self.write_spec()
        self.adopt()
        self.assert_invalid("unreachable por `specs/INDEX.md`")

    def test_rejects_missing_supersession_target(self):
        self.write_spec(status="superseded", superseded_by="new")
        self.adopt()
        self.assert_invalid("references missing ID `new`")

    def test_accepts_reciprocal_supersession(self):
        self.write_spec("old.md", status="superseded", superseded_by="new")
        self.write_spec("new.md", status="active", supersedes="[old]")
        self.adopt("specs/new")
        result = self.run_validator()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_rejects_nonreciprocal_supersession(self):
        self.write_spec("old.md", status="superseded", superseded_by="new")
        self.write_spec("new.md", status="active")
        self.adopt("specs/new")
        self.assert_invalid("non-reciprocal supersession")


if __name__ == "__main__":
    unittest.main()
