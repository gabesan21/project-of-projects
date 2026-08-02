FROM ubuntu:26.04

ARG INSTALL_NODE=0
ARG INSTALL_YARN=0
ARG INSTALL_PNPM=0
ARG INSTALL_PHP=0
ARG INSTALL_COMPOSER=0
ARG INSTALL_PYTHON=0
ARG INSTALL_GO=0
ARG INSTALL_RUST=0
ARG INSTALL_DOCKER=0
ARG SANDBOX_UID
ARG SANDBOX_GID

RUN set -eu; \
    apt-get update; \
    apt-get install -y --no-install-recommends \
      ca-certificates curl fd-find git gh jq less openssh-client procps ripgrep tini tmux util-linux; \
    ln -s /usr/bin/fdfind /usr/local/bin/fd; \
    git_version="$(git version | awk '{print $3}')"; \
    dpkg --compare-versions "$git_version" ge 2.48 || { \
      echo "Git >= 2.48 is required for relative worktrees" >&2; exit 64; \
    }; \
    rm -rf /var/lib/apt/lists/*

RUN set -eu; \
    case "$INSTALL_NODE:$INSTALL_YARN:$INSTALL_PNPM:$INSTALL_PHP:$INSTALL_COMPOSER:$INSTALL_PYTHON:$INSTALL_GO:$INSTALL_RUST:$INSTALL_DOCKER" in \
      *[!01:]*) echo "toolchain flags must be 0 or 1" >&2; exit 64 ;; \
    esac; \
    if [ "$INSTALL_NODE" = 1 ] || [ "$INSTALL_YARN" = 1 ] || [ "$INSTALL_PNPM" = 1 ]; then \
      node_version=22.19.0; \
      case "$(dpkg --print-architecture)" in \
        amd64) node_arch=x64 ;; \
        arm64) node_arch=arm64 ;; \
        *) echo "unsupported architecture for Node.js" >&2; exit 64 ;; \
      esac; \
      node_archive="node-v${node_version}-linux-${node_arch}.tar.xz"; \
      node_url="https://nodejs.org/dist/v${node_version}"; \
      apt-get update; apt-get install -y --no-install-recommends xz-utils; \
      curl --fail --silent --show-error --location \
        --output "/tmp/${node_archive}" "${node_url}/${node_archive}"; \
      curl --fail --silent --show-error --location \
        --output /tmp/node-shasums "${node_url}/SHASUMS256.txt"; \
      grep "  ${node_archive}$" /tmp/node-shasums | \
        sed "s#  ${node_archive}$#  /tmp/${node_archive}#" | sha256sum --check --strict -; \
      tar --extract --xz --file "/tmp/${node_archive}" \
        --directory /usr/local --strip-components 1; \
      [ "$(node --version)" = "v${node_version}" ]; \
      npm --version >/dev/null; \
      rm -f "/tmp/${node_archive}" /tmp/node-shasums; \
    fi; \
    if [ "$INSTALL_YARN" = 1 ]; then npm install --global yarn@1.22.22; fi; \
    if [ "$INSTALL_PNPM" = 1 ]; then npm install --global pnpm; fi; \
    if [ "$INSTALL_PHP" = 1 ] || [ "$INSTALL_COMPOSER" = 1 ]; then \
      apt-get update; apt-get install -y --no-install-recommends php-cli; \
    fi; \
    if [ "$INSTALL_COMPOSER" = 1 ]; then \
      apt-get update; apt-get install -y --no-install-recommends composer; \
    fi; \
    if [ "$INSTALL_PYTHON" = 1 ]; then \
      apt-get update; apt-get install -y --no-install-recommends python3 python3-pip python3-venv; \
    fi; \
    if [ "$INSTALL_GO" = 1 ]; then \
      apt-get update; apt-get install -y --no-install-recommends golang-go; \
    fi; \
    if [ "$INSTALL_RUST" = 1 ]; then \
      apt-get update; apt-get install -y --no-install-recommends cargo rustc; \
    fi; \
    if [ "$INSTALL_DOCKER" = 1 ]; then \
      apt-get update; apt-get install -y --no-install-recommends \
        docker.io docker-compose-v2; \
    fi; \
    rm -rf /var/lib/apt/lists/*

COPY recipe.json /tmp/coding-docker-recipe.json
RUN ["bash", "-euo", "pipefail", "-c", "jq -e '.install.status == \"complete\" and (.install.argv | type == \"array\" and length > 0 and all(.[]; type == \"string\" and length > 0 and (contains(\"\\u0000\") | not)))' /tmp/coding-docker-recipe.json >/dev/null; mapfile -d '' -t install_argv < <(jq -j '.install.argv[] | ., \"\\u0000\"' /tmp/coding-docker-recipe.json); \"${install_argv[@]}\"; rm -f /tmp/coding-docker-recipe.json"]

COPY sandbox.json /tmp/coding-docker-sandbox.json
RUN set -eu; \
    jq -r '.stack.additional_packages[]?' /tmp/coding-docker-sandbox.json > /tmp/additional-packages; \
    if [ -s /tmp/additional-packages ]; then \
      apt-get update; \
      while IFS= read -r package; do \
        case "$package" in *[!a-z0-9+.-]*|'') echo "invalid package name" >&2; exit 64 ;; esac; \
        apt-get install -y --no-install-recommends -- "$package"; \
      done < /tmp/additional-packages; \
    fi; \
    rm -rf /var/lib/apt/lists/* /tmp/additional-packages /tmp/coding-docker-sandbox.json

RUN set -eu; \
    case "$SANDBOX_UID:$SANDBOX_GID" in \
      *[!0-9:]*|:*|*:) echo "SANDBOX_UID and SANDBOX_GID must be decimal integers" >&2; exit 64 ;; \
    esac; \
    if [ "$SANDBOX_UID" -eq 0 ] || [ "$SANDBOX_GID" -eq 0 ]; then \
      echo "sandbox identity must be non-root" >&2; exit 77; \
    fi; \
    existing_group="$(getent group "$SANDBOX_GID" | cut -d: -f1 || true)"; \
    if [ -n "$existing_group" ]; then \
      [ "$existing_group" = coder ] || groupmod --new-name coder "$existing_group"; \
    else \
      groupadd --gid "$SANDBOX_GID" coder; \
    fi; \
    existing_user="$(getent passwd "$SANDBOX_UID" | cut -d: -f1 || true)"; \
    if [ -n "$existing_user" ]; then \
      if [ "$existing_user" != coder ]; then \
        usermod --login coder --home /home/coder --move-home \
          --gid coder --shell /bin/bash "$existing_user"; \
      fi; \
    else \
      useradd --uid "$SANDBOX_UID" --gid coder --create-home --shell /bin/bash coder; \
    fi; \
    if getent group docker >/dev/null; then usermod --append --groups docker coder; fi; \
    install -d -m 0700 -o coder -g coder \
      /home/coder/.local /home/coder/.local/share /home/coder/.local/share/docker \
      "/run/user/$SANDBOX_UID"

COPY entrypoint.sh /usr/local/bin/entrypoint.sh
COPY seccomp-docker.json /usr/local/share/coding-docker/seccomp-docker.json
RUN chmod 0755 /usr/local/bin/entrypoint.sh

WORKDIR /home/coder
ENV HOME=/home/coder
RUN runuser --user coder -- git config --global gc.auto 0
ENTRYPOINT ["/usr/bin/tini", "--", "/usr/local/bin/entrypoint.sh"]
