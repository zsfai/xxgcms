import { useCallback, useEffect, useMemo, useState } from 'react'
import { Copy, KeyRound, Plus, Trash2 } from 'lucide-react'
import { toast } from 'sonner'
import {
  createMcpKeyService,
  getMcpKeyListService,
  getSiteListService,
  revokeMcpKeyService,
} from '@/api/service'
import { ConfirmDialog } from '@/components/ConfirmDialog'
import { Loading } from '@/components/Loading'
import { PageShell } from '@/components/PageShell'
import { AiSecondaryNav } from '@/pages/sys/AiSecondaryNav'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { FormLabel } from '@/components/FormLabel'
import { Label } from '@/components/ui/label'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { formatDateTime } from '@/lib/utils'
import type { SiteItem } from '@/types'

interface McpKeyRow {
  id: number
  name: string
  key_prefix: string
  site_id?: number | null
  site_name?: string | null
  site_desc?: string | null
  enabled: string
  last_used_at?: string | null
  create_time?: string
}

const TOKEN_PLACEHOLDER = '在下方签发后替换此处'

function mcpEndpoint() {
  return `${window.location.origin.replace(/\/$/, '')}/mcp`
}

function mcpConfigJson(rawKey: string) {
  return JSON.stringify(
    {
      mcpServers: {
        xxgcms: {
          type: 'http',
          url: mcpEndpoint(),
          headers: {
            Authorization: `Bearer ${rawKey}`,
          },
        },
      },
    },
    null,
    2,
  )
}

async function copyText(text: string) {
  try {
    await navigator.clipboard.writeText(text)
    toast.success('已复制到剪贴板')
  } catch {
    toast.error('复制失败，请手动选中文本复制')
  }
}

