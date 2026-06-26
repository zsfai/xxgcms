#!/usr/bin/env bash
# Restore persisted .env from config volume.
# Usage: sync-env-from-config.sh [backend|website]
set -euo pipefail

TARGET="${1:-backend}"
CONFIG_DIR="${CONFIG_DIR:-/data/config}"

case "${TARGET}" in
  backend)
    if [[ -f "${CONFIG_DIR}/admin-backend.env" ]]; then
      cp "${CONFIG_DIR}/admin-backend.env" /app/.env
    fi
    if [[ -f "${CONFIG_DIR}/.credentials" ]]; then
      cp "${CONFIG_DIR}/.credentials" /app/.credentials
    fi
    ;;
  website)
    if [[ -f "${CONFIG_DIR}/website.env" ]]; then
      cp "${CONFIG_DIR}/website.env" /app/.env
    fi
    ;;
  *)
    echo "Unknown target: ${TARGET}" >&2
    exit 1
    ;;
esac
