import { useCallback, useEffect, useState } from 'react'
import { Pencil, Plus, Trash2 } from 'lucide-react'
import { toast } from 'sonner'
import {
  createAiVerticalService,
  deleteAiVerticalService,
  getAiVerticalsAdminService,
  updateAiVerticalService,
} from '@/api/service'
import { ConfirmDialog } from '@/components/ConfirmDialog'
import { Loading } from '@/components/Loading'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { PageShell } from '@/components/PageShell'
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
import { Switch } from '@/components/ui/switch'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Textarea } from '@/components/ui/textarea'

interface PromptTemplateOption {
  code: string
  name: string
}

interface VerticalRow {
  id: number
  code: string
  name: string
  description?: string
  topic_system_prompt: string
  topic_user_hint?: string
  article_system_prompt: string
  article_user_hint?: string
  search_queries: string[]
  default_template_code?: string
  default_word_count: number
  sort_num: number
  enabled: boolean
}

interface VerticalForm {
  id?: number
  code: string
  name: string
  description: string
  topic_system_prompt: string
  topic_user_hint: string
  article_system_prompt: string
  article_user_hint: string
  search_queries_text: string
  default_template_code: string
  default_word_count: string
  sort_num: string
  enabled: boolean
}

const emptyForm: VerticalForm = {
  code: '',
  name: '',
  description: '',
  topic_system_prompt: '',
  topic_user_hint: '',
  article_system_prompt: '',
  article_user_hint: '',
  search_queries_text: '',
  default_template_code: 'news_general',
  default_word_count: '800',
  sort_num: '9999',
  enabled: true,
}

function queriesToText(queries: string[]) {
  return (queries || []).join('\n')
}

function formFromRow(row: VerticalRow): VerticalForm {
  return {
    id: row.id,
    code: row.code,
    name: row.name,
    description: row.description || '',
    topic_system_prompt: row.topic_system_prompt,
    topic_user_hint: row.topic_user_hint || '',
    article_system_prompt: row.article_system_prompt,
    article_user_hint: row.article_user_hint || '',
    search_queries_text: queriesToText(row.search_queries),
    default_template_code: row.default_template_code || 'news_general',
    default_word_count: String(row.default_word_count || 800),
    sort_num: String(row.sort_num ?? 9999),
    enabled: row.enabled,
  }
}

