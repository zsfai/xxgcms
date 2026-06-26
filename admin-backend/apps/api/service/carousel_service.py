# coding: utf-8
from apps.api.db.connection import cms_x_connection
from apps.api.sql_mapper.carousel_mapper import CarouselMapper
from apps.api.utils.public import log_debug
from apps.api.utils.upload import save_upload


def get_carousel_list(site_name, start_page, page_size):
    with cms_x_connection(site_name) as conn:
        with conn.cursor() as cursor:
            cursor.execute(CarouselMapper.select_all_carousel(), (start_page, page_size))
            datas = cursor.fetchall()
            cursor.execute(CarouselMapper.select_carousel_total_count())
            total_count = cursor.fetchone().get('num', 0)
            return datas, total_count


def check_title(site_name, title):
    with cms_x_connection(site_name) as conn:
        with conn.cursor() as cursor:
            cursor.execute(CarouselMapper.select_carousel_by_title(), (title,))
            return cursor.fetchone().get('num', 0) >= 1


def get_id_by_title(site_name, title):
    with cms_x_connection(site_name) as conn:
        with conn.cursor() as cursor:
            cursor.execute(CarouselMapper.select_id_by_title(), (title,))
            data = cursor.fetchone()
            return data.get('id') if data else None


def add_carousel(site_name, req):
    with cms_x_connection(site_name) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                CarouselMapper.insert_carousel(),
                (
                    req.get('title', ''),
                    req.get('pic_url', ''),
                    req.get('click_url', ''),
                    req.get('sort_num', ''),
                    req.get('status', '0'),
                    req.get('desc', ''),
                ),
            )
            conn.commit()
    return True


def upload_carousel_pic(file, ext_name):
    log_debug('开始上传轮播图')
    return save_upload(file, 'img/carousel', ext_name)


def update_carousel(site_name, carousel_id, req):
    with cms_x_connection(site_name) as conn:
        with conn.cursor() as cursor:
            title = req.get('title', '')
            status = req.get('status', '')
            pic_url = req.get('pic_url', '')
            click_url = req.get('click_url', '')
            sort_num = req.get('sort_num', '')
            desc = req.get('desc', '')
            sql_str = CarouselMapper.update_carousel(pic_url)
            if pic_url:
                cursor.execute(sql_str, (title, status, pic_url, click_url, sort_num, desc, carousel_id))
            else:
                cursor.execute(sql_str, (title, status, click_url, sort_num, desc, carousel_id))
            conn.commit()
    return True


def del_carousel(site_name, carousel_id):
    with cms_x_connection(site_name) as conn:
        with conn.cursor() as cursor:
            cursor.execute(CarouselMapper.del_carousel(), (carousel_id,))
            conn.commit()
    return True


def view_carousels(site_name):
    with cms_x_connection(site_name) as conn:
        with conn.cursor() as cursor:
            cursor.execute(CarouselMapper.select_view_carousels())
            return cursor.fetchall()
