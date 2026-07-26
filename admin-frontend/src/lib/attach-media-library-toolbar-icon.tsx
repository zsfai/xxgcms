import { createRoot, type Root } from 'react-dom/client'
import { MediaLibraryIcon } from '@/components/MediaLibraryIcon'
import { MEDIA_LIBRARY_MENU_KEY } from '@/lib/media-library-menu'

/** wangEditor 工具栏默认图标尺寸 */
const TOOLBAR_ICON_CLASS = 'h-[15px] w-[15px]'

/**
 * 把侧栏同款 MediaLibraryIcon 挂到 wangEditor 工具栏按钮上。
 * 不依赖 iconSvg（会被编辑器 CSS fill 破坏）。
 */
export function attachMediaLibraryToolbarIcon(scope: HTMLElement): () => void {
  let root: Root | null = null
  let host: HTMLElement | null = null
  let attachedBtn: HTMLButtonElement | null = null

  const sync = () => {
    const btn = scope.querySelector(
      `button[data-menu-key="${MEDIA_LIBRARY_MENU_KEY}"]`,
    ) as HTMLButtonElement | null
    if (!btn) return

    // 去掉 wangEditor 注入的 svg，避免盖住我们的图标
    btn.querySelectorAll(':scope > svg').forEach((el) => el.remove())

    if (!host || !host.isConnected || attachedBtn !== btn) {
      root?.unmount()
      root = null
      host = document.createElement('span')
      host.setAttribute('data-media-lib-icon', '1')
      host.className = 'xxgcms-media-lib-icon'
      btn.insertBefore(host, btn.firstChild)
      attachedBtn = btn
      root = createRoot(host)
      root.render(<MediaLibraryIcon className={TOOLBAR_ICON_CLASS} />)
      return
    }

    if (!host.querySelector('svg')) {
      root?.render(<MediaLibraryIcon className={TOOLBAR_ICON_CLASS} />)
    }
  }

  sync()
  const timer = window.setTimeout(sync, 80)
  const timer2 = window.setTimeout(sync, 300)

  const observer = new MutationObserver(() => {
    const btn = scope.querySelector(
      `button[data-menu-key="${MEDIA_LIBRARY_MENU_KEY}"]`,
    ) as HTMLButtonElement | null
    if (!btn) return
    // 仅在编辑器又塞回 svg、或我们的挂载点丢失时重建
    if (btn.querySelector(':scope > svg') || !btn.querySelector('[data-media-lib-icon] svg')) {
      sync()
    }
  })
  observer.observe(scope, { childList: true, subtree: true })

  return () => {
    window.clearTimeout(timer)
    window.clearTimeout(timer2)
    observer.disconnect()
    root?.unmount()
    root = null
    host = null
    attachedBtn = null
  }
}
