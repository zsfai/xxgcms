# coding: utf-8


class BaseMapper:
    @staticmethod
    def insert_user():
        sql = '''
                insert into user(user_name,user_pwd)
                VALUES (%s, %s)
            '''
        return sql

    @staticmethod
    def select_user_by_name():
        sql = '''
                select id, user_pwd
                from user
                WHERE user_name = %s
                      and status=1
            '''
        return sql

    @staticmethod
    def update_user_password():
        sql = '''
                update user
                set user_pwd = %s
                where user_name = %s
                      and status = 1
            '''
        return sql

    @staticmethod
    def select_site_list():
        sql = '''
                select a.*
                from site a
                left join site_user b on a.id = b.site_id
                where b.user_id = %s
                    and a.del_flag = 'N'
                order by id desc
            '''
        return sql

    @staticmethod
    def select_site_list_without_user():
        sql = '''
                select *
                from site
                WHERE del_flag = 'N'
                order by id desc
            '''
        return sql

    @staticmethod
    def select_site_page_list():
        sql = '''
                select a.*
                from site a
                left join site_user b on a.id = b.site_id
                where b.user_id = %s
                    and a.del_flag = 'N'
                order by sort_num asc
                limit %s, %s
            '''
        return sql

    @staticmethod
    def select_site_total_count():
        sql = '''
                select count(*) as num
                from site a
                left join site_user b on a.id = b.site_id
                where b.user_id = %s
                    and a.del_flag = 'N'
            '''
        return sql

    @staticmethod
    def select_site_by_name():
        sql = '''
                select a.*
                from site a
                left join site_user b on a.id = b.site_id
                where b.user_id = %s
                    and a.del_flag = 'N'
                and name = %s
            '''
        return sql

    @staticmethod
    def select_site_by_root_path():
        sql = '''
                select a.*
                from site a
                left join site_user b on a.id = b.site_id
                where b.user_id = %s
                    and a.del_flag = 'N'
                and root_path = %s
            '''
        return sql

    @staticmethod
    def insert_site():
        sql = '''
                insert into site(
                  name, root_path, pic_url,
                  db_host, db_port, db_name,
                  db_user, db_pwd, db_x_host,
                  db_x_port, db_x_name, db_x_user,
                  db_x_pwd, sort_num, `desc`,
                  add_time
                )
                VALUES (
                  %s,%s,%s,
                  %s,%s,%s,
                  %s,%s,%s,
                  %s,%s,%s,
                  %s,%s,%s,
                  now()
                )
            '''
        return sql

    @staticmethod
    def insert_site_user():
        sql = '''
                insert into site_user (user_id, site_id)
                VALUES (%s, %s)
            '''
        return sql

    @staticmethod
    def update_site():
        sql = '''
                update site
                set name = %s,
                    root_path = %s,
                    pic_url = %s,
                    db_host = %s,
                    db_port = %s,
                    db_name = %s,
                    db_user = %s,
                    db_pwd = %s,
                    db_x_host = %s,
                    db_x_port = %s,
                    db_x_name = %s,
                    db_x_user = %s,
                    db_x_pwd = %s,
                    sort_num = %s,
                    `desc` = %s,
                    update_time = now()
                where id = %s
            '''
        return sql

    @staticmethod
    def del_site_by_id():
        sql = '''
                update site
                set del_flag = 'Y',
                    update_time = now()
                where id = %s
            '''
        return sql

    @staticmethod
    def select_site_by_id_for_user():
        sql = '''
                select a.id
                from site a
                left join site_user b on a.id = b.site_id
                where b.user_id = %s
                    and a.id = %s
                    and a.del_flag = 'N'
            '''
        return sql

    @staticmethod
    def select_site_by_id():
        sql = '''
                select *
                from site
                where id = %s
                    and del_flag = 'N'
            '''
        return sql

    @staticmethod
    def update_site_ssl_meta():
        sql = '''
                update site
                set domain_aliases = %s,
                    ssl_enabled = %s,
                    force_https = %s,
                    cert_status = %s,
                    cert_not_after = %s,
                    nginx_status = %s,
                    nginx_error = %s,
                    update_time = now()
                where id = %s
            '''
        return sql

    @staticmethod
    def select_ssl_enabled_sites():
        sql = '''
                select *
                from site
                where del_flag = 'N'
                  and ssl_enabled = 'Y'
                order by id asc
            '''
        return sql