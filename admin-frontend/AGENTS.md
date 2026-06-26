# admin-frontend — Agent Instructions

> React admin SPA for xxg-cms. 说明用中文，命令/路径保持英文。

Parent doc: [../AGENTS.md](../AGENTS.md)

## Stack

| Layer | Technology |
|-------|------------|
| UI | React 18 + TypeScript |
| Build | Vite 6 |
| Routing | React Router 6 (`createBrowserRouter`) |
| Styling | Tailwind CSS 3 + shadcn/ui (new-york) |
| State | zustand (minimal) + page-local `useState` |
| HTTP | axios |
| Forms | react-hook-form + zod (login only) |
| Rich text | @wangeditor-next |
| Toast | sonner |
| Icons | lucide-react |

Entry: `src/main.tsx` → `src/router/index.tsx` → `src/layouts/MainLayout.tsx`

Path alias: `@/` → `src/`

## Key Paths

| Purpose | Path |
|---------|------|
| All API calls | `src/api/service.ts` |
| Routes | `src/router/index.tsx` |
| Sidebar menu | `src/components/layout/Sidebar.tsx` |
| Page shell | `src/components/PageShell.tsx` |
| Form label | `src/components/FormLabel.tsx` |
| Shared types | `src/types/index.ts` |
| Global store | `src/stores/app-store.ts` |
| Utilities | `src/lib/utils.ts` |
| Layout CSS classes | `src/index.css` |
| shadcn primitives | `src/components/ui/*` |
| Vite config + proxy | `vite.config.ts` |

## Dev Commands

```bash
npm install
npm run dev       # http://localhost:8080, proxy /api /media → :8000
npm run build     # tsc -b && vite build
npm run preview
npm run lint
```

Requires `admin-backend` running on `:8000`.

## Page Organization

```
src/pages/
├── login/LoginPage.tsx           # Standalone, no MainLayout
├── sys/                          # Global (no site selection required)
│   ├── SitePage.tsx
│   ├── AiConfigPage.tsx
│   ├── AiVerticalPage.tsx
│   └── AiTemplatePage.tsx
├── article/                      # Site-scoped features
│   ├── ArticleListPage.tsx
│   ├── AiTopicPage.tsx
│   ├── CatePage.tsx
│   ├── CarouselPage.tsx
│   ├── FriendLinkPage.tsx
│   └── SiteConfPage.tsx
└── keyword/
    └── KeywordListPage.tsx
```

Naming: file `{Feature}Page.tsx`, export `export function {Feature}Page()`.

## Routes

Defined in `src/router/index.tsx`:

| Path | Page | Scope |
|------|------|-------|
| `/` | LoginPage | — |
| `/sites` | SitePage | Global |
| `/ai-config` | AiConfigPage | Global |
| `/ai-verticals` | AiVerticalPage | Global |
| `/ai-templates` | AiTemplatePage | Global |
| `/articles` | ArticleListPage | Site |
| `/ai-topics` | AiTopicPage | Site |
| `/cates` | CatePage | Site |
| `/keywords` | KeywordListPage | Site |
| `/carousels` | CarouselPage | Site |
| `/links` | FriendLinkPage | Site |
| `/conf` | SiteConfPage | Site |

Sidebar sections in `Sidebar.tsx`: global items vs `requiresSite: true` (disabled when no `domain` selected).

## API Client Pattern

All services in **one file**: `src/api/service.ts`. Do not split unless explicitly requested.

### Naming

`{verb}{Resource}Service` — e.g. `getLinkListService`, `topicSuggestService`

### Site-Scoped Calls

```typescript
export const getLinkListService = (data: Record<string, unknown>) =>
  axios.post('/api/get_link_list/', xData(data)) as Promise<ApiResponse>
```

`xData()` injects `domain` from `sessionStorage`.

### Auth Interceptor

- Request: sets header `auth-key` from `sessionStorage.token`
- Response: `code === 403` → `useAppStore.getState().showLoginForm()`

### Response Type

`src/types/index.ts` → `ApiResponse<T>` with `code`, `message`, `data`/`datas`, `total_count`, `ret`.

Success check: `res.code === 0`. Some write ops also check `res.ret`.

### File Upload

Do **not** use axios service. Use `src/components/FileUpload.tsx` with `getAuthHeaders()` from `service.ts`.

## Add New Page (5 Steps)

