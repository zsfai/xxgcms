import { useCallback, useEffect, useMemo, useState } from 'react'
import { Plus, Pencil, Trash2, ScrollText, FolderPlus, Menu, Home } from 'lucide-react'
import { toast } from 'sonner'
import {
  addCateService,
  delCateService,
  getAuthHeaders,
  getCateListService,
  updateCateContentService,
  updateCateService,
} from '@/api/service'
import { CategoryTree } from '@/components/CategoryTree'
import { ConfirmDialog } from '@/components/ConfirmDialog'
import { FileUpload } from '@/components/FileUpload'
import { Loading } from '@/components/Loading'
import { RichTextEditor } from '@/components/RichTextEditor'
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
import { Textarea } from '@/components/ui/textarea'
import { getMediaUrl, listToTree, normalizeParentId } from '@/lib/utils'
import type { CateItem } from '@/types'

interface CateForm {
  id?: number
  name: string
  name_en: string
  p_id: number | null
  pic_url: string
  visiable: string
  home_visiable: string
  sort_num: number
  seo_title: string
  kws: string
  desc: string
}

const emptyForm: CateForm = {
  name: '',
  name_en: '',
  p_id: null,
  pic_url: '',
  visiable: 'Y',
  home_visiable: 'N',
  sort_num: 9999,
  seo_title: '',
  kws: '',
  desc: '',
}

