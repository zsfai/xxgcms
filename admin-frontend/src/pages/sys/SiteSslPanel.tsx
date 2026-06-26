import { useCallback, useEffect, useState } from 'react'
import { toast } from 'sonner'
import { getSiteSslService, testSiteSslService, updateSiteSslService } from '@/api/service'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Switch } from '@/components/ui/switch'
import { Textarea } from '@/components/ui/textarea'
import type { SiteSslInfo } from '@/types'

interface SiteSslPanelProps {
  siteId: number
  siteName: string
}

type StatusConfig = {
  label: string
  dotClass: string
  textClass: string
}

const CERT_STATUS: Record<string, StatusConfig> = {
  none: { label: '未配置', dotClass: 'bg-muted-foreground/50', textClass: 'text-muted-foreground' },
  pending: { label: '待生效', dotClass: 'bg-amber-500', textClass: 'text-amber-700' },
  active: { label: '正常', dotClass: 'bg-emerald-500', textClass: 'text-emerald-700' },
  expired: { label: '已过期', dotClass: 'bg-destructive', textClass: 'text-destructive' },
  error: { label: '异常', dotClass: 'bg-destructive', textClass: 'text-destructive' },
}

const NGINX_STATUS: Record<string, StatusConfig> = {
  none: { label: '未同步', dotClass: 'bg-muted-foreground/50', textClass: 'text-muted-foreground' },
  pending: { label: '同步中', dotClass: 'bg-amber-500', textClass: 'text-amber-700' },
  synced: { label: '已同步', dotClass: 'bg-emerald-500', textClass: 'text-emerald-700' },
  error: { label: '同步失败', dotClass: 'bg-destructive', textClass: 'text-destructive' },
}

function StatusText({ status, map }: { status?: string; map: Record<string, StatusConfig> }) {
  const key = (status || 'none').toLowerCase()
  const cfg = map[key] ?? { label: status || '未知', dotClass: 'bg-muted-foreground/50', textClass: 'text-foreground' }
  return (
    <span className={cn('inline-flex items-center gap-1.5', cfg.textClass)}>
      <span className={cn('size-2 shrink-0 rounded-full', cfg.dotClass)} />
      {cfg.label}
    </span>
  )
}

