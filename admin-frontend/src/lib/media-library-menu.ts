import type { IButtonMenu, IDomEditor } from '@wangeditor-next/editor'

/** 编辑器自定义事件：打开媒体库选择器 */
export const MEDIA_LIBRARY_EVENT = 'xxgcms-open-media-library'

export const MEDIA_LIBRARY_MENU_KEY = 'xxgcmsMediaLibrary'

/**
 * 占位即可：真实图标由 attachMediaLibraryToolbarIcon 注入侧栏同款 React 组件。
 */
const PLACEHOLDER_SVG = `<svg viewBox="0 0 18 18" width="18" height="18" aria-hidden="true"></svg>`

class MediaLibraryMenu implements IButtonMenu {
  title = '媒体库'
  iconSvg = PLACEHOLDER_SVG
  tag = 'button'

  getValue(): string | boolean {
    return ''
  }

  isActive(): boolean {
    return false
  }

  isDisabled(editor: IDomEditor): boolean {
    return editor.isDisabled()
  }

  exec(editor: IDomEditor) {
    editor.emit(MEDIA_LIBRARY_EVENT)
  }
}

export const mediaLibraryMenuConf = {
  key: MEDIA_LIBRARY_MENU_KEY,
  factory() {
    return new MediaLibraryMenu()
  },
}
