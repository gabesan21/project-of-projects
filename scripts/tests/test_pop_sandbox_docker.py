#!/usr/bin/env python3
"""Real opt-in experiment for the coding docker's internal Docker daemon."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
import uuid
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[2]
TEMPLATES = ROOT / "_templates" / "coding-dockers"
sys.path.insert(0, str(ROOT / "scripts"))
import pop_sandbox as sandbox  # noqa: E402
DOCKER_CAPABILITIES = (
    "AUDIT_WRITE", "CHOWN", "DAC_OVERRIDE", "FOWNER", "FSETID", "KILL", "MKNOD",
    "NET_ADMIN", "NET_BIND_SERVICE", "NET_RAW", "SETFCAP", "SETGID", "SETPCAP",
    "SETUID", "SYS_ADMIN", "SYS_CHROOT",
)


class PopSandboxDockerExperiment(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if os.environ.get("POP_SANDBOX_DOCKER_TEST") != "1":
            raise unittest.SkipTest("set POP_SANDBOX_DOCKER_TEST=1 for the required experiment")
        probe = subprocess.run(["docker", "info"], capture_output=True, text=True)
        if probe.returncode != 0:
            raise RuntimeError("an external Docker daemon is a prerequisite and is unavailable:\n" + probe.stderr)

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.base = Path(self._tmp.name)
        token = uuid.uuid4().hex[:12]
        self.scope = f"probe{token}"
        self.vault = self.base / "vault"
        self.project = self.vault / "categories" / "applications" / self.scope
        self.project.mkdir(parents=True)
        shutil.copytree(TEMPLATES, self.vault / "_templates" / "coding-dockers")
        recipe_path = self.vault / "_templates" / "coding-dockers" / "recipes" / "codex.json"
        recipe = json.loads(recipe_path.read_text(encoding="utf-8"))
        recipe["install"] = {"status": "complete", "argv": ["true"]}
        recipe["open"] = {"status": "complete", "argv": ["bash"]}
        recipe_path.write_text(json.dumps(recipe), encoding="utf-8")
        (self.project / "Dockerfile").write_text("FROM scratch\n", encoding="utf-8")
        subprocess.run(["git", "init", "-q", str(self.project)], check=True)
        (self.project / "tracked.txt").write_text("base\n", encoding="utf-8")
        subprocess.run(["git", "-C", str(self.project), "add", "tracked.txt"], check=True)
        subprocess.run(["git", "-C", str(self.project), "-c", "user.name=PoP Test",
                        "-c", "user.email=test@example.invalid", "commit", "-qm", "base"], check=True)
        self.home = self.base / "home"
        for relative, kind in (*sandbox.COMMON_BINDS, sandbox.AGENT_BINDS["codex"]):
            path = self.home / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("fixture\n", encoding="utf-8") if kind == "file" else path.mkdir()
        patches = (
            mock.patch.object(sandbox.poplib, "discover_projects", return_value=[self.project]),
            mock.patch.object(sandbox.poplib, "project_label",
                              return_value=f"applications/{self.scope}"),
            mock.patch.object(sandbox.poplib, "templates_dir",
                              return_value=self.vault / "_templates"),
            mock.patch.object(sandbox.Path, "home", return_value=self.home),
        )
        for patcher in patches:
            patcher.start()
            self.addCleanup(patcher.stop)
        _, shown = sandbox.proposal(
            self.vault, f"applications/{self.scope}", self.project, "codex", []
        )
        sandbox.command_new(argparse.Namespace(
            project=f"applications/{self.scope}", agent="codex", package=[],
            confirm=shown["confirmation_hash"],
        ), self.vault)
        self.context = self.vault / "coding-dockers" / self.scope / "codex"
        descriptor = json.loads((self.context / "sandbox.json").read_text(encoding="utf-8"))
        self.image = descriptor["image"]
        self.container = descriptor["container"]
        self.project_target = descriptor["project"]["target"]
        self.compose_project = f"inner{token}"
        self.addCleanup(self.cleanup_resources)

    def docker(self, *args, check=True, timeout=180):
        return subprocess.run(["docker", *args], check=check, capture_output=True,
                              text=True, timeout=timeout)

    def cleanup_resources(self):
        self.docker("rm", "-f", self.container, check=False)
        self.docker("image", "rm", "-f", self.image, check=False)

    def inner(self, *args, check=True, timeout=180):
        return self.docker("exec", "--user", "coder", "--env", "HOME=/home/coder",
                           "--env", "DOCKER_HOST=unix:///run/coding-docker/docker.sock",
                           self.container, *args, check=check, timeout=timeout)

    def test_daemon_proprio_isolamento_compose_lifecycle_e_worktree(self):
        descriptor = json.loads((self.context / "sandbox.json").read_text(encoding="utf-8"))
        self.assertTrue(descriptor["stack"]["docker"])
        self.assertTrue((self.context / "seccomp-docker.json").is_file())
        self.docker("build", "--build-arg", f"SANDBOX_UID={os.getuid()}",
                    "--build-arg", f"SANDBOX_GID={os.getgid()}",
                    "--build-arg", "INSTALL_DOCKER=1",
                    "--label", f"io.project-of-projects.scope={self.scope}",
                    "--label", "io.project-of-projects.agent=codex", "-t", self.image,
                    str(self.context), timeout=900)
        smoke = self.docker(
            "run", "--rm", "--cap-drop", "ALL", "--security-opt", "no-new-privileges",
            "--user", "coder", "--entrypoint", "sh", self.image, "-c",
            "printf '%s:%s\\n' \"$(id -u)\" \"$(id -g)\"; "
            "command -v git gh docker jq rg fd tmux; "
            "! command -v node; ! command -v pnpm; ! command -v go; ! command -v rustc",
        )
        self.assertEqual(smoke.stdout.splitlines()[0], f"{os.getuid()}:{os.getgid()}")
        create_args = ["create", "--name", self.container, "--cap-drop", "ALL"]
        for capability in DOCKER_CAPABILITIES:
            create_args.extend(("--cap-add", capability))
        create_args.extend((
                    "--label", f"io.project-of-projects.scope={self.scope}",
                    "--label", "io.project-of-projects.agent=codex",
                    "--security-opt", f"seccomp={self.context / 'seccomp-docker.json'}",
                    "--pids-limit", "2048", "--user", "root",
                    "--sysctl", "net.ipv4.ip_forward=1",
                    "--ulimit", "memlock=-1:-1",
                    "--tmpfs", "/sys/fs/cgroup:rw,nosuid,nodev,noexec",
                    "--env", f"SANDBOX_PROJECT_DIR={self.project_target}",
                    "--env", "ENABLE_DOCKER=1", "--env",
                    "DOCKER_HOST=unix:///run/coding-docker/docker.sock", "--mount",
                    f"type=bind,src={self.project},dst={self.project_target}", self.image))
        self.docker(*create_args)

        inspect = json.loads(self.docker("inspect", self.container).stdout)[0]
        host = inspect["HostConfig"]
        self.assertEqual(inspect["Config"]["User"], "root")
        self.assertFalse(host["Privileged"])
        self.assertEqual(set(host.get("CapAdd") or []),
                         {f"CAP_{capability}" for capability in DOCKER_CAPABILITIES})
        self.assertEqual(host.get("CapDrop"), ["ALL"])
        self.assertFalse(host.get("Devices"))
        self.assertEqual(host.get("Sysctls"), {"net.ipv4.ip_forward": "1"})
        self.assertTrue(any(option.startswith("seccomp=")
                            for option in host.get("SecurityOpt") or []))
        self.assertNotIn("unconfined", " ".join(host.get("SecurityOpt") or []))
        for mount in inspect.get("Mounts", []):
            self.assertNotIn("docker.sock", mount.get("Source", ""))
            self.assertNotIn("docker.sock", mount.get("Destination", ""))
        self.assertFalse(host.get("Binds"))
        self.assertEqual(
            [mount["Destination"] for mount in inspect.get("Mounts", [])],
            [self.project_target],
        )

        self.docker("start", self.container)
        running = self.docker("inspect", "-f", "{{.State.Running}}", self.container)
        if running.stdout.strip() != "true":
            stopped_logs = self.docker("logs", self.container, check=False)
            self.fail("coding docker parou durante o bootstrap:\n"
                      + stopped_logs.stdout + stopped_logs.stderr)
        namespace_pid = self.docker(
            "exec", self.container, "pgrep", "-f", "^sleep infinity$"
        ).stdout.splitlines()[0]
        forwarding = self.docker(
            "exec", self.container, "cat", "/proc/sys/net/ipv4/ip_forward"
        ).stdout.strip()
        self.assertEqual(forwarding, "1")
        deadline = time.monotonic() + 45
        last = None
        while time.monotonic() < deadline:
            last = self.inner("docker", "info", check=False, timeout=10)
            if last.returncode == 0:
                break
            time.sleep(1)
        self.assertIsNotNone(last)
        if last.returncode != 0:
            logged = self.docker("logs", self.container, check=False)
            logs = logged.stdout + logged.stderr
            state = self.docker("inspect", "-f",
                                "exit={{.State.ExitCode}} error={{.State.Error}}",
                                self.container, check=False).stdout
            copied_log = self.base / "daemon.log"
            copied = self.docker("cp", f"{self.container}:/home/coder/.local/share/docker/daemon.log",
                                 str(copied_log), check=False)
            daemon_log = (copied_log.read_text(encoding="utf-8", errors="replace")
                          if copied.returncode == 0 else copied.stderr)
            self.fail("internal daemon did not start under the required boundary\n"
                      f"docker info: {last.stderr}\nstate: {state}"
                      f"container logs: {logs}\ndaemon log: {daemon_log}")

        mounted = self.docker(
            "exec", self.container, "nsenter", "--target", namespace_pid, "--mount",
            "--", "findmnt", "--noheadings", "--output", "FSTYPE", "--target",
            "/sys/fs/cgroup",
        )
        self.assertEqual(mounted.stdout.splitlines()[-1].strip(), "cgroup2")
        outer_mount_ns = self.docker(
            "exec", self.container, "readlink", "/proc/1/ns/mnt"
        ).stdout.strip()
        holder_mount_ns = self.docker(
            "exec", self.container, "nsenter", "--target", namespace_pid, "--mount",
            "--", "readlink", "/proc/self/ns/mnt",
        ).stdout.strip()
        self.assertNotEqual(outer_mount_ns, holder_mount_ns)
        outer_net_ns = self.docker(
            "exec", self.container, "readlink", "/proc/1/ns/net"
        ).stdout.strip()
        holder_net_ns = self.docker(
            "exec", self.container, "readlink", f"/proc/{namespace_pid}/ns/net"
        ).stdout.strip()
        self.assertEqual(outer_net_ns, holder_net_ns)

        identity = self.docker(
            "exec", "--user", "coder", self.container, "setpriv", "--no-new-privs", "--",
            "sh", "-c", "printf '%s:%s:' \"$(id -u)\" \"$(id -g)\"; "
            "awk '/^NoNewPrivs:/ {print $2}' /proc/self/status",
        )
        self.assertEqual(identity.stdout.strip(), f"{os.getuid()}:{os.getgid()}:1")
        processes = self.inner("ps", "-eo", "user,pid,ppid,args")
        self.assertRegex(processes.stdout, r"(?m)^root\s+\d+\s+\d+\s+dockerd\b")
        self.assertNotIn("slirp4netns", processes.stdout)

        outer_ids_before = self.docker("ps", "-aq").stdout.splitlines()
        inner_run = self.inner("docker", "run", "--name", "inner-proof",
                               "hello-world:latest", check=False, timeout=300)
        self.assertEqual(inner_run.returncode, 0, inner_run.stdout + inner_run.stderr)
        inner_ids = self.inner("docker", "ps", "-aq").stdout.splitlines()
        outer_ids_after = self.docker("ps", "-aq").stdout.splitlines()
        self.assertTrue(inner_ids)
        self.assertEqual(outer_ids_before, outer_ids_after)

        compose = self.project / "compose.yaml"
        compose.write_text("services:\n  proof:\n    image: hello-world:latest\n", encoding="utf-8")
        compose_run = self.inner(
            "docker", "compose", "--project-name", self.compose_project,
            "-f", f"{self.project_target}/compose.yaml", "up",
            "--abort-on-container-exit", check=False, timeout=300,
        )
        self.assertEqual(compose_run.returncode, 0,
                         compose_run.stdout + compose_run.stderr)
        self.inner("docker", "network", "inspect", f"{self.compose_project}_default")
        self.assertNotEqual(
            self.docker("network", "inspect", f"{self.compose_project}_default",
                        check=False).returncode,
            0,
        )

        self.inner("git", "-C", self.project_target, "config", "gc.auto", "0")
        self.inner("git", "-C", self.project_target, "worktree", "add", "--relative-paths",
                   ".worktrees/project-worktree", "-b", "probe-worktree")
        gitfile = (self.project / ".worktrees" / "project-worktree" / ".git").read_text(
            encoding="utf-8"
        )
        self.assertNotIn("/home/coder", gitfile)
        host_gitdir = (self.project / ".git" / "worktrees" / "project-worktree" / "gitdir")
        self.assertNotIn("/home/coder", host_gitdir.read_text(encoding="utf-8"))

        for _ in range(2):
            self.docker("exec", "-d", "--user", "coder", self.container,
                        "setpriv", "--no-new-privs", "--", "sleep", "30")
        session_pids = self.docker(
            "exec", self.container, "pgrep", "--uid", str(os.getuid()), "--exact", "sleep"
        ).stdout.splitlines()
        self.assertGreaterEqual(len(set(session_pids)), 2)
        subprocess.run([str(self.context / "stop.sh")], check=True,
                       capture_output=True, text=True)
        self.assertEqual(self.docker("inspect", "-f", "{{.State.Running}}", self.container).stdout.strip(),
                         "false")
        self.docker("start", self.container)
        self.assertEqual(self.docker("inspect", "-f", "{{.State.Running}}", self.container).stdout.strip(),
                         "true")
        subprocess.run([str(self.context / "clean.sh"), "--yes"], check=True,
                       capture_output=True, text=True)
        self.assertNotEqual(self.docker("container", "inspect", self.container,
                                       check=False).returncode, 0)
        self.assertNotEqual(self.docker("image", "inspect", self.image,
                                       check=False).returncode, 0)
        self.assertTrue((self.project / "tracked.txt").is_file())


if __name__ == "__main__":
    unittest.main()
