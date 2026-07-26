import type { MediaItem } from '@/types'
import { getAdminMediaUrl } from '@/lib/utils'

function escapeHtml(text: string) {
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
}

export function mediaItemUrl(item: MediaItem) {
  return item.url || getAdminMediaUrl(item.file_path)
}

/** 将媒体库条目转为可插入编辑器的 HTML */
export function buildMediaInsertHtml(items: MediaItem[]) {
  return items
    .map((item) => {
      const url = mediaItemUrl(item)
      const name = escapeHtml(item.name || '文件')
      if (item.file_type === 'image') {
        return `<img src="${escapeHtml(url)}" alt="${name}" style="max-width:100%;"/>`
      }
      if (item.file_type === 'video') {
        return `<p><video src="${escapeHtml(url)}" controls style="max-width:100%;"></video></p>`
      }
      return `<p><a href="${escapeHtml(url)}" target="_blank" rel="noopener noreferrer">${name}</a></p>`
    })
    .join('')
}
