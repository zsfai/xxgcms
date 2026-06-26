#!/usr/bin/env bash
# 离线安装：等待 backend 就绪时的进度与日志摘要（由 install.sh source）

BACKEND_CONTAINER="${BACKEND_CONTAINER:-xxgcms-admin-backend}"
MYSQL_CONTAINER="${MYSQL_CONTAINER:-xxgcms-mysql}"
_SPINNER_FRAMES=('|' '/' '-' '\\')
_RECENT_BACKEND_LINES=10
_RECENT_MYSQL_LINES=8

_fetch_backend_logs() {
  docker logs "${BACKEND_CONTAINER}" 2>&1 | tail -n 60 || true
}

_fetch_mysql_logs() {
  docker logs "${MYSQL_CONTAINER}" 2>&1 | tail -n 30 || true
}

_backend_recent_lines() {
  local logs="$1"
  echo "${logs}" | tail -n "${_RECENT_BACKEND_LINES}"
}

_mysql_is_first_init() {
  local mlogs="$1"
  echo "${mlogs}" | grep -qiE 'Initializing database|entrypoint-initdb|/docker-entrypoint-initdb\.d/'
}

_backend_first_run_count() {
  docker logs "${BACKEND_CONTAINER}" 2>&1 | grep -c 'First run — initializing' 2>/dev/null || echo 0
}

_classify_backend_line() {
  local line="$1"
  case "${line}" in
    *"Starting uWSGI"*) echo "uwsgi|启动 API 服务 (uWSGI)" ;;
    *"Refreshing deployment credentials"*) echo "creds|更新部署凭据" ;;
    *"Syncing database schema"*) echo "sync|同步数据库结构" ;;
    *"Ensuring site root_path"*) echo "paths|修正站点路径" ;;
    *"Setup complete"*) echo "setup_done|首次配置完成，即将启动服务" ;;
    *"数据库初始化全部完成"*) echo "db_done|数据库初始化完成" ;;
    *"初始化 CMS 库"*) echo "init_cms|初始化 CMS 站点库" ;;
    *"初始化系统库"*) echo "init_xxgcms|初始化系统库 (xxgcms)" ;;
    *"First run — initializing"*) echo "first_run|准备环境与数据库 (setup)" ;;
    *"Restoring config from"*) echo "restore|恢复已有配置" ;;
    *"MySQL is ready"*) echo "mysql_ok|MySQL 已连接" ;;
    *"[wait-for-mysql]"*"Attempt"*) echo "wait_mysql|等待 MySQL 连接…" ;;
    *"[wait-for-mysql]"*"Waiting for MySQL"*) echo "wait_mysql|连接 MySQL…" ;;
    *Traceback*|*OperationalError*|*"did not become ready"*|*"ERROR"*) echo "error|初始化出错（见下方日志）" ;;
    *) echo "" ;;
  esac
}

_detect_backend_init_stage() {
  local logs="$1"
  local mysql_hint="$2"
  local restart_count line classified stage_id stage_label recent

  if [[ -z "${logs}" ]]; then
    if docker ps --format '{{.Names}}' | grep -qx "${BACKEND_CONTAINER}"; then
      if [[ -n "${mysql_hint}" ]]; then
        echo "${mysql_hint} · 等待 backend 日志"
      else
        echo "backend 已启动，等待输出…"
      fi
    elif [[ -n "${mysql_hint}" ]]; then
      echo "${mysql_hint} · 等待 backend 容器"
    else
      echo "等待 backend 容器启动"
    fi
    return
  fi

  restart_count="$(_backend_first_run_count)"
  if [[ "${restart_count}" -gt 1 ]]; then
    echo "backend 异常重启（第 ${restart_count} 次，请查看日志排查）"
    return
  fi

  recent="$(_backend_recent_lines "${logs}")"
  while IFS= read -r line; do
    [[ -z "${line//[[:space:]]/}" ]] && continue
    classified="$(_classify_backend_line "${line}")"
    if [[ -n "${classified}" ]]; then
      stage_id="${classified%%|*}"
      stage_label="${classified#*|}"
      if [[ "${stage_id}" == "error" ]]; then
        echo "${stage_label}"
        return
      fi
      echo "${stage_label}"
      return
    fi
  done < <(echo "${recent}" | tac 2>/dev/null || tail -r <<< "${recent}" 2>/dev/null || echo "${recent}" | awk '{lines[NR]=$0} END {for (i=NR; i>0; i--) print lines[i]}')

  if [[ -n "${mysql_hint}" ]]; then
    echo "${mysql_hint} · backend 处理中"
  else
    echo "backend 初始化中…"
  fi
}

