import { useCallback, useEffect, useRef, useState } from 'react'
import { Plus, Search, Trash2, Tags, ListChecks, Upload, Pencil } from 'lucide-react'
import { toast } from 'sonner'
import {
  addKwService,
  delKwService,
  getAuthHeaders,
  getKwListService,
  matchKwKwsService,
  matchSomeKwKwsService,
  searchKwService,
  updateKwService,
} from '@/api/service'
import { ConfirmDialog } from '@/components/ConfirmDialog'
import { Loading } from '@/components/Loading'
import { Pagination } from '@/components/Pagination'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { PageShell } from '@/components/PageShell'
import { Checkbox } from '@/components/ui/checkbox'
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { FormLabel } from '@/components/FormLabel'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { cn, formatDateTime } from '@/lib/utils'
import type { KeywordItem } from '@/types'

export function KeywordListPage() {
  const [loading, setLoading] = useState(false)
  const [list, setList] = useState<KeywordItem[]>([])
  const [total, setTotal] = useState(0)
  const [pageNum, setPageNum] = useState(1)
  const [pageSize, setPageSize] = useState(10)
  const [searchKeyword, setSearchKeyword] = useState('')
  const [activeKeyword, setActiveKeyword] = useState('')
  const [selectedIds, setSelectedIds] = useState<number[]>([])
  const [formDialogOpen, setFormDialogOpen] = useState(false)
  const [form, setForm] = useState<{ id?: number; kw: string }>({ kw: '' })
  const [deleteTarget, setDeleteTarget] = useState<KeywordItem | null>(null)
  const excelInputRef = useRef<HTMLInputElement>(null)

  const loadList = useCallback(async () => {
    setLoading(true)
    try {
      const payload = { page_num: pageNum, page_size: pageSize }
      const res = activeKeyword
        ? await searchKwService({ ...payload, keyword: activeKeyword })
        : await getKwListService(payload)

      if (res.code === 0) {
        const rows = (activeKeyword ? res.data : res.datas) as KeywordItem[] | undefined
        setList(rows || [])
        setTotal(res.total_count ?? 0)
        setSelectedIds([])
      } else {
        toast.error(res.message || '加载关键词列表失败')
      }
    } catch (e) {
      toast.error(`加载关键词列表失败：${String(e)}`)
    } finally {
      setLoading(false)
    }
  }, [pageNum, pageSize, activeKeyword])

  useEffect(() => {
    loadList()
  }, [loadList])

  const handleSearch = () => {
    setActiveKeyword(searchKeyword.trim())
    setPageNum(1)
  }

  const openAdd = () => {
    setForm({ kw: '' })
    setFormDialogOpen(true)
  }

  const openEdit = (item: KeywordItem) => {
    setForm({ id: item.id, kw: item.kw })
    setFormDialogOpen(true)
  }

  const handleSave = async () => {
    const kw = form.kw.trim()
    if (!kw) {
      toast.error('请填写关键词')
      return
    }

    setLoading(true)
    try {
      const res = form.id
        ? await updateKwService({ id: form.id, kw })
        : await addKwService({ kw })

      if (res.code === 0 && res.ret) {
        toast.success(form.id ? '更新成功' : '添加成功')
        setFormDialogOpen(false)
        setForm({ kw: '' })
        await loadList()
      } else {
        toast.error(res.message || (form.id ? '更新失败' : '添加失败'))
      }
    } catch (e) {
      toast.error(`${form.id ? '更新' : '添加'}失败：${String(e)}`)
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async () => {
    if (!deleteTarget) return
    setLoading(true)
    try {
      const res = await delKwService({ id: deleteTarget.id })
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

  const handleExcelUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    const ext = file.name.split('.').pop()?.toLowerCase()
    if (ext !== 'xls' && ext !== 'xlsx') {
      toast.error('请上传 xls 或 xlsx 格式的 Excel 文件')
      e.target.value = ''
      return
    }

    setLoading(true)
    try {
      const formData = new FormData()
      formData.append('file', file)
      const res = await fetch('/api/upload_excel/', {
        method: 'POST',
        headers: getAuthHeaders(),
        body: formData,
      })
      const data = await res.json()
      if (data.code === 0) {
        toast.success(`导入成功，新增 ${data.add_kw_count ?? 0} 个关键词`)
        await loadList()
      } else {
        toast.error(data.message || 'Excel 导入失败')
      }
    } catch (err) {
      toast.error(`Excel 导入失败：${String(err)}`)
    } finally {
      setLoading(false)
      e.target.value = ''
    }
  }

  const handleMatchAll = async () => {
    setLoading(true)
    try {
      const res = await matchKwKwsService({})
      if (res.code === 0) {
        toast.success('全部关键词匹配完成')
        await loadList()
      } else {
        toast.error(res.message || '匹配失败')
      }
    } catch (e) {
      toast.error(`匹配失败：${String(e)}`)
    } finally {
      setLoading(false)
    }
  }

  const handleMatchSelected = async () => {
    if (selectedIds.length === 0) {
      toast.error('请先选择要匹配的关键词')
      return
    }

    setLoading(true)
    try {
      const res = await matchSomeKwKwsService({ ids: selectedIds })
      if (res.code === 0 && res.ret) {
        toast.success('选中关键词匹配完成')
        await loadList()
      } else {
        toast.error(res.message || '匹配失败')
      }
    } catch (e) {
      toast.error(`匹配失败：${String(e)}`)
    } finally {
      setLoading(false)
    }
  }

  const toggleSelectAll = (checked: boolean) => {
    setSelectedIds(checked ? list.map((item) => item.id) : [])
  }

  const toggleSelect = (id: number, checked: boolean) => {
    setSelectedIds((prev) => (checked ? [...prev, id] : prev.filter((itemId) => itemId !== id)))
  }

  const allSelected = list.length > 0 && selectedIds.length === list.length

  return (
    <>
      <Loading loading={loading} />

      <PageShell
        title="关键词管理"
        description="维护 SEO 关键词及关联关系"
        actions={
          <div className="flex flex-wrap items-center gap-2">
            <Input
              className="h-9 w-72 min-w-[18rem]"
              placeholder="搜索关键词"
              value={searchKeyword}
              onChange={(e) => setSearchKeyword(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
            />
            <Button variant="outline" onClick={handleSearch}>
              <Search className="h-4 w-4" />
              搜索
            </Button>
            <Button onClick={openAdd}>
              <Plus className="h-4 w-4" />
              新增
            </Button>
            <Button variant="outline" onClick={() => excelInputRef.current?.click()}>
              <Upload className="h-4 w-4" />
              导入
            </Button>
            <Button variant="outline" onClick={handleMatchAll}>
              <Tags className="h-4 w-4" />
              匹配全部
            </Button>
            <Button variant="outline" onClick={handleMatchSelected}>
              <ListChecks className="h-4 w-4" />
              匹配选中
            </Button>
          </div>
        }
      >
        <input
          ref={excelInputRef}
          type="file"
          accept=".xls,.xlsx,application/vnd.ms-excel,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
          className="hidden"
          onChange={handleExcelUpload}
        />

        <div className="content-panel">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>
                  <Checkbox checked={allSelected} onCheckedChange={(v) => toggleSelectAll(v === true)} />
                </TableHead>
                <TableHead className="min-w-[4rem]">序号</TableHead>
                <TableHead className="min-w-[8rem]">关键词</TableHead>
                <TableHead className="min-w-[16rem]">相关关键词</TableHead>
                <TableHead className="min-w-[5rem]">状态</TableHead>
                <TableHead className="min-w-[10rem]">创建时间</TableHead>
                <TableHead className="min-w-[10rem]">更新时间</TableHead>
                <TableHead className="min-w-[7rem]">操作</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {list.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={8} className="text-center text-muted-foreground">
                    暂无数据
                  </TableCell>
                </TableRow>
              ) : (
                list.map((item, index) => (
                  <TableRow key={item.id}>
                    <TableCell>
                      <Checkbox
                        checked={selectedIds.includes(item.id)}
                        onCheckedChange={(v) => toggleSelect(item.id, v === true)}
                      />
                    </TableCell>
                    <TableCell>{(pageNum - 1) * pageSize + index + 1}</TableCell>
                    <TableCell>{item.kw}</TableCell>
                    <TableCell className="max-w-md whitespace-normal align-top">
                      <div className="line-clamp-2 break-words text-sm leading-snug">{item.r_kws || '-'}</div>
                    </TableCell>
                    <TableCell>
                      <Badge
                        variant="outline"
                        className={cn(
                          'font-normal',
                          item.del_flag === 'Y'
                            ? 'text-muted-foreground'
                            : 'border-primary/30 bg-primary/5 text-primary',
                        )}
                      >
                        {item.del_flag === 'Y' ? '已删除' : '正常'}
                      </Badge>
                    </TableCell>
                    <TableCell>{formatDateTime(item.create_time)}</TableCell>
                    <TableCell>{formatDateTime(item.update_time)}</TableCell>
                    <TableCell>
                      <div className="flex items-center gap-1">
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

      <Dialog open={formDialogOpen} onOpenChange={setFormDialogOpen}>
        <DialogContent className="max-w-xl">
          <DialogHeader className="pb-4">
            <DialogTitle>{form.id ? '编辑关键词' : '新增关键词'}</DialogTitle>
          </DialogHeader>
          <div className="dialog-form-row-top dialog-form-row-compact">
            <FormLabel required>关键词</FormLabel>
            <div className="min-w-0 space-y-2">
              <Input
                value={form.kw}
                onChange={(e) => setForm((prev) => ({ ...prev, kw: e.target.value }))}
                placeholder="请输入关键词"
                autoFocus
                onKeyDown={(e) => e.key === 'Enter' && handleSave()}
              />
              {form.id ? (
                <p className="rounded-md border border-amber-200 bg-amber-50 px-3 py-2 text-xs leading-relaxed text-amber-900">
                  修改后，该词原来的前台链接将失效，访问可能出现 404。
                </p>
              ) : null}
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

      <ConfirmDialog
        open={!!deleteTarget}
        onOpenChange={(open) => !open && setDeleteTarget(null)}
        title="删除确认"
        description={
          <div className="space-y-2 text-sm">
            <p>{`确定要删除关键词「${deleteTarget?.kw}」吗？`}</p>
            <p className="text-muted-foreground">
              删除后将同步清理该词的相关关键词关联，以及文章内指向该词的标签链接。
            </p>
            <p className="text-destructive">
              前台原关键词页面与相关链接将失效，可能出现 404，此操作不可恢复。
            </p>
          </div>
        }
        onConfirm={handleDelete}
      />
    </>
  )
}
