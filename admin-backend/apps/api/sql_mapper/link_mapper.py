# coding: utf-8


class LinkMapper:
    @staticmethod
    def select_link_page_list():
        sql = '''
                select * from friend_link
                where del_flag = '0'
                order by sort_num asc
                limit %s, %s
            '''
        return sql

    @staticmethod
    def select_link_total_count():
        sql = '''
                select count(1) as num
                from friend_link
                where del_flag = '0'
            '''
        return sql

    @staticmethod
    def select_link_by_name():
        sql = '''
                select count(1) as num
                from friend_link
                where name = %s
            '''
        return sql

    @staticmethod
    def select_id_by_name():
        sql = '''
                select id
                from friend_link
                where name = %s
            '''
        return sql

    @staticmethod
    def insert_link():
        sql = '''
                insert into
                friend_link(name,pic_url,click_url,sort_num,status,`add_time`,`desc`)
                VALUES(%s,%s,%s,%s,%s, NOW(),%s)
            '''
        return sql

    @staticmethod
    def update_link(pic_url):
        sql = '''
                update friend_link
                set name = %s,
                    status = %s,
              '''
        if pic_url != "":
            sql += '''
                    pic_url = %s,
                '''
        sql += '''
                click_url = %s,
                sort_num = %s,
                `desc` = %s
                where id = %s
            '''
        return sql

    @staticmethod
    def del_link():
        sql = '''
                update friend_link
                set del_flag = '1'
                where id = %s
            '''
        return sql