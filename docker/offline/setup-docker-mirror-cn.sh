#!/usr/bin/env bash
# 在 Ubuntu 构建机上一键配置 Docker Hub 国内镜像加速（仅需执行一次）
# 用法: sudo ./docker/offline/setup-docker-mirror-cn.sh
set -euo pipefail

DAEMON_JSON="/etc/docker/daemon.json"

if [[ "${EUID}" -ne 0 ]]; then
  echo "请使用 root 执行: sudo $0" >&2
  exit 1
fi

mkdir -p /etc/docker

if [[ -f "${DAEMON_JSON}" ]]; then
  if grep -q 'registry-mirrors' "${DAEMON_JSON}"; then
    echo "已配置 registry-mirrors，当前内容:"
    cat "${DAEMON_JSON}"
    exit 0
  fi
  echo "警告: ${DAEMON_JSON} 已存在但未含 registry-mirrors，请手动合并后重启 docker" >&2
  exit 1
fi

cat > "${DAEMON_JSON}" <<'EOF'
{
  "registry-mirrors": [
    "https://docker.m.daocloud.io",
    "https://docker.1ms.run"
  ]
}
EOF

systemctl restart docker
echo "Docker 已重启，镜像加速已生效"
