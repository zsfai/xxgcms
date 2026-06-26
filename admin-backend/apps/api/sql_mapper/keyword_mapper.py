# coding: utf-8


class KeywordMapper:
    @staticmethod
    def select_kw_by_kw():
        sql = '''
                select * from keyword
                where kw = %s
            '''
        return sql

    @staticmethod
    def select_kw_page():
        sql = '''
                select a.*
                from keyword a
                order by a.id desc
                limit %s, %s
            '''
        return sql

    @staticmethod
    def select_kws_by_sid():
        sql = '''
                select related_kw
                from kw_kw
                where source_kw_id = %s
            '''
        return sql

    @staticmethod
    def select_kw_total_count():
        sql = '''
                select count(*) as num
                from keyword
            '''
        return sql

    @staticmethod
    def select_kw_total_count_by_name():
        sql = '''
                select count(*) as num
                from keyword
                where kw like %s
            '''
        return sql

    @staticmethod
    def del_xpk_by_id():
        sql = '''
                delete from keyword
                where id = %s
            '''
        return sql

    @staticmethod
    def select_kw_by_name():
         sql = '''
                select count(*) as num
                from keyword
                where kw = %s
            '''
         return sql

    @staticmethod
    def insert_kw():
         sql = '''
                insert into keyword(kw, kw_slug, create_time)
                VALUES(%s, %s, NOW())
            '''
         return sql

    @staticmethod
    def search_kw():
         sql = '''
                select * from keyword
                where kw like %s
                order by id desc
                limit %s, %s
            '''
         return sql

    @staticmethod
    def select_kw_by_id():
        sql = '''
                select id, kw
                from keyword
                where id = %s
            '''
        return sql

    @staticmethod
    def count_kw_by_name_exclude_id():
        sql = '''
                select count(*) as num
                from keyword
                where kw = %s
                    and id != %s
            '''
        return sql

    @staticmethod
    def update_kw():
        sql = '''
                update keyword
                set kw = %s,
                    kw_slug = %s,
                    update_time = NOW()
                where id = %s
            '''
        return sql

    @staticmethod
    def update_kw_kw_source_text():
        sql = '''
                update kw_kw
                set source_kw = %s
                where source_kw_id = %s
            '''
        return sql

    @staticmethod
    def update_kw_kw_related_text():
        sql = '''
                update kw_kw
                set related_kw = %s
                where related_kw_id = %s
            '''
        return sql

    @staticmethod
    def del_kw_kw_by_skw_id():
        sql = '''
                delete from kw_kw
                where source_kw_id = %s
            '''
        return sql

    @staticmethod
    def del_kw_kw_by_rkw_id():
        sql = '''
                delete from kw_kw
                where related_kw_id = %s
            '''
        return sql

    @staticmethod
    def update_article_kw_text():
        sql = '''
                update article_kw
                set kw = %s
                where kw = %s
            '''
        return sql

    @staticmethod
    def del_article_kw_by_kw():
        sql = '''
                delete from article_kw
                where kw = %s
            '''
        return sql