export function CatePage() {
  const domain = sessionStorage.getItem('domain') || ''
  const [loading, setLoading] = useState(false)
  const [flatList, setFlatList] = useState<CateItem[]>([])
  const [selectedId, setSelectedId] = useState<number | null>(null)
  const [formDialogOpen, setFormDialogOpen] = useState(false)
  const [contentDialogOpen, setContentDialogOpen] = useState(false)
  const [form, setForm] = useState<CateForm>(emptyForm)
  const [content, setContent] = useState('')
  const [contentTarget, setContentTarget] = useState<CateItem | null>(null)
  const [deleteTarget, setDeleteTarget] = useState<CateItem | null>(null)
  const [editorFullScreen, setEditorFullScreen] = useState(false)

  const treeData = useMemo(() => listToTree(flatList.map((item) => ({ ...item }))), [flatList])

  const loadList = useCallback(async () => {
    setLoading(true)
    try {
      const res = await getCateListService({ page_num: 1, page_size: 9999 })
      if (res.code === 0) {
        setFlatList((res.datas as CateItem[]) || [])
      } else {
        toast.error(res.message || '加载分类列表失败')
      }
    } catch (e) {
      toast.error(`加载分类列表失败：${String(e)}`)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    loadList()
  }, [loadList])

  const openAdd = (parentId: number | null = null) => {
    setForm({ ...emptyForm, p_id: parentId })
    setFormDialogOpen(true)
  }

  const openEdit = (item: CateItem) => {
    setForm({
      id: item.id,
      name: item.name || '',
      name_en: item.name_en || '',
      p_id: normalizeParentId(item.p_id),
      pic_url: item.pic_url || '',
      visiable: item.visiable || 'Y',
      home_visiable: item.home_visiable || 'N',
      sort_num: item.sort_num ?? 9999,
      seo_title: item.seo_title || '',
      kws: item.kws || '',
      desc: item.desc || '',
    })
    setFormDialogOpen(true)
  }

  const openContent = (item: CateItem) => {
    setContentTarget(item)
    setContent(item.content || '')
    setContentDialogOpen(true)
  }

  const handleSave = async () => {
    if (!form.name.trim()) {
      toast.error('请填写分类名称')
      return
    }
    if (!form.name_en.trim()) {
      toast.error('请填写英文名称')
      return
    }

    setLoading(true)
    try {
      const payload = {
        id: form.id,
        name: form.name.trim(),
        name_en: form.name_en.trim(),
        p_id: form.p_id ?? -1,
        pic_url: form.pic_url,
        visiable: form.visiable,
        home_visiable: form.home_visiable,
        sort_num: form.sort_num,
        seo_title: form.seo_title.trim(),
        kws: form.kws.trim(),
        desc: form.desc.trim(),
      }
      const res = form.id ? await updateCateService(payload) : await addCateService(payload)

      if (res.code === 0 && res.ret) {
        toast.success(form.id ? '更新成功' : '添加成功')
        setFormDialogOpen(false)
        await loadList()
      } else {
        toast.error(res.message || '保存失败')
      }
    } catch (e) {
      toast.error(`保存失败：${String(e)}`)
    } finally {
      setLoading(false)
    }
  }

  const handleSaveContent = async () => {
    if (!contentTarget) return

    setLoading(true)
    try {
      const res = await updateCateContentService({ id: contentTarget.id, content })
      if (res.code === 0 && res.ret) {
        toast.success('内容保存成功')
        setContentDialogOpen(false)
        await loadList()
      } else {
        toast.error(res.message || '内容保存失败')
      }
    } catch (e) {
      toast.error(`内容保存失败：${String(e)}`)
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async () => {
    if (!deleteTarget) return

    setLoading(true)
    try {
      const res = await delCateService({ id: deleteTarget.id })
      if (res.code === 0 && res.ret) {
        toast.success('删除成功')
        setDeleteTarget(null)
        if (selectedId === deleteTarget.id) setSelectedId(null)
        await loadList()
      } else {
        toast.error(res.message || '删除失败')
      }
    } catch (e) {
      toast.error(`删除失败：${String(e)}`)
    } finally {
      setLoading(false)
    }
  }

  const updateField = <K extends keyof CateForm>(key: K, value: CateForm[K]) => {
    setForm((prev) => ({ ...prev, [key]: value }))
  }

  const parentOptions = flatList.filter((item) => item.id !== form.id)

  const renderActions = (item: CateItem) => (
    <div className="flex shrink-0 items-center justify-end gap-1">
      <Button variant="outline" size="sm" className="gap-1 px-2.5" onClick={() => openAdd(item.id)}>
        <FolderPlus className="h-3.5 w-3.5" />
        子分类
      </Button>
      <Button variant="outline" size="sm" className="gap-1 px-2.5" onClick={() => openEdit(item)}>
        <Pencil className="h-3.5 w-3.5" />
        编辑
      </Button>
      <Button variant="outline" size="sm" className="gap-1 px-2.5" onClick={() => openContent(item)}>
        <ScrollText className="h-3.5 w-3.5" />
        内容
      </Button>
      <Button
        variant="outline"
        size="icon"
        className="table-action-icon-sm-danger"
        title="删除"
        onClick={() => setDeleteTarget(item)}
      >
        <Trash2 className="h-3.5 w-3.5" />
      </Button>
    </div>
  )

  return (
    <>
      <Loading loading={loading} />

      <PageShell
        title="分类管理"
        description="维护站点栏目结构与 SEO 信息"
        actions={
          <Button onClick={() => openAdd(null)}>
            <Plus className="h-4 w-4" />
            新增顶级分类
          </Button>
        }
      >
        {treeData.length === 0 ? (
          <p className="py-12 text-center text-sm text-muted-foreground">暂无分类数据</p>
        ) : (
          <div className="content-panel p-4">
            <div className="mb-3 flex flex-wrap items-center gap-3 rounded-lg border border-dashed border-border/80 bg-muted/25 px-3 py-2 text-xs text-muted-foreground">
              <span className="font-medium text-foreground/80">展示状态</span>
              <span className="inline-flex items-center gap-1.5">
                <span className="inline-flex h-6 w-6 items-center justify-center rounded-md bg-primary/12 text-primary">
                  <Menu className="h-3.5 w-3.5" />
                </span>
                主菜单
              </span>
              <span className="inline-flex items-center gap-1.5">
                <span className="inline-flex h-6 w-6 items-center justify-center rounded-md bg-primary/12 text-primary">
                  <Home className="h-3.5 w-3.5" />
                </span>
                首页
              </span>
              <span className="text-muted-foreground/80">亮色=展示，灰暗=隐藏（悬停可看说明）</span>
            </div>
            <CategoryTree
              data={treeData}
              selectedId={selectedId}
              onSelect={setSelectedId}
              renderActions={renderActions}
              defaultExpandAll
              showVisibility
            />
          </div>
        )}
      </PageShell>

      <Dialog open={formDialogOpen} onOpenChange={setFormDialogOpen}>
        <DialogContent className="max-w-3xl">
          <DialogHeader className="pb-4">
            <DialogTitle>{form.id ? '编辑分类' : '新增分类'}</DialogTitle>
          </DialogHeader>
          <div className="dialog-form-narrow space-y-2.5">
            <div className="dialog-form-row">
              <FormLabel required>分类名称</FormLabel>
              <Input
                value={form.name}
                onChange={(e) => updateField('name', e.target.value)}
                placeholder="请输入分类名称"
              />
            </div>
            <div className="dialog-form-row">
              <FormLabel required>英文名称</FormLabel>
              <Input
                value={form.name_en}
                onChange={(e) => updateField('name_en', e.target.value)}
                placeholder="请输入英文名称（URL 标识）"
              />
            </div>
            <div className="dialog-form-row">
              <Label>上级分类</Label>
              <Select
                value={form.p_id === null ? '__root__' : String(form.p_id)}
                onValueChange={(v) => updateField('p_id', v === '__root__' ? null : Number(v))}
              >
                <SelectTrigger>
                  <SelectValue placeholder="选择上级分类" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="__root__">顶级分类</SelectItem>
                  {parentOptions.map((item) => (
                    <SelectItem key={item.id} value={String(item.id)}>
                      {item.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="dialog-form-row">
              <Label>分类图片</Label>
              <div className="flex items-center gap-3">
                {form.pic_url && (
                  <img
                    src={getMediaUrl(domain, form.pic_url)}
                    alt="预览"
                    className="h-12 w-20 rounded border object-cover"
                  />
                )}
                <FileUpload
                  action="/api/upload_cate_pic/"
                  headers={getAuthHeaders()}
                  label="上传图片"
                  onSuccess={(url) => updateField('pic_url', url)}
                />
              </div>
            </div>
            <div className="dialog-form-row">
              <Label>排序</Label>
              <Input
                type="number"
                className="max-w-[10rem]"
                value={form.sort_num}
                onChange={(e) => updateField('sort_num', Number(e.target.value) || 0)}
              />
            </div>
            <div className="dialog-form-row">
              <Label>SEO 标题</Label>
              <Input
                value={form.seo_title}
                onChange={(e) => updateField('seo_title', e.target.value)}
                placeholder="请输入 SEO 标题"
              />
            </div>
            <div className="dialog-form-row">
              <Label>关键词</Label>
              <Input
                value={form.kws}
                onChange={(e) => updateField('kws', e.target.value)}
                placeholder="多个关键词用逗号分隔"
              />
            </div>
            <div className="dialog-form-row-top">
              <Label>描述</Label>
              <Textarea
                value={form.desc}
                onChange={(e) => updateField('desc', e.target.value)}
                placeholder="请输入分类描述"
                rows={5}
              />
            </div>
            <div className="dialog-form-row">
              <Label>主菜单可见</Label>
              <div className="flex items-center gap-2">
                <Switch
                  checked={form.visiable === 'Y'}
                  onCheckedChange={(checked) => updateField('visiable', checked ? 'Y' : 'N')}
                />
                <Badge variant={form.visiable === 'Y' ? 'success' : 'muted'}>
                  {form.visiable === 'Y' ? '可见' : '隐藏'}
                </Badge>
              </div>
            </div>
            <div className="dialog-form-row">
              <Label>首页可见</Label>
              <div className="flex items-center gap-2">
                <Switch
                  checked={form.home_visiable === 'Y'}
                  onCheckedChange={(checked) => updateField('home_visiable', checked ? 'Y' : 'N')}
                />
                <Badge variant={form.home_visiable === 'Y' ? 'success' : 'muted'}>
                  {form.home_visiable === 'Y' ? '可见' : '隐藏'}
                </Badge>
              </div>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setFormDialogOpen(false)}>
              取消
            </Button>
            <Button onClick={handleSave}>保存</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Dialog
        open={contentDialogOpen}
        onOpenChange={(open) => {
          setContentDialogOpen(open)
          if (!open) setEditorFullScreen(false)
        }}
      >
        <DialogContent
          fullscreen
          hideClose={editorFullScreen}
          onPointerDownOutside={(e) => e.preventDefault()}
        >
          <DialogHeader className="shrink-0 pb-4">
            <DialogTitle>编辑分类内容 — {contentTarget?.name}</DialogTitle>
          </DialogHeader>
          <div className="flex min-h-0 flex-1 flex-col overflow-hidden">
            <RichTextEditor
              key={contentTarget?.id ?? 'content'}
              className="flex min-h-0 flex-1 flex-col"
              borderless
              value={content}
              onChange={setContent}
              uploadImageUrl="/api/upload_file/"
              uploadImageHeaders={getAuthHeaders()}
              onFullScreenChange={setEditorFullScreen}
            />
          </div>
          <DialogFooter className="shrink-0 justify-center pt-4 sm:justify-center">
            <Button variant="outline" onClick={() => setContentDialogOpen(false)}>
              取消
            </Button>
            <Button onClick={handleSaveContent}>保存</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <ConfirmDialog
        open={!!deleteTarget}
        onOpenChange={(open) => !open && setDeleteTarget(null)}
        title="删除确认"
        description={`确定要删除分类「${deleteTarget?.name}」吗？`}
        onConfirm={handleDelete}
      />
    </>
  )
}
