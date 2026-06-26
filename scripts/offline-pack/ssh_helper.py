#!/usr/bin/env python3
"""SSH/SFTP helper for password auth when sshpass is unavailable (e.g. Git Bash on Windows)."""
from __future__ import annotations

import fnmatch
import os
import posixpath
import shlex
import sys
import time
from pathlib import Path

try:
    import paramiko
except ImportError:
    print("缺少 paramiko，请执行: pip install paramiko", file=sys.stderr)
    sys.exit(1)


def _connect() -> paramiko.SSHClient:
    host = os.environ["REMOTE_HOST"]
    user = os.environ["REMOTE_USER"]
    password = os.environ.get("REMOTE_PASSWORD", "")
    port = int(os.environ.get("SSH_PORT", "22"))

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(
        hostname=host,
        port=port,
        username=user,
        password=password,
        look_for_keys=False,
        allow_agent=False,
        timeout=30,
    )
    return client


def _stream_channel(channel, out_stream) -> None:
    """实时输出远程命令 stdout/stderr（避免等命令结束才一次性打印）。"""
    while True:
        got = False
        if channel.recv_ready():
            data = channel.recv(4096)
            if data:
                out_stream.buffer.write(data)
                out_stream.buffer.flush()
                got = True
        if channel.recv_stderr_ready():
            data = channel.recv_stderr(4096)
            if data:
                sys.stderr.buffer.write(data)
                sys.stderr.buffer.flush()
                got = True
        if channel.exit_status_ready() and not channel.recv_ready() and not channel.recv_stderr_ready():
            break
        if not got:
            time.sleep(0.05)

    while channel.recv_ready():
        data = channel.recv(4096)
        if data:
            out_stream.buffer.write(data)
            out_stream.buffer.flush()
    while channel.recv_stderr_ready():
        data = channel.recv_stderr(4096)
        if data:
            sys.stderr.buffer.write(data)
            sys.stderr.buffer.flush()


def cmd_exec(command: str, stdin_data: bytes | None = None) -> int:
    client = _connect()
    try:
        # 管道脚本（exec-stdin）不用 PTY，避免 bash 回显 if/else 等语句造成误解
        use_pty = stdin_data is None
        stdin, stdout, stderr = client.exec_command(command, get_pty=use_pty)
        if stdin_data:
            stdin.write(stdin_data)
            stdin.channel.shutdown_write()
        _stream_channel(stdout.channel, sys.stdout)
        return stdout.channel.recv_exit_status()
    finally:
        client.close()


def _resolve_local_path(local_path: str) -> Path:
    """Resolve Git Bash / MSYS / Windows paths for SFTP upload."""
    p = local_path.strip().splitlines()[-1].strip()
    candidates = [Path(p)]

    # Git Bash: /d/workspace/foo -> D:/workspace/foo
    if (
        os.name == "nt"
        and len(p) >= 3
        and p[0] == "/"
        and p[1].isalpha()
        and p[2] == "/"
    ):
        candidates.append(Path(f"{p[1].upper()}:{p[2:]}"))

    for candidate in candidates:
        try:
            resolved = candidate.resolve()
        except OSError:
            continue
        if resolved.is_file():
            return resolved

    raise SystemExit(f"本地文件不存在: {p}")


def _ensure_remote_dir(client: paramiko.SSHClient, remote_path: str) -> None:
    remote_dir = posixpath.dirname(remote_path)
    if not remote_dir or remote_dir == ".":
        return
    cmd = f"mkdir -p {shlex.quote(remote_dir)}"
    status = cmd_exec_via(client, cmd)
    if status != 0:
        raise SystemExit(f"无法创建远程目录: {remote_dir} (exit {status})")


def cmd_exec_via(client: paramiko.SSHClient, command: str) -> int:
    _, stdout, stderr = client.exec_command(command)
    exit_status = stdout.channel.recv_exit_status()
    err = stderr.read().decode("utf-8", errors="replace").strip()
    if exit_status != 0 and err:
        print(err, file=sys.stderr)
    return exit_status