1. Create `src/pages/{domain}/{Name}Page.tsx` with `export function {Name}Page()`
2. Register route in `src/router/index.tsx` under `MainLayout` children
3. Add sidebar entry in `src/components/layout/Sidebar.tsx` (site-scoped → `requiresSite: true` section)
4. Add API functions in `src/api/service.ts` (use `xData()` for site endpoints)
5. Add shared entity types in `src/types/index.ts` if needed (page-local types can stay in the page file)

## UI Conventions

### PageShell

```tsx
<PageShell title="标题" description="说明" actions={<Button>操作</Button>}>
  {children}
</PageShell>
```

Max width 1400px. Used on every page.

### List / CRUD Pages

Pattern (reference: `src/pages/article/FriendLinkPage.tsx`):

```
PageShell
  └── content-panel
        └── Table (shadcn) + Pagination
  └── Dialog (create/edit form)
  └── ConfirmDialog (delete)
  └── Loading overlay
  └── toast via sonner
```

State: `useState` for `loading`, `list`, `total`, `pageNum`, `pageSize`, `dialogOpen`, `form`, `deleteTarget`; `useEffect` + `useCallback` for data fetch.

### Form Layout Classes (`src/index.css`)

| Class | Use |
|-------|-----|
| `dialog-form-row` | Label + control, vertically centered |
| `dialog-form-row-top` | Label + control, top-aligned (textarea, Select) |
| `dialog-form-row-wide` / `-wide-top` | Wider label column |
| `dialog-form-narrow` | Narrow label (6rem) |
| `content-panel` | Card wrapper for table/content |
| `table-scroll-panel` | Horizontal scroll for wide tables |
| `table-action-icon` / `-danger` | Row action buttons |

Use `FormLabel` for required fields (shows red `*`), `Label` from shadcn for simple labels.

### Interactive Pages

Reference: `src/pages/article/AiTopicPage.tsx` — form panels, polling, navigation after job complete.

## State Management Reality

| Tool | Usage |
|------|-------|
| Page `useState` + `useEffect` | **Primary pattern** for all list/form pages |
| zustand (`useAppStore`) | Login dialog, `siteNameX`, sidebar collapsed |
| sessionStorage | `token`, `name`, `domain`, `root_path` |
| TanStack Query | Provider mounted in `main.tsx` but **not used** — do not introduce unless requested |
| TanStack Table | Dependency installed but **not used** — use shadcn `Table` |

## AI Pages

| Route | File | Flow |
|-------|------|------|
| `/ai-topics` | `AiTopicPage.tsx` | Seed keyword → suggestions → select → confirm generate → poll → navigate `/articles?ai=1` |
| `/ai-config` | `AiConfigPage.tsx` | Provider/model settings panel |
| `/ai-verticals` | `AiVerticalPage.tsx` | Vertical CRUD |
| `/ai-templates` | `AiTemplatePage.tsx` | Prompt template CRUD |

AI API services (all in `service.ts`, prefix `/api/ai/`):

| Service | Endpoint |
|---------|----------|
| `topicSuggestService` | `topic_suggest/` |
| `topicConfirmGenerateService` | `topic_confirm_generate/` |
| `getTopicSessionService` | `topic_session/` |
| `getTopicSessionsService` | `topic_sessions/` |
| `getAiVerticalsService` | `verticals/` |
| `getAiTemplatesService` | `templates/` |
| `getAiConfigSettingsService` | `config_settings/` |

`ArticleListPage.tsx` integrates AI: URL `?ai=1` filters `ai_only`, shows `AI` badge when `ai_generated === 'Y'`.

## Reference Pages

| Pattern | File |
|---------|------|
| Standard CRUD | `src/pages/article/FriendLinkPage.tsx` |
| Complex list | `src/pages/article/ArticleListPage.tsx` |
| Interactive / polling | `src/pages/article/AiTopicPage.tsx` |
| Global admin CRUD | `src/pages/sys/AiVerticalPage.tsx` |
| Config panel | `src/pages/sys/AiConfigPage.tsx` |

## DO NOT

- Split `service.ts` into multiple files without explicit request
- Use TanStack Table in new pages — use shadcn `Table`
- Introduce TanStack Query in new pages by default
- Upload files via axios — use `FileUpload.tsx`
- Add routes without updating `Sidebar.tsx` when the page needs menu access
- Use class components
