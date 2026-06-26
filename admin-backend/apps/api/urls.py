# coding:utf-8
from django.urls import re_path
from apps.api.controller import base, keyword, article, carousel, link, slugurl, ai, ssl


urlpatterns = [

    # 创建系统内置用户，不对外开放，注意生产环境注释掉
    # re_path(r'^add_user/', base.add_user),
    re_path(r'^refesh_site_conf/', base.refesh_site_conf),
    re_path(r'^login/', base.login),
    re_path(r'^change_password/', base.change_password),
    re_path(r'^add_site/', base.add_site),
    re_path(r'^update_site/', base.update_site),
    re_path(r'^del_site/', base.del_site),
    re_path(r'^get_site_list/', base.get_site_list),
    re_path(r'^get_site_page_list/', base.get_site_page_list),
    re_path(r'^upload_site_pic/', base.upload_site_pic),
    re_path(r'^test_site_db/', base.test_site_db),
    re_path(r'^get_site_ssl/', ssl.get_site_ssl),
    re_path(r'^update_site_ssl/', ssl.update_site_ssl),
    re_path(r'^test_site_ssl/', ssl.test_site_ssl),
    re_path(r'^sync_nginx/', ssl.sync_nginx),

    # 关键词
    re_path(r'^upload_excel/', keyword.upload_excel),
    re_path(r'^get_kw_list/', keyword.get_kw_list),
    re_path(r'^del_kw/', keyword.del_kw),
    re_path(r'^add_kw/', keyword.add_kw),
    re_path(r'^update_kw/', keyword.update_kw),
    re_path(r'^search_kw/', keyword.search_kw),

    # 链接url
    re_path(r'^generate_article_slug_url/', slugurl.generate_article_slug_url_by_title),

    # 文章
    re_path(r'^sync_latest_articles/', article.sync_latest_articles),
    re_path(r'^sync_article_info/', article.sync_article_info),
    re_path(r'^del_article_item/', article.del_article_item),
    re_path(r'^renew_article_item/', article.renew_article_item),
    re_path(r'^purge_article_item/', article.purge_article_item),
    re_path(r'^get_article_list/', article.get_article_list),
    re_path(r'^get_article_cate_list/', article.get_article_cate_list),
    re_path(r'^match_article_kws/', article.match_article_kws),
    re_path(r'^match_some_article_kws/', article.match_some_article_kws),
    re_path(r'^match_kw_kws/', article.match_kw_kws),
    re_path(r'^match_some_kw_kws/', article.match_some_kw_kws),
    re_path(r'^update_article_cate/', article.update_article_cate),
    re_path(r'^update_article_pre_pub/', article.update_article_pre_pub),
    re_path(r'^make_thumb_pic/', article.make_thumb_pic),
    re_path(r'^hct_auto_post/', article.hct_auto_post),
    re_path(r'^update_article_desc/', article.update_article_desc),
    re_path(r'^search_article/', article.search_article),
    re_path(r'^get_article_detail/', article.get_article_detail),
    re_path(r'^add_or_update_article/', article.add_or_update_article),
    re_path(r'^upload_file/', article.upload_file),
    re_path(r'^update_cate_content/', article.update_cate_content),

    # 站点参数配置
    re_path(r'^upload_site_logo_pic/', article.upload_site_logo_pic),
    re_path(r'^upload_defaul_pic/', article.upload_defaul_pic),
    re_path(r'^get_site_conf/', article.get_site_conf),
    re_path(r'^update_site_conf/', article.update_site_conf),

    # 类别
    re_path(r'^get_cate_list/', article.get_cate_list),
    re_path(r'^upload_cate_pic/', article.upload_cate_pic),
    re_path(r'^add_cate/', article.add_cate),
    re_path(r'^update_cate/', article.update_cate),
    re_path(r'^del_cate/', article.del_cate),

    # 轮播
    re_path(r'^get_carousel_list/', carousel.get_carousel_list),
    re_path(r'^upload_carousel_pic/', carousel.upload_carousel_pic),
    re_path(r'^add_carousel/', carousel.add_carousel),
    re_path(r'^update_carousel/', carousel.update_carousel),
    re_path(r'^del_carousel/', carousel.del_carousel),
    re_path(r'^view_carousels/', carousel.view_carousels),

    # 友链
    re_path(r'^get_link_list/', link.get_link_list),
    re_path(r'^upload_link_pic/', link.upload_link_pic),
    re_path(r'^add_link/', link.add_link),
    re_path(r'^update_link/', link.update_link),
    re_path(r'^del_link/', link.del_link),

    # AI（选题 / 写稿 / 配置）
    re_path(r'^ai/topic_suggest/', ai.topic_suggest),
    re_path(r'^ai/topic_update/', ai.topic_update),
    re_path(r'^ai/topic_confirm_generate/', ai.topic_confirm_generate),
    re_path(r'^ai/topic_session/', ai.topic_session),
    re_path(r'^ai/topic_sessions/', ai.topic_sessions),
    re_path(r'^ai/verticals_admin/', ai.verticals_admin),
    re_path(r'^ai/verticals/', ai.verticals_for_topic),
    re_path(r'^ai/create_vertical/', ai.create_vertical),
    re_path(r'^ai/update_vertical/', ai.update_vertical),
    re_path(r'^ai/delete_vertical/', ai.delete_vertical),
    re_path(r'^ai/templates_admin/', ai.templates_admin),
    re_path(r'^ai/templates/', ai.templates_for_topic),
    re_path(r'^ai/create_template/', ai.create_template),
    re_path(r'^ai/update_template/', ai.update_template),
    re_path(r'^ai/delete_template/', ai.delete_template),
    re_path(r'^ai/generate_article/', ai.generate_article),
    re_path(r'^ai/batch_generate/', ai.batch_generate),
    re_path(r'^ai/batch_job/', ai.batch_job),
    re_path(r'^ai/regenerate_body/', ai.regenerate_body),
    re_path(r'^ai/models/', ai.ai_models),
    re_path(r'^ai/providers/', ai.ai_providers),
    re_path(r'^ai/refresh_config/', ai.refresh_config),
    re_path(r'^ai/config_settings/', ai.config_settings),
    re_path(r'^ai/update_provider_config/', ai.update_provider_config),
    re_path(r'^ai/update_model_config/', ai.update_model_config),
    re_path(r'^ai/create_model_config/', ai.create_model_config),
    re_path(r'^ai/update_default_providers/', ai.update_default_providers),

]
