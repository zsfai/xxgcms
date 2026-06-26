# coding: utf-8


def format_search_snippets(items, max_chars=8000) -> str:
    lines = []
    total = 0
    for idx, item in enumerate(items, start=1):
        block = '[%d] %s\n来源: %s\n摘要: %s\n' % (idx, item.title, item.url, item.snippet)
        if total + len(block) > max_chars:
            break
        lines.append(block)
        total += len(block)
    return '\n'.join(lines)


def build_topic_system_prompt(vertical: str) -> str:
    if vertical == 'travel':
        role = '你是资深旅游内容策划编辑，熟悉国内旅游目的地。'
    elif vertical == 'news':
        role = '你是资深资讯编辑。'
    else:
        role = '你是资深内容策划编辑。'
    return (
        '%s根据联网检索摘要提炼选题建议。不得捏造检索中未出现的事实；'
        '不确定的数据标注「待核实」。输出必须是合法 JSON，不要 markdown 代码块。'
    ) % role


def build_topic_user_prompt(seed, vertical_label, cate_name, suggest_count, snippets_text, user_hint=None) -> str:
    cate_line = '目标栏目：%s\n' % cate_name if cate_name else ''
    hint_line = ('%s\n' % user_hint.strip()) if user_hint and user_hint.strip() else ''
    return (
        '垂类：%s\n'
        '种子词：%s\n'
        '%s%s'
        '检索摘要：\n---\n%s\n---\n'
        '请生成 %d 个互不重复、适合 SEO 的中文选题，JSON 格式：\n'
        '{"topics":[{"title":"文章标题","angle":"角度","timeliness":"为何值得写",'
        '"summary":"2-3句内容方向","ref_indexes":[1,2]}]}'
    ) % (vertical_label, seed, hint_line, cate_line, snippets_text, suggest_count)


def build_article_system_prompt(template_code: str) -> str:
    if template_code == 'travel_guide':
        return '你是专业旅游攻略作者，内容实用准确。不得捏造票价与开放时间。输出纯 JSON。'
    if template_code == 'industry_analysis':
        return '你是行业分析师。不得捏造数据。输出纯 JSON。'
    return '你是资深资讯作者。客观准确。不得捏造数据。输出纯 JSON。'


def build_article_user_prompt(
    title,
    cate_name,
    template_name,
    word_count,
    ref_titles,
    topic_context=None,
    user_hint=None,
) -> str:
    ctx = ''
    if topic_context:
        ctx = '选题背景：%s\n' % topic_context
    refs = ''
    if ref_titles:
        refs = '同栏目近期标题参考：%s\n' % '；'.join(ref_titles[:5])
    hint = ''
    if user_hint and str(user_hint).strip():
        hint = '%s\n' % str(user_hint).strip()
    return (
        '标题：%s\n栏目：%s\n模板：%s\n目标字数：约 %d 字\n%s%s%s'
        '请按 JSON 输出：{"desc":"80-120字摘要","kws":["词1"],"sections":'
        '[{"heading":"小节标题","body":"段落正文","image_hint":"英文配图描述"}],'
        '"suggested_slug":"slug"}。每个小节必须有独立 image_hint，用于生成配图。'
    ) % (title, cate_name, template_name, word_count, ctx, refs, hint)
