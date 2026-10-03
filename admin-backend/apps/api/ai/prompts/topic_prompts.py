# coding: utf-8

DEFAULT_TOPIC_SYSTEM_PROMPT = (
    '你是资深内容编辑，服务于网站 CMS。根据种子词提出对读者真正有用的选题：'
    '能帮人做决策、解决问题或学到可执行信息。避免空泛口号、标题党和无法核实的噱头。'
    '不得捏造事实与数据；不确定须标注「待核实」。'
    '输出必须是合法 JSON，不要 markdown 代码块。'
)

DEFAULT_ARTICLE_SYSTEM_PROMPT = (
    '你是资深网站内容作者。文章必须对读者有价值：信息具体、结构清楚、可执行，避免套话。'
    '不得捏造数据、政策、价格或出处。不确定的信息标注待核实。'
    '输出纯 JSON，不要 markdown。'
)


def build_topic_user_prompt(seed, cate_name, suggest_count, context_text) -> str:
    cate_line = '目标栏目：%s\n' % cate_name if cate_name else ''
    return (
        '种子词：%s\n'
        '%s'
        '补充说明：\n---\n%s\n---\n'
        '请生成 %d 个互不重复、适合搜索的中文选题，JSON 格式：\n'
        '{"topics":[{"title":"文章标题","angle":"角度","timeliness":"为何值得写",'
        '"summary":"2-3句内容方向","ref_indexes":[]}]}'
    ) % (seed, cate_line, context_text, suggest_count)


def build_article_user_prompt(
    title,
    cate_name,
    word_count,
    ref_titles,
    topic_context=None,
) -> str:
    ctx = ''
    if topic_context:
        ctx = '选题背景：%s\n' % topic_context
    refs = ''
    if ref_titles:
        refs = '同栏目近期标题参考：%s\n' % '；'.join(ref_titles[:5])
    return (
        '标题：%s\n栏目：%s\n目标字数：约 %d 字\n%s%s'
        '请按 JSON 输出：{"desc":"80-120字摘要","kws":["词1"],"sections":'
        '[{"heading":"小节标题","body":"段落正文","image_hint":"英文配图描述"}],'
        '"suggested_slug":"slug"}。每个小节必须有独立 image_hint，用于生成配图。'
    ) % (title, cate_name, word_count, ctx, refs)
