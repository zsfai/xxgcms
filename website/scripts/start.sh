#!/usr/bin/env bash
# 快捷入口：等同于 ./scripts/website.sh start
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "$SCRIPT_DIR/website.sh" start "$@"
