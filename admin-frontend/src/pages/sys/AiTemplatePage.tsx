import { useCallback, useEffect, useState } from 'react'
import { Pencil, Plus, Trash2 } from 'lucide-react'
import axios from 'axios'
import { toast } from 'sonner'
import {
  createAiTemplateService,
  deleteAiTemplateService,
  getAiTemplatesAdminService,
  updateAiTemplateService,
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
import { Switch } from '@/components/ui/switch'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Textarea } from '@/components/ui/textarea'

interface TemplateRow {
  id: number
  code: string
  name: string
  system_prompt: string
  enabled: boolean
}

interface TemplateForm {
  id?: number
  code: string
  name: string
  system_prompt: string
  enabled: boolean
}

const emptyForm: TemplateForm = {
  code: '',
  name: '',
  system_prompt: '',
  enabled: true,
}

function formFromRow(row: TemplateRow): TemplateForm {
  return {
    id: row.id,
    code: row.code,
    name: row.name,
    system_prompt: row.system_prompt || '',
    enabled: row.enabled,
  }
}

export function AiTemplatePage() {
  const [loading, setLoading] = useState(false)
  const [templates, setTemplates] = useState<TemplateRow[]>([])
  const [dialogOpen, setDialogOpen] = useState(false)
  const [form, setForm] = useState<TemplateForm>(emptyForm)
  const [isCreate, setIsCreate] = useState(false)
  const [deleteTarget, setDeleteTarget] = useState<TemplateRow | null>(null)

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const res = await getAiTemplatesAdminService()
      if (res.code === 0 && Array.isArray(res.data)) {
        setTemplates(res.data as TemplateRow[])
      } else {
        toast.error(res.message || '加载失败')
      }
    } catch (e) {
      if (axios.isAxiosError(e) && e.response?.status === 404) {
        toast.error('模板管理接口未找到，请重启 admin-backend 后再试')
      } else if (axios.isAxiosError(e) && !e.response) {
        toast.error('无法连接后端服务，请确认 admin-backend 已启动')
      } else {
        toast.error(String(e))
      }
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

  const openEdit = (row: TemplateRow) => {
    setIsCreate(false)
    setForm(formFromRow(row))
    setDialogOpen(true)
  }

  const updateField = <K extends keyof TemplateForm>(key: K, value: TemplateForm[K]) => {
    setForm((prev) => ({ ...prev, [key]: value }))
  }

  const handleSave = async () => {
    const payload = {
      code: form.code.trim().toLowerCase(),
      name: form.name.trim(),
      system_prompt: form.system_prompt.trim(),
      enabled: form.enabled,
    }
    setLoading(true)
    try {
      const res = isCreate
        ? await createAiTemplateService(payload)
        : await updateAiTemplateService({ id: form.id, ...payload })
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
      const res = await deleteAiTemplateService({ id: deleteTarget.id })
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

  return (
    <>
      <Loading loading={loading} />
      <PageShell
        title="模板管理"
        description="配置 AI 写稿时使用的文章模板与 System 提示词；AI 选题确认写稿时可选择"
        actions={
          <Button onClick={openCreate}>
            <Plus className="h-4 w-4" />
            新增模板
          </Button>
        }
      >
        <div className="content-panel p-4">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>名称</TableHead>
                <TableHead>标识</TableHead>
                <TableHead>状态</TableHead>
                <TableHead className="min-w-[7rem]">操作</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {templates.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={4} className="text-center text-muted-foreground">
                    暂无模板，请新增或执行数据库补丁
                  </TableCell>
                </TableRow>
              ) : (
                templates.map((row) => (
                  <TableRow key={row.id}>
                    <TableCell className="font-medium">{row.name}</TableCell>
                    <TableCell className="text-muted-foreground">{row.code}</TableCell>
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
            <DialogTitle>{isCreate ? '新增模板' : '编辑模板'}</DialogTitle>
          </DialogHeader>
          <div className="space-y-2.5">
            <div className="dialog-form-row">
              <FormLabel required>名称</FormLabel>
              <Input
                value={form.name}
                onChange={(e) => updateField('name', e.target.value)}
                placeholder="如：旅游攻略"
              />
            </div>
            <div className="dialog-form-row">
              <FormLabel required>标识 code</FormLabel>
              <Input
                value={form.code}
                disabled={!isCreate}
                placeholder="如 travel_guide"
                onChange={(e) => updateField('code', e.target.value)}
              />
            </div>
            <div className="dialog-form-row-wide-top">
              <FormLabel required>System</FormLabel>
              <Textarea
                rows={5}
                value={form.system_prompt}
                onChange={(e) => updateField('system_prompt', e.target.value)}
                placeholder="定义 AI 写稿时的角色、风格与禁忌；输出须为纯 JSON"
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
        description={`确定要删除模板「${deleteTarget?.name}」吗？若垂类默认引用该模板将无法删除。`}
        onConfirm={handleDelete}
      />
    </>
  )
}
