#!/bin/sh
# 将 Alpine apk 源替换为国内镜像
# 用法: APK_MIRROR=mirrors.aliyun.com ./alpine-apk-cn.sh
set -eu

MIRROR="${APK_MIRROR:-mirrors.aliyun.com}"

if [ -f /etc/apk/repositories ]; then
  sed -i "s|dl-cdn.alpinelinux.org|${MIRROR}|g" /etc/apk/repositories
  echo "[apk-cn] 已切换为 ${MIRROR}"
fi
