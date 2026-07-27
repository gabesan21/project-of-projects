#!/usr/bin/env python3
"""Tests for the strict `pop/` anatomy of the PoP scripts.

Only the new anatomy (harness in `pop/`) is recognized; the legacy one
(harness at the project root, content in `project/`) is a violation. Fixture:
a mini-vault in a TemporaryDirectory with the meta-project at the root, a new
project and a new embedded repo (full-multi-repo). Stdlib only.

Usage:
    python3 -m unittest discover -s scripts/tests -v   (from the vault root)
"""
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent
VAULT = SCRIPTS.parent
# The PoP's poplib shadows the stdlib one: make sure we import the right one.
sys.modules.pop("poplib", None)
sys.path.insert(0, str(SCRIPTS))
import poplib  # noqa: E402

assert hasattr(poplib, "discover_projects"), "imported the wrong poplib (stdlib)"


def make_kanban(base: Path) -> None:
    for stage in poplib.STAGES:
        (base / stage).mkdir(parents=True)


def release_card(card: Path) -> None:
    """Marks the human release and a valid size on the freshly-created card."""
    text = card.read_text(encoding="utf-8")
    text = text.replace("- [ ] Ready to plan", "- [x] Ready to plan")
    text = text.replace("size: S | M | L", "size: S")
    card.write_text(text, encoding="utf-8")


