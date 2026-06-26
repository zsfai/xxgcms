import axios from 'axios'
import { useAppStore } from '@/stores/app-store'
import type { ApiResponse } from '@/types'

axios.defaults.timeout = 60000
axios.defaults.headers.post['Content-Type'] = 'application/json;charset=UTF-8'

axios.interceptors.request.use((config) => {
  config.headers['auth-key'] = sessionStorage.getItem('token') || ''
  return config
})

axios.interceptors.response.use((res) => {
  const data = res.data as ApiResponse
  if (data.code === 403) {
    useAppStore.getState().showLoginForm()
  }
  return data as unknown as typeof res
})

const xData = <T extends Record<string, unknown>>(data: T): T & { domain: string } => ({
  ...data,
  domain: sessionStorage.getItem('domain') || '',
})

export const refreshSysService = (data: Record<string, unknown> = {}) =>
  axios.post('/api/refesh_site_conf/', data) as Promise<ApiResponse>

export const loginService = (data: { name: string; pwd: string }) =>
  axios.post('/api/login/', data) as Promise<ApiResponse<{ token: string }>>

export const changePasswordService = (data: { old_pwd: string; new_pwd: string }) =>
  axios.post('/api/change_password/', data) as Promise<ApiResponse>

export const getKwListService = (data: Record<string, unknown>) =>
  axios.post('/api/get_kw_list/', xData(data)) as Promise<ApiResponse>

export const delKwService = (data: Record<string, unknown>) =>
  axios.post('/api/del_kw/', xData(data)) as Promise<ApiResponse>

export const addKwService = (data: Record<string, unknown>) =>
  axios.post('/api/add_kw/', xData(data)) as Promise<ApiResponse>

export const updateKwService = (data: Record<string, unknown>) =>
  axios.post('/api/update_kw/', xData(data)) as Promise<ApiResponse>

export const searchKwService = (data: Record<string, unknown>) =>
  axios.post('/api/search_kw/', xData(data)) as Promise<ApiResponse>

export const getArticleListService = (data: Record<string, unknown>) =>
  axios.post('/api/get_article_list/', xData(data)) as Promise<ApiResponse>

export const getArticleCateListService = (data: Record<string, unknown> = {}) =>
  axios.post('/api/get_article_cate_list/', xData(data)) as Promise<ApiResponse>

export const syncLatestArticlesService = (data: Record<string, unknown>) =>
  axios.post('/api/sync_latest_articles/', xData(data)) as Promise<ApiResponse>

export const delArticleItemService = (data: Record<string, unknown>) =>
  axios.post('/api/del_article_item/', xData(data)) as Promise<ApiResponse>

export const renewArticleItemService = (data: Record<string, unknown>) =>
  axios.post('/api/renew_article_item/', xData(data)) as Promise<ApiResponse>

export const purgeArticleItemService = (data: Record<string, unknown>) =>
  axios.post('/api/purge_article_item/', xData(data)) as Promise<ApiResponse>

export const matchArticleKwsService = (data: Record<string, unknown>) =>
  axios.post('/api/match_article_kws/', xData(data)) as Promise<ApiResponse>

export const matchKwKwsService = (data: Record<string, unknown>) =>
  axios.post('/api/match_kw_kws/', xData(data)) as Promise<ApiResponse>

export const matchSomeKwKwsService = (data: Record<string, unknown>) =>
  axios.post('/api/match_some_kw_kws/', xData(data)) as Promise<ApiResponse>

export const updateArticleCateService = (data: Record<string, unknown>) =>
  axios.post('/api/update_article_cate/', xData(data)) as Promise<ApiResponse>

export const updateArticlePrePubService = (data: Record<string, unknown>) =>
  axios.post('/api/update_article_pre_pub/', xData(data)) as Promise<ApiResponse>

export const syncArticleInfoService = (data: Record<string, unknown>) =>
  axios.post('/api/sync_article_info/', xData(data)) as Promise<ApiResponse>

export const matchSomeArticleKwsService = (data: Record<string, unknown>) =>
  axios.post('/api/match_some_article_kws/', xData(data)) as Promise<ApiResponse>

export const makeThumbPicService = (data: Record<string, unknown> = {}) =>
  axios.post('/api/make_thumb_pic/', xData(data)) as Promise<ApiResponse>

export const searchArticleService = (data: Record<string, unknown>) =>
  axios.post('/api/search_article/', xData(data)) as Promise<ApiResponse>