export function AiVerticalPage() {
  const [loading, setLoading] = useState(false)
  const [verticals, setVerticals] = useState<VerticalRow[]>([])
  const [templates, setTemplates] = useState<PromptTemplateOption[]>([])
  const [dialogOpen, setDialogOpen] = useState(false)
  const [form, setForm] = useState<VerticalForm>(emptyForm)
  const [isCreate, setIsCreate] = useState(false)
  const [deleteTarget, setDeleteTarget] = useState<VerticalRow | null>(null)

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const res = await getAiVerticalsAdminService()
      if (res.code === 0 && res.data) {
        const data = res.data as { verticals?: VerticalRow[]; templates?: PromptTemplateOption[] }
        setVerticals(data.verticals || [])
        setTemplates(data.templates || [])
      } else {
        toast.error(res.message || '加载失败')
      }
    } catch (e) {
      toast.error(String(e))
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    void load()
  }, [load])

  const openCreate = () => {
    setIsCreate(true)
    setForm({ ...emptyForm })
    setDialogOpen(true)
  }

  const openEdit = (row: VerticalRow) => {
    setIsCreate(false)
    setForm(formFromRow(row))
    setDialogOpen(true)
  }

  const handleSave = async () => {
    const payload = {
      code: form.code.trim().toLowerCase(),
      name: form.name.trim(),
      description: form.description.trim(),
      topic_system_prompt: form.topic_system_prompt.trim(),
      topic_user_hint: form.topic_user_hint.trim(),
      article_system_prompt: form.article_system_prompt.trim(),
      article_user_hint: form.article_user_hint.trim(),
      search_queries: form.search_queries_text.split('\n').map((s) => s.trim()).filter(Boolean),
      default_template_code: form.default_template_code,
      default_word_count: Number(form.default_word_count) || 800,
      sort_num: Number(form.sort_num) || 9999,
      enabled: form.enabled,
    }
    setLoading(true)
    try {
      const res = isCreate
        ? await createAiVerticalService(payload)
        : await updateAiVerticalService({ id: form.id, ...payload })
      if (res.code === 0) {
        toast.success('保存成功')
        setDialogOpen(false)
        void load()
      } else {
        toast.error(res.message || '保存失败')
      }
    } catch (e) {
      toast.error(String(e))
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async () => {
    if (!deleteTarget) return
    setLoading(true)
    try {
      const res = await deleteAiVerticalService({ id: deleteTarget.id })
      if (res.code === 0) {
        toast.success('删除成功')
        setDeleteTarget(null)
        void load()
      } else {
        toast.error(res.message || '删除失败')
      }
    } catch (e) {
      toast.error(String(e))
    } finally {
      setLoading(false)
    }
  }

  const updateField = <K extends keyof VerticalForm>(key: K, value: VerticalForm[K]) => {
    setForm((prev) => ({ ...prev, [key]: value }))
  }

  return (
    <>
      <Loading loading={loading} />
      <PageShell
        title="垂类管理"
        description="配置选题与写稿的提示词、联网检索词；直接影响 AI 选题与文章质量"
        actions={
          <Button onClick={openCreate}>
            <Plus className="h-4 w-4" />
            新增垂类
          </Button>
        }
      >
        <div className="content-panel p-4">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>名称</TableHead>
                <TableHead>标识</TableHead>
                <TableHead>默认模板</TableHead>
                <TableHead>字数</TableHead>
                <TableHead>排序</TableHead>
                <TableHead>状态</TableHead>
                <TableHead className="min-w-[7rem]">操作</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {verticals.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={7} className="text-center text-muted-foreground">
                    暂无垂类，请新增或执行数据库补丁
                  </TableCell>
                </TableRow>
              ) : (
                verticals.map((row) => (
                  <TableRow key={row.id}>
                    <TableCell className="font-medium">{row.name}</TableCell>
                    <TableCell className="text-muted-foreground">{row.code}</TableCell>
                    <TableCell>{row.default_template_code || '-'}</TableCell>
                    <TableCell>{row.default_word_count}</TableCell>
                    <TableCell>{row.sort_num}</TableCell>
                    <TableCell>
                      <Badge variant={row.enabled ? 'default' : 'secondary'}>
                        {row.enabled ? '启用' : '停用'}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <div className="flex gap-1">
                        <Button
                          variant="outline"
                          size="icon"
                          className="table-action-icon"
                          title="编辑"
                          onClick={() => openEdit(row)}
                        >
                          <Pencil className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="outline"
                          size="icon"
                          className="table-action-icon-danger"
                          title="删除"
                          onClick={() => setDeleteTarget(row)}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </div>
      </PageShell>

      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent className="max-w-3xl">
          <DialogHeader className="pb-4">
            <DialogTitle>{isCreate ? '新增垂类' : '编辑垂类'}</DialogTitle>
          </DialogHeader>
          <div className="dialog-form-narrow space-y-5">
            <div className="space-y-3">
              <h4 className="text-sm font-medium text-muted-foreground">基本信息</h4>
              <div className="space-y-2.5">
                <div className="dialog-form-row">
                  <FormLabel required>名称</FormLabel>
                  <Input
                    value={form.name}
                    onChange={(e) => updateField('name', e.target.value)}
                    placeholder="如：旅游"
                  />
                </div>
                <div className="dialog-form-row">
                  <FormLabel required>标识 code</FormLabel>
                  <Input
                    value={form.code}
                    disabled={!isCreate}
                    placeholder="如 travel"
                    onChange={(e) => updateField('code', e.target.value)}
                  />
                </div>
                <div className="dialog-form-row">
                  <Label>说明</Label>
                  <Input
                    value={form.description}
                    placeholder="简要说明适用场景"
                    onChange={(e) => updateField('description', e.target.value)}
                  />
                </div>
              </div>
            </div>

            <div className="space-y-3">
              <h4 className="text-sm font-medium text-muted-foreground">选题提示词</h4>
              <div className="space-y-2.5">
                <div className="dialog-form-row-wide-top">
                  <FormLabel required>System</FormLabel>
                  <Textarea
                    rows={5}
                    value={form.topic_system_prompt}
                    onChange={(e) => updateField('topic_system_prompt', e.target.value)}
                    placeholder="定义 AI 选题时的角色、规则与输出格式"
                  />
                </div>
                <div className="dialog-form-row-wide-top">
                  <Label>User 补充</Label>
                  <Textarea
                    rows={3}
                    value={form.topic_user_hint}
                    onChange={(e) => updateField('topic_user_hint', e.target.value)}
                    placeholder="可选"
                  />
                </div>
              </div>
            </div>

            <div className="space-y-3">
              <h4 className="text-sm font-medium text-muted-foreground">写稿提示词</h4>
              <div className="space-y-2.5">
                <div className="dialog-form-row-wide-top">
                  <FormLabel required>System</FormLabel>
                  <Textarea
                    rows={5}
                    value={form.article_system_prompt}
                    onChange={(e) => updateField('article_system_prompt', e.target.value)}
                    placeholder="定义 AI 写稿时的角色、风格与禁忌"
                  />
                </div>
                <div className="dialog-form-row-wide-top">
                  <Label>User 补充</Label>
                  <Textarea
                    rows={3}
                    value={form.article_user_hint}
                    onChange={(e) => updateField('article_user_hint', e.target.value)}
                    placeholder="可选"
                  />
                </div>
              </div>
            </div>

            <div className="space-y-3">
              <h4 className="text-sm font-medium text-muted-foreground">默认参数</h4>
              <div className="space-y-2.5">
                <div className="dialog-form-row-wide-top">
                  <FormLabel required>检索词</FormLabel>
                  <div className="space-y-1">
                    <Textarea
                      rows={4}
                      value={form.search_queries_text}
                      onChange={(e) => updateField('search_queries_text', e.target.value)}
                      placeholder="{seed} 旅游攻略 {year}"
                    />
                    <p className="text-xs text-muted-foreground">
                      每行一条，支持占位符 {'{seed}'}（种子词）、{'{year}'}（当前年份）
                    </p>
                  </div>
                </div>
                <div className="dialog-form-row">
                  <Label>默认模板</Label>
                  <Select
                    value={form.default_template_code}
                    onValueChange={(v) => updateField('default_template_code', v)}
                  >
                    <SelectTrigger><SelectValue /></SelectTrigger>
                    <SelectContent>
                      {templates.map((t) => (
                        <SelectItem key={t.code} value={t.code}>{t.name}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div className="dialog-form-row">
                  <Label>默认字数</Label>
                  <Input
                    className="max-w-[10rem]"
                    value={form.default_word_count}
                    onChange={(e) => updateField('default_word_count', e.target.value)}
                  />
                </div>
                <div className="dialog-form-row">
                  <Label>排序</Label>
                  <Input
                    className="max-w-[10rem]"
                    value={form.sort_num}
                    onChange={(e) => updateField('sort_num', e.target.value)}
                  />
                </div>
                <div className="dialog-form-row">
                  <Label>启用</Label>
                  <div className="flex items-center gap-3">
                    <Switch
                      checked={form.enabled}
                      onCheckedChange={(c) => updateField('enabled', c)}
                    />
                    <span className="text-sm text-muted-foreground">
                      {form.enabled ? '启用' : '停用'}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDialogOpen(false)}>取消</Button>
            <Button onClick={handleSave}>保存</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <ConfirmDialog
        open={!!deleteTarget}
        onOpenChange={(open) => !open && setDeleteTarget(null)}
        title="删除确认"
        description={`确定要删除垂类「${deleteTarget?.name}」吗？删除后 AI 选题将无法再选择该垂类。`}
        onConfirm={handleDelete}
      />
    </>
  )
}