class StrictAnatomyTest(unittest.TestCase):
    """Mini-vault with the 3 valid scopes: meta, new, new embedded."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name) / "vault"
        make_kanban(self.root / "kanban")                                # meta
        shutil.copytree(VAULT / "_templates", self.root / "_templates")
        make_kanban(self.root / "categories/a/novo/pop/kanban")          # new
        make_kanban(self.root / "categories/a/fmr/repo1/pop/kanban")     # new fmr

    def run_script(self, script, *args):
        return subprocess.run(
            [sys.executable, str(SCRIPTS / script), *args,
             "--vault", str(self.root)],
            capture_output=True, text=True)

    def test_discover_projects_acha_os_3_escopos_sem_duplicata(self):
        scopes = poplib.discover_projects(self.root)
        expected = sorted([
            self.root,
            self.root / "categories/a/novo",
            self.root / "categories/a/fmr/repo1",
        ])
        self.assertEqual(scopes, expected)
        self.assertEqual(len(scopes), len(set(scopes)))

    def test_roundtrip_label_dir(self):
        for label in ("a/novo", "a/fmr/repo1"):
            path = poplib.project_dir(self.root, label)
            self.assertTrue((poplib.harness_root(path) / "kanban").is_dir(),
                            f"{label}: {path} without kanban")
            self.assertEqual(poplib.project_label(self.root, path), label)
        self.assertEqual(poplib.project_dir(self.root, "pop"), self.root)
        self.assertEqual(poplib.project_label(self.root, self.root), "pop")

    def test_pop_task_cria_card_na_anatomia_pop(self):
        for label, rel in (
                ("a/novo", "categories/a/novo/pop/kanban"),
                ("a/fmr/repo1", "categories/a/fmr/repo1/pop/kanban")):
            task_id = f"1.1.{hash(label) % 9 + 1}-task-{label.replace('/', '-')}"
            result = self.run_script("pop_task.py", label, task_id)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            card = (self.root / rel / "001_initial_task" / task_id
                    / f"{task_id}.md")
            self.assertTrue(card.is_file(), f"card missing: {card}")

    def test_pop_task_roadmap_fills_epoch_phase_and_deletes_modification(self):
        task_id = "5.1.1-roadmap-ok"
        result = self.run_script("pop_task.py", "a/novo", task_id)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        card = (self.root / "categories/a/novo/pop/kanban/001_initial_task"
                / task_id / f"{task_id}.md")
        meta, _ = poplib.parse_frontmatter(card.read_text(encoding="utf-8"))
        self.assertEqual(meta.get("id"), "5.1.1")
        self.assertEqual(meta.get("origin"), "roadmap")
        self.assertEqual(meta.get("epoch"), "5")
        self.assertEqual(meta.get("phase"), "5.1")
        self.assertNotIn("modification", meta)

    def test_pop_task_modification_fills_modification_and_deletes_epoch_phase(self):
        task_id = "M-1.1-adjust-contract"
        result = self.run_script("pop_task.py", "a/novo", task_id)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        card = (self.root / "categories/a/novo/pop/kanban/001_initial_task"
                / task_id / f"{task_id}.md")
        self.assertTrue(card.is_file(), f"card missing: {card}")
        meta, _ = poplib.parse_frontmatter(card.read_text(encoding="utf-8"))
        self.assertEqual(meta.get("id"), "M-1.1")
        self.assertEqual(meta.get("origin"), "modifications")
        self.assertEqual(meta.get("modification"), "M-1")
        self.assertNotIn("epoch", meta)
        self.assertNotIn("phase", meta)
        # the final reminder points at the link in the modification
        self.assertIn("modifications/m-1-", result.stdout)

    def test_pop_task_rejects_invalid_ids(self):
        for bad in ("M-1.1.1-extra-part", "1.1-missing-part",
                    "m-1.1-lowercase", "M-1.x-no-slug"):
            result = self.run_script("pop_task.py", "a/novo", bad)
            self.assertEqual(result.returncode, 1, f"{bad} should fail")
            self.assertIn("Invalid id", result.stdout)

    def test_pop_validate_accepts_modification_card(self):
        task_id = "M-2.1-val-modification"
        self.assertEqual(
            self.run_script("pop_task.py", "a/novo", task_id).returncode, 0)
        release_card(self.root / "categories/a/novo/pop/kanban"
                     / "001_initial_task" / task_id / f"{task_id}.md")
        result = self.run_script("pop_validate.py")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_pop_validate_requires_epoch_phase_in_roadmap_origin(self):
        task_id = "9.9.9-no-epoch"
        folder = self.root / "kanban/001_initial_task" / task_id
        folder.mkdir(parents=True)
        (folder / f"{task_id}.md").write_text(
            "---\nid: 9.9.9\nproject: pop\norigin: roadmap\n"
            "stage: 001_initial_task\ncreated: 2026-07-21\n"
            "updated: 2026-07-21\n---\n", encoding="utf-8")
        result = self.run_script("pop_validate.py")
        self.assertEqual(result.returncode, 1)
        self.assertIn("`epoch`", result.stdout)
        self.assertIn("`phase`", result.stdout)

    def test_pop_validate_requires_modification_in_modifications_origin(self):
        task_id = "M-3.1-no-modification"
        folder = self.root / "kanban/001_initial_task" / task_id
        folder.mkdir(parents=True)
        (folder / f"{task_id}.md").write_text(
            "---\nid: M-3.1\nproject: pop\norigin: modifications\n"
            "stage: 001_initial_task\ncreated: 2026-07-21\n"
            "updated: 2026-07-21\n---\n", encoding="utf-8")
        result = self.run_script("pop_validate.py")
        self.assertEqual(result.returncode, 1)
        self.assertIn("`modification`", result.stdout)

    def test_pop_move_001_para_002(self):
        label, rel, task_id = (
            "a/novo", "categories/a/novo/pop/kanban", "2.1.1-move-novo")
        self.assertEqual(
            self.run_script("pop_task.py", label, task_id).returncode, 0)
        card = (self.root / rel / "001_initial_task" / task_id
                / f"{task_id}.md")
        release_card(card)
        result = self.run_script("pop_move.py", task_id, "002_planning")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue(
            (self.root / rel / "002_planning" / task_id).is_dir())
        self.assertFalse(
            (self.root / rel / "001_initial_task" / task_id).exists())

    def test_pop_validate_exit_0_na_fixture(self):
        # with live cards in the pop/ anatomy, including one already moved to 002
        self.assertEqual(
            self.run_script("pop_task.py", "a/novo", "3.1.1-val-novo")
            .returncode, 0)
        release_card(self.root / "categories/a/novo/pop/kanban"
                     / "001_initial_task" / "3.1.1-val-novo"
                     / "3.1.1-val-novo.md")
        self.assertEqual(
            self.run_script("pop_move.py", "3.1.1-val-novo", "002_planning")
            .returncode, 0)
        result = self.run_script("pop_validate.py")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_pop_validate_flags_invalid_return_kind(self):
        # `return_kind` is written only by pop_move; a value outside the enum
        # means a hand edit and breaks the choice of the re-review mode.
        self.assertEqual(
            self.run_script("pop_task.py", "a/novo", "5.1.1-return-kind")
            .returncode, 0)
        card = (self.root / "categories/a/novo/pop/kanban" / "001_initial_task"
                / "5.1.1-return-kind" / "5.1.1-return-kind.md")
        release_card(card)
        self.assertEqual(self.run_script("pop_validate.py").returncode, 0)

        card.write_text(card.read_text(encoding="utf-8").replace(
            "return_kind:", "return_kind: parcial"), encoding="utf-8")
        result = self.run_script("pop_validate.py")
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("`return_kind` invalid `parcial`", result.stdout)

    def test_pop_validate_nao_avisa_link_estagio_irmao(self):
        # a card in 001 links `.plan/.approval/.verify` (from the template)
        # that are only born as the task advances — expected navigation link,
        # must not become a warning.
        self.assertEqual(
            self.run_script("pop_task.py", "a/novo", "4.1.1-links-estagio")
            .returncode, 0)
        release_card(self.root / "categories/a/novo/pop/kanban"
                     / "001_initial_task" / "4.1.1-links-estagio"
                     / "4.1.1-links-estagio.md")
        result = self.run_script("pop_validate.py")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertNotIn("4.1.1-links-estagio.plan", result.stdout)
        self.assertNotIn("4.1.1-links-estagio.approval", result.stdout)
        self.assertNotIn("4.1.1-links-estagio.verify", result.stdout)

    def test_pop_validate_rejeita_anatomia_legada(self):
        # harness at the folder root (legacy kanban/) => violation, exit 1
        make_kanban(self.root / "categories/a/legado/kanban")
        result = self.run_script("pop_validate.py")
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("legacy anatomy", result.stdout)
        self.assertIn("categories/a/legado/kanban", result.stdout)

    def test_pop_validate_ignora_scaffold_sem_harness(self):
        # a folder with only `project/` and no harness = not-yet-imported
        # scaffold, not a PoP project => NOT an anatomy violation.
        (self.root / "categories/a/scaffold/project").mkdir(parents=True)
        (self.root / "categories/a/scaffold/.gitignore").write_text(
            "project/*\n", encoding="utf-8")
        result = self.run_script("pop_validate.py")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_pop_validate_applies_150_line_limit_to_harness_note(self):
        notes = self.root / "specs"
        notes.mkdir()
        note = notes / "limit.md"
        note.write_text("line\n" * 150, encoding="utf-8")
        self.assertEqual(self.run_script("pop_validate.py").returncode, 0)

        note.write_text("line\n" * 151, encoding="utf-8")
        result = self.run_script("pop_validate.py")
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("151 lines (max. 150)", result.stdout)

    def test_pop_validate_applies_80_line_limit_to_plan_root(self):
        # A big plan modularizes into `subtasks/`; the root is read by everyone.
        folder = self.root / "kanban/002_planning/1.1.1-t"
        folder.mkdir(parents=True)
        plan = folder / "1.1.1-t.plan.md"
        plan.write_text("line\n" * 80, encoding="utf-8")
        self.assertEqual(self.run_script("pop_validate.py").returncode, 0)

        plan.write_text("line\n" * 81, encoding="utf-8")
        result = self.run_script("pop_validate.py")
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("81 lines (max. 80)", result.stdout)

    def test_pop_validate_applies_50_line_limit_to_front_file(self):
        # A front file is the reading slice of a single executor.
        folder = self.root / "kanban/002_planning/1.1.1-t/subtasks"
        folder.mkdir(parents=True)
        front = folder / "1.1.1-t.g01-front.md"
        front.write_text("line\n" * 50, encoding="utf-8")
        self.assertEqual(self.run_script("pop_validate.py").returncode, 0)

        front.write_text("line\n" * 51, encoding="utf-8")
        result = self.run_script("pop_validate.py")
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("51 lines (max. 50)", result.stdout)


class ProjectAgentsCapTest(unittest.TestCase):
    """A project's AGENTS.md is a pointer: 60 lines, DOX the only exception."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)
        self.project = self.root / "categories/agents/p"
        (self.project / "pop/kanban/001_initial_task").mkdir(parents=True)
        self.agents = self.project / "AGENTS.md"

    def validate(self):
        return subprocess.run(
            [sys.executable, str(SCRIPTS / "pop_validate.py"),
             "--vault", str(self.root)], capture_output=True, text=True)

    def test_accepts_short_pointer_and_refuses_narrating_the_flow(self):
        self.agents.write_text("line\n" * 60, encoding="utf-8")
        self.assertNotIn("max. 60", self.validate().stdout)

        self.agents.write_text("line\n" * 61, encoding="utf-8")
        result = self.validate()
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("61 lines (max. 60)", result.stdout)

    def test_application_with_dox_is_exempt(self):
        self.agents.write_text("## DOX process\n" + "line\n" * 200,
                               encoding="utf-8")
        self.assertNotIn("max. 60", self.validate().stdout)

    def test_vault_root_agents_is_not_a_project_agents(self):
        (self.root / "AGENTS.md").write_text("line\n" * 200, encoding="utf-8")
        self.assertNotIn("max. 60", self.validate().stdout)