_mysql_status_hint() {
  local health status mlogs recent line
  if ! docker ps --format '{{.Names}}' | grep -qx "${MYSQL_CONTAINER}"; then
    echo "等待 MySQL 容器启动"
    return
  fi

  mlogs="$(_fetch_mysql_logs)"
  health="$(docker inspect --format '{{if .State.Health}}{{.State.Health.Status}}{{end}}' "${MYSQL_CONTAINER}" 2>/dev/null || true)"
  status="$(docker inspect --format '{{.State.Status}}' "${MYSQL_CONTAINER}" 2>/dev/null || true)"

  recent="$(echo "${mlogs}" | tail -n "${_RECENT_MYSQL_LINES}")"
  if echo "${recent}" | grep -qiE 'Initializing database|entrypoint-initdb'; then
    echo "MySQL 首次初始化数据目录（约 1～3 分钟）"
    return
  fi

  if echo "${recent}" | grep -qi 'ready for connections'; then
    if [[ "${health}" == "healthy" ]]; then
      return
    fi
    echo "MySQL 已启动，等待健康检查"
    return
  fi

  case "${health}" in
    healthy) ;;
    starting) echo "MySQL 健康检查中" ;;
    unhealthy) echo "MySQL 启动中" ;;
    *)
      if [[ "${status}" == "running" ]]; then
        echo "MySQL 运行中"
      else
        echo "MySQL 状态: ${status:-未知}"
      fi
      ;;
  esac
}

_sanitize_log_hint() {
  local text="$1"
  text="$(echo "${text}" | sed 's/^[[:space:]]*//; s/[[:space:]]*$//')"
  [[ -z "${text}" ]] && return
  case "${text}" in
    *"====="*|*"请务必将上述凭据"*|*"【重要】"*) return ;;
  esac
  echo "${text}" | cut -c1-76
}

_latest_log_hint() {
  local logs="$1"
  local recent line hint
  recent="$(_backend_recent_lines "${logs}")"
  while IFS= read -r line; do
    hint="$(_sanitize_log_hint "${line}")"
    if [[ -n "${hint}" ]]; then
      echo "${hint}"
      return
    fi
  done < <(echo "${recent}" | tac 2>/dev/null || tail -r <<< "${recent}" 2>/dev/null || echo "${recent}" | awk '{lines[NR]=$0} END {for (i=NR; i>0; i--) print lines[i]}')
}

_latest_mysql_log_hint() {
  local mlogs="$1"
  local hint
  hint="$(echo "${mlogs}" | tail -n "${_RECENT_MYSQL_LINES}" | grep -viE '^$|^=*$' | tail -1)"
  _sanitize_log_hint "${hint}"
}

_backend_exec() {
  local use_up_core="$1"
  local compose_file="$2"
  shift 2
  if [[ "${use_up_core}" == "1" ]]; then
    docker exec "${BACKEND_CONTAINER}" "$@"
  else
    compose_cmd -f "${compose_file}" exec -T backend "$@"
  fi
}

# slim 镜像通常无 pgrep；优先看 PID1（entrypoint exec uwsgi 后即为 uwsgi）
_backend_is_ready() {
  local use_up_core="$1"
  local compose_file="$2"
  local pid1

  if ! docker ps --format '{{.Names}}' | grep -qx "${BACKEND_CONTAINER}"; then
    return 1
  fi

  pid1="$(_backend_exec "${use_up_core}" "${compose_file}" sh -c \
    'tr "\0" " " </proc/1/cmdline 2>/dev/null' 2>/dev/null || true)"

  if [[ "${pid1}" == *uwsgi* ]]; then
    return 0
  fi

  # entrypoint / manage.py 阶段 8002 尚未监听，跳过端口探测以免误报 Connection refused
  if [[ "${pid1}" == *entrypoint-backend* || "${pid1}" == *manage.py* ]]; then
    return 1
  fi

  if _backend_exec "${use_up_core}" "${compose_file}" python3 -c \
    'import socket, sys
try:
    socket.create_connection(("127.0.0.1", 8002), 2).close()
except OSError:
    sys.exit(1)' 2>/dev/null; then
    return 0
  fi

  _backend_exec "${use_up_core}" "${compose_file}" pgrep -x uwsgi >/dev/null 2>&1
}

