# 小西瓜CMS Admin Frontend

React 18 + TypeScript + Vite + shadcn/ui 管理后台。

## 技术栈

- React 18 + TypeScript
- Vite 6
- React Router 6
- shadcn/ui + Tailwind CSS
- zustand（状态管理）
- TanStack Query
- react-hook-form + zod
- @wangeditor/editor-for-react（富文本）
- sonner（通知）
- axios（API 请求）

## 开发

```bash
npm install
npm run dev
```

开发服务器默认运行在 http://localhost:8080，API 代理至 `http://127.0.0.1:8000/`。

## 离线字体

管理后台使用自托管字体（不依赖 Google Fonts）：

| 字体 | 用途 | 路径 |
|------|------|------|
| Plus Jakarta Sans | 英文、数字（现代 SaaS 风格） | `static/fonts/plus-jakarta-sans/` |
| Noto Sans SC | 中文 | `static/fonts/noto-sans-sc/` |

样式入口：`src/fonts.css`（SIL Open Font License，可商用）。

## 构建

```bash
npm run build
npm run preview
```

## 路由

| 路径 | 页面 |
|------|------|
| `/` | 登录 |
| `/sites` | 站点管理 |
| `/articles` | 文章管理 |
| `/cates` | 分类管理 |
| `/keywords` | 关键词管理 |
| `/carousels` | 轮播配置 |
| `/links` | 友链管理 |
| `/conf` | 网站配置 |
