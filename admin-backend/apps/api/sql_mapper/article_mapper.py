# coding: utf-8

class ArticleMapper:
    @staticmethod
    def select_wp_article_list():
        sql = '''
                select ID id,
                    post_title title,
                    post_date_gmt pubdate,
                    post_content content,
                    '未分类' cate_name
                from
                    wp_posts a
                where
                    a.post_status = 'publish'
                    and a.post_type = 'post'
                order by
                    id desc
                limit %s, %s
            '''
        return sql

    # 该语句在数据量大的情况下非常缓慢
    @staticmethod
    def select_wp_article_list2():
        sql = '''
                select ID id,
                    post_title title,
                    post_date_gmt pubdate,
                    post_content content,
                    d.name cate_name
                from
                    wp_posts a
                LEFT JOIN wp_term_relationships b on
                    a.id = b.object_id
                LEFT JOIN wp_term_taxonomy c on
                    b.term_taxonomy_id = c.term_taxonomy_id
                LEFT JOIN wp_terms d on
                    c.term_id = d.term_id
                where
                    a.post_status = 'publish'
                    and a.post_type = 'post'
                    and c.taxonomy = 'category'
                order by
                    id desc
                limit %s, %s
            '''
        return sql

    @staticmethod
    def select_wp_article_by_id():
        sql = '''
                select ID id,
                    post_title title,
                    post_date_gmt pubdate,
                    post_content content,
                    d.name cate_name
                from
                    wp_posts a
                LEFT JOIN wp_term_relationships b on
                    a.id = b.object_id
                LEFT JOIN wp_term_taxonomy c on
                    b.term_taxonomy_id = c.term_taxonomy_id
                LEFT JOIN wp_terms d on
                    c.term_id = d.term_id
                where
                    ID = %s
                    and a.post_type = 'post'
                    and c.taxonomy = 'category'
            '''
        return sql

    @staticmethod
    def select_article_by_source_id():
        sql = '''
                select *
                from
                    article
                where
                    source_id = %s
            '''
        return sql

    @staticmethod
    def del_article_item_sql():
        sql = '''
                update article
                set del_flag = 'Y',
                    update_time = now()
                where source_id = %s
            '''
        return sql

    @staticmethod
    def renew_article_item_sql():
        sql = '''
                update article
                set del_flag = 'N',
                    update_time = now()
                where source_id = %s
            '''
        return sql

    @staticmethod
    def select_deleted_article_id_by_source_id():
        sql = '''
                select id
                from article
                where source_id = %s
                  and del_flag = 'Y'
            '''
        return sql

    @staticmethod
    def delete_article_annex_by_aid():
        sql = '''
                delete from article_annex
                where article_id = %s
            '''
        return sql

    @staticmethod
    def delete_article_ci_by_aid():
        sql = '''
                delete from article_ci
                where article_id = %s
            '''
        return sql

    @staticmethod
    def delete_article_source_url_by_aid():
        sql = '''
                delete from article_source_url
                where article_id = %s
            '''
        return sql

    @staticmethod
    def purge_article_by_id():
        sql = '''
                delete from article
                where id = %s
                  and del_flag = 'Y'
            '''
        return sql

    @staticmethod
    def select_wp_article_annex_by_sid():
        sql = '''
                select ID id,
                        guid pic_url
                from wp_posts
                where post_parent = %s
                      and post_status = 'inherit'
                      and post_type = 'attachment'
                order by id desc
                limit 4
            '''
        return sql

    @staticmethod
    def update_article_sql():
        sql = '''
                update article
                set title = %s,
                    source_cate_name = %s,
                    update_time = now()
                where source_id = %s
            '''
        return sql

    @staticmethod
    def update_article_annex_sql():
        sql = '''
                update article_annex
                set content = %s,
                    `desc` = %s,
                    pic_url = %s
                where article_id = %s
            '''
        return sql

    @staticmethod
    def select_wp_article_total_count():
        sql = '''
                select count(*) as num
                from wp_posts
                where post_status = 'publish'
                      and post_type = 'post'
            '''
        return sql

    @staticmethod
    def select_dede_article_list():
        sql = '''
                select a.id,
                      a.title,
                      a.pubdate,
                      b.body content
                from dede_archives a
                left join dede_addonarticle b
                on a.id = b.aid
                order by a.id desc
                limit %s, %s
            '''
        return sql

    @staticmethod
    def select_dede_article_max_id():
        sql = '''
                select id
                from dede_archives
                order by id desc
                limit 1
            '''
        return sql

    @staticmethod
    def insert_article_sql_sync_latest_articles():
        sql = '''
                insert into article(
                  title,
                  add_time,
                  pub_time,
                  source_id,
                  source_cate_name
                )
                VALUES (
                  %s,
                  now(),
                  %s,
                  %s,
                  %s
                )
            '''
        return sql

    @staticmethod
    def update_article_post_time_sql():
        sql = '''update article
                  set pub_time = %s
                  where source_id = %s
         '''
        return sql

    @staticmethod
    def insert_article_annex_sql_sync_latest_articles():
        sql = '''
                insert into article_annex(
                  content,
                  `desc`,
                  pic_url,
                  article_id
                )
                VALUES (
                  %s,
                  %s,
                  %s,
                  %s
                )
            '''
        return sql

    @staticmethod
    def select_article_count_by_sid():
        sql = '''
                select count(*) as num
                from article
                where source_id = %s
            '''
        return sql

    @staticmethod
    def select_article_by_sid():
        sql = '''
                select a.*,
                        b.content,
                        b.desc
                from article a
                left join article_annex b
                on a.id = b.article_id
                where a.source_id = %s
                  and a.del_flag = 'N'
            '''
        return sql

    @staticmethod
    def select_article_list(cate_id, ai_only=False):
        sql = '''
                select a.*,
                      b.name cate_name,
                      b.name_en cate_name_en,
                      b.p_id p_cate_id,
                      c.slug_url
                from article a
                LEFT JOIN cate b
                on a.cate_id = b.id
                LEFT JOIN article_slug c
                on a.id = c.article_id
                where 1 = 1
              '''
        if cate_id not in (-1, -2):
            sql += 'and a.cate_id = %s' % int(cate_id)
        if cate_id == -2:
            sql += '''
                        and a.del_flag = 'Y'
                    '''
        else:
            sql += '''
                        and  a.del_flag = 'N'
                   '''
        if ai_only:
            sql += '''
                        and a.ai_generated = 'Y'
                   '''
        sql += '''
                order by a.id desc
                limit %s, %s
            '''
        return sql

    @staticmethod
    def select_article_total_count(cate_id, ai_only=False):
        sql = '''
                select count(*) as num
                from article
                where 1=1
            '''
        if cate_id not in (-1, -2):
            sql += 'and cate_id = %s' % int(cate_id)
        if cate_id == -2:
            sql += '''
                        and del_flag = 'Y'
                    '''
        else:
            sql += '''
                        and del_flag = 'N'
                   '''
        if ai_only:
            sql += '''
                        and ai_generated = 'Y'
                   '''
        return sql

    @staticmethod
    def select_article_total_count_for_match_kws():
        sql = '''
                select count(*) as num
                from article
                where del_flag = 'N'
            '''
        return sql

    @staticmethod
    def select_article_total_count_for_sync_article():
        sql = '''
                select count(*) as num
                from article
                where del_flag = 'N'
            '''
        return sql

    @staticmethod
    def select_site_conf():
        sql = '''
                select *
                from site_conf
                where domain = %s
            '''
        return sql

    @staticmethod
    def del_site_conf():
        sql = '''
                delete FROM
                site_conf
                where domain = %s
            '''
        return sql

    @staticmethod
    def insert_site_conf():
        sql = '''
                insert into site_conf(
                  site_name,
                  title,
                  logo_url,
                  defaul_pic_url,
                  favicon_url,
                  icp,
                  kws,
                  theme_dir,
                  tongji_code,
                  baidu_tsapi,
                  https,
                  `desc`,
                  domain
                )
                VALUES (
                  %s,
                  %s,
                  %s,
                  %s,
                  %s,
                  %s,
                  %s,
                  %s,
                  %s,
                  %s,
                  %s,
                  %s,
                  %s
                )
            '''
        return sql

    @staticmethod
    def select_cate_list():
        sql = '''
                select *
                from cate
                where del_flag = 'N'
                order by sort_num ASC
                limit %s, %s
            '''
        return sql

    @staticmethod
    def update_article_cate():
        sql = '''
                update article
                set cate_id = %s
                where id = %s
            '''
        return sql

    @staticmethod
    def update_article_defualt_cate():
        sql = '''
                update article
                set cate_id = %s
                where cate_id = -1
            '''
        return sql

    @staticmethod
    def update_article_pre_pub():
        sql = '''
                update article
                set pub_time = %s,
                    pub_status = 'Y'
                where id = %s
            '''
        return sql

    @staticmethod
    def select_articles_wait_pub():
        sql = '''
                select id
                from article
                where pub_status = 'N'
                order by id asc
            '''
        return sql

    @staticmethod
    def select_article_info_by_id():
        sql = '''
                select a.id,
                      a.source_id,
                      b.name_en
                from article a
                left join cate b
                on a.cate_id = b.id
                where a.id = %s
            '''
        return sql

    @staticmethod
    def select_ts_ret_by_sid():
        sql = '''
                select count(*) num
                from ts_ret
                where source_id = %s
                      and ts_type = %s
                      and success = 1
                limit 1
            '''
        return sql

    @staticmethod
    def insert_ts_data_sql():
        sql = '''
                insert into ts_ret(
                  url,
                  ts_type,
                  success,
                  msg,
                  source_id,
                  ts_time
                )
                VALUES (
                  %s,
                  %s,
                  %s,
                  %s,
                  %s,
                  now()
                )
            '''
        return sql

    @staticmethod
    def select_article_cate_list():
        sql = '''
                select id, name, p_id
                from cate
                where del_flag = 'N'
                order by sort_num ASC
            '''
        return sql

    @staticmethod
    def select_cate_total_count():
        sql = '''
                select count(*) as num
                from cate
                where del_flag = 'N'
            '''
        return sql

    @staticmethod
    def select_cate_article_total_count():
        sql = '''
                select count(*) as num
                from article
                where del_flag = 'N'
                      and cate_id = %s
            '''
        return sql

    @staticmethod
    def del_cate_by_id():
        sql = '''
                delete from cate
                where id = %s
            '''
        return sql

    @staticmethod
    def select_cate_by_name():
        sql = '''
                select *
                from cate
                where name_en = %s
                  and p_id = %s
                  AND del_flag = 'N'
            '''
        return sql

    @staticmethod
    def insert_cate():
        sql = '''
                insert into cate(
                  name,
                  name_en,
                  pic_url,
                  p_id,
                  visiable,
                  home_visiable,
                  sort_num,
                  seo_title,
                  kws,
                  `desc`,
                  add_time
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, now())
            '''
        return sql

    @staticmethod
    def update_cate():
        sql = '''
                update cate
                set name = %s,
                    name_en = %s,
                    pic_url = %s,
                    p_id = %s,
                    visiable = %s,
                    home_visiable = %s,
                    sort_num = %s,
                    seo_title = %s,
                    kws = %s,
                    `desc` = %s,
                    update_time = now()
                where id = %s
            '''
        return sql

    @staticmethod
    def select_kw_list():
        sql = '''
                select id,
                        kw
                from keyword
                where del_flag = 'N'
                limit %s, %s
            '''
        return sql

    @staticmethod
    def select_kw_total_count():
        sql = '''
                select count(*) as num
                from keyword
                where del_flag = 'N'
            '''
        return sql

    @staticmethod
    def select_kw_by_id():
        sql = '''
                select id,
                        kw
                from keyword
                where id = %s
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
    def select_article_kws():
        sql = '''
                select kw
                from article_kw
                where article_id = %s
                limit 6
            '''
        return sql

    @staticmethod
    def select_article_list_with_content():
        sql = '''
                select a.*,
                      b.content
                from article a
                left join article_annex b
                on a.id = b.article_id
                where a.del_flag = 'N'
                order by a.id desc
                limit %s, %s
            '''
        return sql

    @staticmethod
    def check_this_article_kws():
        sql = '''
                select kw_matched
                from article
                where id = %s
            '''
        return sql

    @staticmethod
    def select_dede_article_total_count():
        sql = '''
                select count(*) as num
                from dede_archives
            '''
        return sql

    @staticmethod
    def select_kw_by_ci():
        sql = '''
                select id, kw
                from  keyword
                where kw like %s
                  and del_flag = 'N'
                limit 100
            '''
        return sql

    @staticmethod
    def insert_kw_kw():
        sql = '''
                insert into
                  kw_kw(source_kw_id, source_kw, related_kw_id, related_kw, related_kw_sort)
                VALUES (%s, %s, %s, %s, %s)
            '''
        return sql

    @staticmethod
    def insert_article_kw():
        sql = '''
                insert into
                  article_kw(article_id, kw, sort, type, add_time)
                VALUES (%s, %s, %s, %s, now())
            '''
        return sql

    @staticmethod
    def delete_article_kw_by_aid():
        sql = '''
                delete from article_kw
                where article_id = %s
            '''
        return sql

    @staticmethod
    def update_match_kw_status():
        sql = '''
                update article
                set kw_matched = 'Y'
                where id = %s
            '''
        return sql

    @staticmethod
    def del_article_kw_by_aid():
        sql = '''
                delete from
                  article_kw
                where article_id = %s
            '''
        return sql

    @staticmethod
    def select_all_no_thumb_articles():
        sql = '''
                select id,
                      article_id
                from article_annex
                where pic_url = '' or pic_url is NULL
                order by id desc
            '''
        return sql

    @staticmethod
    def select_article_annex_by_aid():
        sql = '''
                select id,
                      content,
                      pic_url
                from
                  article_annex
                where article_id = %s
            '''
        return sql

    @staticmethod
    def update_article_thumbpic_by_id():
        sql = '''
                update article_annex
                set pic_url = %s
                where id = %s
            '''
        return sql

    @staticmethod
    def select_cate_id_count_sql():
        sql = '''
                select count(*) as num
                from cate c
                where c.id = %s
                and del_flag = 'N';
            '''
        return sql

    @staticmethod
    def select_article_count_by_title_sql():
        sql = '''
                select count(*) as num
                from article a
                where a.title = %s
                and del_flag = 'N';
            '''
        return sql

    @staticmethod
    def select_article_by_title_sql():
        sql = '''
                select *
                from article a
                where a.title = %s
                and cate_id = %s
                and del_flag = 'N'
                limit 1;
            '''
        return sql

    @staticmethod
    def insert_hct_post_article_sql():
        sql = '''
                insert into
                    article (title,
                            cate_id,
                            source_id,
                            add_time)
                values (%s,
                        %s,
                        (
                                    (select
                                        max(source_id) as id
                                    from
                                        article as ar) + 1),
                          now()
                                  );
            '''
        return sql

    @staticmethod
    def insert_cj_source_url_sql():
        sql = '''
                insert into
                    article_source_url (article_id,
                            url)
                values (%s,
                        %s);
            '''
        return sql

    @staticmethod
    def insert_hct_post_article_content_sql():
        sql = '''
                insert into
                article_annex (content,`desc`,article_id)
                values(%s, %s, %s)
            '''
        return sql

    @staticmethod
    def update_hct_post_article_content_sql():
        sql = '''
                update article_annex
                set content = %s
                where article_id = %s
            '''
        return sql

    @staticmethod
    def select_no_desc_articles_sql():
        sql = '''
                SELECT id, content, `desc`
                from article_annex aa
                where aa.`desc` is NULL;
            '''
        return sql

    @staticmethod
    def update_article_desc_sql():
        sql = '''
                UPDATE article_annex
                set `desc` = %s
                WHERE id = %s;
            '''
        return sql


    @staticmethod
    def select_article_ids_not_match_kws():
        sql = '''
                SELECT id
                from article
                where kw_matched = 'N';
            '''
        return sql

    @staticmethod
    def select_article_by_id():
        sql = '''
                SELECT a.*, b.content
                from article a
                left join article_annex b
                on a.id = b.article_id
                where a.id = %s;
            '''
        return sql

    @staticmethod
    def search_article():
        sql = '''
                select a.*,
                      b.name cate_name,
                      b.name_en cate_name_en
                from article a
                LEFT JOIN cate b
                on a.cate_id = b.id
                where a.title = %s
                order by a.id desc
                limit %s, %s
            '''
        return sql

    @staticmethod
    def search_article_total_count():
        sql = '''
                select count(*) as num
                from article
                where title = %s
            '''
        return sql

    @staticmethod
    def get_article_detail_sql():
        sql = '''
                select a.id,
                      a.title,
                      a.show_type,
                      a.cate_id,
                      b.content,
                      b.pic_url,
                      b.desc,
                      c.name cate_name,
                      d.slug_url
                from article a
                LEFT JOIN article_annex b
                on a.id = b.article_id
                LEFT JOIN cate c
                on a.cate_id = c.id
                LEFT JOIN article_slug d
                on a.id = d.article_id
                where a.id = %s
            '''
        return sql

    @staticmethod
    def update_article_info_sql(publish=False):
        if publish:
            sql = '''
                    UPDATE article 
                    SET title=%s, 
                    cate_id=%s,
                    show_type=%s,
                    pub_status='Y',
                    pub_time=NOW(),
                    update_time=NOW() 
                    WHERE id=%s
                '''
        else:
            sql = '''
                    UPDATE article 
                    SET title=%s, 
                    cate_id=%s,
                    show_type=%s,
                    update_time=NOW() 
                    WHERE id=%s
                '''
        return sql

    @staticmethod
    def update_article_annex_sql_for_handadd():
        sql = '''
                UPDATE article_annex 
                SET content=%s,
                    pic_url=%s,
                    `desc`=%s
                WHERE article_id=%s
            '''
        return sql

    @staticmethod
    def publish_article_sql():
        sql = '''
                UPDATE article
                SET pub_status = 'Y',
                    pub_time = NOW(),
                    update_time = NOW()
                WHERE id = %s
            '''
        return sql

    @staticmethod
    def insert_article_sql():
        sql = '''
                insert into
                    article (title,
                            cate_id,
                            show_type,
                            source_id,
                            add_time)
                values (
                    %s,
                    %s,
                    %s,
                    (
                        (select
                            max(source_id) as id
                        from
                            article as ar) + 1),
                        now()
                    );
            '''
        return sql

    @staticmethod
    def insert_article_annex_sql():
        sql = '''
                INSERT INTO article_annex (content, pic_url, `desc`,article_id) 
                VALUES (%s, %s, %s, %s)
            '''
        return sql
    
    @staticmethod
    def update_cate_content_sql():
        sql = '''
                update cate
                set content = %s
                where id = %s
            '''
        return sql

    @staticmethod
    def select_cate_by_id_sql():
        sql = '''
                select id, name, name_en
                from cate
                where id = %s
            '''
        return sql