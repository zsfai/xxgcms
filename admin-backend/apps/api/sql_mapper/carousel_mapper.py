# coding: utf-8


class CarouselMapper:

    @staticmethod
    def select_all_carousel():
         sql = '''
                select * from carousel
                where del_flag = '0'
                order by sort_num asc
                limit %s, %s
            '''
         return sql

    @staticmethod
    def select_carousel_total_count():
         sql = '''
                select count(1) as num
                from carousel
                where del_flag = '0'
            '''
         return sql

    @staticmethod
    def select_carousel_by_title():
         sql = '''
                select count(1) as num
                from carousel
                where title = %s
            '''
         return sql

    @staticmethod
    def select_id_by_title():
         sql = '''
                select id
                from carousel
                where title = %s
            '''
         return sql

    @staticmethod
    def insert_carousel():
         sql = '''
                insert into
                carousel(title,pic_url,click_url,sort_num,status,`create_time`,`desc`)
                VALUES(%s,%s,%s,%s,%s, NOW(),%s)
            '''
         return sql

    @staticmethod
    def update_carousel(pic_url):
         sql = '''
                update carousel
                set title = %s,
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
    def del_carousel():
         sql = '''
                update carousel
                set del_flag = '1'
                where id = %s
            '''
         return sql

    @staticmethod
    def select_view_carousels():
         sql = '''
                select *
                from carousel
                where status = '1' and del_flag = '0'
                order by sort_num asc
            '''
         return sql