export function McpAccessPage() {
  const [loading, setLoading] = useState(false)
  const [list, setList] = useState<McpKeyRow[]>([])
  const [sites, setSites] = useState<SiteItem[]>([])
  const [createOpen, setCreateOpen] = useState(false)
  const [name, setName] = useState('桌面 Agent')
  const [siteId, setSiteId] = useState('all')
  const [creating, setCreating] = useState(false)
  const [secretOpen, setSecretOpen] = useState(false)
  const [secretJson, setSecretJson] = useState('')
  const [revokeTarget, setRevokeTarget] = useState<McpKeyRow | null>(null)
  const exampleJson = useMemo(() => mcpConfigJson(TOKEN_PLACEHOLDER), [])
  const endpoint = useMemo(() => mcpEndpoint(), [])

  const loadList = useCallback(async () => {
    setLoading(true)
    try {
      const [keyRes, siteRes] = await Promise.all([
        getMcpKeyListService(),
        getSiteListService(),
      ])
      if (keyRes.code === 0) {
        setList((keyRes.datas as McpKeyRow[]) || [])
      } else {
        toast.error(keyRes.message || '加载 MCP 密钥失败')
      }
      if (siteRes.code === 0) {
        const rows = siteRes.datas
        setSites(Array.isArray(rows) ? (rows as SiteItem[]) : [])
      }
    } catch (e) {
      toast.error(`加载失败：${String(e)}`)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    void loadList()
  }, [loadList])

  const handleCreate = async () => {
    const label = name.trim()
    if (!label) {
      toast.error('请填写备注名')
      return
    }
    setCreating(true)
    try {
      const res = await createMcpKeyService({
        name: label,
        site_id: siteId === 'all' ? null : Number(siteId),
      })
      if (res.code !== 0 || !res.data) {
        toast.error(res.message || '创建失败')
        return
      }
      const created = res.data as { key?: string }
      if (!created.key) {
        toast.error('未返回明文密钥')
        return
      }
      setSecretJson(mcpConfigJson(created.key))
      setCreateOpen(false)
      setSecretOpen(true)
      setName('桌面 Agent')
      setSiteId('all')
      toast.success('已创建，请立即复制配置（明文只显示一次）')
      await loadList()
    } catch (e) {
      toast.error(`创建失败：${String(e)}`)
    } finally {
      setCreating(false)
    }
  }

  const handleRevoke = async () => {
    if (!revokeTarget) return
    setLoading(true)
    try {
      const res = await revokeMcpKeyService({ id: revokeTarget.id })
      if (res.code === 0) {
        toast.success('已撤销')
        setRevokeTarget(null)
        await loadList()
      } else {
        toast.error(res.message || '撤销失败')
      }
    } catch (e) {
      toast.error(`撤销失败：${String(e)}`)
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      <Loading loading={loading} />
      <PageShell
        title="MCP 连接器"
        description="把下面的配置贴进 Cursor / Claude / WorkBuddy。推送的文章一律为草稿，需在文章管理中人工审核发布。"
        sideNav={<AiSecondaryNav />}
        actions={
          <Button onClick={() => setCreateOpen(true)}>
            <Plus className="mr-1.5 h-4 w-4" />
            新建密钥
          </Button>
        }
      >
        <div className="content-panel mb-4 space-y-4 p-4">
          <div>
            <div className="mb-1.5 text-[13px] font-medium text-foreground">怎么配到桌面 Agent</div>
            <ol className="list-decimal space-y-1 pl-5 text-[13px] leading-relaxed text-muted-foreground">
              <li>复制下方 JSON，粘贴到 Cursor / Claude / WorkBuddy 的 MCP 设置。</li>
              <li>点「新建密钥」，把 JSON 里的 Bearer 换成弹窗里的明文（只显示一次）。</li>
              <li>
                让 Agent 读本地文档，先 <code className="text-foreground">upload_image</code>，再{' '}
                <code className="text-foreground">push_article</code>；到「文章管理」审草稿。
              </li>
            </ol>
          </div>
          <div className="grid gap-3 sm:grid-cols-2">
            <div className="space-y-1.5">
              <Label>服务地址</Label>
              <div className="flex gap-2">
                <Input readOnly value={endpoint} className="h-9 font-mono text-xs" />
                <Button variant="outline" className="shrink-0" onClick={() => void copyText(endpoint)}>
                  <Copy className="mr-1.5 h-4 w-4" />
                  复制
                </Button>
              </div>
            </div>
            <div className="space-y-1.5">
              <Label>鉴权头</Label>
              <Input readOnly value="Authorization: Bearer <密钥>" className="h-9 font-mono text-xs" />
            </div>
          </div>
          <div className="space-y-1.5">
            <div className="flex items-center justify-between gap-2">
              <Label>配置示例（占位密钥，签发后替换）</Label>
              <Button variant="outline" size="sm" onClick={() => void copyText(exampleJson)}>
                <Copy className="mr-1.5 h-3.5 w-3.5" />
                复制示例
              </Button>
            </div>
            <pre className="m-0 overflow-hidden whitespace-pre-wrap break-all rounded-md border border-input bg-card p-3 font-mono text-xs leading-5">
              {exampleJson}
            </pre>
          </div>
        </div>
        <div className="content-panel table-scroll-panel">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="w-16">ID</TableHead>
                <TableHead>备注</TableHead>
                <TableHead>Key 前缀</TableHead>
                <TableHead>站点范围</TableHead>
                <TableHead>状态</TableHead>
                <TableHead>最近使用</TableHead>
                <TableHead>创建时间</TableHead>
                <TableHead className="w-24">操作</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {list.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={8} className="py-10 text-center text-sm text-muted-foreground">
                    还没有 MCP 密钥，先点右上角签发
                  </TableCell>
                </TableRow>
              ) : (
                list.map((row) => (
                  <TableRow key={row.id}>
                    <TableCell className="tabular-nums text-muted-foreground">{row.id}</TableCell>
                    <TableCell>{row.name}</TableCell>
                    <TableCell className="font-mono text-xs">{row.key_prefix}…</TableCell>
                    <TableCell>
                      {row.site_id
                        ? row.site_name || `站点 #${row.site_id}`
                        : '全部站点'}
                    </TableCell>
                    <TableCell>
                      <Badge variant={row.enabled === 'Y' ? 'default' : 'secondary'}>
                        {row.enabled === 'Y' ? '有效' : '已撤销'}
                      </Badge>
                    </TableCell>
                    <TableCell className="whitespace-nowrap tabular-nums text-sm">
                      {formatDateTime(row.last_used_at) || '—'}
                    </TableCell>
                    <TableCell className="whitespace-nowrap tabular-nums text-sm">
                      {formatDateTime(row.create_time)}
                    </TableCell>
                    <TableCell>
                      {row.enabled === 'Y' ? (
                        <Button
                          variant="ghost"
                          size="icon"
                          className="table-action-icon-danger"
                          title="撤销"
                          onClick={() => setRevokeTarget(row)}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      ) : (
                        <span className="text-xs text-muted-foreground">—</span>
                      )}
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </div>
      </PageShell>

      <Dialog open={createOpen} onOpenChange={setCreateOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>新建 MCP 密钥</DialogTitle>
          </DialogHeader>
          <div className="space-y-3">
            <div className="dialog-form-row">
              <FormLabel required>备注名</FormLabel>
              <Input value={name} onChange={(e) => setName(e.target.value)} placeholder="例如 WorkBuddy" />
            </div>
            <div className="dialog-form-row">
              <Label>站点范围</Label>
              <Select value={siteId} onValueChange={setSiteId}>
                <SelectTrigger>
                  <SelectValue placeholder="全部站点" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">全部站点</SelectItem>
                  {sites.map((site) => (
                    <SelectItem key={site.id} value={String(site.id)}>
                      {site.name}
                      {site.desc ? `（${site.desc}）` : ''}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setCreateOpen(false)}>
              取消
            </Button>
            <Button onClick={() => void handleCreate()} disabled={creating}>
              {creating ? '创建中…' : '创建'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Dialog open={secretOpen} onOpenChange={setSecretOpen}>
        <DialogContent className="max-w-xl">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <KeyRound className="h-4 w-4" />
              复制到桌面 Agent
            </DialogTitle>
          </DialogHeader>
          <p className="text-[13px] text-muted-foreground">
            明文 Token 只显示这一次。把这段 JSON 整段贴进 Agent；关闭后无法再查看，丢失请撤销后重新签发。
          </p>
          <pre className="m-0 max-h-none overflow-hidden whitespace-pre-wrap break-all rounded-md border border-input bg-card p-3 font-mono text-xs leading-5">
            {secretJson}
          </pre>
          <DialogFooter>
            <Button variant="outline" onClick={() => setSecretOpen(false)}>
              关闭
            </Button>
            <Button onClick={() => void copyText(secretJson)}>
              <Copy className="mr-1.5 h-4 w-4" />
              复制配置
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <ConfirmDialog
        open={!!revokeTarget}
        onOpenChange={(open) => {
          if (!open) setRevokeTarget(null)
        }}
        title="撤销密钥"
        description={
          revokeTarget
            ? `撤销后 ${revokeTarget.key_prefix}… 立刻失效，已配置该 Key 的 Agent 将无法推送。`
            : ''
        }
        confirmText="撤销"
        onConfirm={() => void handleRevoke()}
      />
    </>
  )
}
