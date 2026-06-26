#!/usr/bin/env bash
# Shared SSH/SCP helpers: key auth via openssh, password auth via sshpass or paramiko.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SSH_HELPER="${SCRIPT_DIR}/ssh_helper.py"

# Git Bash on Windows: `python3` 常指向 WindowsApps 占位符，无法 import paramiko；
# 须逐个探测 python / python3 / py，选用能成功 import paramiko 的解释器。
_python_with_paramiko() {
  local candidate
  for candidate in python python3 py; do
    if command -v "${candidate}" >/dev/null 2>&1; then
      if "${candidate}" -c "import paramiko" 2>/dev/null; then
        echo "${candidate}"
        return 0
      fi
    fi
  done
  return 1
}

_has_paramiko() {
  _python_with_paramiko >/dev/null 2>&1
}

init_ssh_opts() {
  SSH_PORT="${SSH_PORT:-22}"
  SSH_OPTS=(-p "${SSH_PORT}" -o StrictHostKeyChecking=accept-new)
  SCP_OPTS=(-P "${SSH_PORT}" -o StrictHostKeyChecking=accept-new)
  SSH_TARGET="${REMOTE_USER}@${REMOTE_HOST}"
}

_use_password_auth() {
  [[ -n "${REMOTE_PASSWORD:-}" ]]
}

run_ssh() {
  init_ssh_opts
  if _use_password_auth; then
    if command -v sshpass >/dev/null 2>&1; then
      SSHPASS="${REMOTE_PASSWORD}" sshpass -e ssh "${SSH_OPTS[@]}" "${SSH_TARGET}" "$@"
    elif [[ -f "${SSH_HELPER}" ]] && py="$(_python_with_paramiko)"; then
      REMOTE_HOST="${REMOTE_HOST}" REMOTE_USER="${REMOTE_USER}" \
        REMOTE_PASSWORD="${REMOTE_PASSWORD}" SSH_PORT="${SSH_PORT}" \
        "${py}" "${SSH_HELPER}" exec "$*"
    else
      echo "已设置 REMOTE_PASSWORD，但未找到 sshpass 或 paramiko。" >&2
      echo "  pip install paramiko   # Windows: 用 python -m pip install paramiko" >&2
      echo "  sudo apt install sshpass  # Linux/WSL" >&2
      exit 1
    fi
  else
    ssh "${SSH_OPTS[@]}" "${SSH_TARGET}" "$@"
  fi
}

run_scp_to_remote() {
  local local_path="$1"
  local remote_path="$2"
  init_ssh_opts
  if _use_password_auth; then
    if command -v sshpass >/dev/null 2>&1; then
      SSHPASS="${REMOTE_PASSWORD}" sshpass -e scp "${SCP_OPTS[@]}" "${local_path}" "${SSH_TARGET}:${remote_path}"
    elif [[ -f "${SSH_HELPER}" ]] && py="$(_python_with_paramiko)"; then
      # Git Bash 会把 /home/... 环境变量转成 Windows 路径
      MSYS2_ENV_CONV_EXCL='*' \
        REMOTE_HOST="${REMOTE_HOST}" REMOTE_USER="${REMOTE_USER}" \
        REMOTE_PASSWORD="${REMOTE_PASSWORD}" SSH_PORT="${SSH_PORT}" \
        REMOTE_SFTP_LOCAL="${local_path}" REMOTE_SFTP_REMOTE="${remote_path}" \
        "${py}" "${SSH_HELPER}" upload
    else
      echo "已设置 REMOTE_PASSWORD，但未找到 sshpass 或 paramiko。" >&2
      exit 1
    fi
  else
    scp "${SCP_OPTS[@]}" "${local_path}" "${SSH_TARGET}:${remote_path}"
  fi
}

run_scp_from_remote() {
  local remote_spec="$1"
  local local_dir="$2"
  init_ssh_opts
  if _use_password_auth; then
    if command -v sshpass >/dev/null 2>&1; then
      SSHPASS="${REMOTE_PASSWORD}" sshpass -e scp "${SCP_OPTS[@]}" "${SSH_TARGET}:${remote_spec}" "${local_dir}/"
    elif [[ -f "${SSH_HELPER}" ]] && py="$(_python_with_paramiko)"; then
      MSYS2_ENV_CONV_EXCL='*' \
        REMOTE_HOST="${REMOTE_HOST}" REMOTE_USER="${REMOTE_USER}" \
        REMOTE_PASSWORD="${REMOTE_PASSWORD}" SSH_PORT="${SSH_PORT}" \
        REMOTE_SFTP_REMOTE="${remote_spec}" REMOTE_SFTP_LOCAL="${local_dir}" \
        "${py}" "${SSH_HELPER}" download
    else
      echo "已设置 REMOTE_PASSWORD，但未找到 sshpass 或 paramiko。" >&2
      exit 1
    fi
  else
    scp "${SCP_OPTS[@]}" "${SSH_TARGET}:${remote_spec}" "${local_dir}/"
  fi
}

run_ssh_script() {
  local remote_preamble="$1"
  local script_file="$2"
  init_ssh_opts
  if _use_password_auth; then
    if command -v sshpass >/dev/null 2>&1; then
      SSHPASS="${REMOTE_PASSWORD}" sshpass -e ssh -t "${SSH_OPTS[@]}" "${SSH_TARGET}" \
        "${remote_preamble} bash -s" < "${script_file}"
    elif [[ -f "${SSH_HELPER}" ]] && py="$(_python_with_paramiko)"; then
      MSYS2_ENV_CONV_EXCL='*' \
        REMOTE_HOST="${REMOTE_HOST}" REMOTE_USER="${REMOTE_USER}" \
        REMOTE_PASSWORD="${REMOTE_PASSWORD}" SSH_PORT="${SSH_PORT}" \
        "${py}" "${SSH_HELPER}" exec-stdin "${remote_preamble} bash -s" < "${script_file}"
    else
      echo "已设置 REMOTE_PASSWORD，但未找到 sshpass 或 paramiko。" >&2
      return 1
    fi
  else
    ssh -t "${SSH_OPTS[@]}" "${SSH_TARGET}" "${remote_preamble} bash -s" < "${script_file}"
  fi
}
