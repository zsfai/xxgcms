# coding: utf-8
from datetime import datetime


TRAVEL_TEMPLATES = [
    '{seed} 旅游攻略 {year}',
    '{seed} 最新 门票 政策',
    '{seed} 必去 景点 推荐',
    '{seed} 交通 住宿 攻略',
    '{seed} 最佳旅游时间',
]

NEWS_TEMPLATES = [
    '{seed} 最新 动态 {year}',
    '{seed} 行业 新闻',
    '{seed} 政策 解读',
]

GENERAL_TEMPLATES = [
    '{seed} 介绍',
    '{seed} 攻略 {year}',
    '{seed} 常见问题',
]


def expand_search_queries(seed: str, query_templates=None, vertical: str = 'general') -> list:
    seed = (seed or '').strip()
    year = datetime.now().year
    if query_templates:
        templates = query_templates
    elif vertical == 'travel':
        templates = TRAVEL_TEMPLATES
    elif vertical == 'news':
        templates = NEWS_TEMPLATES
    else:
        templates = GENERAL_TEMPLATES
    return [t.format(seed=seed, year=year) for t in templates]