export const getArticleDetailService = (data: Record<string, unknown>) =>
  axios.post('/api/get_article_detail/', xData(data)) as Promise<ApiResponse>

export const updateArticleService = (data: Record<string, unknown>) =>
  axios.post('/api/add_or_update_article/', xData(data)) as Promise<ApiResponse>

export const getCateListService = (data: Record<string, unknown>) =>
  axios.post('/api/get_cate_list/', xData(data)) as Promise<ApiResponse>

export const addCateService = (data: Record<string, unknown>) =>
  axios.post('/api/add_cate/', xData(data)) as Promise<ApiResponse>

export const updateCateService = (data: Record<string, unknown>) =>
  axios.post('/api/update_cate/', xData(data)) as Promise<ApiResponse>

export const updateCateContentService = (data: Record<string, unknown>) =>
  axios.post('/api/update_cate_content/', xData(data)) as Promise<ApiResponse>

export const delCateService = (data: Record<string, unknown>) =>
  axios.post('/api/del_cate/', xData(data)) as Promise<ApiResponse>

export const getSitePageListService = (data: Record<string, unknown>) =>
  axios.post('/api/get_site_page_list/', data) as Promise<ApiResponse>

export const getSiteListService = (data: Record<string, unknown> = {}) =>
  axios.post('/api/get_site_list/', data) as Promise<ApiResponse>

export const addSiteService = (data: Record<string, unknown>) =>
  axios.post('/api/add_site/', data) as Promise<ApiResponse>

export const testSiteDbService = (data: Record<string, unknown>) =>
  axios.post('/api/test_site_db/', data) as Promise<
    ApiResponse<{
      connected: boolean
      database: string
      database_exists: boolean
      has_cms_tables: boolean
      table_count: number
    }>
  >

export const updateSiteService = (data: Record<string, unknown>) =>
  axios.post('/api/update_site/', data) as Promise<ApiResponse>

export const delSiteService = (data: Record<string, unknown>) =>
  axios.post('/api/del_site/', data) as Promise<ApiResponse>

export const getSiteSslService = (data: { site_id: number }) =>
  axios.post('/api/get_site_ssl/', data) as Promise<ApiResponse>

export const testSiteSslService = (data: Record<string, unknown>) =>
  axios.post('/api/test_site_ssl/', data) as Promise<ApiResponse>

export const updateSiteSslService = (data: Record<string, unknown>) =>
  axios.post('/api/update_site_ssl/', data) as Promise<ApiResponse>

export const syncNginxService = (data: Record<string, unknown> = {}) =>
  axios.post('/api/sync_nginx/', data) as Promise<ApiResponse>

export const getCarouselListService = (data: Record<string, unknown>) =>
  axios.post('/api/get_carousel_list/', xData(data)) as Promise<ApiResponse>

export const addCarouselService = (data: Record<string, unknown>) =>
  axios.post('/api/add_carousel/', xData(data)) as Promise<ApiResponse>

export const uploadCarouselPicService = (data: Record<string, unknown>) =>
  axios.post('/api/upload_carousel_pic/', xData(data)) as Promise<ApiResponse>

export const updateCarouselService = (data: Record<string, unknown>) =>
  axios.post('/api/update_carousel/', xData(data)) as Promise<ApiResponse>

export const delCarouselService = (data: Record<string, unknown>) =>
  axios.post('/api/del_carousel/', xData(data)) as Promise<ApiResponse>

export const viewCarouselsService = (data: Record<string, unknown>) =>
  axios.post('/api/view_carousels/', xData(data)) as Promise<ApiResponse>

export const getLinkListService = (data: Record<string, unknown>) =>
  axios.post('/api/get_link_list/', xData(data)) as Promise<ApiResponse>

export const addLinkService = (data: Record<string, unknown>) =>
  axios.post('/api/add_link/', xData(data)) as Promise<ApiResponse>

export const uploadLinkPicService = (data: Record<string, unknown>) =>
  axios.post('/api/upload_link_pic/', xData(data)) as Promise<ApiResponse>

export const updateLinkService = (data: Record<string, unknown>) =>
  axios.post('/api/update_link/', xData(data)) as Promise<ApiResponse>

export const delLinkService = (data: Record<string, unknown>) =>
  axios.post('/api/del_link/', xData(data)) as Promise<ApiResponse>

export const getSiteConfService = (data: Record<string, unknown> = {}) =>
  axios.post('/api/get_site_conf/', xData(data)) as Promise<ApiResponse>

export const updateSiteConfService = (data: Record<string, unknown>) =>
  axios.post('/api/update_site_conf/', xData(data)) as Promise<ApiResponse>

