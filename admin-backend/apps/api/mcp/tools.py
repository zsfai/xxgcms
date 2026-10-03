# coding: utf-8
import json

from apps.api.service import mcp_push_service
from apps.api.utils.public import log_error

SERVER_INSTRUCTIONS = (
    '将用户电脑上的产品资料、说明书整理成一篇或多篇文章后推入 CMS。'
    '流程：1) list_sites 确认站点 name；2) 可用 list_categories 查看已有栏目；'
    '3) 正文中的图片先 upload_image，把返回的 url 写入 HTML/Markdown；'
    '4) push_article 提交，文章固定为草稿，需人工在后台审核发布。'
    '没有匹配栏目时服务端会新建隐藏栏目（前台菜单不可见）。'
)

TOOL_DEFS = [
    {
        'name': 'list_sites',
        'description': '列出当前 MCP Key 可写入的站点。push_article / upload_image 的 site 参数必须使用返回的 name。',
        'inputSchema': {
            'type': 'object',
            'properties': {},
            'additionalProperties': False,
        },
    },
    {
        'name': 'list_categories',
        'description': '列出站点已有文章栏目（含隐藏栏目）。',
        'inputSchema': {
            'type': 'object',
            'properties': {
                'site': {
                    'type': 'string',
                    'description': '站点 name（与 list_sites 返回的 name 一致）',
                },
            },
            'required': ['site'],
            'additionalProperties': False,
        },
    },
    {
        'name': 'upload_image',
        'description': (
            '上传一张图片。服务端会压缩为 JPEG：最长边不超过 1200px，体积不超过 1MB。'
            '将返回的 url 嵌入文章正文，不要把原始 base64 写进 push_article。'
        ),
        'inputSchema': {
            'type': 'object',
            'properties': {
                'site': {'type': 'string', 'description': '站点 name'},
                'filename': {'type': 'string', 'description': '原始文件名，如 photo.png'},
                'content_base64': {
                    'type': 'string',
                    'description': '图片文件的 base64（可带 data:image/...;base64, 前缀）',
                },
            },
            'required': ['site', 'content_base64'],
            'additionalProperties': False,
        },
    },
    {
        'name': 'push_article',
        'description': (
            '推送一篇文章，固定保存为草稿（pub_status=N），不会发布到前台。'
            '按 category_name 匹配栏目，匹配不到则自动创建隐藏栏目。'
            'content 可以是 HTML 或 Markdown。'
        ),
        'inputSchema': {
            'type': 'object',
            'properties': {
                'site': {'type': 'string', 'description': '站点 name'},
                'title': {'type': 'string', 'description': '文章标题'},
                'content': {'type': 'string', 'description': '正文 HTML 或 Markdown'},
                'category_name': {
                    'type': 'string',
                    'description': '栏目中文名或英文标识。没有则自动创建',
                },
                'summary': {'type': 'string', 'description': '摘要，可空'},
                'keywords': {
                    'type': 'array',
                    'items': {'type': 'string'},
                    'description': '关键词列表，可空',
                },
                'cover_image_base64': {
                    'type': 'string',
                    'description': '封面图 base64，可空；会按同样规则压缩',
                },
                'cover_url': {
                    'type': 'string',
                    'description': '已上传封面的 /media/... 地址，可空',
                },
            },
            'required': ['site', 'title', 'content', 'category_name'],
            'additionalProperties': False,
        },
    },
]


def _text_result(payload, is_error=False):
    if isinstance(payload, str):
        text = payload
    else:
        text = json.dumps(payload, ensure_ascii=False)
    return {
        'content': [{'type': 'text', 'text': text}],
        'isError': bool(is_error),
    }


def call_tool(key_row, name, arguments):
    args = arguments if isinstance(arguments, dict) else {}
    try:
        if name == 'list_sites':
            return _text_result({'sites': mcp_push_service.list_sites_for_key(key_row)})
        if name == 'list_categories':
            site = mcp_push_service.resolve_site_name(key_row, args.get('site'))
            rows = mcp_push_service.list_categories(site)
            return _text_result({'site': site, 'categories': rows})
        if name == 'upload_image':
            site = mcp_push_service.resolve_site_name(key_row, args.get('site'))
            data = mcp_push_service.save_normalized_image(
                site,
                args.get('filename') or 'image.jpg',
                args.get('content_base64') or '',
            )
            return _text_result(data)
        if name == 'push_article':
            site = mcp_push_service.resolve_site_name(key_row, args.get('site'))
            data = mcp_push_service.push_article(
                site,
                args.get('title') or '',
                args.get('content') or '',
                args.get('category_name') or '',
                summary=args.get('summary') or '',
                keywords=args.get('keywords'),
                cover_image_base64=args.get('cover_image_base64') or '',
                cover_url=args.get('cover_url') or '',
            )
            return _text_result(data)
        return _text_result('未知工具：%s' % name, is_error=True)
    except Exception as exc:
        log_error('MCP tool %s failed: %s' % (name, exc))
        return _text_result(str(exc), is_error=True)
