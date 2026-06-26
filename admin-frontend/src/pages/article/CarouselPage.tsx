import { useCallback, useEffect, useState } from 'react'
import { Plus, Pencil, Trash2 } from 'lucide-react'
import { toast } from 'sonner'
import {
  addCarouselService,
  delCarouselService,
  getAuthHeaders,
  getCarouselListService,
  updateCarouselService,
  viewCarouselsService,
} from '@/api/service'
import { ConfirmDialog } from '@/components/ConfirmDialog'
import { CarouselPreview } from '@/components/CarouselPreview'
import { ClampedTextWithTooltip } from '@/components/ClampedTextWithTooltip'
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
import type { CarouselItem } from '@/types'

function CarouselCreateTime({ value }: { value?: string }) {
  const text = formatDateTime(value)
  if (!text) return <span className="text-sm text-muted-foreground">-</span>

  const spaceIndex = text.indexOf(' ')
  if (spaceIndex === -1) {
    return <div className="whitespace-nowrap text-sm">{text}</div>
  }

  const date = text.slice(0, spaceIndex)
  const time = text.slice(spaceIndex + 1)

  return (
    <div className="w-[5.5rem] text-sm leading-snug">
      <div className="whitespace-nowrap">{date}</div>
      <div className="whitespace-nowrap text-muted-foreground">{time}</div>
    </div>
  )
}

interface CarouselForm {
  id?: number
  title: string
  pic_url: string
  click_url: string
  sort_num: number
  desc: string
  status: string
}

const emptyForm: CarouselForm = {
  title: '',
  pic_url: '',
  click_url: '',
  sort_num: 99,
  desc: '',
  status: '0',
}

