import { useCallback, useEffect, useState } from 'react'
import { Save } from 'lucide-react'
import { toast } from 'sonner'
import { getAuthHeaders, getSiteConfService, updateSiteConfService } from '@/api/service'
import { FileUpload } from '@/components/FileUpload'
import { Loading } from '@/components/Loading'
import { Button } from '@/components/ui/button'
import { PageShell } from '@/components/PageShell'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Switch } from '@/components/ui/switch'
import { Textarea } from '@/components/ui/textarea'
import { getMediaUrl } from '@/lib/utils'
import type { SiteConf } from '@/types'

const emptyConf: SiteConf = {
  domain: '',
  site_name: '',
  title: '',
  kws: '',
  desc: '',
  logo_url: '',
  defaul_pic_url: '',
  favicon_url: '',
  theme_dir: 'default',
  tongji_code: '',
  baidu_tsapi: '',
  icp: '',
  https: 'Y',
}

export function SiteConfPage() {
  const domain = sessionStorage.getItem('domain') || ''
  const [loading, setLoading] = useState(false)
  const [notConfigured, setNotConfigured] = useState(false)
  const [form, setForm] = useState<SiteConf>({ ...emptyConf, domain })

  const loadConf = useCallback(async () => {
    setLoading(true)
    try {
      const res = await getSiteConfService({})
      if (res.code === 0) {
        if (res.data) {
          setNotConfigured(false)
          const data = res.data as SiteConf
          setForm({
            ...emptyConf,
            ...data,
            domain: data.domain || domain,
            https: data.https === 'N' || data.https === false ? 'N' : 'Y',
          })
        } else {
          setNotConfigured(true)
          setForm({ ...emptyConf, domain })
        }
      } else {
        toast.error(res.message || '加载网站配置失败')
      }
    } catch (e) {
      toast.error(`加载网站配置失败：${String(e)}`)
    } finally {
      setLoading(false)
    }
  }, [domain])

  useEffect(() => {
    loadConf()
  }, [loadConf])

  const handleSave = async () => {
    setLoading(true)
    try {
      const res = await updateSiteConfService({
        domain: form.domain || domain,
        site_name: form.site_name || '',
        title: form.title || '',
        kws: form.kws || '',
        desc: form.desc || '',
        logo_url: form.logo_url || '',
        defaul_pic_url: form.defaul_pic_url || '',
        favicon_url: form.favicon_url || '',
        theme_dir: form.theme_dir || 'default',
        tongji_code: form.tongji_code || '',
        baidu_tsapi: form.baidu_tsapi || '',
        icp: form.icp || '',
        https: form.https === 'N' ? 'N' : 'Y',
      })
      if (res.code === 0 && res.ret) {
        toast.success('保存成功')
        await loadConf()
      } else {
        toast.error(res.message || '保存失败')
      }
    } catch (e) {
      toast.error(`保存失败：${String(e)}`)
    } finally {
      setLoading(false)
    }
  }

  const updateField = <K extends keyof SiteConf>(key: K, value: SiteConf[K]) => {
    setForm((prev) => ({ ...prev, [key]: value }))
  }

  const mediaDomain = form.domain || domain

  return (
    <>
      <Loading loading={loading} />

      <PageShell
        title="网站配置"
        description={
          notConfigured ? (
            <span className="inline-flex items-center gap-2 text-amber-700">
              <span className="h-1.5 w-1.5 shrink-0 rounded-full bg-amber-500" />
              站点尚未配置，请填写下方信息并保存
            </span>
          ) : (
            '站点 SEO、品牌资源与全局参数'
          )
        }
        actions={
          <Button onClick={handleSave}>
            <Save className="h-4 w-4" />
            保存配置
          </Button>
        }
      >
        <div className="content-panel space-y-8 p-6">
          <div className="space-y-4">
            <h4 className="text-sm font-medium text-muted-foreground">站点与 SEO</h4>
            <div className="grid gap-4 md:grid-cols-2">
              <div className="dialog-form-row">
                <Label>域名</Label>
                <Input value={form.domain || domain} disabled />
              </div>
              <div className="dialog-form-row">
                <Label>启用 HTTPS</Label>
                <div className="flex items-center gap-3">
                  <Switch
                    checked={form.https !== 'N'}
                    onCheckedChange={(checked) => updateField('https', checked ? 'Y' : 'N')}
                  />
                  <span className="text-sm text-muted-foreground">{form.https !== 'N' ? '已启用' : '未启用'}</span>
                </div>
              </div>
            </div>
            <div className="grid gap-4 md:grid-cols-2">
              <div className="dialog-form-row">
                <Label>站点名称</Label>
                <Input
                  value={form.site_name || ''}
                  onChange={(e) => updateField('site_name', e.target.value)}
                  placeholder="请输入站点名称"
                />
              </div>
              <div className="dialog-form-row">
                <Label>站点标题</Label>
                <Input
                  value={form.title || ''}
                  onChange={(e) => updateField('title', e.target.value)}
                  placeholder="请输入站点标题"
                />
              </div>
              <div className="dialog-form-row">
                <Label>关键词</Label>
                <Input
                  value={form.kws || ''}
                  onChange={(e) => updateField('kws', e.target.value)}
                  placeholder="请输入关键词，多个用逗号分隔"
                />
              </div>
              <div className="dialog-form-row">
                <Label>主题目录</Label>
                <Input
                  value={form.theme_dir || ''}
                  onChange={(e) => updateField('theme_dir', e.target.value)}
                  placeholder="default"
                />
              </div>
            </div>
            <div className="dialog-form-row-top">
              <Label>站点描述</Label>
              <Textarea
                value={form.desc || ''}
                onChange={(e) => updateField('desc', e.target.value)}
                placeholder="请输入站点描述"
                rows={3}
              />
            </div>
          </div>

          <div className="space-y-4">
            <h4 className="text-sm font-medium text-muted-foreground">品牌资源</h4>
            <div className="grid gap-6 md:grid-cols-3">
              <div className="dialog-form-row-top">
                <Label>站点 Logo</Label>
                <div className="flex min-w-0 flex-col gap-2">
                  {form.logo_url && (
                    <img
                      src={getMediaUrl(mediaDomain, form.logo_url)}
                      alt="Logo"
                      className="h-16 max-w-full rounded border object-contain"
                    />
                  )}
                  <FileUpload
                    action="/api/upload_site_logo_pic/"
                    headers={getAuthHeaders()}
                    label="上传 Logo"
                    onSuccess={(url) => updateField('logo_url', url)}
                  />
                </div>
              </div>
              <div className="dialog-form-row-top">
                <Label>默认图片</Label>
                <div className="flex min-w-0 flex-col gap-2">
                  {form.defaul_pic_url && (
                    <img
                      src={getMediaUrl(mediaDomain, form.defaul_pic_url)}
                      alt="默认图片"
                      className="h-16 max-w-full rounded border object-contain"
                    />
                  )}
                  <FileUpload
                    action="/api/upload_defaul_pic/"
                    headers={getAuthHeaders()}
                    label="上传默认图"
                    onSuccess={(url) => updateField('defaul_pic_url', url)}
                  />
                </div>
              </div>
              <div className="dialog-form-row-top">
                <Label>Favicon</Label>
                <div className="flex min-w-0 flex-col gap-2">
                  {form.favicon_url && (
                    <img
                      src={getMediaUrl(mediaDomain, form.favicon_url)}
                      alt="Favicon"
                      className="h-16 w-16 rounded border object-contain"
                    />
                  )}
                  <FileUpload
                    action="/api/upload_site_logo_pic/"
                    headers={getAuthHeaders()}
                    label="上传 Favicon"
                    onSuccess={(url) => updateField('favicon_url', url)}
                  />
                </div>
              </div>
            </div>
          </div>

          <div className="space-y-4">
            <h4 className="text-sm font-medium text-muted-foreground">统计与推送</h4>
            <div className="dialog-form-row">
              <Label>百度推送 API</Label>
              <Input
                value={form.baidu_tsapi || ''}
                onChange={(e) => updateField('baidu_tsapi', e.target.value)}
                placeholder="请输入百度推送 API 地址"
              />
            </div>
            <div className="dialog-form-row">
              <Label>ICP 备案号</Label>
              <Input
                value={form.icp || ''}
                onChange={(e) => updateField('icp', e.target.value)}
                placeholder="请输入 ICP 备案号"
              />
            </div>
            <div className="dialog-form-row-top">
              <Label>统计代码</Label>
              <Textarea
                value={form.tongji_code || ''}
                onChange={(e) => updateField('tongji_code', e.target.value)}
                placeholder="请输入第三方统计代码"
                rows={5}
                className="font-mono text-xs placeholder:font-sans placeholder:text-base md:placeholder:text-sm"
              />
            </div>
          </div>
        </div>
      </PageShell>
    </>
  )
}
