# coding: utf-8


class SiteMapMapper:
    @staticmethod
    def get_site_list_sql():
        sql = '''
                select id, name
                from site
                WHERE del_flag = 'N'
                order by id desc
            '''
        return sql

    @staticmethod
    def get_site_conf_sql():
        sql = '''
                select theme_dir, https
                from site_conf
                WHERE domain = %s
            '''
        return sql

    @staticmethod
    def get_topic_total_num_sql():
        sql = '''
                select count(*) num
                from keyword
                WHERE del_flag = 'N'
            '''
        return sql

    @staticmethod
    def get_topic_ids_sql():
        sql = '''
                select id
                from keyword
                WHERE del_flag = 'N'
                order by id ASC
                LIMIT %s, %s
            '''
        return sql

    @staticmethod
    def get_cate_names_sql():
        sql = '''
                select id, name_en
                from cate
                WHERE del_flag = 'N'
                order by id ASC
            '''
        return sql

    @staticmethod
    def get_article_total_num_sql():
        sql = '''
                select count(*) num
                from article
                WHERE del_flag = 'N' and pub_status = 'Y'
            '''
        return sql

    @staticmethod
    def get_article_info_list_sql():
        sql = '''
                SELECT a.id,
                    a.source_id,
                    c.name_en
                from article a
                left join cate c on
                    a.cate_id = c.id
                where a.del_flag = 'N'
                    and pub_status = 'Y'
                order by a.id ASC
                LIMIT %s, %s
            '''
        return sql