# 远程制作离线安装包

在 **Windows/Mac 本地** 打包源码，上传到 **Ubuntu 构建机** 制作 Docker 离线包，再下载回本地。

## 前置条件

### 本地（开发机）

- Git Bash 或 Linux/macOS 终端
- `tar`、`ssh`、`scp`
- 密码登录时：已安装 Python 3 + `paramiko`（Windows Git Bash 推荐），或 Linux 上的 `sshpass`

### Ubuntu 构建服务器

- Docker 已安装
- SSH 登录：**密钥**（推荐）或 **密码**（填 `deploy.env` 的 `REMOTE_PASSWORD`）

```bash
# 方式 A：SSH 密钥（推荐）
ssh-keygen -t ed25519
ssh-copy-id -p 22 abc@192.168.1.100

# 方式 B：密码（懒人模式，密码只写在本地 deploy.env，勿提交 Git）
# 在 deploy.env 中设置 REMOTE_PASSWORD=你的密码
# Windows Git Bash: pip install paramiko
```

## 配置

```bash
cp scripts/offline-pack/deploy.env.example scripts/offline-pack/deploy.env
# 编辑 deploy.env
```

| 变量 | 说明 |
|------|------|
| `REMOTE_USER` | SSH 用户名 |
| `REMOTE_HOST` | 服务器 IP 或域名 |
| `REMOTE_DIR` | 服务器上的工作目录（**建议 ≥ 5GB 可用空间、纯英文路径**，如 `/home/abc/xxg-cms-build`） |
| `SSH_PORT` | SSH 端口，默认 22 |
| `REMOTE_PASSWORD` | SSH 密码（可选，留空用密钥；仅本地 deploy.env） |
| `DOWNLOAD_BUNDLE` | 1=构建完自动 scp 回本地 |

## 一键执行

在项目根目录：

```bash
chmod +x scripts/build-offline-remote.sh scripts/offline-pack/*.sh
./scripts/build-offline-remote.sh
```

流程：

1. `pack.sh` — 打包源码为 `xxgcms-src-YYYYMMDD.tar.gz`（同日覆盖）
2. `scp` — 上传到服务器 `REMOTE_DIR`
3. `remote-build.sh` — 服务器解压并执行 `make-offline-bundle.sh`
4. 下载 `xxgcms-YYYYMMDD.tar.gz` 到本地（若 `DOWNLOAD_BUNDLE=1`）

## 分步执行

```bash
# 仅打包
./scripts/offline-pack/pack.sh

# 仅下载已有离线包
./scripts/offline-pack/download-bundle.sh
```

## 离线服务器安装

```bash
tar xzf xxgcms-YYYYMMDD.tar.gz
cd xxgcms
sudo ./install.sh        # 或 sudo ./up-core.sh
```

## 安全说明

- `deploy.env` 已在 `.gitignore` 中忽略，可在此填写 `REMOTE_PASSWORD`
- **请勿** 将 `deploy.env` 提交到 Git 或分享给他人
- 生产环境仍推荐 SSH 公钥认证

## 构建失败：`xxgcms-website.tar 缺少 manifest.json`

说明 **构建机磁盘空间不足**，`docker save` 写到第 4 个镜像时被中断，生成了损坏的 tar。

在 **Ubuntu 构建机** 上执行：

```bash
df -h ~/桌面/XXGCMS    # 或你的 REMOTE_DIR
docker system df
docker system prune -a   # 清理未用镜像/缓存（会删掉旧 xxgcms 镜像，可重建）
```

建议将 `deploy.env` 中 `REMOTE_DIR` 改为空间更大的英文路径，例如：

```bash
REMOTE_DIR=/home/abc/xxg-cms-build
```

然后重新运行 `./scripts/build-offline-remote.sh`。
