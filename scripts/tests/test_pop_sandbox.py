#!/usr/bin/env python3
"""Testes comportamentais do motor local de coding dockers."""

from __future__ import annotations

import argparse
import contextlib
import io
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


class PopSandboxTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name) / "vault"
        self.project = self.root / "categories" / "applications" / "demo"
        shutil.copytree(FIXTURE, self.project)
        shutil.copytree(ROOT / "_templates" / "coding-dockers",
                        self.root / "_templates" / "coding-dockers")
        self.home = Path(self._tmp.name) / "home"
        for relative, kind in (*sandbox.COMMON_BINDS, sandbox.AGENT_BINDS["codex"]):
            path = self.home / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("fixture\n", encoding="utf-8") if kind == "file" else path.mkdir()
        self.patches = (
            mock.patch.object(sandbox.poplib, "discover_projects", return_value=[self.project]),
            mock.patch.object(sandbox.poplib, "project_label", return_value="applications/demo"),
            mock.patch.object(sandbox.poplib, "templates_dir", return_value=self.root / "_templates"),
            mock.patch.object(sandbox.Path, "home", return_value=self.home),
        )
        for patcher in self.patches:
            patcher.start()
            self.addCleanup(patcher.stop)

    def propose(self, agent="codex", packages=()):
        return sandbox.proposal(self.root, "applications/demo", self.project, agent, list(packages))

    def complete_recipe(self, agent="codex"):
        path = self.root / "_templates" / "coding-dockers" / "recipes" / f"{agent}.json"
        recipe = json.loads(path.read_text(encoding="utf-8"))
        recipe["install"] = {"status": "complete", "argv": ["true"]}
        recipe["open"] = {"status": "complete", "argv": ["bash"]}
        path.write_text(json.dumps(recipe), encoding="utf-8")

    def new_args(self, confirmation=None, packages=()):
        return argparse.Namespace(project="applications/demo", agent="codex",
                                  package=list(packages), confirm=confirmation)

    def test_proposta_detecta_stack_ordena_pacotes_e_inclui_binds_exatos(self):
        profile, shown = self.propose(packages=("zlib1g-dev", "jq", "jq"))

        self.assertEqual(profile["stack"], {
            "node": True, "yarn": False, "pnpm": True,
            "php": False, "composer": False, "python": False,
            "go": True, "rust": True,
            "docker": True, "additional_packages": ["jq", "zlib1g-dev"],
        })
        self.assertEqual(shown["confirmation_hash"], profile["input_sha256"])
        self.assertEqual(len(profile["binds"]), 5)
        self.assertEqual({item["target"] for item in profile["binds"]}, {
            "/home/coder/.git-credentials", "/home/coder/.gitconfig",
            "/home/coder/.config/git", "/home/coder/.config/gh", "/home/coder/.codex",
        })

    def test_catalogo_tem_exatamente_cinco_slots_e_cada_bind_de_sessao(self):
        expected = set(sandbox.AGENTS)
        self.assertEqual(expected, {"claude-code", "codex", "opencode", "pi", "kimi-code"})
        for agent in expected:
            profile, _ = self.propose(agent=agent)
            relative, _ = sandbox.AGENT_BINDS[agent]
            self.assertIn(str(Path("/home/coder") / relative),
                          {item["target"] for item in profile["binds"]})

    def test_claude_inclui_runtime_node_na_proposta_e_no_hash(self):
        (self.project / "package.json").unlink()
        (self.project / "pnpm-lock.yaml").unlink()

        profile, shown = self.propose(agent="claude-code")
        self.assertTrue(profile["stack"]["node"])
        self.assertEqual(shown["confirmation_hash"], profile["input_sha256"])

        recipe_path = (self.root / "_templates" / "coding-dockers" / "recipes"
                       / "claude-code.json")
        recipe = json.loads(recipe_path.read_text(encoding="utf-8"))
        recipe["runtime"]["kind"] = "standalone"
        recipe_path.write_text(json.dumps(recipe), encoding="utf-8")
        changed, changed_shown = self.propose(agent="claude-code")
        self.assertFalse(changed["stack"]["node"])
        self.assertNotEqual(shown["confirmation_hash"], changed_shown["confirmation_hash"])

    def test_receitas_documentadas_sao_declarativas_e_abrem_tui_sem_flags(self):
        base = self.root / "_templates" / "coding-dockers"
        expected = {
            "claude-code": {
                "install": ["npm", "install", "--global", "@anthropic-ai/claude-code"],
                "open": ["claude"],
            },
            "codex": {
                "install": ["npm", "install", "--global", "@openai/codex"],
                "open": ["codex"],
            },
            "opencode": {
                "install": ["npm", "install", "--global", "opencode-ai"],
                "open": ["opencode"],
            },
        }
        for agent, commands in expected.items():
            with self.subTest(agent=agent):
                recipe = sandbox.recipe_for(base, agent)
                self.assertEqual(recipe["install"]["argv"], commands["install"])
                self.assertEqual(recipe["open"]["argv"], commands["open"])
        dockerfile = (base / "Dockerfile").read_text(encoding="utf-8")
        self.assertIn("COPY recipe.json", dockerfile)
        self.assertIn('mapfile -d \'\' -t install_argv', dockerfile)
        self.assertIn("${install_argv[@]}", dockerfile)
        self.assertNotIn("eval", dockerfile)

    def test_sem_confirmacao_exibe_proposta_sem_criar_artefatos(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            result = sandbox.command_new(self.new_args(), self.root)

        self.assertEqual(result, 0)
        self.assertIn("confirmation_hash", output.getvalue())
        self.assertFalse((self.root / "coding-dockers" / "demo" / "codex").exists())

    def test_confirmacao_errada_e_receita_incompleta_falham_fechado(self):
        with self.assertRaisesRegex(sandbox.SandboxError, "confirmation does not exactly match"):
            sandbox.command_new(self.new_args("0" * 64), self.root)
        recipe_path = self.root / "_templates" / "coding-dockers" / "recipes" / "codex.json"
        recipe = json.loads(recipe_path.read_text(encoding="utf-8"))
        recipe["install"] = {"status": "incomplete", "argv": []}
        recipe_path.write_text(json.dumps(recipe), encoding="utf-8")
        _, shown = self.propose()
        with self.assertRaisesRegex(sandbox.SandboxError, "codex recipe is incomplete"):
            sandbox.command_new(self.new_args(shown["confirmation_hash"]), self.root)

    def test_confirmacao_materializa_artefatos_e_segunda_execucao_e_idempotente(self):
        self.complete_recipe()
        _, shown = self.propose()
        sandbox.command_new(self.new_args(shown["confirmation_hash"]), self.root)
        destination = self.root / "coding-dockers" / "demo" / "codex"

        self.assertEqual({path.name for path in destination.iterdir()}, {
            "Dockerfile", "entrypoint.sh", "start.sh", "stop.sh", "clean.sh",
            "profile.json", "recipe.json", "sandbox.json", "seccomp-docker.json",
        })
        self.assertEqual(
            (destination / "seccomp-docker.json").read_bytes(),
            (self.root / "_templates" / "coding-dockers" / "seccomp-docker.json").read_bytes(),
        )
        descriptor = json.loads((destination / "sandbox.json").read_text(encoding="utf-8"))
        self.assertEqual(descriptor["status"], "ready")
        with self.assertRaisesRegex(sandbox.SandboxError, "sandbox already exists"):
            sandbox.command_new(self.new_args(shown["confirmation_hash"]), self.root)

    def test_check_fresh_detecta_mudanca_em_template(self):
        self.complete_recipe()
        _, shown = self.propose()
        sandbox.command_new(self.new_args(shown["confirmation_hash"]), self.root)
        self.assertEqual(sandbox.check_fresh(self.root, "applications/demo", "codex"), 0)

        dockerfile = self.root / "_templates" / "coding-dockers" / "Dockerfile"
        dockerfile.write_text(dockerfile.read_text(encoding="utf-8") + "\n# stale\n", encoding="utf-8")
        with self.assertRaisesRegex(sandbox.SandboxError, "stale sandbox"):
            sandbox.check_fresh(self.root, "applications/demo", "codex")

    def test_rm_remove_so_artefatos_quando_daemon_prova_ausencia(self):
        self.complete_recipe()
        _, shown = self.propose()
        sandbox.command_new(self.new_args(shown["confirmation_hash"]), self.root)
        destination = self.root / "coding-dockers" / "demo" / "codex"
        absent = [subprocess.CompletedProcess([], 0), subprocess.CompletedProcess([], 1),
                  subprocess.CompletedProcess([], 1)]
        with mock.patch.object(sandbox.subprocess, "run", side_effect=absent):
            sandbox.command_rm(self.new_args(), self.root)

        self.assertFalse(destination.exists())
        self.assertTrue(self.project.exists())
        self.assertTrue(all((self.home / relative).exists()
                            for relative, _ in (*sandbox.COMMON_BINDS, sandbox.AGENT_BINDS["codex"])))

    def test_rm_recusa_recurso_remanescente(self):
        self.complete_recipe()
        _, shown = self.propose()
        sandbox.command_new(self.new_args(shown["confirmation_hash"]), self.root)
        present = [subprocess.CompletedProcess([], 0), subprocess.CompletedProcess([], 0)]
        with mock.patch.object(sandbox.subprocess, "run", side_effect=present):
            with self.assertRaisesRegex(sandbox.SandboxError, "remaining internal resource"):
                sandbox.command_rm(self.new_args(), self.root)

    def test_rejeita_traversal_agente_pacote_e_socket(self):
        with self.assertRaisesRegex(sandbox.SandboxError, "without an external path or traversal"):
            sandbox.resolve_project(self.root, "../demo")
        with self.assertRaisesRegex(sandbox.SandboxError, "unknown agent"):
            sandbox.validate_agent("cursor")
        with self.assertRaisesRegex(sandbox.SandboxError, "invalid additional packages"):
            self.propose(packages=("jq;id",))
        with mock.patch.object(sandbox.Path, "is_socket", return_value=True):
            profile, _ = self.propose()
            with self.assertRaisesRegex(sandbox.SandboxError, "host socket"):
                sandbox.validate_binds(profile["binds"])

    def test_catalogo_adulterado_e_rejeitado(self):
        catalog_path = self.root / "_templates" / "coding-dockers" / "catalog.json"
        catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
        catalog["agents"].append({"slug": "cursor", "recipe": "recipes/cursor.json"})
        catalog_path.write_text(json.dumps(catalog), encoding="utf-8")
        with self.assertRaisesRegex(sandbox.SandboxError, "five expected slots"):
            self.propose()

    def test_identidade_e_bootstrap_docker_sao_separados_da_sessao_do_agente(self):
        dockerfile = (self.root / "_templates" / "coding-dockers" / "Dockerfile").read_text(
            encoding="utf-8"
        )
        entrypoint = (self.root / "_templates" / "coding-dockers" / "entrypoint.sh").read_text(
            encoding="utf-8"
        )
        start = (self.root / "_templates" / "coding-dockers" / "start.sh").read_text(
            encoding="utf-8"
        )
        seccomp = json.loads(
            (self.root / "_templates" / "coding-dockers" / "seccomp-docker.json").read_text(
                encoding="utf-8"
            )
        )

        self.assertIn("ARG SANDBOX_UID", dockerfile)
        self.assertIn("ARG SANDBOX_GID", dockerfile)
        self.assertTrue(dockerfile.startswith("FROM ubuntu:"))
        self.assertIn('dpkg --compare-versions "$git_version" ge 2.48', dockerfile)
        self.assertNotIn("USER coder", dockerfile)
        self.assertIn("runuser --user coder -- git config --global gc.auto 0", dockerfile)
        self.assertIn('--build-arg "SANDBOX_UID=$project_uid"', start)
        self.assertIn('--build-arg "SANDBOX_GID=$project_gid"', start)
        for forbidden in ("groupmod", "usermod", "gosu"):
            self.assertNotIn(forbidden, entrypoint)
        self.assertNotIn("/proc/sys", entrypoint)
        self.assertIn("mount -t proc", entrypoint)
        self.assertIn("unshare --mount -- bash", entrypoint)
        self.assertNotIn("slirp4netns", dockerfile + entrypoint + start)
        self.assertIn("nsenter --target", entrypoint)
        self.assertIn("--mount -- dockerd", entrypoint)
        self.assertNotIn("mount -o remount", entrypoint)
        self.assertIn("unix:///run/coding-docker/docker.sock", entrypoint)
        self.assertIn("--data-root=/var/lib/coding-docker", entrypoint)
        self.assertIn("mount -t cgroup2", entrypoint)
        self.assertIn("internal Docker bootstrap must start as root", entrypoint)
        self.assertIn("mount -t cgroup2", entrypoint)
        self.assertIn("--tmpfs", start)
        self.assertIn("/sys/fs/cgroup", start)
        self.assertNotIn("/dev/net/tun", dockerfile + entrypoint + start)
        self.assertIn("--sysctl net.ipv4.ip_forward=1", start)
        self.assertNotIn("modprobe", start)
        self.assertIn("--user coder", start)
        self.assertIn("setpriv --no-new-privs", start)
        self.assertNotIn("--privileged", start)
        self.assertNotIn("seccomp=unconfined", start)
        allow_rules = [rule for rule in seccomp["syscalls"]
                       if rule.get("action") == "SCMP_ACT_ALLOW"]
        self.assertTrue(any("keyctl" in rule.get("names", []) for rule in allow_rules))
        bpf_rules = [rule for rule in allow_rules if "bpf" in rule.get("names", [])]
        self.assertEqual(
            {rule["args"][0]["value"] for rule in bpf_rules},
            {5, 8, 16},
            "seccomp must allow only BPF_PROG_LOAD/ATTACH/QUERY",
        )
        self.assertTrue(all(rule.get("args") for rule in bpf_rules),
                        "bpf must be filtered by operation, never allowed wholesale")


if __name__ == "__main__":
    unittest.main()
