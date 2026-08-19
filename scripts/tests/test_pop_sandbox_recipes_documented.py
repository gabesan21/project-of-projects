#!/usr/bin/env python3
"""Deterministic proofs of documented recipes without starting coding agents."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
FIXTURE = Path(__file__).parent / "fixtures" / "coding-dockers" / "project"
sys.path.insert(0, str(SCRIPTS))
import pop_sandbox as sandbox  # noqa: E402


AGENT_EXECUTABLES = {"claude", "codex", "opencode", "pi", "kimi"}


def guarded_subprocess(argv, *_args, **_kwargs):
    """Subprocess substitute that turns agent execution into an explicit failure."""
    executable = Path(argv[0]).name if isinstance(argv, (list, tuple)) and argv else ""
    if executable in AGENT_EXECUTABLES:
        raise AssertionError(f"coding agent cannot be executed in this test: {executable}")
    return subprocess.CompletedProcess(argv, 0)


class DocumentedRecipesTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name) / "vault"
        self.project = self.root / "projects" / "demo"
        shutil.copytree(FIXTURE, self.project)
        shutil.copytree(
            ROOT / "_templates" / "coding-dockers",
            self.root / "_templates" / "coding-dockers",
        )
        self.home = Path(self._tmp.name) / "home"
        required_binds = {
            *sandbox.COMMON_BINDS,
            sandbox.AGENT_BINDS["codex"],
            sandbox.AGENT_BINDS["opencode"],
        }
        for relative, kind in required_binds:
            path = self.home / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("fixture\n", encoding="utf-8") if kind == "file" else path.mkdir()
        patches = (
            mock.patch.object(sandbox.poplib, "discover_projects", return_value=[self.project]),
            mock.patch.object(sandbox.poplib, "project_label", return_value="demo"),
            mock.patch.object(sandbox.poplib, "templates_dir", return_value=self.root / "_templates"),
            mock.patch.object(sandbox.Path, "home", return_value=self.home),
            mock.patch.object(sandbox.subprocess, "run", side_effect=guarded_subprocess),
        )
        for patcher in patches:
            patcher.start()
            self.addCleanup(patcher.stop)

    def args_for(self, agent: str, confirmation: str) -> argparse.Namespace:
        return argparse.Namespace(
            project="demo", agent=agent, package=[], confirm=confirmation
        )

    def test_guard_rejects_all_five_executables_with_any_subcommand(self):
        attempts = {
            "claude": "--version",
            "codex": "auth",
            "opencode": "--help",
            "pi": "--version",
            "kimi": "auth",
        }
        for executable, argument in attempts.items():
            with self.subTest(executable=executable):
                with self.assertRaisesRegex(AssertionError, executable):
                    sandbox.subprocess.run([executable, argument])

    def test_recipes_propose_hash_render_and_binds_without_starting_agent(self):
        expectations = {
            "codex": {
                "state": "/home/coder/.codex",
                "open": ["codex"],
            },
            "opencode": {
                "state": "/home/coder/.config/opencode",
                "open": ["opencode"],
            },
        }
        common_targets = {
            "/home/coder/.git-credentials",
            "/home/coder/.gitconfig",
            "/home/coder/.config/git",
            "/home/coder/.config/gh",
        }

        for agent, expected in expectations.items():
            with self.subTest(agent=agent):
                profile, shown = sandbox.proposal(
                    self.root, "demo", self.project, agent, []
                )
                self.assertTrue(profile["stack"]["node"])
                self.assertEqual(shown["confirmation_hash"], profile["input_sha256"])
                self.assertEqual(len(profile["binds"]), 5)
                self.assertEqual(
                    {bind["target"] for bind in profile["binds"]},
                    common_targets | {expected["state"]},
                )
                self.assertTrue(all(bind["read_only"] is False for bind in profile["binds"]))

                sandbox.command_new(
                    self.args_for(agent, shown["confirmation_hash"]), self.root
                )
                destination = self.root / "coding-dockers" / "demo" / agent
                descriptor = json.loads(
                    (destination / "sandbox.json").read_text(encoding="utf-8")
                )
                rendered_recipe = json.loads(
                    (destination / "recipe.json").read_text(encoding="utf-8")
                )
                self.assertEqual(descriptor["agent"]["open_argv"], expected["open"])
                self.assertEqual(rendered_recipe["open"]["argv"], expected["open"])
                self.assertEqual(descriptor["binds"], profile["binds"])

    def test_hash_covers_recipe_without_assuming_other_slot_state(self):
        _, original = sandbox.proposal(
            self.root, "demo", self.project, "codex", []
        )
        recipe_path = self.root / "_templates" / "coding-dockers" / "recipes" / "codex.json"
        recipe = json.loads(recipe_path.read_text(encoding="utf-8"))
        recipe["open"]["argv"].append("--fixture")
        recipe_path.write_text(json.dumps(recipe), encoding="utf-8")
        _, changed = sandbox.proposal(
            self.root, "demo", self.project, "codex", []
        )
        self.assertNotEqual(original["confirmation_hash"], changed["confirmation_hash"])

    def test_lifecycle_consumes_argv_and_preserves_binds_by_contract(self):
        base = self.root / "_templates" / "coding-dockers"
        start = (base / "start.sh").read_text(encoding="utf-8")
        stop = (base / "stop.sh").read_text(encoding="utf-8")
        clean = (base / "clean.sh").read_text(encoding="utf-8")

        self.assertIn("mapfile -t open_argv", start)
        self.assertIn('setpriv --no-new-privs -- "${open_argv[@]}"', start)
        self.assertNotIn("eval", start)
        self.assertIn('docker stop "$container"', stop)
        self.assertNotIn("docker rm", stop)
        self.assertIn('docker rm --force "$container"', clean)
        self.assertIn('docker image rm "$image"', clean)
        self.assertNotIn("binds", clean)
        self.assertIn("host bind sources were preserved", clean)


if __name__ == "__main__":
    unittest.main()
