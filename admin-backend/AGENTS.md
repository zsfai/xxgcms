# admin-backend — Agent Instructions

> Django REST API for xxg-cms admin. 说明用中文，命令/路径保持英文。

Parent doc: [../AGENTS.md](../AGENTS.md)

## Architecture

**Django shell + PyMySQL raw SQL** — no Django ORM, no DRF, no Serializers.

```
HTTP Request
  → apps/api/controller/*.py     (@csrf_exempt, @perm)
  → apps/api/service/*.py        (business logic)
  → apps/api/sql_mapper/*.py     (SQL strings)
  → apps/api/db/connection.py    (PyMySQL connections)
```

AI sub-package follows the same pattern under `apps/api/ai/` with its own mapper, service, pipeline, providers.

## Key Paths

| Purpose | Path |
|---------|------|
| Root URL | `apps/urls.py` → prefix `/api/` |
| API routes | `apps/api/urls.py` |
| Controllers | `apps/api/controller/` |
| Services | `apps/api/service/` |
| SQL mappers | `apps/api/sql_mapper/` |
| Auth decorator | `apps/api/utils/perm_wrapper.py` |
| JSON response | `apps/api/utils/response.py` |
| DB connections | `apps/api/db/connection.py` |
| Site config cache | `apps/api/utils/base_conf.py` |
| Upload helpers | `apps/api/utils/upload.py` |
| Settings | `apps/settings/{base,dev,prod}.py` |
| System DB schema | `sql/xxgcms.sql` |
| CMS DB schema | `sql/cmsdb.sql` |
| Schema patches | `sql/patch_*.sql` |
| Ops scripts | `scripts/xxgcms.sh` |

## Database Connections

Use context managers from `apps/api/db/connection.py`:

| Function | Database | Tables |
|----------|----------|--------|
| `xxgcms_connection()` | System `xxgcms` | `user`, `site`, `site_user`, `ai_*` |
| `cms_x_connection(domain)` | Site processed DB `db_x_*` | `article`, `cate`, `keyword`, `carousel`, `friend_link`, `site_conf` |
| `cms_connection(domain)` | Site source DB `db_*` | Read-only legacy data |

- Cursor type: `DictCursor`
- Transactions: manual `conn.commit()` / `conn.begin()`
- Site DB credentials cached in `SITE_MAP` (refreshed on login via `refesh_site_conf`)

## API Conventions

### Routing

- All routes in `apps/api/urls.py`
- Pattern: `re_path(r'^endpoint_name/', module.view_fn)` — trailing slash required
- AI routes: prefix `ai/` (e.g. `ai/topic_suggest/`)
- Full path example: `POST /api/get_kw_list/`

### Request

- Method: mostly `POST`
- Body: JSON (`parse_json`) or `multipart/form-data` for uploads
- Site context: field `domain` (site `name`) or header `HTTP_DOMAIN`
- Auth header: `HTTP_AUTH_KEY`

### Response

Use helpers from `apps/api/utils/response.py`:

```python
from apps.api.utils.response import api_success, api_error, parse_json

return api_success(datas=rows, total_count=count)
return api_error('message', code=10001)
```

Legacy controllers may build `JsonResponse` manually — prefer `api_success`/`api_error` for new code.

### Controller Template

Reference: `apps/api/controller/keyword.py`

```python
from django.views.decorators.csrf import csrf_exempt
from apps.api.utils.perm_wrapper import perm
from apps.api.utils.response import api_success, api_error, parse_json
from apps.api.utils.public import log_error

@csrf_exempt
@perm(code=None)
def get_kw_list(request):
    try:
        req = parse_json(request)
        domain = req.get('domain', '')
        datas, total_count = keyword_service.get_kw_list(domain, ...)
        return api_success(datas=datas, total_count=total_count)
    except Exception as exc:
        log_error(str(exc))
        return api_error(str(exc))
```

### Service + Mapper Template

```python
# sql_mapper/keyword_mapper.py
class KeywordMapper:
    @staticmethod
    def select_kw_by_kw():
        return 'SELECT * FROM keyword WHERE kw = %s'

# service/keyword_service.py
def get_kw_by_kw(domain, kw):
    with cms_x_connection(domain) as conn:
        with conn.cursor() as cursor:
            cursor.execute(KeywordMapper.select_kw_by_kw(), (kw,))
            return cursor.fetchone()
```

## Add New API Endpoint (4 Steps)

1. **Mapper** — add SQL method in `apps/api/sql_mapper/{domain}_mapper.py`
2. **Service** — add business function in `apps/api/service/{domain}_service.py`
3. **Controller** — add view in `apps/api/controller/{domain}.py` with `@csrf_exempt` + `@perm`
4. **Route** — register in `apps/api/urls.py`

If new tables/columns needed:

