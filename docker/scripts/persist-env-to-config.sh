#!/usr/bin/env bash
# Persist generated .env files to config volume (run from backend container).
set -euo pipefail

CONFIG_DIR="${CONFIG_DIR:-/data/config}"
mkdir -p "${CONFIG_DIR}"

if [[ -f /app/.env ]]; then
  cp /app/.env "${CONFIG_DIR}/admin-backend.env"
fi

if [[ -f /app/.env ]]; then
  # Generate website.env from same compose vars + website template
  python3 - /docker/website.env.example "${CONFIG_DIR}/website.env" <<'PY'
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
    lines_out.append(f'{key}={value}')

output_path.write_text('\n'.join(lines_out) + '\n', encoding='utf-8')
PY
fi

if [[ -f /app/.credentials ]]; then
  cp /app/.credentials "${CONFIG_DIR}/.credentials"
fi

touch "${CONFIG_DIR}/.initialized"
