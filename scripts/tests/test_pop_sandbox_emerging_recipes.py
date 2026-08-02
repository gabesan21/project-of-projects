#!/usr/bin/env python3
"""Deterministic proofs for Pi and Kimi without running agents or Docker."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))
import pop_sandbox as sandbox  # noqa: E402


class EmergingRecipesTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name) / "vault"
        self.project = self.root / "categories" / "applications" / "demo"
        self.project.mkdir(parents=True)
        shutil.copytree(
            ROOT / "_templates" / "coding-dockers",
            self.root / "_templates" / "coding-dockers",
        )
        self.home = Path(self._tmp.name) / "home"
        required_binds = {
            *sandbox.COMMON_BINDS,
            sandbox.AGENT_BINDS["pi"],
            sandbox.AGENT_BINDS["kimi-code"],
        }
        for relative, kind in required_binds:
            path = self.home / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            if kind == "file":
                path.write_text("fixture\n", encoding="utf-8")
            else:
                path.mkdir()

        patches = (
            mock.patch.object(sandbox.poplib, "discover_projects", return_value=[self.project]),
            mock.patch.object(
                sandbox.poplib, "project_label", return_value="applications/demo"
            ),
            mock.patch.object(
                sandbox.poplib, "templates_dir", return_value=self.root / "_templates"
            ),
            mock.patch.object(sandbox.Path, "home", return_value=self.home),
            mock.patch.object(
                sandbox.subprocess,
                "run",
                side_effect=AssertionError("subprocess is forbidden in this suite"),
            ),
        )
        for patcher in patches:
            patcher.start()
            self.addCleanup(patcher.stop)

    def args_for(self, agent: str, confirmation: str) -> argparse.Namespace:
        return argparse.Namespace(
            project="applications/demo", agent=agent, package=[], confirm=confirmation
        )

    def test_node_controlado_e_opt_in_atende_kimi(self):
        dockerfile = (
            self.root / "_templates" / "coding-dockers" / "Dockerfile"
        ).read_text(encoding="utf-8")
        match = re.search(r"node_version=(\d+)\.(\d+)\.(\d+);", dockerfile)

        self.assertIsNotNone(match)
        self.assertGreaterEqual(tuple(map(int, match.groups())), (22, 19, 0))
        self.assertIn("ARG INSTALL_NODE=0", dockerfile)
        self.assertIn(
            'if [ "$INSTALL_NODE" = 1 ] || [ "$INSTALL_YARN" = 1 ] || '
            '[ "$INSTALL_PNPM" = 1 ]',
            dockerfile,
        )
        self.assertIn('node_url="https://nodejs.org/dist/v${node_version}"', dockerfile)
        self.assertNotIn("apt-get install -y --no-install-recommends nodejs", dockerfile)

    def test_receitas_usam_npm_atual_e_abrem_tui_pura(self):
        base = self.root / "_templates" / "coding-dockers" / "recipes"
        expectations = {
            "pi": {
                "install": [
                    "npm", "install", "-g", "--ignore-scripts",
                    "@earendil-works/pi-coding-agent",
                ],
                "open": ["pi"],
            },
            "kimi-code": {
                "install": ["npm", "install", "-g", "@moonshot-ai/kimi-code"],
                "open": ["kimi"],
            },
        }

        for agent, expected in expectations.items():
            with self.subTest(agent=agent):
                recipe = json.loads((base / f"{agent}.json").read_text(encoding="utf-8"))
                self.assertEqual(recipe["runtime"], {"kind": "node", "required": True})
                self.assertEqual(recipe["install"]["argv"], expected["install"])
                self.assertEqual(recipe["open"]["argv"], expected["open"])
                self.assertNotIn("@mariozechner/pi-coding-agent", json.dumps(recipe))

    def test_proposta_hash_render_e_cinco_binds_rw_diretos(self):
        state_targets = {
            "pi": "/home/coder/.pi",
            "kimi-code": "/home/coder/.kimi-code",
        }
        common_targets = {
            "/home/coder/.git-credentials",
            "/home/coder/.gitconfig",
            "/home/coder/.config/git",
            "/home/coder/.config/gh",
        }

        for agent, state_target in state_targets.items():
            with self.subTest(agent=agent):
                profile, shown = sandbox.proposal(
                    self.root, "applications/demo", self.project, agent, []
                )
                self.assertTrue(profile["stack"]["node"])
                self.assertEqual(profile["input_sha256"], shown["confirmation_hash"])
                self.assertEqual(len(profile["binds"]), 5)
                self.assertEqual(
                    {bind["target"] for bind in profile["binds"]},
                    common_targets | {state_target},
                )
                self.assertTrue(all(bind["read_only"] is False for bind in profile["binds"]))
                self.assertTrue(
                    all(bind["source"].startswith(str(self.home)) for bind in profile["binds"])
                )

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
                self.assertEqual(descriptor["binds"], profile["binds"])
                self.assertEqual(
                    descriptor["agent"]["open_argv"], rendered_recipe["open"]["argv"]
                )

    def test_hash_cobre_receita_emergente(self):
        _, original = sandbox.proposal(
            self.root, "applications/demo", self.project, "kimi-code", []
        )
        recipe_path = (
            self.root
            / "_templates"
            / "coding-dockers"
            / "recipes"
            / "kimi-code.json"
        )
        recipe = json.loads(recipe_path.read_text(encoding="utf-8"))
        recipe["open"]["argv"].append("--fixture")
        recipe_path.write_text(json.dumps(recipe), encoding="utf-8")
        _, changed = sandbox.proposal(
            self.root, "applications/demo", self.project, "kimi-code", []
        )

        self.assertNotEqual(original["confirmation_hash"], changed["confirmation_hash"])


if __name__ == "__main__":
    unittest.main()
