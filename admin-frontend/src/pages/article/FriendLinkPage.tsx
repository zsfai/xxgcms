import { useCallback, useEffect, useState } from 'react'
import { Plus, Pencil, Trash2 } from 'lucide-react'
import { toast } from 'sonner'
import {
  addLinkService,
  delLinkService,
  getAuthHeaders,
  getLinkListService,
  updateLinkService,
} from '@/api/service'
import { ConfirmDialog } from '@/components/ConfirmDialog'
import { FileUpload } from '@/components/FileUpload'
import { Loading } from '@/components/Loading'
import { Pagination } from '@/components/Pagination'
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
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { Textarea } from '@/components/ui/textarea'
import { formatDateTime, getMediaUrl } from '@/lib/utils'
import type { LinkItem } from '@/types'

interface LinkForm {
  id?: number
  name: string
  pic_url: string
  click_url: string
  sort_num: number
  desc: string
  status: string
}

const emptyForm: LinkForm = {
  name: '',
  pic_url: '',
  click_url: '',
  sort_num: 99,
  desc: '',
  status: '0',
}

export function FriendLinkPage() {
  const domain = sessionStorage.getItem('domain') || ''
  const [loading, setLoading] = useState(false)
  const [list, setList] = useState<LinkItem[]>([])
  const [total, setTotal] = useState(0)
  const [pageNum, setPageNum] = useState(1)
  const [pageSize, setPageSize] = useState(10)
  const [dialogOpen, setDialogOpen] = useState(false)
  const [form, setForm] = useState<LinkForm>(emptyForm)
  const [deleteTarget, setDeleteTarget] = useState<LinkItem | null>(null)

  const loadList = useCallback(async () => {
    setLoading(true)
    try {
      const res = await getLinkListService({ page_num: pageNum, page_size: pageSize })
      if (res.code === 0) {
        setList((res.data as LinkItem[]) || [])
        setTotal(res.total_count ?? 0)
      } else {
        toast.error(res.message || '加载友链列表失败')
      }
    } catch (e) {
      toast.error(`加载友链列表失败：${String(e)}`)
    } finally {
      setLoading(false)
    }
  }, [pageNum, pageSize])

  useEffect(() => {
    loadList()
  }, [loadList])

  const openAdd = () => {
    setForm(emptyForm)
    setDialogOpen(true)
  }

  const openEdit = (item: LinkItem) => {
    setForm({
      id: item.id,
      name: item.name || '',
      pic_url: item.pic_url || '',
      click_url: item.click_url || '',
      sort_num: item.sort_num ?? 99,
      desc: item.desc || '',
      status: String(item.status ?? '0'),
    })
    setDialogOpen(true)
  }

  const handleSave = async () => {
    if (!form.name.trim()) {
      toast.error('请填写名称')
      return
    }
    if (!form.pic_url) {
      toast.error('请上传友链图片')
      return
    }

    setLoading(true)
    try {
      const payload = {
        id: form.id,
        name: form.name.trim(),
        pic_url: form.pic_url,
        click_url: form.click_url.trim(),
        sort_num: form.sort_num,
        desc: form.desc.trim(),
        status: form.status,
      }
      const res = form.id ? await updateLinkService(payload) : await addLinkService(payload)

      if (res.code === 0 && res.ret) {
        toast.success(form.id ? '更新成功' : '添加成功')
        setDialogOpen(false)
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

  const handleStatusChange = async (item: LinkItem, checked: boolean) => {
    const status = checked ? '1' : '0'
    try {
      const res = await updateLinkService({
        id: item.id,
        name: item.name,
        pic_url: '',
        click_url: item.click_url,
        sort_num: item.sort_num,
        desc: item.desc || '',
        status,
      })
      if (res.code === 0 && res.ret) {
        toast.success('状态已更新')
        await loadList()
      } else {
        toast.error(res.message || '状态更新失败')
      }
    } catch (e) {
      toast.error(`状态更新失败：${String(e)}`)
    }
  }

  const handleDelete = async () => {
    if (!deleteTarget) return
    setLoading(true)
    try {
      const res = await delLinkService({ id: deleteTarget.id })
      if (res.code === 0 && res.ret) {
        toast.success('删除成功')
        setDeleteTarget(null)
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

  return (
    <>
      <Loading loading={loading} />

      <PageShell
        title="友链管理"
        description="维护站点友情链接与展示顺序"
        actions={
          <Button onClick={openAdd}>
            <Plus className="h-4 w-4" />
            新增友链
          </Button>
        }
      >
        <div className="content-panel">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="min-w-[4rem]">序号</TableHead>
                <TableHead className="min-w-[8rem]">名称</TableHead>
                <TableHead className="min-w-[6rem]">图片</TableHead>
                <TableHead className="min-w-[10rem]">链接</TableHead>
                <TableHead className="min-w-[4rem]">排序</TableHead>
                <TableHead className="min-w-[5rem]">状态</TableHead>
                <TableHead className="min-w-[10rem]">添加时间</TableHead>
                <TableHead className="min-w-[8rem]">描述</TableHead>
                <TableHead className="min-w-[7rem]">操作</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {list.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={9} className="text-center text-muted-foreground">
                    暂无数据
                  </TableCell>
                </TableRow>
              ) : (
                list.map((item, index) => (
                  <TableRow key={item.id}>
                    <TableCell>{(pageNum - 1) * pageSize + index + 1}</TableCell>
                    <TableCell>{item.name}</TableCell>
                    <TableCell>
                      {item.pic_url ? (
                        <img
                          src={getMediaUrl(domain, item.pic_url)}
                          alt={item.name}
                          className="h-10 w-16 rounded object-cover"
                        />
                      ) : (
                        '-'
                      )}
                    </TableCell>
                    <TableCell className="max-w-[180px] whitespace-normal align-top">
                      {item.click_url ? (
                        <a
                          href={item.click_url}
                          target="_blank"
                          rel="noreferrer"
                          className="break-all text-sm leading-snug text-primary hover:underline"
                        >
                          {item.click_url}
                        </a>
                      ) : (
                        '-'
                      )}
                    </TableCell>
                    <TableCell>{item.sort_num}</TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        <Switch
                          checked={String(item.status) === '1'}
                          onCheckedChange={(checked) => handleStatusChange(item, checked)}
                        />
                        <Badge variant={String(item.status) === '1' ? 'success' : 'muted'}>
                          {String(item.status) === '1' ? '有效' : '失效'}
                        </Badge>
                      </div>
                    </TableCell>
                    <TableCell>{formatDateTime(item.add_time)}</TableCell>
                    <TableCell className="max-w-[120px] truncate">{item.desc || '-'}</TableCell>
                    <TableCell>
                      <div className="flex gap-1">
                        <Button
                          variant="outline"
                          size="icon"
                          className="table-action-icon"
                          title="编辑"
                          onClick={() => openEdit(item)}
                        >
                          <Pencil className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="outline"
                          size="icon"
                          className="table-action-icon-danger"
                          title="删除"
                          onClick={() => setDeleteTarget(item)}
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
          <div className="border-t border-border/60 px-3 py-2">
            <Pagination
              total={total}
              pageNum={pageNum}
              pageSize={pageSize}
              onPageChange={setPageNum}
              onPageSizeChange={(size) => {
                setPageSize(size)
                setPageNum(1)
              }}
            />
          </div>
        </div>
      </PageShell>

      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent className="max-w-3xl">
          <DialogHeader className="pb-4">
            <DialogTitle>{form.id ? '编辑友链' : '新增友链'}</DialogTitle>
          </DialogHeader>
          <div className="dialog-form-narrow space-y-2.5">
            <div className="dialog-form-row">
              <FormLabel required>名称</FormLabel>
              <Input
                value={form.name}
                onChange={(e) => setForm((prev) => ({ ...prev, name: e.target.value }))}
                placeholder="请输入友链名称"
              />
            </div>
            <div className="dialog-form-row">
              <FormLabel required>友链图片</FormLabel>
              <div className="flex items-center gap-3">
                {form.pic_url && (
                  <img
                    src={getMediaUrl(domain, form.pic_url)}
                    alt="预览"
                    className="h-16 w-28 rounded border object-cover"
                  />
                )}
                <FileUpload
                  action="/api/upload_link_pic/"
                  headers={getAuthHeaders()}
                  label="上传图片"
                  onSuccess={(url) => setForm((prev) => ({ ...prev, pic_url: url }))}
                />
              </div>
            </div>
            <div className="dialog-form-row">
              <Label>跳转链接</Label>
              <Input
                value={form.click_url}
                onChange={(e) => setForm((prev) => ({ ...prev, click_url: e.target.value }))}
                placeholder="请输入点击跳转链接"
              />
            </div>
            <div className="dialog-form-row">
              <Label>排序</Label>
              <Input
                type="number"
                className="max-w-[10rem]"
                value={form.sort_num}
                onChange={(e) => setForm((prev) => ({ ...prev, sort_num: Number(e.target.value) || 0 }))}
              />
            </div>
            <div className="dialog-form-row-top">
              <Label>描述</Label>
              <Textarea
                value={form.desc}
                onChange={(e) => setForm((prev) => ({ ...prev, desc: e.target.value }))}
                placeholder="请输入描述"
                rows={4}
              />
            </div>
            <div className="dialog-form-row">
              <Label>生效状态</Label>
              <div className="flex items-center gap-3">
                <Switch
                  checked={form.status === '1'}
                  onCheckedChange={(checked) =>
                    setForm((prev) => ({ ...prev, status: checked ? '1' : '0' }))
                  }
                />
                <span className="text-sm text-muted-foreground">{form.status === '1' ? '有效' : '失效'}</span>
              </div>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDialogOpen(false)}>
              取消
            </Button>
            <Button onClick={handleSave}>保存</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <ConfirmDialog
        open={!!deleteTarget}
        onOpenChange={(open) => !open && setDeleteTarget(null)}
        title="删除确认"
        description={`确定要删除友链「${deleteTarget?.name}」吗？`}
        onConfirm={handleDelete}
      />
    </>
  )
}