export function SiteSslPanel({ siteId, siteName }: SiteSslPanelProps) {
  const [loading, setLoading] = useState(false)
  const [info, setInfo] = useState<SiteSslInfo | null>(null)
  const [domainAliases, setDomainAliases] = useState('')
  const [sslEnabled, setSslEnabled] = useState(false)
  const [forceHttps, setForceHttps] = useState(true)
  const [fullchainPem, setFullchainPem] = useState('')
  const [privkeyPem, setPrivkeyPem] = useState('')

  const loadSsl = useCallback(async () => {
    setLoading(true)
    try {
      const res = await getSiteSslService({ site_id: siteId })
      if (res.code === 0 && res.data) {
        const data = res.data as SiteSslInfo
        setInfo(data)
        setDomainAliases(data.domain_aliases || '')
        setSslEnabled(data.ssl_enabled === 'Y')
        setForceHttps(data.force_https !== 'N')
        setFullchainPem(data.fullchain_pem || '')
        setPrivkeyPem(data.privkey_pem || '')
      } else {
        toast.error(res.message || '加载 SSL 配置失败')
      }
    } catch (e) {
      toast.error(`加载 SSL 配置失败：${String(e)}`)
    } finally {
      setLoading(false)
    }
  }, [siteId])

  useEffect(() => {
    void loadSsl()
  }, [loadSsl])

  const buildPayload = () => ({
    site_id: siteId,
    domain_aliases: domainAliases,
    ssl_enabled: sslEnabled ? 'Y' : 'N',
    force_https: forceHttps ? 'Y' : 'N',
    fullchain_pem: fullchainPem,
    privkey_pem: privkeyPem,
  })

  const handleTest = async () => {
    setLoading(true)
    try {
      const res = await testSiteSslService(buildPayload())
      if (res.code === 0) {
        toast.success(res.message || '证书校验通过')
      } else {
        toast.error(res.message || '证书校验失败')
      }
    } catch (e) {
      toast.error(`证书校验失败：${String(e)}`)
    } finally {
      setLoading(false)
    }
  }

  const handleSave = async () => {
    setLoading(true)
    try {
      const res = await updateSiteSslService(buildPayload())
      if (res.code === 0) {
        toast.success(res.message || 'SSL 配置已保存')
        if (res.data) {
          setInfo(res.data as SiteSslInfo)
          const data = res.data as SiteSslInfo
          setFullchainPem(data.fullchain_pem || '')
          setPrivkeyPem(data.privkey_pem || '')
        } else {
          await loadSsl()
        }
      } else {
        toast.error(res.message || '保存失败')
      }
    } catch (e) {
      toast.error(`保存失败：${String(e)}`)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="dialog-form-narrow space-y-4">
      <p className="text-sm text-muted-foreground">
        主域名：<span className="font-medium text-foreground">{siteName}</span>
        。保存后系统将自动生成 Nginx 配置并热加载（约数秒）。请确保 DNS 已指向本服务器，防火墙放行 443。
      </p>

      <div className="dialog-form-row">
        <Label>域名别名</Label>
        <Input
          value={domainAliases}
          onChange={(e) => setDomainAliases(e.target.value)}
          placeholder="逗号分隔，如 www.xxg.ai"
        />
      </div>

      <div className="dialog-form-row">
        <Label>启用 HTTPS</Label>
        <Switch checked={sslEnabled} onCheckedChange={setSslEnabled} />
      </div>

      <div className="dialog-form-row">
        <Label>强制 HTTPS</Label>
        <Switch checked={forceHttps} onCheckedChange={setForceHttps} disabled={!sslEnabled} />
      </div>

      {sslEnabled && (
        <>
          <div className="dialog-form-row-top">
            <Label>证书链</Label>
            <Textarea
              value={fullchainPem}
              onChange={(e) => setFullchainPem(e.target.value)}
              placeholder="粘贴 -----BEGIN CERTIFICATE----- ..."
              rows={6}
              className="font-mono text-xs"
            />
          </div>
          <div className="dialog-form-row-top">
            <Label>私钥</Label>
            <Textarea
              value={privkeyPem}
              onChange={(e) => setPrivkeyPem(e.target.value)}
              placeholder="粘贴 -----BEGIN PRIVATE KEY----- ..."
              rows={6}
              className="font-mono text-xs"
            />
          </div>
        </>
      )}

      {info && (
        <div className="rounded-md border bg-muted/40 p-3 text-sm space-y-2">
          <div className="dialog-form-row">
            <Label className="text-muted-foreground">证书状态</Label>
            <StatusText status={info.cert_status} map={CERT_STATUS} />
          </div>
          <div className="dialog-form-row">
            <Label className="text-muted-foreground">证书到期</Label>
            <span>{info.cert_not_after || '—'}</span>
          </div>
          <div className="dialog-form-row">
            <Label className="text-muted-foreground">Nginx 同步</Label>
            <StatusText status={info.nginx_status} map={NGINX_STATUS} />
          </div>
          {info.has_cert_files && (
            <div className="dialog-form-row">
              <Label className="text-muted-foreground">证书文件</Label>
              <span>已保存</span>
            </div>
          )}
          {info.nginx_error && (
            <div className="dialog-form-row-top">
              <Label className="text-muted-foreground">最近错误</Label>
              <span className="text-destructive break-all">{info.nginx_error}</span>
            </div>
          )}
        </div>
      )}

      <div className="flex gap-2 justify-end">
        <Button type="button" variant="outline" disabled={loading || !sslEnabled} onClick={() => void handleTest()}>
          测试证书
        </Button>
        <Button type="button" disabled={loading} onClick={() => void handleSave()}>
          保存并应用
        </Button>
      </div>
    </div>
  )
}
