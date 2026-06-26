#!/usr/bin/env bash
# Build .env from container environment (docker compose env_file).
# Usage: prepare-env-from-compose.sh backend
set -euo pipefail

TARGET="${1:-backend}"

write_env_from_example() {
  local example_path="$1"
  local output_path="$2"
  python3 - "$example_path" "$output_path" <<'PY'
import os
import sys
from pathlib import Path

example_path = Path(sys.argv[1])
output_path = Path(sys.argv[2])
lines_out = []

for raw_line in example_path.read_text(encoding='utf-8').splitlines():
    stripped = raw_line.strip()
    if not stripped or stripped.startswith('#') or '=' not in raw_line:
        lines_out.append(raw_line)
        continue
    key, example_val = raw_line.split('=', 1)
    key = key.strip()
    example_val = example_val.strip()
    value = os.environ.get(key, example_val)
    if key == 'XXGCMS_DB_HOST' and value in ('127.0.0.1', 'localhost', ''):
        value = 'mysql'
    lines_out.append(f'{key}={value}')

output_path.write_text('\n'.join(lines_out) + '\n', encoding='utf-8')
PY
}

if [[ "${TARGET}" == "backend" ]]; then
  write_env_from_example /app/.env.example /app/.env
  echo "[prepare-env] Wrote /app/.env from compose environment."
else
  echo "Unknown target: ${TARGET}" >&2
  exit 1
fi