export const generateArticleSlugUrlService = (data: Record<string, unknown>) =>
  axios.post('/api/generate_article_slug_url/', xData(data)) as Promise<ApiResponse>

export const topicSuggestService = (data: Record<string, unknown>) =>
  axios.post('/api/ai/topic_suggest/', xData(data)) as Promise<ApiResponse>

export const topicUpdateService = (data: Record<string, unknown>) =>
  axios.post('/api/ai/topic_update/', xData(data)) as Promise<ApiResponse>

export const topicConfirmGenerateService = (data: Record<string, unknown>) =>
  axios.post('/api/ai/topic_confirm_generate/', xData(data)) as Promise<ApiResponse>

export const getTopicSessionService = (data: Record<string, unknown>) =>
  axios.post('/api/ai/topic_session/', xData(data)) as Promise<ApiResponse>

export const getTopicSessionsService = (data: Record<string, unknown> = {}) =>
  axios.post('/api/ai/topic_sessions/', xData(data)) as Promise<ApiResponse>

export const getAiVerticalsService = () =>
  axios.post('/api/ai/verticals/', xData({})) as Promise<ApiResponse>

export const getAiVerticalsAdminService = () =>
  axios.post('/api/ai/verticals_admin/', xData({})) as Promise<ApiResponse>

export const createAiVerticalService = (data: Record<string, unknown>) =>
  axios.post('/api/ai/create_vertical/', xData(data)) as Promise<ApiResponse>

export const updateAiVerticalService = (data: Record<string, unknown>) =>
  axios.post('/api/ai/update_vertical/', xData(data)) as Promise<ApiResponse>

export const deleteAiVerticalService = (data: Record<string, unknown>) =>
  axios.post('/api/ai/delete_vertical/', xData(data)) as Promise<ApiResponse>

export const getAiTemplatesService = () =>
  axios.post('/api/ai/templates/', xData({})) as Promise<ApiResponse>

export const getAiTemplatesAdminService = () =>
  axios.post('/api/ai/templates_admin/', xData({})) as Promise<ApiResponse>

export const createAiTemplateService = (data: Record<string, unknown>) =>
  axios.post('/api/ai/create_template/', xData(data)) as Promise<ApiResponse>

export const updateAiTemplateService = (data: Record<string, unknown>) =>
  axios.post('/api/ai/update_template/', xData(data)) as Promise<ApiResponse>

export const deleteAiTemplateService = (data: Record<string, unknown>) =>
  axios.post('/api/ai/delete_template/', xData(data)) as Promise<ApiResponse>

export const generateArticleAiService = (data: Record<string, unknown>) =>
  axios.post('/api/ai/generate_article/', xData(data)) as Promise<ApiResponse>

export const batchGenerateAiService = (data: Record<string, unknown>) =>
  axios.post('/api/ai/batch_generate/', xData(data)) as Promise<ApiResponse>

export const getAiBatchJobService = (data: Record<string, unknown>) =>
  axios.post('/api/ai/batch_job/', xData(data)) as Promise<ApiResponse>

export const regenerateArticleBodyService = (data: Record<string, unknown>) =>
  axios.post('/api/ai/regenerate_body/', xData(data)) as Promise<ApiResponse>

export const getAiModelsService = () =>
  axios.post('/api/ai/models/', xData({})) as Promise<ApiResponse>

export const getAiProvidersService = () =>
  axios.post('/api/ai/providers/', xData({})) as Promise<ApiResponse>

export const getAiConfigSettingsService = () =>
  axios.post('/api/ai/config_settings/', xData({})) as Promise<ApiResponse>

export const updateAiProviderConfigService = (data: Record<string, unknown>) =>
  axios.post('/api/ai/update_provider_config/', xData(data)) as Promise<ApiResponse>

export const updateAiModelConfigService = (data: Record<string, unknown>) =>
  axios.post('/api/ai/update_model_config/', xData(data)) as Promise<ApiResponse>

export const createAiModelConfigService = (data: Record<string, unknown>) =>
  axios.post('/api/ai/create_model_config/', xData(data)) as Promise<ApiResponse>

export const updateAiDefaultProvidersService = (data: Record<string, unknown>) =>
  axios.post('/api/ai/update_default_providers/', xData(data)) as Promise<ApiResponse>

export function getAuthHeaders() {
  return {
    'auth-key': sessionStorage.getItem('token') || '',
    domain: sessionStorage.getItem('domain') || '',
  }
}
