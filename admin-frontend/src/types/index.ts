export interface ApiResponse<T = unknown> {
  code: number
  ret?: boolean
  message?: string
  data?: T
  datas?: T
  total_count?: number
  token?: string
  add_kw_count?: number
}

export interface SiteItem {
  id: number
  name: string
  root_path?: string
  sort_num?: number
  desc?: string
  pic_url?: string
  db_host?: string
  db_port?: number
  db_name?: string
  db_user?: string
  db_pwd?: string
  db_x_host?: string
  db_x_port?: number
  db_x_name?: string
  db_x_user?: string
  db_x_pwd?: string
  add_time?: string
  update_time?: string
  domain_aliases?: string
  ssl_enabled?: string
  force_https?: string
  cert_status?: string
  cert_not_after?: string
  nginx_status?: string
  nginx_error?: string
}

export interface SiteSslInfo {
  site_id?: number
  name?: string
  domain_aliases?: string
  ssl_enabled?: string
  force_https?: string
  cert_status?: string
  cert_not_after?: string
  nginx_status?: string
  nginx_error?: string
  has_cert_files?: boolean
  fullchain_pem?: string
  privkey_pem?: string
}

export interface KeywordItem {
  id: number
  kw: string
  r_kws?: string
  del_flag?: string
  create_time?: string
  update_time?: string
}

export interface CateItem {
  id: number
  name: string
  name_en?: string
  p_id?: number | null
  visiable?: string
  home_visiable?: string
  pic_url?: string
  sort_num?: number
  seo_title?: string
  kws?: string
  desc?: string
  content?: string
  add_time?: string
  children?: CateItem[]
}

export interface ArticleItem {
  id: number
  source_id: number
  title: string
  slug_url?: string
  cate_id?: number
  cate_name?: string
  p_cate_name_en?: string
  cate_name_en?: string
  source_cate_name?: string
  kws?: string
  pub_status?: string
  view_num?: number
  add_time?: string
  pub_time?: string
  del_flag?: string
  show_type?: number
  ai_generated?: string
}

export interface ArticleDetail {
  info: {
    id: number
    title: string
    slug_url?: string
    cate_id?: number
    show_type?: number
    content?: string
    desc?: string
    pic_url?: string
  }
  kws?: string[]
}

export interface CarouselItem {
  id: number
  title: string
  click_url: string
  pic_url: string
  sort_num: number
  status?: string | number
  desc?: string
  create_time?: string
  click_num?: number
}

export interface LinkItem {
  id: number
  name: string
  click_url: string
  pic_url: string
  sort_num: number
  status?: string | number
  desc?: string
  add_time?: string
}

export interface SiteConf {
  domain: string
  https?: string | boolean
  site_name?: string
  title?: string
  kws?: string
  desc?: string
  logo_url?: string
  defaul_pic_url?: string
  favicon_url?: string
  theme_dir?: string
  tongji_code?: string
  baidu_tsapi?: string
  icp?: string
}
