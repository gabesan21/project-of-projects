#!/usr/bin/env python3
"""Characterize nested first-party stack detection for coding dockers."""

from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import pop_sandbox as sandbox  # noqa: E402


class PopSandboxProjectStackTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        temp = Path(self._tmp.name)
        self.root = temp / "vault"
        self.project = self.root / "categories" / "applications" / "demo"
        shutil.copytree(ROOT / "_templates" / "coding-dockers",
                        self.root / "_templates" / "coding-dockers")
        self.home = temp / "home"
        for relative, kind in (*sandbox.COMMON_BINDS, sandbox.AGENT_BINDS["codex"]):
            item = self.home / relative
            item.parent.mkdir(parents=True, exist_ok=True)
            item.write_text("fixture\n", encoding="utf-8") if kind == "file" else item.mkdir()
        (self.project / "frontend").mkdir(parents=True)
        (self.project / "frontend" / "package.json").write_text(
            '{"name":"frontend","private":true}\n', encoding="utf-8")
        (self.project / "frontend" / "yarn.lock").write_text(
            "# yarn lockfile v1\n", encoding="utf-8")
        (self.project / "backend" / "scripts").mkdir(parents=True)
        (self.project / "backend" / "composer.json").write_text(json.dumps({
            "require": {"php": "^8.1"},
            "require-dev": {"laravel/sail": "^1.18"},
        }), encoding="utf-8")
        (self.project / "backend" / "scripts" / "requirements.txt").write_text(
            "requests>=2.31.0\n", encoding="utf-8")
        self.patches = (
            mock.patch.object(sandbox.poplib, "templates_dir",
                              return_value=self.root / "_templates"),
            mock.patch.object(sandbox.Path, "home", return_value=self.home),
        )
        for patcher in self.patches:
            patcher.start()
            self.addCleanup(patcher.stop)

    def propose(self):
        return sandbox.proposal(
            self.root, "applications/demo", self.project, "codex", [])

    def test_detecta_stack_first_party_aninhada_e_sail(self):
        profile, shown = self.propose()

        self.assertEqual(profile["schema_version"], 2)
        self.assertEqual(profile["stack"], {
            "node": True, "yarn": True, "pnpm": False,
            "php": True, "composer": True, "python": True,
            "go": False, "rust": False, "docker": True,
            "additional_packages": [],
        })
        self.assertEqual(profile["input_sha256"], shown["confirmation_hash"])

    def test_dependencias_caches_harness_e_artefatos_nao_alteram_proposta(self):
        profile, shown = self.propose()
        ignored = (
            ".git", "node_modules", "vendor", "pop", ".opencode", ".cache",
            "__pycache__", ".pytest_cache", ".venv", "dist", "build", "target",
        )
        for name in ignored:
            generated = self.project / name / "nested"
            generated.mkdir(parents=True)
            (generated / "package.json").write_text("{}\n", encoding="utf-8")
            (generated / "compose.yaml").write_text("services: {}\n", encoding="utf-8")

        unchanged, unchanged_shown = self.propose()
        self.assertEqual(profile, unchanged)
        self.assertEqual(shown["confirmation_hash"], unchanged_shown["confirmation_hash"])

    def test_manifest_first_party_novo_altera_proposta_e_hash(self):
        profile, shown = self.propose()
        (self.project / "worker").mkdir()
        (self.project / "worker" / "go.mod").write_text(
            "module example.invalid/worker\n", encoding="utf-8")

        changed, changed_shown = self.propose()
        self.assertFalse(profile["stack"]["go"])
        self.assertTrue(changed["stack"]["go"])
        self.assertNotEqual(shown["confirmation_hash"], changed_shown["confirmation_hash"])

    def test_manifest_symlink_nao_atravessa_fronteira_do_projeto(self):
        outside = Path(self._tmp.name) / "outside-package.json"
        outside.write_text("{}\n", encoding="utf-8")
        clean = self.project / "clean"
        clean.mkdir()
        (clean / "package.json").symlink_to(outside)

        stack = sandbox.detect_stack(clean)
        self.assertFalse(stack["node"])

    def test_schema_e_imagem_declaram_toda_stack_sem_shell_livre(self):
        schema = json.loads((self.root / "_templates" / "coding-dockers"
                             / "profile.schema.json").read_text(encoding="utf-8"))
        required = set(schema["properties"]["stack"]["required"])
        self.assertTrue({"node", "yarn", "php", "composer", "python", "docker"} <= required)

        dockerfile = (self.root / "_templates" / "coding-dockers" / "Dockerfile").read_text(
            encoding="utf-8")
        start = (self.root / "_templates" / "coding-dockers" / "start.sh").read_text(
            encoding="utf-8")
        for flag in ("YARN", "PHP", "COMPOSER", "PYTHON"):
            self.assertIn(f"ARG INSTALL_{flag}=0", dockerfile)
            self.assertIn(f'--build-arg "INSTALL_{flag}=', start)
        self.assertNotIn("INSTALL_COMMAND", dockerfile + start)
        self.assertNotIn("eval", dockerfile + start)


if __name__ == "__main__":
    unittest.main()