# 用法: wait_for_backend_ready_with_progress <max_tries> <use_up_core:0|1> <compose_file>
wait_for_backend_ready_with_progress() {
  local max_tries="${1:-300}"
  local use_up_core="${2:-0}"
  local compose_file="${3:-}"
  local start_ts="${SECONDS}"
  local i=0
  local last_stage=""
  local last_hint=""
  local spin_idx=0
  local mlogs
  local uwsgi_stage_ts=0

  mlogs="$(_fetch_mysql_logs)"
  echo ""
  if _mysql_is_first_init "${mlogs}"; then
    echo "等待服务就绪（MySQL 首次初始化约 2～4 分钟；后续步骤约 1～2 分钟）"
  else
    echo "等待服务就绪（通常 1～2 分钟内完成）"
  fi
  echo "  详细日志: docker logs -f ${BACKEND_CONTAINER}"
  echo ""

  while [[ "${i}" -lt "${max_tries}" ]]; do
    if _backend_is_ready "${use_up_core}" "${compose_file}"; then
      printf '\r\033[K'
      local elapsed=$((SECONDS - start_ts))
      printf '  ✓ backend 已就绪（用时 %d分%d秒）\n' $((elapsed / 60)) $((elapsed % 60))
      return 0
    fi

    local logs mysql_hint stage hint elapsed spin
    logs="$(_fetch_backend_logs)"
    mlogs="$(_fetch_mysql_logs)"
    mysql_hint="$(_mysql_status_hint)"
    stage="$(_detect_backend_init_stage "${logs}" "${mysql_hint}")"

    if [[ "${stage}" == *"uWSGI"* || "${stage}" == *"API 服务"* ]]; then
      [[ "${uwsgi_stage_ts}" -eq 0 ]] && uwsgi_stage_ts="${SECONDS}"
      if [[ $((SECONDS - uwsgi_stage_ts)) -gt 30 ]]; then
        stage="uWSGI 启动异常（超过 30 秒，请查 backend 日志）"
      elif [[ $((SECONDS - uwsgi_stage_ts)) -gt 10 ]]; then
        stage="等待 uWSGI 就绪（通常数秒内完成）"
      fi
    else
      uwsgi_stage_ts=0
    fi
    elapsed=$((SECONDS - start_ts))
    spin="${_SPINNER_FRAMES[$((spin_idx % 4))]}"
    spin_idx=$((spin_idx + 1))

    if [[ -z "${logs}" ]]; then
      hint="$(_latest_mysql_log_hint "${mlogs}")"
      [[ -n "${hint}" ]] && hint="[mysql] ${hint}"
    else
      hint="$(_latest_log_hint "${logs}")"
    fi

    printf '\r\033[K  [%02d:%02d] %s %s' $((elapsed / 60)) $((elapsed % 60)) "${spin}" "${stage}"

    if [[ -n "${hint}" && "${hint}" != "${last_hint}" ]]; then
      printf '\n    └ %s\n' "${hint}"
      last_hint="${hint}"
    elif [[ "${stage}" != "${last_stage}" ]]; then
      last_hint=""
    fi

    last_stage="${stage}"
    sleep 1
    i=$((i + 1))
  done

  printf '\r\033[K'
  local restart_count
  restart_count="$(_backend_first_run_count)"
  if _backend_is_ready "${use_up_core}" "${compose_file}"; then
    local elapsed=$((SECONDS - start_ts))
    printf '  ✓ backend 已就绪（用时 %d分%d秒）\n' $((elapsed / 60)) $((elapsed % 60))
    return 0
  fi
  if [[ "${restart_count}" -gt 1 ]]; then
    echo "  检测到 backend 已重启 ${restart_count} 次，可能初始化失败，请执行:" >&2
    echo "    docker compose -f docker-compose.offline.yml logs --tail 80 backend" >&2
  else
    echo "  安装脚本未能确认 backend 就绪；若后台可访问可忽略，或执行:" >&2
    echo "    docker compose -f docker-compose.offline.yml ps backend" >&2
    echo "    docker compose -f docker-compose.offline.yml logs --tail 30 backend" >&2
  fi
  return 1
}
