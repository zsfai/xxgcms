import { Boot } from '@wangeditor-next/editor'
import markdownModule from '@wangeditor-next/plugin-markdown'
import { mediaLibraryMenuConf } from '@/lib/media-library-menu'

let registered = false

/** 注册 wangEditor 扩展模块，全局仅执行一次 */
export function registerWangEditorModules() {
  if (registered) return
  Boot.registerModule(markdownModule)
  Boot.registerMenu(mediaLibraryMenuConf)
  registered = true
}

registerWangEditorModules()