5. Update `sql/xxgcms.sql` or `sql/cmsdb.sql` (or add `sql/patch_*.sql`)
6. Run `python manage.py sync_db` (or `./scripts/xxgcms.sh sync-db`)

## AI Module

Recent focus area. Root: `apps/api/ai/`

### Structure

| Path | Role |
|------|------|
| `apps/api/controller/ai.py` | HTTP entry (imports from `apps/api/ai/service/`) |
| `service/topic_service.py` | Topic sessions, confirm generate |
| `service/template_service.py` | Prompt template CRUD |
| `service/vertical_service.py` | Vertical (industry) CRUD |
| `service/ai_service.py` | Single/batch article generation |
| `service/config_service.py` | Provider/model config |
| `service/batch_runner.py` | Async batch jobs (thread, not Celery) |
| `pipeline/topic_pipeline.py` | Search → LLM → suggestions |
| `pipeline/article_pipeline.py` | LLM → metadata → cover image → save draft |
| `mapper/ai_mapper.py` | `ai_*` table SQL |
| `prompts/` | Prompt builders |
| `providers/registry.py` | Text / Image / Search provider registry |
| `config/model_config.py` | Load provider config from DB |

### Provider Registry

Three provider types: **Text**, **Image**, **Search**.

- Registry: `apps/api/ai/providers/registry.py`
- Registration triggered by import in `apps/api/ai/providers/__init__.py` (called from `apps.py` `ready()`)
- Implemented: `deepseek_text`, `qwen_image`, `bocha_search`, `tavily_search`

To add a provider:

1. Implement in `apps/api/ai/providers/{name}.py`
2. Register in `registry.py`
3. Import in `providers/__init__.py`
4. Add DB config rows in `ai_provider` / `ai_model` (schema in `sql/xxgcms.sql`)

### AI Flow

```
topic_suggest → topic_pipeline → search (optional) → DeepSeek → ai_topic_suggestion
topic_confirm_generate → batch_runner → article_pipeline → article (draft)
```

Key endpoints (all under `/api/ai/`):

| Endpoint | Purpose |
|----------|---------|
| `topic_suggest/` | Generate topic suggestions from seed keyword |
| `topic_confirm_generate/` | Confirm selected topics, start write job |
| `topic_session/` / `topic_sessions/` | Query session status/history |
| `verticals/` / `templates/` | Read-only lists for topic page |
| `verticals_admin/` / `templates_admin/` | Admin CRUD |
| `generate_article/` | Direct write from known title |
| `config_settings/` | Provider/model configuration |

### AI Tables (system DB)

Defined in `sql/xxgcms.sql`: `ai_provider`, `ai_model`, `ai_prompt_template`, `ai_system_setting`, `ai_vertical`, `ai_topic_session`, `ai_topic_suggestion`, `ai_search_log`, `ai_batch_job`, `ai_batch_item`, `ai_generation_log`

## Commands

### Local Development

```bash
./scripts/xxgcms.sh install       # venv + pip install
./scripts/xxgcms.sh setup         # .env + DB + admin user
./scripts/xxgcms.sh start         # dev server :8000
./scripts/xxgcms.sh check         # Django system check
./scripts/xxgcms.sh sync-db       # incremental schema sync
./scripts/xxgcms.sh credentials   # show admin credentials
python manage.py sync_db --dry-run
python manage.py init_db          # full re-init — use with caution
```

### Docker Production

From repo root:

```bash
docker compose up -d --build
docker compose exec backend cat /app/admin-backend/.credentials
docker compose logs -f backend
```

Backend runs uWSGI via `docker/uwsgi/backend.ini` on internal port `8002`. Image: `xxgcms/admin-backend:latest`.

Optional website is a **separate image** `xxgcms/website:latest` — enable with compose profile `website`.

## Environment Variables

See `.env.example`. Key groups:

| Variable | Purpose |
|----------|---------|
| `XXGCMS_DB_*` | MySQL connection (shared with website) |
| `XXGCMS_SECRET_KEY`, `XXGCMS_AUTH_SALT` | Token signing |
| `XXGCMS_MEDIA_URL` | Media URL prefix |
| `DEEPSEEK_API_KEY` | Text generation |
| `DASHSCOPE_API_KEY` | Qwen image generation |
| `BOCHA_API_KEY`, `TAVILY_API_KEY` | Web search providers |

Fields marked `__AUTO__` are randomly generated on first `setup`.

## DO NOT

- Introduce Django Models, migrations, or DRF Serializers
- Write complex SQL in controllers — put in `sql_mapper/`
- Put AI endpoints in `controller/article.py` — use `controller/ai.py` with `ai/` route prefix
- Skip `@perm` on protected endpoints
- Use `cms_connection` for admin writes — use `cms_x_connection`
- Commit `.env`, `.credentials`, or `xxgcms_static_files/`
