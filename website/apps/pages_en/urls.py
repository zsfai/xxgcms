# coding: utf-8
from django.urls import re_path

from apps.pages import view

urlpatterns = [
    re_path(r'^$', view.index, name='index_en'),
    re_path(r'^tag/(?P<tname>[\w\-\(\) ]+)$', view.tag_list, name='tag_list_en'),
    re_path(r'^page/(?P<page_num>[0-9]+)$', view.page_list, name='page_list_en'),
    re_path(r'^(?P<cate_name_en>[A-Za-z0-9\-_]+)/$', view.article_list, name='article_list_en'),
    re_path(
        r'^(?P<cate_name_en>[A-Za-z0-9\-_]+)/page/(?P<page_num>[0-9]+)/$',
        view.article_list,
        name='article_list_page_en',
    ),
    re_path(
        r'^(?P<cate_name_en>[A-Za-z0-9\-_]+)/(?P<sub_name>[A-Za-z0-9\-_]+)/$',
        view.article_list,
        name='article_list_with_sub_cate_en',
    ),
    re_path(
        r'^(?P<cate_name_en>[A-Za-z0-9\-_]+)/(?P<sub_name>[A-Za-z0-9\-_]+)/page/(?P<page_num>[0-9]+)/$',
        view.article_list,
        name='article_list_page_with_sub_cate_en',
    ),
    re_path(r'^(?P<url_path_slug>[\w\-\(\) ]+)$', view.article_detail_by_slug, name='article_detail_by_slug'),
    re_path(
        r'^(?P<cate_name_en>[A-Za-z0-9\-_]+)/(?P<url_path_slug>[\w\-\(\) ]+)$',
        view.article_detail_by_slug,
        name='article_detail_with_cate',
    ),
    re_path(
        r'^(?P<cate_name_en>[A-Za-z0-9\-_]+)/(?P<sub_name>[A-Za-z0-9\-_]+)/(?P<url_path_slug>[\w\-\(\) ]+)$',
        view.article_detail_by_slug,
        name='article_detail_with_sub_cate',
    ),
]
