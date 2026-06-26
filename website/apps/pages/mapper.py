# coding: utf-8


class FArticleMapper:
    @staticmethod
    def select_site_list():
        sql = '''
                select *
                from site
                WHERE del_flag = 'N'
                order by id desc
            '''
        return sql

    @staticmethod
    def select_article_page_list():
        sql = '''
                select a.*,
                      c.pic_url,
                      c.desc,
                      d.slug_url
                from article a
                  LEFT JOIN cate b
                  on a.cate_id = b.id
                  LEFT JOIN article_annex c
                  on a.id = c.article_id
                  LEFT JOIN article_slug d
                  on a.id = d.article_id
                where a.pub_status = 'Y'
                      and a.del_flag = 'N'
                      and a.pub_time < now()
                      and b.name_en = %s
                order by a.pub_time desc
                limit %s, %s
            '''
        return sql

    @staticmethod
    def select_page_list():
        sql = '''
                select a.*,
                      b.name_en cate_name_en,
                      c.pic_url,
                      c.desc,
                      d.slug_url
                from article a
                  LEFT JOIN cate b
                  on a.cate_id = b.id
                  LEFT JOIN article_annex c
                  on a.id = c.article_id
                  LEFT JOIN article_slug d
                  on a.id = d.article_id
                where a.pub_status = 'Y'
                      and a.del_flag = 'N'
                      and a.pub_time < now()
                order by a.pub_time desc
                limit %s, %s
            '''
        return sql

    @staticmethod
    def select_total_count():
        sql = '''
                select count(*) as num
                from article a
                  LEFT JOIN cate b
                  on a.cate_id = b.id
                where a.pub_status = 'Y'
                      and a.del_flag = 'N'
                      and a.pub_time < now()
            '''
        return sql

    @staticmethod
    def select_article_total_count():
        sql = '''
                select count(*) as num
                from article a
                  LEFT JOIN cate b
                  on a.cate_id = b.id
                where a.pub_status = 'Y'
                      and a.del_flag = 'N'
                      and a.pub_time < now()
                      and b.name_en = %s
            '''
        return sql

    @staticmethod
    def select_tag_article_by_kw():
        sql = '''
                SELECT DISTINCT (c.id) aid,
                        c.*,
                        d.desc,
                        d.pic_url,
                        e.name_en
                from keyword a
                left join article_kw b on
                    a.kw = b.kw
                left join article c
                on b.article_id = c.id
                left join article_annex d
                on c.id = d.article_id
                left join cate e
                on e.id = c.cate_id
                WHERE c.title like %s
                      and c.pub_status = 'Y'
                limit %s
            '''
        return sql

    @staticmethod
    def select_tag_article_list():
        sql = '''
                SELECT  DISTINCT (c.id) aid,
                        c.*,
                        d.desc,
                        d.pic_url,
                        e.name_en,
                        e.p_id,
                        f.slug_url
                from keyword a
                left join article_kw b on
                    a.kw = b.kw
                left join article c
                on b.article_id = c.id
                left join article_annex d
                on c.id = d.article_id
                left join cate e
                on e.id = c.cate_id
                left join article_slug f
                on c.id = f.article_id
                WHERE a.id = %s
                      and b.type = 't'
                      and c.pub_status = 'Y'
                      and c.pub_time < now()
                order by b.sort asc
                limit %s
            '''
        return sql
        
    @staticmethod
    def select_topic_article_list():
        sql = '''
                SELECT  DISTINCT (c.id) aid,
                        c.*,
                        d.desc,
                        d.pic_url,
                        e.name_en,
                        e.p_id
                from keyword a
                left join article_kw b on
                    a.kw = b.kw
                left join article c
                on b.article_id = c.id
                left join article_annex d
                on c.id = d.article_id
                left join cate e
                on e.id = c.cate_id
                WHERE a.id = %s
                      and b.type = 't'
                      and c.pub_status = 'Y'
                order by b.sort asc
                limit %s
            '''
        return sql

    @staticmethod
    def select_kw_by_id():
        sql = '''
                SELECT kw, kw_slug
                from keyword
                WHERE id = %s
                      and del_flag = 'N'
                limit 1
            '''
        return sql

    @staticmethod
    def select_kw_by_name():
        sql = '''
                SELECT kw, id, kw_slug
                from keyword
                WHERE LOWER(kw) = LOWER(%s)
                      and del_flag = 'N'
                limit 1
            '''
        return sql

    @staticmethod
    def select_tag_article_rand():
        sql = '''
                select t1.*
                from
                    (SELECT
                        a.*,
                        b.desc,
                        b.pic_url,
                        c.name_en,
                        c.p_id,
                        d.slug_url
                    from
                        article a
                    left join article_annex b on
                        a.id = b.article_id
                    left join cate c on
                        c.id = a.cate_id
                    left join article_slug d on
                        a.id = d.article_id
                    WHERE
                        a.pub_status = 'Y'
                        and a.del_flag = 'N'
                        and a.pub_time < now()
                        and a.id >= ((
                            SELECT
                                MAX(id)
                            FROM
                                article)-(
                            SELECT
                                MIN(id)
                            FROM
                                article)) * RAND() + (
                            SELECT
                                MIN(id)
                            FROM
                                article)
                        limit %s
                ) t1
            '''
        return sql

    @staticmethod
    def select_tag_article_total_count():
        sql = '''
                SELECT count(*) num
                from keyword a
                left join article_kw b on
                    a.kw = b.kw
                left join article c
                on b.article_id = c.id
                WHERE a.id = %s
                      and c.pub_status = 'Y'
                      and c.del_flag = 'N'
                      and c.pub_time < now()
            '''
        return sql

    @staticmethod
    def select_tag_info():
        sql = '''
                SELECT *
                from keyword
                WHERE id = %s
            '''
        return sql

    @staticmethod
    def select_main_menu():
        sql = '''
                select id,
                      name,
                      name_en
                from cate
                where visiable = 'Y'
                  and del_flag = 'N'
                  and (p_id is null or p_id <= 0)
                order by sort_num asc
            '''
        return sql

    @staticmethod
    def select_menu_list():
        sql = '''
                select 
                    c.id,
                    c.name,
                    c.name_en,
                    p.id as p_id,
                    p.name as p_name,
                    p.name_en as p_name_en
                from cate c
                left join cate p on c.p_id = p.id
                where c.visiable = 'Y'
                  and c.del_flag = 'N'
                  and c.p_id = %s
                order by c.sort_num asc
            '''
        return sql

    @staticmethod
    def select_site_base_info():
        sql = '''
                select *
                from site_conf
                where `domain` = %s
            '''
        return sql

    @staticmethod
    def select_cate_list():
        sql = '''
                select id,
                        name,
                        name_en
                from cate
                where home_visiable = 'Y'
                  and del_flag = 'N'
                ORDER by sort_num ASC
            '''
        return sql

    @staticmethod
    def select_cate_list_top_level():
        sql = '''
                select id,
                        name,
                        name_en
                from cate
                where (p_id is null or p_id <= 0)
                  and home_visiable = 'Y'
                  and del_flag = 'N'
                ORDER by sort_num ASC
            '''
        return sql

    @staticmethod
    def select_cate_list_by_p_id():
        sql = '''
                select id,
                        name,
                        name_en
                from cate
                where p_id = %s
                  and home_visiable = 'Y'
                  and del_flag = 'N'
                ORDER by sort_num ASC
            '''
        return sql

    @staticmethod
    def select_swiper_list():
        sql = '''
                select title,
                      pic_url,
                      click_url
                from carousel
                where status = '1' and del_flag = '0'
                order by sort_num asc
                limit 7
            '''
        return sql

    @staticmethod
    def select_article_list_by_cate_id():
        sql = '''
                select a.id,
                        a.title,
                        a.source_id,
                        a.pub_time,
                        b.pic_url,
                        b.desc,
                        c.slug_url
                from article a
                LEFT JOIN article_annex b
                on a.id = b.article_id
                LEFT JOIN article_slug c
                on a.id = c.article_id
                where a.cate_id = %s
                  and a.del_flag = 'N'
                  and a.pub_status = 'Y'
                  and a.pub_time < now()
                ORDER by a.pub_time desc
                limit %s
            '''
        return sql

    @staticmethod
    def select_cate_info():
        sql = '''
                select *
                from cate
                where name_en = %s
                  and del_flag = 'N'
            '''
        return sql

    @staticmethod
    def select_source_id_by_slug():
        sql = '''
                select a.source_id
                from article a
                inner join article_slug b on a.id = b.article_id
                where b.slug_url = %s
                  and a.del_flag = 'N'
            '''
        return sql

    @staticmethod
    def select_article_by_sid():
        sql = '''
                select a.*,
                        b.content,
                        b.desc,
                        c.slug_url
                from article a
                left join article_annex b
                on a.id = b.article_id
                left join article_slug c
                on a.id = c.article_id
                where a.source_id = %s
                  and a.del_flag = 'N'
            '''
        return sql

    @staticmethod
    def select_article_kws():
        sql = '''
                select b.id,
                      b.kw,
                      b.kw_slug,
                      a.`type`
                from article_kw a
                LEFT JOIN keyword b
                on a.kw = b.kw
                where a.article_id = %s
                ORDER by a.sort asc
            '''
        return sql

    @staticmethod
    def select_r_kw_by_kw_id():
        sql = '''
                select related_kw_id id,
                       related_kw kw
                from kw_kw
                where source_kw_id = %s
                limit %s
            '''
        return sql

    @staticmethod
    def select_related_tags():
        sql = '''
                select DISTINCT related_kw_id id,
                      related_kw kw
                from kw_kw
                where source_kw_id = %s
            '''
        return sql

    @staticmethod
    def select_article_by_kw():
        sql = '''
                select b.id,
                      b.source_id,
                      b.title,
                      b.pub_time,
                      c.pic_url,
                      d.name_en name_en,
                      d.name cate_name,
                      d.id cate_id,
                      d.p_id p_cate_id
                from article_kw a
                LEFT JOIN article b
                on a.article_id = b.id
                LEFT JOIN article_annex c
                on b.id = c.article_id
                left join cate d
                on b.cate_id = d.id
                where a.kw = %s
                  and b.del_flag = 'N'
                  and b.pub_status = 'Y'
                  and b.pub_time < now()
                limit 3
            '''
        return sql

    @staticmethod
    def select_cate_info():
        sql = '''
                select *
                from cate
                where id = %s
            '''
        return sql

    @staticmethod
    def select_cate_info_by_name_en():
        sql = '''
                select *
                from cate
                where name_en = %s
            '''
        return sql

    @staticmethod
    def select_cate_related_kws():
        sql = '''
                select
                    related_kw kw,
                    related_kw_id id
                from
                    kw_kw
                where
                    source_kw_id in (
                    select
                        id
                    from
                        keyword
                    where
                        kw = %s )
            '''
        return sql

    @staticmethod
    def select_prev_article():
        sql = '''
                select a.id,
                    a.source_id,
                    a.title,
                    b.name_en,
                    c.slug_url
                from article a
                LEFT join cate b
                on a.cate_id = b.id
                LEFT join article_slug c
                on a.id = c.article_id
                WHERE a.id > %s and b.id = %s
                      and a.pub_status = 'Y'
                      and a.del_flag = 'N'
                ORDER BY a.id ASC
                LIMIT 1
            '''
        return sql

    @staticmethod
    def select_next_article():
        sql = '''
                select a.id,
                    a.source_id,
                    a.title,
                    b.name_en,
                    c.slug_url
                from article a
                LEFT join cate b
                on a.cate_id = b.id
                LEFT join article_slug c
                on a.id = c.article_id
                WHERE a.id < %s and b.id = %s
                      and a.pub_status = 'Y'
                      and a.del_flag = 'N'
                ORDER BY a.id DESC
                LIMIT 1
            '''
        return sql

    @staticmethod
    def select_article_related_kws():
        sql = '''
              select related_kw kw,
                      related_kw_id id
                from kw_kw
                where source_kw_id = %s
                limit 5
            '''
        return sql

    @staticmethod
    def select_hots_articles():
        sql = '''
              select a.id,
                    a.title,
                    a.source_id,
                    b.name_en,
                    b.id cate_id,
                    b.p_id p_cate_id,
                    c.slug_url
                from article a
                LEFT join cate b
                on a.cate_id = b.id
                left join article_slug c
                on a.id = c.article_id
                WHERE b.id = %s
                      and a.pub_time < now()
                      and a.del_flag = 'N'
                      and a.pub_status = 'Y'
                ORDER BY a.id DESC
                LIMIT 10
            '''
        return sql

    @staticmethod
    def select_lastest_articles():
        sql = '''
              select a.id,
                    a.title,
                    a.source_id,
                    b.name_en,
                    b.id cate_id,
                    b.p_id p_cate_id
                from article a
                LEFT join cate b
                  on a.cate_id = b.id
                WHERE a.del_flag = 'N'
                      and a.pub_status = 'Y'
                      and a.cate_id != -1
                      and a.pub_time < now()
                ORDER BY a.id DESC
                LIMIT 10
            '''
        return sql

    @staticmethod
    def update_view_num():
        sql = '''
              update article
              set view_num = view_num + 1
              where id = %s
            '''
        return sql

    @staticmethod
    def select_friend_links():
        sql = '''
              select * from friend_link
              where status = '1'
              and del_flag = '0'
              ORDER by sort_num ASC
            '''
        return sql

    @staticmethod
    def get_lastest_article_page_list():
        sql = '''
              select a.title,
                    a.source_id,
                    b.name_en
              from article a
              left join cate b
              on a.cate_id = b.id
              where a.pub_status = 'Y'
              and a.del_flag = 'N'
              ORDER by a.pub_time DESC
              limit %s,%s
            '''
        return sql

    @staticmethod
    def select_cate_info_by_id():
        sql = '''
                select *
                from cate
                where id = %s
            '''
        return sql