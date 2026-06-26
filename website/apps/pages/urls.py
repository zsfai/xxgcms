# coding: utf-8
from django.urls import re_path

from apps.pages import view

urlpatterns = [
    re_path(r'^$', view.index, name='index_zh'),
    re_path(r'^(?P<cate_name_en>[A-Za-z0-9\-_]+)/$', view.article_list, name='article_list'),
    re_path(r'^(?P<cate_name_en>[A-Za-z0-9\-_]+)/index.html$', view.article_list, name='article_list2'),
    re_path(
        r'^(?P<cate_name_en>[A-Za-z0-9\-_]+)/list-(?P<page_num>[0-9]+).html$',
        view.article_list,
        name='article_list_page',
    ),
    re_path(r'^tag/(?P<tname>[\w\-\(\) ]+)$', view.tag_list, name='tag_list'),
    re_path(r'^topics/(?P<tname>[A-Za-z0-9\-]+)$', view.tag_list, name='tag_list2'),
    re_path(r'^topic/(?P<tid>[0-9]+).html$', view.topic_list, name='topic_list'),
    re_path(r'^page/(?P<page_num>[0-9]+)$', view.page_list, name='page_list'),
    re_path(r'^(?P<source_id>[0-9]+).html$', view.article_detail, name='article_detail'),
    re_path(
        r'^(?P<cate_name_en>[A-Za-z0-9\-_]+)/(?P<source_id>[0-9]+).html$',
        view.article_detail,
        name='article_detail2',
    ),
    re_path(
        r'^(?P<cate_name_en>[A-Za-z0-9\-_]+)/(?P<sub_name>[A-Za-z0-9\-_]+)/$',
        view.article_list,
        name='article_list_sub',
    ),
    re_path(
        r'^(?P<cate_name_en>[A-Za-z0-9\-_]+)/(?P<sub_name>[A-Za-z0-9\-_]+)/(?P<source_id>[0-9]+).html$',
        view.article_detail,
        name='article_detail_sub',
    ),
    re_path(
        r'^(?P<cate_name_en>[A-Za-z0-9\-_]+)/(?P<sub_name>[A-Za-z0-9\-_]+)/list-(?P<page_num>[0-9]+).html$',
        view.article_list,
        name='article_list_sub_page',
    ),
]
