#!/usr/bin/env bash
set -euo pipefail

project_dir=${SANDBOX_PROJECT_DIR:?SANDBOX_PROJECT_DIR is required}
if [[ ! -d "$project_dir" ]]; then
  printf 'project mount is missing: %s\n' "$project_dir" >&2
  exit 66
fi

project_uid=$(stat -c %u -- "$project_dir")
project_gid=$(stat -c %g -- "$project_dir")
coder_uid=$(id -u coder)
coder_gid=$(id -g coder)
if [[ "$coder_uid" != "$project_uid" || "$coder_gid" != "$project_gid" ]]; then
  printf 'sandbox identity does not match project mount: expected %s:%s, coder is %s:%s\n' \
    "$project_uid" "$project_gid" "$coder_uid" "$coder_gid" >&2
  exit 77
fi

if [[ ${ENABLE_DOCKER:-0} == 1 ]]; then
  if [[ $(id -u) != 0 ]]; then
    printf 'internal Docker bootstrap must start as root\n' >&2
    exit 78
  fi
  mkdir -p /run/coding-docker /var/lib/coding-docker
  chown root:docker /run/coding-docker
  chmod 0710 /run/coding-docker
  chown root:root /var/lib/coding-docker
  chmod 0700 /var/lib/coding-docker

  namespace_ready=/run/coding-docker/namespace.ready
  rm -f -- "$namespace_ready"
  unshare --mount -- bash -c '
    set -euo pipefail
    mount --make-rprivate /
    mount -t proc -o rw,nosuid,nodev,noexec proc /proc
    mount -t cgroup2 -o rw,nosuid,nodev,noexec cgroup2 /sys/fs/cgroup
    : > /run/coding-docker/namespace.ready
    exec sleep infinity
  ' >/home/coder/.local/share/docker/namespace.log 2>&1 &
  namespace_pid=$!

  cleanup() {
    local pid
    for pid in "${daemon_pid:-}" "${namespace_pid:-}"; do
      [[ -n "$pid" ]] && kill "$pid" 2>/dev/null || true
    done
    for pid in "${daemon_pid:-}" "${namespace_pid:-}"; do
      [[ -n "$pid" ]] && wait "$pid" 2>/dev/null || true
    done
  }
  trap cleanup EXIT INT TERM

  namespace_is_ready=0
  for _ in {1..120}; do
    if ! kill -0 "$namespace_pid" 2>/dev/null; then break; fi
    if [[ -f "$namespace_ready" ]]; then namespace_is_ready=1; break; fi
    sleep 0.05
  done
  if [[ "$namespace_is_ready" != 1 ]]; then
    printf 'private mount namespace did not become ready\n' >&2
    tail -n 40 /home/coder/.local/share/docker/namespace.log >&2 || true
    exit 78
  fi

  nsenter --target "$namespace_pid" --mount -- dockerd \
    --host=unix:///run/coding-docker/docker.sock \
    --group=docker \
    --data-root=/var/lib/coding-docker \
    --exec-root=/run/coding-docker/exec \
    --pidfile=/run/coding-docker/docker.pid \
    --storage-driver=vfs \
    >/home/coder/.local/share/docker/daemon.log 2>&1 &
  daemon_pid=$!
  daemon_ready=0
  for _ in {1..120}; do
    if ! kill -0 "$daemon_pid" 2>/dev/null; then break; fi
    if docker --host unix:///run/coding-docker/docker.sock info >/dev/null 2>&1; then
      daemon_ready=1
      break
    fi
    sleep 0.25
  done
  if [[ "$daemon_ready" != 1 ]]; then
    printf 'internal Docker daemon did not become ready\n' >&2
    tail -n 40 /home/coder/.local/share/docker/daemon.log >&2 || true
    exit 78
  fi
  wait "$daemon_pid"
  exit 0
fi

exec sleep infinity
