#!/bin/sh
# 将 Debian apt 源替换为国内镜像（构建镜像时加速 apt-get）
# 用法: APT_MIRROR=mirrors.aliyun.com ./debian-apt-cn.sh
set -eu

MIRROR="${APT_MIRROR:-mirrors.aliyun.com}"

for f in /etc/apt/sources.list /etc/apt/sources.list.d/debian.sources; do
  if [ -f "${f}" ]; then
    sed -i \
      "s|deb.debian.org|${MIRROR}|g; s|security.debian.org|${MIRROR}|g" \
      "${f}"
  fi
done

echo "[apt-cn] 已切换为 ${MIRROR}"
