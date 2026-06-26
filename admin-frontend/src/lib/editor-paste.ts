import type { IDomEditor } from '@wangeditor-next/editor'
import { marked } from 'marked'

marked.setOptions({
  gfm: true,
  breaks: true,
})

const ALLOWED_TAGS = new Set([
  'P',
  'H1',
  'H2',
  'H3',
  'H4',
  'H5',
  'H6',
  'UL',
  'OL',
  'LI',
  'BLOCKQUOTE',
  'PRE',
  'CODE',
  'A',
  'IMG',
  'STRONG',
  'B',
  'EM',
  'I',
  'U',
  'S',
  'DEL',
  'BR',
  'HR',
  'DIV',
  'SPAN',
  'TABLE',
  'THEAD',
  'TBODY',
  'TR',
  'TH',
  'TD',
  'SUP',
  'SUB',
])

const SIMPLE_HTML_TAGS = new Set(['HTML', 'HEAD', 'BODY', 'META', 'P', 'BR', 'DIV', 'SPAN'])

function escapeHtml(text: string) {
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
}

export function normalizePasteText(text: string) {
  return text
    .replace(/\uFEFF/g, '')
    .replace(/\r\n/g, '\n')
    .replace(/\u00A0/g, ' ')
}

/** 识别 AI / 文档中常见的 Markdown 语法 */
export function looksLikeMarkdown(text: string) {
  const t = normalizePasteText(text).trim()
  if (!t) return false

  const patterns = [
    /^#{1,6}\s+\S/m,
    /^[-*+]\s+\S/m,
    /^\d+\.\s+\S/m,
    /^>\s+\S/m,
    /^```[\s\S]*?```/m,
    /\*\*[^*\n]+?\*\*/,
    /__[^_\n]+?__/,
    /(?<![*\\])\*[^*\n]+?\*(?!\*)/,
    /`[^`\n]+?`/,
    /\[.+?\]\([^)]+\)/,
    /^---+$/m,
    /^\*\*\*+$/m,
    /^\|.+\|/m,
    /^#{1,6}[^#\s]/m,
  ]

  return patterns.some((pattern) => pattern.test(t))
}

export function isRiskyPasteHtml(html: string) {
  return /<(meta|link|style|script|svg|head|html|body|object|iframe)[\s>/]/i.test(html)
}

/** 聊天窗口复制时 HTML 往往只有 p/div，结构在 plain 文本里 */
export function isSimplifiedChatHtml(html: string) {
  if (!html.trim()) return false

  const doc = new DOMParser().parseFromString(html, 'text/html')
  const elements = Array.from(doc.body.querySelectorAll('*'))
  if (elements.length === 0) return false

  return elements.every((el) => SIMPLE_HTML_TAGS.has(el.tagName))
}

export function hasRichHtmlStructure(html: string) {
  return /<(h[1-6]|ul|ol|li|table|pre|blockquote|code|hr|img|a)\b/i.test(html)
}

export function shouldPreferMarkdownPaste(text: string, rawHtml: string) {
  const normalized = normalizePasteText(text)
  if (!normalized.trim()) return false

  if (looksLikeMarkdown(normalized)) return true

  if (rawHtml && isSimplifiedChatHtml(rawHtml)) return true

  // 多行纯文本 + 无富文本 HTML：按 Markdown 解析（AI 回复常见）
  if (normalized.includes('\n') && rawHtml && !hasRichHtmlStructure(rawHtml)) {
    return true
  }

  return false
}

export function plainTextToHtml(text: string) {
  const normalized = normalizePasteText(text)
  const blocks = normalized.split(/\n{2,}/)
  if (blocks.length <= 1 && !normalized.includes('\n')) {
    return `<p>${escapeHtml(normalized)}</p>`
  }
  return blocks
    .map((block) => {
      const trimmed = block.trim()
      if (!trimmed) return ''
      return `<p>${escapeHtml(trimmed).replace(/\n/g, '<br>')}</p>`
    })
    .filter(Boolean)
    .join('')
}

/** 将 marked 输出调整为 wangEditor 更易识别的结构 */
function postProcessMarkedHtml(html: string) {
  const doc = new DOMParser().parseFromString(html, 'text/html')

  doc.querySelectorAll('pre code').forEach((codeEl) => {
    const pre = codeEl.parentElement
    if (!pre || pre.tagName !== 'PRE') return
    pre.removeAttribute('class')
    codeEl.removeAttribute('class')
    codeEl.removeAttribute('data-language')
  })

  doc.querySelectorAll('a').forEach((a) => {
    a.setAttribute('target', '_blank')
    a.setAttribute('rel', 'noopener noreferrer')
  })

  doc.querySelectorAll('table').forEach((table) => {
    table.removeAttribute('class')
  })

  return doc.body.innerHTML
}

export function markdownToHtml(text: string) {
  const normalized = normalizePasteText(text)
  const html = marked.parse(normalized, { async: false }) as string
  return sanitizeHtmlForEditor(postProcessMarkedHtml(html))
}

/** 移除 wangEditor 无法解析的标签，避免 parseElemHtml 报错 */
export function sanitizeHtmlForEditor(html: string) {
  const doc = new DOMParser().parseFromString(html, 'text/html')
  doc.querySelectorAll('meta, link, style, script, svg, head, object, iframe, noscript').forEach((el) => {
    el.remove()
  })

  const walk = (node: Node) => {
    const children = Array.from(node.childNodes)
    for (const child of children) {
      if (child.nodeType === Node.COMMENT_NODE) {
        child.remove()
        continue
      }
      if (child.nodeType === Node.TEXT_NODE) {
        continue
      }
      if (child.nodeType !== Node.ELEMENT_NODE) {
        child.remove()
        continue
      }

      const el = child as HTMLElement
      const tag = el.tagName
      if (!tag || !ALLOWED_TAGS.has(tag)) {
        const parent = el.parentNode
        if (parent) {
          while (el.firstChild) {
            parent.insertBefore(el.firstChild, el)
          }
          parent.removeChild(el)
          walk(parent)
        }
        continue
      }
      walk(el)
    }
  }

  walk(doc.body)
  const result = doc.body.innerHTML.trim()
  return result || '<p></p>'
}

export function handleEditorPaste(editor: IDomEditor, event: ClipboardEvent) {
  const text = event.clipboardData?.getData('text/plain') ?? ''
  const rawHtml = event.clipboardData?.getData('text/html') ?? ''
  const normalizedText = normalizePasteText(text)

  if (!normalizedText.trim() && !rawHtml.trim()) {
    return true
  }

  try {
    event.preventDefault()

    // 已带完整富文本结构（如网页复制）时优先 HTML
    if (rawHtml && !isRiskyPasteHtml(rawHtml) && hasRichHtmlStructure(rawHtml) && !looksLikeMarkdown(normalizedText)) {
      editor.dangerouslyInsertHtml(sanitizeHtmlForEditor(rawHtml))
      return false
    }

    // AI / Markdown 源文本优先
    if (shouldPreferMarkdownPaste(normalizedText, rawHtml)) {
      editor.dangerouslyInsertHtml(markdownToHtml(normalizedText))
      return false
    }

    if (rawHtml && !isRiskyPasteHtml(rawHtml)) {
      editor.dangerouslyInsertHtml(sanitizeHtmlForEditor(rawHtml))
      return false
    }

    if (normalizedText.trim()) {
      editor.dangerouslyInsertHtml(plainTextToHtml(normalizedText))
      return false
    }

    if (rawHtml) {
      editor.dangerouslyInsertHtml(sanitizeHtmlForEditor(rawHtml))
      return false
    }
  } catch {
    if (normalizedText.trim()) {
      try {
        editor.dangerouslyInsertHtml(markdownToHtml(normalizedText))
      } catch {
        editor.insertText(normalizedText)
      }
    }
    return false
  }

  return true
}
