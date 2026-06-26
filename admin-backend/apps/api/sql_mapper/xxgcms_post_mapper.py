# coding: utf-8


class XxgcmsPostMapper:
    @staticmethod
    def select_rand_post_article_id_sql():
        sql = '''
                select id
                FROM article
                where pub_status = 'N'
                order by rand()
                limit 1
            '''
        return sql

    @staticmethod
    def post_article_sql():
        sql = '''
                update article
                set pub_time = now(),
                    pub_status = 'Y'
                where id = %s
            '''
        return sql

    @staticmethod
    def select_no_ts_articles():
        sql = '''
                select a.id
                from article a
                left join ts_ret b
                on a.source_id = b.source_id
                where a.pub_status = 'Y' and b.success is NULL
                order by a.id DESC
                limit 10
            '''
        return sql