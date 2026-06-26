import { type ClassValue, clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatDateTime(value?: string | null) {
  if (!value) return ''
  return value.replace('T', ' ')
}

export function getMediaUrl(_domain: string, path?: string | null) {
  // 上传文件保存在 admin-backend 的 MEDIA_ROOT，后台预览统一走 /media（Vite 代理到 API）
  return getAdminMediaUrl(path)
}

/** 前台站点域名下的 media 地址（用于外链预览，非后台 img src） */
export function getSiteMediaUrl(domain: string, path?: string | null) {
  if (!path || !domain) return ''
  const normalized = path.replace(/\\/g, '/').replace(/^\/+/, '')
  return `//${domain}/media/${normalized}`
}

/** 管理后台 media 目录下的静态资源（站点注册图等） */
export function getAdminMediaUrl(path?: string | null) {
  if (!path) return ''
  if (path.startsWith('http://') || path.startsWith('https://') || path.startsWith('//')) {
    return path
  }
  const normalized = path.replace(/\\/g, '/').replace(/^\/+/, '')
  return `/media/${normalized}`
}

/** 站点 CMS 上传资源（文章封面等含 root_path 前缀的路径） */
export function resolveSiteMediaUrl(path?: string | null, rootPath?: string | null) {
  if (!path) return ''
  const normalized = path.replace(/\\/g, '/').replace(/^\/+/, '')
  if (normalized.startsWith('upload/files/') && rootPath) {
    const root = rootPath.replace(/\\/g, '/').replace(/^\/+|\/+$/g, '')
    if (root) return getAdminMediaUrl(`${root}/${normalized}`)
  }
  return getAdminMediaUrl(normalized)
}

/** 后端顶级分类 p_id 为 -1，与 null 均表示无父级 */
export function normalizeParentId(pId?: number | null): number | null {
  if (pId == null || pId === -1) return null
  return pId
}

export function listToTree<T extends { id: number; p_id?: number | null; children?: T[] }>(
  list: T[],
  pId: number | null = null,
): T[] {
  const tree: T[] = []
  list.forEach((item) => {
    if (normalizeParentId(item.p_id) === pId) {
      const children = listToTree(list, item.id)
      if (children.length) item.children = children
      tree.push(item)
    }
  })
  return tree
}

export function findCategoryName(
  tree: Array<{ id: number; name: string; children?: Array<{ id: number; name: string; children?: unknown[] }> }>,
  id?: number | null,
): string {
  if (!id) return ''
  for (const item of tree) {
    if (item.id === id) return item.name
    if (item.children?.length) {
      const found = findCategoryName(item.children as typeof tree, id)
      if (found) return found
    }
  }
  return ''
}