export function CarouselPage() {
  const domain = sessionStorage.getItem('domain') || ''
  const [loading, setLoading] = useState(false)
  const [previewList, setPreviewList] = useState<CarouselItem[]>([])
  const [list, setList] = useState<CarouselItem[]>([])
  const [total, setTotal] = useState(0)
  const [pageNum, setPageNum] = useState(1)
  const [pageSize, setPageSize] = useState(10)
  const [dialogOpen, setDialogOpen] = useState(false)
  const [form, setForm] = useState<CarouselForm>(emptyForm)
  const [deleteTarget, setDeleteTarget] = useState<CarouselItem | null>(null)

  const loadPreview = useCallback(async () => {
    try {
      const res = await viewCarouselsService({})
      if (res.code === 0) {
        setPreviewList((res.data as CarouselItem[]) || [])
      }
    } catch (e) {
      toast.error(`加载轮播预览失败：${String(e)}`)
    }
  }, [])

  const loadList = useCallback(async () => {
    setLoading(true)
    try {
      const res = await getCarouselListService({ page_num: pageNum, page_size: pageSize })
      if (res.code === 0) {
        setList((res.data as CarouselItem[]) || [])
        setTotal(res.total_count ?? 0)
      } else {
        toast.error(res.message || '加载轮播列表失败')
      }
    } catch (e) {
      toast.error(`加载轮播列表失败：${String(e)}`)
    } finally {
      setLoading(false)
    }
  }, [pageNum, pageSize])

  useEffect(() => {
    loadPreview()
  }, [loadPreview])

  useEffect(() => {
    loadList()
  }, [loadList])

  const openAdd = () => {
    setForm(emptyForm)
    setDialogOpen(true)
  }

  const openEdit = (item: CarouselItem) => {
    setForm({
      id: item.id,
      title: item.title || '',
      pic_url: item.pic_url || '',
      click_url: item.click_url || '',
      sort_num: item.sort_num ?? 99,
      desc: item.desc || '',
      status: String(item.status ?? '0'),
    })
    setDialogOpen(true)
  }

  const handleSave = async () => {
    if (!form.title.trim()) {
      toast.error('请填写标题')
      return
    }
    if (!form.pic_url) {
      toast.error('请上传轮播图片')
      return
    }

    setLoading(true)
    try {
      const payload = {
        id: form.id,
        title: form.title.trim(),
        pic_url: form.pic_url,
        click_url: form.click_url.trim(),
        sort_num: form.sort_num,
        desc: form.desc.trim(),
        status: form.status,
      }
      const res = form.id
        ? await updateCarouselService(payload)
        : await addCarouselService(payload)

      if (res.code === 0 && res.ret) {
        toast.success(form.id ? '更新成功' : '添加成功')
        setDialogOpen(false)
        await Promise.all([loadList(), loadPreview()])
      } else {
        toast.error(res.message || '保存失败')
      }
    } catch (e) {
      toast.error(`保存失败：${String(e)}`)
    } finally {
      setLoading(false)
    }
  }

  const handleStatusChange = async (item: CarouselItem, checked: boolean) => {
    const status = checked ? '1' : '0'
    try {
      const res = await updateCarouselService({
        id: item.id,
        title: item.title,
        pic_url: '',
        click_url: item.click_url,
        sort_num: item.sort_num,
        desc: item.desc || '',
        status,
      })
      if (res.code === 0 && res.ret) {
        toast.success('状态已更新')
        await Promise.all([loadList(), loadPreview()])
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
      const res = await delCarouselService({ id: deleteTarget.id })
      if (res.code === 0 && res.ret) {
        toast.success('删除成功')
        setDeleteTarget(null)
        await Promise.all([loadList(), loadPreview()])
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
        title="轮播配置"
        description="管理首页轮播图展示与跳转链接"
        actions={
          <Button onClick={openAdd}>
            <Plus className="h-4 w-4" />
            新增轮播
          </Button>
        }
      >
        <div className="content-panel mb-4 p-3">
          {previewList.length === 0 ? (
            <p className="text-sm text-muted-foreground">暂无生效中的轮播图</p>
          ) : (
            <CarouselPreview items={previewList} domain={domain} />
          )}
        </div>

        <div className="content-panel">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="min-w-[4rem]">序号</TableHead>
                <TableHead className="min-w-[8rem]">标题</TableHead>
                <TableHead className="min-w-[6rem]">图片</TableHead>
                <TableHead className="min-w-[10rem]">链接</TableHead>
                <TableHead className="min-w-[4rem]">排序</TableHead>
                <TableHead className="min-w-[5rem]">状态</TableHead>
                <TableHead className="min-w-[4.5rem]">点击</TableHead>
                <TableHead className="w-[5.5rem] min-w-[5.5rem]">创建时间</TableHead>
                <TableHead className="min-w-[8rem]">描述</TableHead>
                <TableHead className="min-w-[7rem]">操作</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {list.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={10} className="text-center text-muted-foreground">
                    暂无数据
                  </TableCell>
                </TableRow>
              ) : (
                list.map((item, index) => (
                  <TableRow key={item.id}>
                    <TableCell>{(pageNum - 1) * pageSize + index + 1}</TableCell>
                    <TableCell className="max-w-[12rem] whitespace-normal align-top">
                      <div className="line-clamp-2 break-words text-sm leading-snug">{item.title}</div>
                    </TableCell>
                    <TableCell>
                      {item.pic_url ? (
                        <img
                          src={getMediaUrl(domain, item.pic_url)}
                          alt={item.title}
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
                          className="line-clamp-2 break-all text-sm leading-snug text-primary hover:underline"
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
                    <TableCell>{item.click_num ?? 0}</TableCell>
                    <TableCell className="whitespace-normal align-top">
                      <CarouselCreateTime value={item.create_time} />
                    </TableCell>
                    <TableCell className="max-w-[120px] whitespace-normal align-top">
                      <ClampedTextWithTooltip text={item.desc} />
                    </TableCell>
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
            <DialogTitle>{form.id ? '编辑轮播' : '新增轮播'}</DialogTitle>
          </DialogHeader>
          <div className="dialog-form-narrow space-y-2.5">
            <div className="dialog-form-row">
              <FormLabel required>标题</FormLabel>
              <Input
                value={form.title}
                onChange={(e) => setForm((prev) => ({ ...prev, title: e.target.value }))}
                placeholder="请输入标题"
              />
            </div>
            <div className="dialog-form-row">
              <FormLabel required>轮播图片</FormLabel>
              <div className="flex items-center gap-3">
                {form.pic_url && (
                  <img
                    src={getMediaUrl(domain, form.pic_url)}
                    alt="预览"
                    className="h-16 w-28 rounded border object-cover"
                  />
                )}
                <FileUpload
                  action="/api/upload_carousel_pic/"
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
        description={`确定要删除轮播「${deleteTarget?.title}」吗？`}
        onConfirm={handleDelete}
      />
    </>
  )
}
