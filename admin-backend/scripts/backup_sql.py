__author__ = 'Administrator'
"""MySQL 备份脚本模板：从环境变量读取连接信息，勿在代码中写密码。"""

import os
import subprocess


def _mysql_env():
    host = os.environ.get('XXGCMS_DB_HOST', '127.0.0.1')
    port = os.environ.get('XXGCMS_DB_PORT', '3306')
    user = os.environ.get('XXGCMS_DB_USER', 'root')
    password = os.environ.get('XXGCMS_DB_PASSWORD', '')
    if not password:
        raise RuntimeError('请配置 XXGCMS_DB_PASSWORD（运行 ./scripts/xxgcms.sh setup）')
    return host, port, user, password


def mysqldump(database, output_path, schema_only=False):
    host, port, user, password = _mysql_env()
    cmd = [
        'mysqldump',
        '-h', host,
        '-P', port,
        '-u', user,
        f'-p{password}',
    ]
    if schema_only:
        cmd.append('--no-data')
    cmd.extend([database])
    with open(output_path, 'w', encoding='utf-8') as out:
        subprocess.run(cmd, stdout=out, check=True)


if __name__ == '__main__':
    # 示例：仅导出结构
    # mysqldump('xxgcms', '/tmp/xxgcms_schema.sql', schema_only=True)
    print('请通过函数调用或自行组装命令，连接信息来自环境变量 / .env')
