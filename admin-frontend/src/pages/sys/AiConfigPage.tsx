import { useCallback, useEffect, useState } from 'react'
import { Save, KeyRound } from 'lucide-react'
import { toast } from 'sonner'
import {
  getAiConfigSettingsService,
  createAiModelConfigService,
  updateAiDefaultProvidersService,
  updateAiModelConfigService,
  updateAiProviderConfigService,
} from '@/api/service'
import { Loading } from '@/components/Loading'
import { Button } from '@/components/ui/button'
import { PageShell } from '@/components/PageShell'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Switch } from '@/components/ui/switch'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Separator } from '@/components/ui/separator'
import { Badge } from '@/components/ui/badge'

interface AiProviderRow {
  id: number
  code: string
  name: string
  provider_type: string
  base_url: string
  api_key_masked: string
  api_key_configured: boolean
  enabled: boolean
}

interface AiModelRow {
  id: number
  provider_id: number
  provider_code: string
  model_id: string
  display_name: string
  capability: string
  is_default: boolean
  enabled: boolean
  params: Record<string, unknown>
}

interface AiDefaults {
  default_text_provider: string
  default_image_provider: string
  default_search_provider: string
}

export function AiConfigPage() {
  const [loading, setLoading] = useState(false)
  const [providers, setProviders] = useState<AiProviderRow[]>([])
  const [models, setModels] = useState<AiModelRow[]>([])
  const [defaults, setDefaults] = useState<AiDefaults>({
    default_text_provider: 'deepseek',
    default_image_provider: 'qwen',
    default_search_provider: 'bocha',
  })
  const [providerKeys, setProviderKeys] = useState<Record<number, string>>({})
  const [providerEdits, setProviderEdits] = useState<Record<number, Partial<AiProviderRow>>>({})
  const [modelIdEdits, setModelIdEdits] = useState<Record<number, string>>({})

  const applyConfig = (data: {
    providers?: AiProviderRow[]
    models?: AiModelRow[]
    defaults?: AiDefaults
  }) => {
    if (data.providers) setProviders(data.providers)
    if (data.models) setModels(data.models)
    if (data.defaults) setDefaults(data.defaults)
  }

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const res = await getAiConfigSettingsService()
      if (res.code === 0 && res.data) {
        applyConfig(res.data as typeof res.data)
      } else {
        toast.error(res.message || '加载配置失败')
      }
    } catch (e) {
      toast.error(String(e))
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    load()
  }, [load])

  const textProviders = providers.filter((p) => p.provider_type === 'text')
  const imageProviders = providers.filter((p) => p.provider_type === 'image')
  const searchProviders = providers.filter((p) => p.provider_type === 'search')

  const primaryModel = (providerId: number) => {
    const list = models.filter((m) => m.provider_id === providerId)
    return list.find((m) => m.is_default) ?? list[0]
  }

  const getModelId = (providerId: number) => {
    if (modelIdEdits[providerId] !== undefined) return modelIdEdits[providerId]
    const m = primaryModel(providerId)
    return m?.model_id ?? ''
  }

  const saveDefaults = async () => {
    setLoading(true)
    try {
      const res = await updateAiDefaultProvidersService({ ...defaults })
      if (res.code === 0) {
        toast.success('默认 Provider 已保存')
        if (res.data) applyConfig(res.data as { providers: AiProviderRow[]; models: AiModelRow[]; defaults: AiDefaults })
      } else {
        toast.error(res.message || '保存失败')
      }
    } catch (e) {
      toast.error(String(e))
    } finally {
      setLoading(false)
    }
  }

  const saveProvider = async (p: AiProviderRow) => {
    const edit = providerEdits[p.id] || {}
    const newKey = providerKeys[p.id]
    const modelId = getModelId(p.id).trim()
    const model = primaryModel(p.id)

    setLoading(true)
    try {
      const providerRes = await updateAiProviderConfigService({
        id: p.id,
        name: edit.name ?? p.name,
        base_url: edit.base_url ?? p.base_url,
        enabled: edit.enabled ?? p.enabled,
        api_key: newKey || undefined,
      })
      if (providerRes.code !== 0) {
        toast.error(providerRes.message || '保存失败')
        return
      }

      if (modelId) {
        if (model) {
          const modelRes = await updateAiModelConfigService({
            id: model.id,
            model_id: modelId,
            display_name: modelId,
          })
          if (modelRes.code !== 0) {
            toast.error(modelRes.message || '模型保存失败')
            return
          }
        } else {
          const createRes = await createAiModelConfigService({
            provider_id: p.id,
            model_id: modelId,
            display_name: modelId,
            is_default: true,
          })
          if (createRes.code !== 0) {
            toast.error(createRes.message || '模型保存失败')
            return
          }
        }
      }

      toast.success(`${p.code} 已保存`)
      setProviderKeys((prev) => ({ ...prev, [p.id]: '' }))
      setProviderEdits((prev) => {
        const next = { ...prev }
        delete next[p.id]
        return next
      })
      setModelIdEdits((prev) => {
        const next = { ...prev }
        delete next[p.id]
        return next
      })
      await load()
    } catch (e) {
      toast.error(String(e))
    } finally {
      setLoading(false)
    }
  }

  const updateProviderField = (id: number, field: keyof AiProviderRow, value: string | boolean) => {
    setProviderEdits((prev) => ({
      ...prev,
      [id]: { ...prev[id], [field]: value },
    }))
  }

  const getProviderField = (p: AiProviderRow, field: 'name' | 'base_url' | 'enabled') => {
    const edit = providerEdits[p.id]
    if (edit && edit[field] !== undefined) return edit[field]
    return p[field]
  }

  return (
    <>
      <Loading loading={loading} />
      <PageShell
        title="AI 配置"
        description="在界面管理 API Key、默认 Provider 与模型，无需改环境变量"
      >
        <div className="content-panel space-y-8 p-6">
          <section className="space-y-4">
            <h4 className="text-sm font-medium text-muted-foreground">默认 Provider</h4>
            <div className="grid gap-4 md:grid-cols-2">
              <div className="dialog-form-row">
                <Label>文本生成</Label>
                <Select
                  value={defaults.default_text_provider}
                  onValueChange={(v) => setDefaults((d) => ({ ...d, default_text_provider: v }))}
                >
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    {textProviders.map((p) => (
                      <SelectItem key={p.code} value={p.code}>{p.name}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="dialog-form-row">
                <Label>图像生成</Label>
                <Select
                  value={defaults.default_image_provider}
                  onValueChange={(v) => setDefaults((d) => ({ ...d, default_image_provider: v }))}
                >
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    {imageProviders.map((p) => (
                      <SelectItem key={p.code} value={p.code}>{p.name}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="dialog-form-row">
                <Label>联网检索</Label>
                <Select
                  value={defaults.default_search_provider}
                  onValueChange={(v) => setDefaults((d) => ({ ...d, default_search_provider: v }))}
                >
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    {searchProviders.map((p) => (
                      <SelectItem key={p.code} value={p.code}>{p.name}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
            <Button variant="outline" onClick={saveDefaults}>
              <Save className="h-4 w-4" />
              保存默认 Provider
            </Button>
          </section>

          <Separator />

          <section className="space-y-4">
            <h4 className="text-sm font-medium text-muted-foreground">Provider 与 API Key</h4>
            <div className="space-y-6">
              {providers.map((p) => (
                <div key={p.id} className="rounded-lg border p-4 space-y-3">
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="font-medium">{p.name}</span>
                    <Badge variant="secondary">{p.code}</Badge>
                    <Badge variant="outline">{p.provider_type}</Badge>
                    {p.api_key_configured ? (
                      <Badge className="bg-green-600">Key 已配置 {p.api_key_masked}</Badge>
                    ) : (
                      <Badge variant="destructive">Key 未配置</Badge>
                    )}
                  </div>
                  <div className="space-y-2.5">
                    <div className="dialog-form-row">
                      <Label>显示名称</Label>
                      <Input
                        value={String(getProviderField(p, 'name'))}
                        onChange={(e) => updateProviderField(p.id, 'name', e.target.value)}
                      />
                    </div>
                    <div className="dialog-form-row">
                      <Label>Base URL</Label>
                      <Input
                        value={String(getProviderField(p, 'base_url'))}
                        onChange={(e) => updateProviderField(p.id, 'base_url', e.target.value)}
                      />
                    </div>
                    <div className="dialog-form-row">
                      <Label className="flex items-center gap-1">
                        <KeyRound className="h-3.5 w-3.5 shrink-0" />
                        API Key
                      </Label>
                      <Input
                        type="password"
                        placeholder="留空则不修改"
                        value={providerKeys[p.id] || ''}
                        onChange={(e) =>
                          setProviderKeys((prev) => ({ ...prev, [p.id]: e.target.value }))
                        }
                      />
                    </div>
                    <div className="dialog-form-row">
                      <Label>模型 ID</Label>
                      <Input
                        className="font-mono text-sm"
                        placeholder="如 deepseek-v4-pro"
                        value={getModelId(p.id)}
                        onChange={(e) =>
                          setModelIdEdits((prev) => ({ ...prev, [p.id]: e.target.value }))
                        }
                      />
                    </div>
                  </div>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Switch
                        checked={Boolean(getProviderField(p, 'enabled'))}
                        onCheckedChange={(c) => updateProviderField(p.id, 'enabled', c)}
                      />
                      <Label>启用</Label>
                    </div>
                    <Button size="sm" onClick={() => saveProvider(p)}>
                      <Save className="h-4 w-4" />
                      保存
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </section>
        </div>
      </PageShell>
    </>
  )
}
