#!/usr/bin/env bash
set -euo pipefail

HOST="${XXGCMS_DB_HOST:-mysql}"
PORT="${XXGCMS_DB_PORT:-3306}"
USER="${XXGCMS_DB_USER:-xxgcms}"
PASSWORD="${XXGCMS_DB_PASSWORD:-}"
MAX_TRIES="${MYSQL_WAIT_TRIES:-45}"
SLEEP_SEC="${MYSQL_WAIT_SLEEP:-1}"

export HOST PORT USER PASSWORD

echo "[wait-for-mysql] Waiting for MySQL at ${HOST}:${PORT} ..."

for ((i = 1; i <= MAX_TRIES; i++)); do
  if python3 - <<'PY'
import os
import sys
import pymysql

host = os.environ.get("HOST")
port = int(os.environ.get("PORT", "3306"))
user = os.environ.get("USER")
password = os.environ.get("PASSWORD")

try:
    conn = pymysql.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        connect_timeout=2,
    )
    conn.close()
    sys.exit(0)
except Exception:
    sys.exit(1)
PY
  then
    echo "[wait-for-mysql] MySQL is ready."
    exit 0
  fi
  if [[ "${i}" -eq 1 || "${i}" -eq "${MAX_TRIES}" || $((i % 5)) -eq 0 ]]; then
    echo "[wait-for-mysql] Attempt ${i}/${MAX_TRIES} failed, retry in ${SLEEP_SEC}s ..."
  fi
  sleep "${SLEEP_SEC}"
done

echo "[wait-for-mysql] MySQL did not become ready in time." >&2
exit 1
