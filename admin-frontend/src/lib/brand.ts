/** 管理后台品牌资源（位于 static/img，由 Vite publicDir 提供） */
const base = import.meta.env.BASE_URL

export const BRAND_LOGO_URL = `${base}img/watermelon.svg`
export const BRAND_FAVICON_URL = `${base}img/watermelon.svg`
export const BRAND_NAME = '小西瓜CMS'
export const BRAND_COPYRIGHT = 'XXG.ai'
export const APP_VERSION = import.meta.env.VITE_APP_VERSION || '0.0.0'
