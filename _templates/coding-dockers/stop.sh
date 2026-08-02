#!/usr/bin/env bash
set -euo pipefail

root_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)
config="$root_dir/sandbox.json"
[[ -f "$config" ]] || { printf 'coding docker: sandbox.json is missing\n' >&2; exit 64; }
container=$(jq -er '.container' "$config")
scope=$(jq -er '.identity.scope' "$config")
agent=$(jq -er '.identity.agent' "$config")

if docker container inspect "$container" >/dev/null 2>&1; then
  actual_scope=$(docker inspect --format '{{index .Config.Labels "io.project-of-projects.scope"}}' "$container")
  actual_agent=$(docker inspect --format '{{index .Config.Labels "io.project-of-projects.agent"}}' "$container")
  [[ "$actual_scope:$actual_agent" == "$scope:$agent" ]] || {
    printf 'coding docker: container ownership labels do not match\n' >&2
    exit 65
  }
  docker stop "$container" >/dev/null
fi
