#!/usr/bin/env bash
set -euo pipefail

root_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)
config="$root_dir/sandbox.json"

fail() { printf 'coding docker: %s\n' "$*" >&2; exit 64; }
read_config() { jq -er "$1" "$config"; }
bool_arg() {
  if [[ $(read_config "$1") == true ]]; then printf 1; else printf 0; fi
}
valid_name() { [[ $1 =~ ^[a-z0-9][a-z0-9_.-]*$ ]]; }

[[ -f "$config" ]] || fail 'sandbox.json is missing'
[[ $(read_config '.schema_version') == 2 ]] || fail 'unsupported sandbox schema'
[[ $(read_config '.status') == ready ]] || fail 'recipe is incomplete; complete it in its owning task'

scope=$(read_config '.identity.scope')
agent=$(read_config '.identity.agent')
image=$(read_config '.image')
container=$(read_config '.container')
project_source=$(read_config '.project.source')
project_target=$(read_config '.project.target')
valid_name "$scope" || fail 'invalid scope name'
[[ "$agent" =~ ^(claude-code|codex|opencode|pi|kimi-code)$ ]] || fail 'unsupported agent'
valid_name "$image" || fail 'invalid image name'
valid_name "$container" || fail 'invalid container name'
[[ "$project_source" == /* && "$project_source" != *','* ]] || fail 'invalid project source path'
[[ -d "$project_source" ]] || fail "project source is not a directory: $project_source"
[[ "$project_target" == /home/coder/* ]] || fail 'project target must stay below /home/coder'
project_uid=$(stat -c %u -- "$project_source")
project_gid=$(stat -c %g -- "$project_source")
(( project_uid > 0 && project_gid > 0 )) || fail 'project source must have a non-root UID and GID'

if ! docker image inspect "$image" >/dev/null 2>&1; then
  docker build \
    --label "io.project-of-projects.scope=$scope" \
    --label "io.project-of-projects.agent=$agent" \
    --label "io.project-of-projects.uid=$project_uid" \
    --label "io.project-of-projects.gid=$project_gid" \
    --build-arg "SANDBOX_UID=$project_uid" \
    --build-arg "SANDBOX_GID=$project_gid" \
    --build-arg "INSTALL_NODE=$(bool_arg '.stack.node')" \
    --build-arg "INSTALL_YARN=$(bool_arg '.stack.yarn')" \
    --build-arg "INSTALL_PNPM=$(bool_arg '.stack.pnpm')" \
    --build-arg "INSTALL_PHP=$(bool_arg '.stack.php')" \
    --build-arg "INSTALL_COMPOSER=$(bool_arg '.stack.composer')" \
    --build-arg "INSTALL_PYTHON=$(bool_arg '.stack.python')" \
    --build-arg "INSTALL_GO=$(bool_arg '.stack.go')" \
    --build-arg "INSTALL_RUST=$(bool_arg '.stack.rust')" \
    --build-arg "INSTALL_DOCKER=$(bool_arg '.stack.docker')" \
    --tag "$image" "$root_dir"
else
  image_scope=$(docker image inspect --format '{{index .Config.Labels "io.project-of-projects.scope"}}' "$image")
  image_agent=$(docker image inspect --format '{{index .Config.Labels "io.project-of-projects.agent"}}' "$image")
  image_uid=$(docker image inspect --format '{{index .Config.Labels "io.project-of-projects.uid"}}' "$image")
  image_gid=$(docker image inspect --format '{{index .Config.Labels "io.project-of-projects.gid"}}' "$image")
  [[ "$image_scope:$image_agent" == "$scope:$agent" ]] || fail 'image ownership labels do not match'
  [[ "$image_uid:$image_gid" == "$project_uid:$project_gid" ]] || fail 'image identity does not match project ownership'
fi

mount_args=(--mount "type=bind,src=$project_source,dst=$project_target")
while IFS=$'\t' read -r source target read_only; do
  [[ "$source" == /* && "$source" != *','* ]] || fail "invalid bind source: $source"
  [[ ! -S "$source" ]] || fail "socket binds are forbidden: $source"
  [[ -e "$source" ]] || fail "bind source is missing: $source"
  [[ "$target" == /home/coder/* ]] || fail "bind target escapes coder home: $target"
  mount_spec="type=bind,src=$source,dst=$target"
  [[ "$read_only" == true ]] && mount_spec+=",readonly"
  mount_args+=(--mount "$mount_spec")
done < <(jq -er '.binds[] | [.source, .target, .read_only] | @tsv' "$config")

if ! docker container inspect "$container" >/dev/null 2>&1; then
  docker_enabled=$(bool_arg '.stack.docker')
  security_args=(--cap-drop ALL --pids-limit 2048)
  runtime_args=(--user coder --security-opt no-new-privileges)
  if [[ "$docker_enabled" == 1 ]]; then
    # Candidate allowlist: F03 must prove and reduce it against Docker/Compose.
    security_args+=(
      --cap-add AUDIT_WRITE --cap-add CHOWN --cap-add DAC_OVERRIDE
      --cap-add FOWNER --cap-add FSETID --cap-add KILL --cap-add MKNOD
      --cap-add NET_ADMIN --cap-add NET_BIND_SERVICE --cap-add NET_RAW
      --cap-add SETFCAP --cap-add SETGID --cap-add SETPCAP --cap-add SETUID
      --cap-add SYS_ADMIN --cap-add SYS_CHROOT
      --security-opt "seccomp=$root_dir/seccomp-docker.json"
    )
    runtime_args=(
      --user root
      --env DOCKER_HOST=unix:///run/coding-docker/docker.sock
      --sysctl net.ipv4.ip_forward=1
      --ulimit memlock=-1:-1
      --tmpfs /sys/fs/cgroup:rw,nosuid,nodev,noexec
    )
  fi
  docker create \
    --name "$container" \
    --hostname "$container" \
    --label "io.project-of-projects.scope=$scope" \
    --label "io.project-of-projects.agent=$agent" \
    "${security_args[@]}" \
    "${runtime_args[@]}" \
    --env "SANDBOX_PROJECT_DIR=$project_target" \
    --env "ENABLE_DOCKER=$(bool_arg '.stack.docker')" \
    "${mount_args[@]}" \
    "$image" >/dev/null
fi

container_scope=$(docker inspect --format '{{index .Config.Labels "io.project-of-projects.scope"}}' "$container")
container_agent=$(docker inspect --format '{{index .Config.Labels "io.project-of-projects.agent"}}' "$container")
[[ "$container_scope:$container_agent" == "$scope:$agent" ]] || fail 'container ownership labels do not match'

if [[ $(docker inspect --format '{{.State.Running}}' "$container") != true ]]; then
  docker start "$container" >/dev/null
fi

mapfile -t open_argv < <(jq -er '.agent.open_argv[]' "$config")
(( ${#open_argv[@]} > 0 )) || fail 'agent open command is empty'
docker exec --interactive --tty --user coder \
  --workdir "$project_target" \
  --env HOME=/home/coder \
  "$container" setpriv --no-new-privs -- "${open_argv[@]}"
