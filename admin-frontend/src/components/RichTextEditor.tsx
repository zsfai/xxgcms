import '@/lib/wangeditor-boot'
import '@wangeditor-next/editor/dist/css/style.css'
import { useEffect, useState } from 'react'
import { IDomEditor, IEditorConfig, IToolbarConfig } from '@wangeditor-next/editor'
import { Editor, Toolbar } from '@wangeditor-next/editor-for-react'
import { toast } from 'sonner'
import { cn, resolveSiteMediaUrl } from '@/lib/utils'
import { handleEditorPaste } from '@/lib/editor-paste'

interface RichTextEditorProps {
  value?: string
  onChange?: (value: string) => void
  uploadImageUrl?: string
  uploadImageHeaders?: Record<string, string>
  /** 站点 root_path，用于补全 upload/files 图片地址；默认读 sessionStorage.root_path */
  mediaRootPath?: string
  className?: string
  height?: string
  borderless?: boolean
  onFullScreenChange?: (fullScreen: boolean) => void
}

export function RichTextEditor({
  value = '',
  onChange,
  uploadImageUrl = '/api/upload_file/',
  uploadImageHeaders = {},
  mediaRootPath,
  className,
  height = '500px',
  borderless = false,
  onFullScreenChange,
}: RichTextEditorProps) {
  const [editor, setEditor] = useState<IDomEditor | null>(null)
  const [html, setHtml] = useState(value)

  useEffect(() => {
    if (!editor || editor.isDestroyed) return

    const onFullScreen = () => onFullScreenChange?.(true)
    const onUnFullScreen = () => onFullScreenChange?.(false)

    editor.on('fullscreen', onFullScreen)
    editor.on('unFullScreen', onUnFullScreen)

    return () => {
      editor.off('fullscreen', onFullScreen)
      editor.off('unFullScreen', onUnFullScreen)
      if (editor.isFullScreen) {
        onFullScreenChange?.(false)
      }
    }
  }, [editor, onFullScreenChange])

  useEffect(() => {
    if (value !== html) {
      setHtml(value)
      if (editor && !editor.isDestroyed) {
        editor.setHtml(value || '')
      }
    }
  }, [value, editor, html])

  useEffect(() => {
    return () => {
      if (editor && !editor.isDestroyed) {
        editor.destroy()
      }
    }
  }, [editor])

  const toolbarConfig: Partial<IToolbarConfig> = {
    excludeKeys: ['fontSize', 'fontFamily', 'lineHeight'],
  }

  const editorConfig: Partial<IEditorConfig> = {
    placeholder: '请输入内容...',
    customPaste: (ed, event) => handleEditorPaste(ed, event),
    MENU_CONF: {
      uploadImage: {
        server: uploadImageUrl,
        fieldName: 'file',
        maxFileSize: 5 * 1024 * 1024,
        headers: uploadImageHeaders,
        customInsert(res: { code?: number; data?: string | { url?: string }; url?: string; message?: string }, insertFn: (url: string, alt?: string, href?: string) => void) {
          let path = ''
          if (res?.code === 0 && res.data) {
            path = typeof res.data === 'string' ? res.data : res.data.url || ''
          } else if (res?.url) {
            path = res.url
          }
          if (path) {
            const rootPath = mediaRootPath ?? sessionStorage.getItem('root_path') ?? ''
            const displayUrl = resolveSiteMediaUrl(path, rootPath)
            insertFn(displayUrl, '', displayUrl)
          } else {
            toast.error(res?.message || '图片上传失败')
          }
        },
      },
    },
  }

  return (
    <div className={cn(borderless && 'flex min-h-0 flex-1 flex-col', className)}>
      <div
        className={cn(
          'overflow-hidden rounded-md border',
          borderless && 'rich-text-editor-borderless flex min-h-0 flex-1 flex-col',
        )}
      >
        <Toolbar
          editor={editor}
          defaultConfig={toolbarConfig}
          mode="default"
          style={{ borderBottom: '1px solid hsl(var(--border))' }}
        />
        <Editor
          defaultConfig={editorConfig}
          value={html}
          onCreated={(ed) => {
            setEditor(ed)
          }}
          onChange={(ed) => {
            const next = ed.getHtml()
            setHtml(next)
            onChange?.(next)
          }}
          mode="default"
          className={borderless ? 'rich-text-editor-body min-h-0 flex-1' : undefined}
          style={
            borderless
              ? { flex: 1, minHeight: 0, overflowY: 'auto' }
              : { height, overflowY: 'auto' }
          }
        />
      </div>
    </div>
  )
}
