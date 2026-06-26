# coding: utf-8
from django.contrib.auth.hashers import check_password, make_password

from apps.api.db.connection import xxgcms_connection
from apps.api.sql_mapper.base_mapper import BaseMapper
from apps.api.utils.base_conf import SITE_MAP
from apps.api.utils.public import log_debug
from apps.api.utils.site_db_init import init_site_cms_database, test_cms_database
from apps.api.utils.upload import save_upload


def _user_id(cursor, user_name):
    cursor.execute(BaseMapper.select_user_by_name(), (user_name,))
    row = cursor.fetchone()
    if not row:
        raise Exception('用户不存在')
    return row.get('id', -1)


def login(name, pwd):
    log_debug('开始验证用户')
    with xxgcms_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(BaseMapper.select_user_by_name(), (name,))
            data = cursor.fetchone()
            if data and check_password(pwd, data.get('user_pwd')):
                return True
    return False


def add_user(name, pwd):
    log_debug('开始创建系统用户')
    with xxgcms_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(BaseMapper.insert_user(), (name, make_password(pwd)))
            conn.commit()


def change_password(user_name, old_pwd, new_pwd):
    old_pwd = (old_pwd or '').strip()
    new_pwd = (new_pwd or '').strip()
    if not old_pwd:
        raise Exception('请填写原密码')
    if len(new_pwd) < 6:
        raise Exception('新密码长度不能小于6位')
    if old_pwd == new_pwd:
        raise Exception('新密码不能与原密码相同')
    if not login(user_name, old_pwd):
        raise Exception('原密码不正确')

    log_debug(f'用户 {user_name} 修改密码')
    with xxgcms_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                BaseMapper.update_user_password(),
                (make_password(new_pwd), user_name),
            )
            if cursor.rowcount != 1:
                raise Exception('密码修改失败')
            conn.commit()
    return True


def refesh_site_conf(user_name):
    log_debug('获取站点配置信息')
    with xxgcms_connection() as conn:
        with conn.cursor() as cursor:
            user_id = _user_id(cursor, user_name)
            cursor.execute(BaseMapper.select_site_list(), (user_id,))
            for site in cursor.fetchall():
                SITE_MAP[site.get('name', '')] = site
    return SITE_MAP


def get_site_page_list(user_name, start_page, page_size):
    with xxgcms_connection() as conn:
        with conn.cursor() as cursor:
            user_id = _user_id(cursor, user_name)
            cursor.execute(BaseMapper.select_site_page_list(), (user_id, start_page, page_size))
            datas = cursor.fetchall()
            cursor.execute(BaseMapper.select_site_total_count(), (user_id,))
            total_count = cursor.fetchone().get('num', 0)
            return datas, total_count


def get_site_list(user_name):
    with xxgcms_connection() as conn:
        with conn.cursor() as cursor:
            user_id = _user_id(cursor, user_name)
            cursor.execute(BaseMapper.select_site_list(), (user_id,))
            return cursor.fetchall()


def select_site_by_name(user_name, name):
    with xxgcms_connection() as conn:
        with conn.cursor() as cursor:
            user_id = _user_id(cursor, user_name)
            cursor.execute(BaseMapper.select_site_by_name(), (user_id, name))
            return cursor.fetchone()


def select_site_by_root_path(user_name, root_path):
    with xxgcms_connection() as conn:
        with conn.cursor() as cursor:
            user_id = _user_id(cursor, user_name)
            cursor.execute(BaseMapper.select_site_by_root_path(), (user_id, root_path))
            return cursor.fetchone()


def upload_site_pic(file, ext_name):
    return save_upload(file, 'img/site', ext_name)


def test_site_cms_db(req):
    return test_cms_database(req)


def add_site(user_name, req):
    site_name = (req.get('name') or '').strip()
    init_site_cms_database(req, site_name)

    with xxgcms_connection() as conn:
        with conn.cursor() as cursor:
            user_id = _user_id(cursor, user_name)
            cursor.execute(
                BaseMapper.insert_site(),
                (
                    req.get('name', ''),
                    req.get('root_path', ''),
                    req.get('pic_url', ''),
                    req.get('db_host', ''),
                    req.get('db_port', 3306),
                    req.get('db_name', ''),
                    req.get('db_user', ''),
                    req.get('db_pwd', ''),
                    req.get('db_x_host', ''),
                    req.get('db_x_port', 3306),
                    req.get('db_x_name', ''),
                    req.get('db_x_user', ''),
                    req.get('db_x_pwd', ''),
                    req.get('sort_num', 9999),
                    req.get('desc', ''),
                ),
            )
            cursor.execute(BaseMapper.insert_site_user(), (user_id, cursor.lastrowid))
            conn.commit()
            refesh_site_conf(user_name)
    return True


def update_site(req):
    with xxgcms_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                BaseMapper.update_site(),
                (
                    req.get('name', ''),
                    req.get('root_path', ''),
                    req.get('pic_url', ''),
                    req.get('db_host', ''),
                    req.get('db_port', 3306),
                    req.get('db_name', ''),
                    req.get('db_user', ''),
                    req.get('db_pwd', ''),
                    req.get('db_x_host', ''),
                    req.get('db_x_port', 3306),
                    req.get('db_x_name', ''),
                    req.get('db_x_user', ''),
                    req.get('db_x_pwd', ''),
                    req.get('sort_num', 9999),
                    req.get('desc', ''),
                    req.get('id', -1),
                ),
            )
            conn.commit()
    return True


def del_site(site_id, user_name=None):
    log_debug('开始删除某个站点')
    site_name = None
    with xxgcms_connection() as conn:
        with conn.cursor() as cursor:
            if user_name:
                user_id = _user_id(cursor, user_name)
                cursor.execute(BaseMapper.select_site_by_id_for_user(), (user_id, site_id))
                row = cursor.fetchone()
                if not row:
                    raise Exception('无权删除该站点')
            cursor.execute(BaseMapper.select_site_by_id(), (site_id,))
            site_row = cursor.fetchone()
            if site_row:
                site_name = site_row.get('name')
            cursor.execute(BaseMapper.del_site_by_id(), (site_id,))
            conn.commit()
    if site_name:
        from apps.api.service import domain_ssl_service
        domain_ssl_service.remove_site_ssl_for_domain(site_name)
    if user_name:
        refesh_site_conf(user_name)
    return True
