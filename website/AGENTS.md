# website — Agent Instructions

> Django public-facing CMS site for xxg-cms. 说明用中文，命令/路径保持英文。

Parent doc: [../AGENTS.md](../AGENTS.md)

## Purpose

- Renders published CMS content as HTML for visitors (SSR via Django Templates)
- **Does not call admin-backend HTTP API** — reads MySQL directly
- Multi-site: selects DB and theme by `HTTP_HOST`
- Content editing happens in `admin-backend` + `admin-frontend`; this project only displays

## Stack

| Layer | Technology |
|-------|------------|
| Framework | Django 4.2 LTS |
| Database | PyMySQL raw SQL (no ORM, no `models.py`) |
| Templates | Django Templates |
| Dates | arrow |

`INSTALLED_APPS` contains only `django.contrib.staticfiles`.

## Key Paths

| Purpose | Path |
|---------|------|
| Root URLs | `apps/urls.py` |
| Chinese-style routes | `apps/pages/urls.py` |
| English/slug routes | `apps/pages_en/urls.py` |
| Views | `apps/pages/view.py` |
| Business logic | `apps/pages/service.py` |
| SQL statements | `apps/pages/mapper.py` |
| Site mapping + DB | `apps/utils/public.py` |
| Media URL rewrite | `apps/utils/media_urls.py` |
| Env bootstrap | `apps/utils/env_bootstrap.py` |
| Settings | `apps/settings/{base,dev,prod}.py` |
| Templates | `templates/{theme_dir}/` |
| Static assets | `static/` |
| Ops scripts | `scripts/website.sh` |
| Production WSGI | `apps/wsgi.py`, `uwsgi.ini` |

## Relation to admin-backend

| Shared | Details |
|--------|---------|
| System DB `xxgcms` | `site` table maps domain → CMS DB credentials |
| CMS DB `db_x_*` | Processed content (articles, categories, etc.) |
| Media directory | `admin-backend/xxgcms_static_files` via `MEDIA_ROOT` |
| Env vars | `XXGCMS_DB_*` synced from admin-backend setup |

```
HTTP Request (HTTP_HOST)
  → SITE_MAP loaded from xxgcms.site (apps/utils/public.py)
  → connect site db_x_* CMS database
  → query article / cate / keyword / site_conf / carousel / friend_link
  → render templates/{theme_dir}/*.html
```

Schema changes belong in `admin-backend/sql/`, not here.

## Multi-Site Flow

1. Request arrives with `HTTP_HOST` (e.g. `localhost:8088`)
2. `SITE_MAP` lookup matches `site.name` — **must include port** if dev uses port
3. Connect to that site's `db_x_*` database
4. Load `site_conf` (includes `theme_dir`, SEO settings)
5. Render template from `templates/{theme_dir}/`

Theme examples: `www_xxg_ai`, `www_17yly_com` (directories under `templates/`).

## URL Routing

Root `apps/urls.py`:

1. `/media/*` → Django `serve` from `MEDIA_ROOT`
2. `pages.urls` (Chinese-style, registered first)
3. `pages_en.urls` (English/slug-style)

### Chinese Routes (`apps/pages/urls.py`)

| Pattern | View | Page |
|---------|------|------|
| `^$` | `index` | Homepage |
| `^{cate}/$` | `article_list` | Category list |
| `^{cate}/list-{page}.html` | `article_list` | Paginated list |
| `^tag/{tname}` / `^topics/{tname}` | `tag_list` | Tag page |
| `^topic/{tid}.html` | `topic_list` | Topic by ID |
| `^page/{page_num}` | `page_list` | Site-wide pagination |
| `^{source_id}.html` | `article_detail` | Article detail |
| `^{cate}/{source_id}.html` | `article_detail` | Article with category |

### English Routes (`apps/pages_en/urls.py`)

- Slug-based article detail: `article_detail_by_slug`
- Paginated lists: `/page/N/` format
- Registered after Chinese routes; numeric ID routes take priority

### View Pattern

Each view in `apps/pages/view.py`:

1. Read `request.META['HTTP_HOST']`
2. `service.get_site_base_info(host)` → site config + `theme_dir`
3. Fetch data via service/mapper
4. `render(request, '{theme_dir}/xxx.html', context)`

WordPress compat: `?p={id}` on homepage → 301 to `/{id}.html`.

## Templates

```
templates/
├── 404.html
├── www_xxg_ai/
│   ├── index.html, article.html, article_list.html, tag_list.html, page_list.html
│   └── inc/          # header, footer, links, tongji, back_top
└── www_17yly_com/    # alternate theme
```

Include partials: `{% include site_info.theme_dir|add:"/inc/header.html" %}`

Site favicon/logo from CMS config: `/media/{{ site_info.favicon_url }}`

## Static Assets

```
static/
├── css/, js/, img/     # shared
└── xxgai          # xxg.ai theme
```

Config: `STATIC_URL='/static/'`, `STATICFILES_DIRS` → `website/static/`

Use `{% load static %}` + `{% static 'path' %}` in templates.

## Add / Modify Public Page

1. **SQL** — add query in `apps/pages/mapper.py`
2. **Logic** — add function in `apps/pages/service.py`
3. **View** — add handler in `apps/pages/view.py`
4. **Route** — register in `apps/pages/urls.py` or `apps/pages_en/urls.py`
5. **Template** — create/edit `templates/{theme_dir}/xxx.html`
6. **CSS/JS** — add to `static/` or theme subdirectory

If schema change needed → edit `admin-backend/sql/cmsdb.sql` + run `sync_db`.

## Commands

Prerequisite: complete `admin-backend` setup first.

```bash
./scripts/website.sh install     # venv + pip (can reuse admin-backend venv)
./scripts/website.sh start       # dev server :8088
./scripts/website.sh check       # Django system check
./scripts/website.sh prod-start  # production settings
```

Manual:

```bash
python manage.py runserver 0.0.0.0:8088
```

Production: `apps.settings.prod` via `apps/wsgi.py`, see `uwsgi.ini`.

## Environment Variables

See `.env.example`:

| Variable | Purpose |
|----------|---------|
| `WEBSITE_SECRET_KEY` | Django secret |
| `XXGCMS_DB_*` | System DB (shared with backend) |
| `WEBSITE_MEDIA_URL` | Media URL prefix |
| `XXGCMS_MEDIA_DIR` | Physical media path (default: `xxgcms_static_files`) |
| `WEBSITE_ALLOWED_HOSTS` | Production allowed hosts |
| `WEBSITE_LOG_DIR` | Production log directory |

## DO NOT

- Add HTTP client calls to admin-backend API — read DB directly
- Read from `db_*` source DB for display — use `db_x_*` processed DB
- Define schema/migrations in website — all schema in `admin-backend/sql/`
- Introduce Django ORM models
- Assume `site.name` is hostname-only — dev requires port (e.g. `localhost:8088`)
- Commit `.env` or `.credentials`
