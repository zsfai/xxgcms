# coding: utf-8


class SlugurlMapper:
    @staticmethod
    def select_slug_url_by_url_sql():
        sql = '''
                select * from article_slug
                where slug_url = %s
            '''
        return sql
    
    @staticmethod
    def delete_article_slug_by_aid_sql():
        sql = '''
                delete from article_slug
                where article_id = %s
            '''
        return sql
    
    @staticmethod
    def insert_article_slug_url_sql():
        sql = '''
                insert into article_slug (article_id, slug_url)
                values (%s, %s)
            '''
        return sql