def _upload_progress(label: str):
    last_pct = [-1]

    def callback(transferred, total):
        if total <= 0:
            return
        pct = int(transferred * 100 / total)
        if pct >= last_pct[0] + 10 or pct == 100:
            last_pct[0] = pct
            print(
                f"  上传进度: {pct}% ({transferred // 1024 // 1024}MB / {total // 1024 // 1024}MB)",
                file=sys.stderr,
            )

    return callback


def cmd_upload(local_path: str, remote_path: str) -> None:
    local = _resolve_local_path(local_path)
    remote_path = remote_path.strip()

    client = _connect()
    try:
        _ensure_remote_dir(client, remote_path)
        sftp = client.open_sftp()
        try:
            size_mb = local.stat().st_size // 1024 // 1024
            print(f"  上传: {local.name} -> {remote_path} ({size_mb}MB)", file=sys.stderr)
            callback = _upload_progress(local.name) if size_mb >= 10 else None
            sftp.put(str(local), remote_path, callback=callback)
        finally:
            sftp.close()
    finally:
        client.close()


def cmd_download(remote_spec: str, local_dir: str) -> None:
    remote_spec = remote_spec.strip()
    remote_dir, _, pattern = remote_spec.rpartition("/")
    if not remote_dir:
        remote_dir = "."
    if not pattern:
        pattern = "*"

    dest = Path(local_dir)
    dest.mkdir(parents=True, exist_ok=True)

    client = _connect()
    try:
        sftp = client.open_sftp()
        try:
            names = sftp.listdir(remote_dir)
            matched = sorted(n for n in names if fnmatch.fnmatch(n, pattern))
            if not matched:
                raise SystemExit(f"远程未找到匹配文件: {remote_spec}")

            for name in matched:
                remote_file = f"{remote_dir}/{name}" if remote_dir != "." else name
                target = dest / name
                print(f"  下载: {remote_file} -> {target}", file=sys.stderr)
                sftp.get(remote_file, str(target))
        finally:
            sftp.close()
    finally:
        client.close()


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit("用法: ssh_helper.py exec|exec-stdin|upload|download ...")

    action = sys.argv[1]
    if action == "exec":
        if len(sys.argv) < 3:
            raise SystemExit("用法: ssh_helper.py exec '<command>'")
        raise SystemExit(cmd_exec(sys.argv[2]))
    if action == "exec-stdin":
        if len(sys.argv) < 3:
            raise SystemExit("用法: ssh_helper.py exec-stdin '<command>'")
        raise SystemExit(cmd_exec(sys.argv[2], sys.stdin.buffer.read()))
    if action == "upload":
        # Windows Git Bash 传中文路径 argv 会乱码，优先读环境变量
        local_path = os.environ.get("REMOTE_SFTP_LOCAL", "")
        remote_path = os.environ.get("REMOTE_SFTP_REMOTE", "")
        if not local_path or not remote_path:
            if len(sys.argv) != 4:
                raise SystemExit("用法: REMOTE_SFTP_LOCAL=... REMOTE_SFTP_REMOTE=... ssh_helper.py upload")
            local_path, remote_path = sys.argv[2], sys.argv[3]
        cmd_upload(local_path, remote_path)
        return
    if action == "download":
        remote_spec = os.environ.get("REMOTE_SFTP_REMOTE", "")
        local_dir = os.environ.get("REMOTE_SFTP_LOCAL", "")
        if not remote_spec or not local_dir:
            if len(sys.argv) != 4:
                raise SystemExit("用法: REMOTE_SFTP_REMOTE=... REMOTE_SFTP_LOCAL=... ssh_helper.py download")
            remote_spec, local_dir = sys.argv[2], sys.argv[3]
        cmd_download(remote_spec, local_dir)
        return

    raise SystemExit(f"未知操作: {action}")


if __name__ == "__main__":
    main()
