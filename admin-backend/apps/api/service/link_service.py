# coding: utf-8
from apps.api.db.connection import cms_x_connection
from apps.api.sql_mapper.link_mapper import LinkMapper
from apps.api.utils.upload import save_upload


def get_link_list(site_name, start_page, page_size):
    with cms_x_connection(site_name) as conn:
        with conn.cursor() as cursor:
            cursor.execute(LinkMapper.select_link_page_list(), (start_page, page_size))
            datas = cursor.fetchall()
            cursor.execute(LinkMapper.select_link_total_count())
            total_count = cursor.fetchone().get('num', 0)
            return datas, total_count


def check_name(site_name, name):
    with cms_x_connection(site_name) as conn:
        with conn.cursor() as cursor:
            cursor.execute(LinkMapper.select_link_by_name(), (name,))
            return cursor.fetchone().get('num', 0) >= 1


def get_id_by_name(site_name, name):
    with cms_x_connection(site_name) as conn:
        with conn.cursor() as cursor:
            cursor.execute(LinkMapper.select_id_by_name(), (name,))
            data = cursor.fetchone()
            return data.get('id') if data else None


def add_link(site_name, req):
    with cms_x_connection(site_name) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                LinkMapper.insert_link(),
                (
                    req.get('name', ''),
                    req.get('pic_url', ''),
                    req.get('click_url', ''),
                    req.get('sort_num', ''),
                    req.get('status', '0'),
                    req.get('desc', ''),
                ),
            )
            conn.commit()
    return True


def upload_link_pic(file, ext_name):
    return save_upload(file, 'img/links', ext_name)


def update_link(site_name, link_id, req):
    with cms_x_connection(site_name) as conn:
        with conn.cursor() as cursor:
            name = req.get('name', '')
            status = req.get('status', '')
            pic_url = req.get('pic_url', '')
            click_url = req.get('click_url', '')
            sort_num = req.get('sort_num', '')
            desc = req.get('desc', '')
            sql_str = LinkMapper.update_link(pic_url)
            if pic_url:
                cursor.execute(sql_str, (name, status, pic_url, click_url, sort_num, desc, link_id))
            else:
                cursor.execute(sql_str, (name, status, click_url, sort_num, desc, link_id))
            conn.commit()
    return True


def del_link(site_name, link_id):
    with cms_x_connection(site_name) as conn:
        with conn.cursor() as cursor:
            cursor.execute(LinkMapper.del_link(), (link_id,))
            conn.commit()
    return True
