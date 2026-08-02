#!/usr/bin/env bash
set -euo pipefail

root_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)
config="$root_dir/sandbox.json"
[[ -f "$config" ]] || { printf 'coding docker: sandbox.json is missing\n' >&2; exit 64; }

scope=$(jq -er '.identity.scope' "$config")
agent=$(jq -er '.identity.agent' "$config")
container=$(jq -er '.container' "$config")
image=$(jq -er '.image' "$config")

if [[ ${1:-} != --yes ]]; then
  printf 'Remove internal resources for %s/%s? Type REMOVE: ' "$scope" "$agent"
  read -r answer
  [[ "$answer" == REMOVE ]] || { printf 'Cancelled.\n'; exit 1; }
fi

if docker container inspect "$container" >/dev/null 2>&1; then
  actual_scope=$(docker inspect --format '{{index .Config.Labels "io.project-of-projects.scope"}}' "$container")
  actual_agent=$(docker inspect --format '{{index .Config.Labels "io.project-of-projects.agent"}}' "$container")
  [[ "$actual_scope:$actual_agent" == "$scope:$agent" ]] || {
    printf 'coding docker: container ownership labels do not match\n' >&2
    exit 65
  }
  docker rm --force "$container" >/dev/null
fi

if docker image inspect "$image" >/dev/null 2>&1; then
  actual_scope=$(docker image inspect --format '{{index .Config.Labels "io.project-of-projects.scope"}}' "$image")
  actual_agent=$(docker image inspect --format '{{index .Config.Labels "io.project-of-projects.agent"}}' "$image")
  [[ "$actual_scope:$actual_agent" == "$scope:$agent" ]] || {
    printf 'coding docker: image ownership labels do not match\n' >&2
    exit 65
  }
  docker image rm "$image" >/dev/null
fi

printf 'Internal resources removed; host bind sources were preserved.\n'