class IncludedInstallV2Test(unittest.TestCase):
    """Included v2 installation (harness_root=pop) in a temporary repo."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.target = Path(self._tmp.name) / "repo"
        self.target.mkdir()
        (self.target / ".gitignore").write_text("node_modules/\n",
                                                encoding="utf-8")

    def test_instala_layout_pop_e_valida_standalone(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPTS / "pop_install_included.py"),
             str(self.target)],
            capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

        pop = self.target / "pop"
        for rel in ("WORKFLOW.md", "INBOX.md",
                    ".included-harness.json", "scripts/pop_validate.py",
                    "_templates/TASK.md", "kanban/001_initial_task/.gitkeep",
                    "worktrees/.gitkeep"):
            self.assertTrue((pop / rel).exists(), f"pop/{rel} missing")
        # skills, AGENTS.md and CLAUDE.md live at the repo root
        self.assertTrue(
            (self.target / ".agents/skills/new-task/SKILL.md").is_file())
        self.assertTrue((self.target / "AGENTS.md").is_file())
        self.assertTrue((self.target / "CLAUDE.md").is_symlink())
        gitignore = (self.target / ".gitignore").read_text(encoding="utf-8")
        self.assertIn("pop/worktrees/*", gitignore)
        self.assertIn("!pop/worktrees/.gitkeep", gitignore)
        workflow = (pop / "WORKFLOW.md").read_text(encoding="utf-8")
        advance = (self.target / ".agents/skills/advance-task/SKILL.md").read_text(
            encoding="utf-8")
        self.assertIn("pop/scripts/pop_roadmap.py", workflow)
        self.assertIn("pop/scripts/pop_move.py", advance)
        self.assertNotIn("`scripts/pop_move.py", advance)

        # pop_validate --standalone running FROM INSIDE the repo (exercises
        # vault_root with scripts in pop/scripts, without --vault)
        result = subprocess.run(
            [sys.executable, str(pop / "scripts" / "pop_validate.py"),
             "--standalone"],
            capture_output=True, text=True, cwd=self.target)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("standalone valid", result.stdout)

        # The copied installer must also find skills at the repo root, not in
        # `pop/.agents/`, to allow future standalone updates.
        result = subprocess.run(
            [sys.executable, str(pop / "scripts" / "pop_install_included.py"),
             "--audit-manifest"], capture_output=True, text=True,
            cwd=self.target)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


class HarnessFreshnessTest(unittest.TestCase):
    """The root PoP as updater: content stamp and failing closed."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.target = Path(self._tmp.name) / "repo"
        self.target.mkdir()
        self.marker = self.target / "pop" / ".included-harness.json"

    def installer(self, *args):
        return subprocess.run(
            [sys.executable, str(SCRIPTS / "pop_install_included.py"), *args],
            capture_output=True, text=True)

    def install(self):
        result = self.installer(str(self.target))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_install_stamps_the_source_content_sha(self):
        self.install()
        stamp = json.loads(self.marker.read_text(encoding="utf-8"))
        sha = self.installer("--sha")
        self.assertEqual(stamp["content_sha"], sha.stdout.strip())

    def test_check_fresh_accepts_a_freshly_installed_target(self):
        self.install()
        result = self.installer("--check-fresh", str(self.target))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("harness current", result.stdout)

    def test_check_fresh_refuses_a_stale_target(self):
        self.install()
        stamp = json.loads(self.marker.read_text(encoding="utf-8"))
        stamp["content_sha"] = "0" * 64
        self.marker.write_text(json.dumps(stamp), encoding="utf-8")
        result = self.installer("--check-fresh", str(self.target))
        self.assertEqual(result.returncode, 1)
        self.assertIn("STALE", result.stderr)

    def test_check_fresh_refuses_a_target_without_a_stamp(self):
        """An installation older than the stamp is indistinguishable from stale."""
        self.install()
        stamp = json.loads(self.marker.read_text(encoding="utf-8"))
        del stamp["content_sha"]
        self.marker.write_text(json.dumps(stamp), encoding="utf-8")
        result = self.installer("--check-fresh", str(self.target))
        self.assertEqual(result.returncode, 1)
        self.assertIn("without a stamp", result.stderr)

    def test_check_fresh_refuses_a_target_without_a_harness(self):
        result = self.installer("--check-fresh", str(self.target))
        self.assertEqual(result.returncode, 1)
        self.assertIn("absent", result.stderr)

    def test_update_prunes_what_the_previous_installation_brought(self):
        """A template retired at the source does not survive forever in the target."""
        self.install()
        residue = self.target / "pop" / "_templates" / "TASK-OBSOLETE.md"
        residue.write_text("a stage that no longer exists\n", encoding="utf-8")
        stamp = json.loads(self.marker.read_text(encoding="utf-8"))
        stamp["installed"].append("pop/_templates/TASK-OBSOLETE.md")
        self.marker.write_text(json.dumps(stamp), encoding="utf-8")

        self.install()
        self.assertFalse(residue.exists())

    def test_pruning_preserves_a_project_file_in_a_managed_folder(self):
        """A managed folder is not an exclusive folder: the project keeps its own
        scripts in `pop/scripts/` and the harness update must not delete them."""
        self.install()
        own = self.target / "pop" / "scripts" / "db-test.mjs"
        own.write_text("// the project's verification\n", encoding="utf-8")
        fixture = self.target / "pop" / "scripts" / "fixtures" / "case.json"
        fixture.parent.mkdir(parents=True, exist_ok=True)
        fixture.write_text("{}\n", encoding="utf-8")

        self.install()
        self.assertTrue(own.is_file())
        self.assertTrue(fixture.is_file())

    def test_first_installation_prunes_nothing(self):
        """With no previous inventory, the pruning has no authorization."""
        (self.target / "pop" / "scripts").mkdir(parents=True)
        preexisting = self.target / "pop" / "scripts" / "legacy.mjs"
        preexisting.write_text("// older than the harness\n", encoding="utf-8")
        self.install()
        self.assertTrue(preexisting.is_file())

    def test_installed_copy_answers_for_itself_and_points_nowhere(self):
        """The copy reports its own version — and never points outside.

        Refusing with an error pushed the agent to run the command at the
        source, which is exactly the boundary crossing the harness must not
        teach.
        """
        self.install()
        vendored = self.target / "pop" / "scripts" / "pop_install_included.py"
        stamp = json.loads((self.target / "pop" / ".included-harness.json")
                           .read_text(encoding="utf-8"))["content_sha"]
        for flag in ("--check-fresh", "--sha"):
            result = subprocess.run(
                [sys.executable, str(vendored), flag, str(self.target)],
                capture_output=True, text=True, cwd=self.target)
            self.assertEqual(result.returncode, 0, flag + result.stderr)
            self.assertIn(stamp[:12], result.stdout, flag)
            for outside in ("parent PoP", "root PoP", "single source"):
                self.assertNotIn(outside, result.stdout + result.stderr, flag)

    def test_target_does_not_receive_hosting_scope_material(self):
        """What only serves a host of projects never travels to the child."""
        self.install()
        for rel in ("pop/TYPES.md", "pop/_templates/NEW_PROJECT.md",
                    "pop/_templates/IMPORT_PROJECT.md",
                    ".agents/skills/weekly-review/origin-scope.md"):
            self.assertFalse((self.target / rel).exists(), rel)
        self.assertTrue(
            (self.target / ".agents/skills/weekly-review/SKILL.md").is_file())

    def test_managed_set_does_not_name_the_hosting_scope(self):
        """The guard that keeps copied text from describing the world above."""
        result = self.installer("--audit-boundary")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_install_fails_when_the_package_leaks_the_host(self):
        """Fail closed: a package naming its host does not install."""
        workflow = SCRIPTS.parent / "WORKFLOW.md"
        original = workflow.read_text(encoding="utf-8")
        self.addCleanup(workflow.write_text, original, "utf-8")
        workflow.write_text(original + "\nRun it from the root PoP.\n",
                            encoding="utf-8")
        result = subprocess.run(
            [sys.executable, str(SCRIPTS / "pop_install_included.py"),
             str(self.target)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("hosting scope", result.stderr)

    def test_target_does_not_receive_the_parents_test_suite(self):
        self.install()
        self.assertFalse((self.target / "pop/scripts/tests").exists())
        self.assertTrue((self.target / "pop/scripts/poplib.py").is_file())

    def test_content_sha_follows_a_change_in_the_harness(self):
        """The stamp is content identity, not layout identity."""
        before = self.installer("--sha").stdout.strip()
        workflow = SCRIPTS.parent / "WORKFLOW.md"
        original = workflow.read_text(encoding="utf-8")
        self.addCleanup(workflow.write_text, original, "utf-8")
        workflow.write_text(original + "\n<!-- test touch -->\n",
                            encoding="utf-8")
        self.assertNotEqual(self.installer("--sha").stdout.strip(), before)


if __name__ == "__main__":
    unittest.main()
