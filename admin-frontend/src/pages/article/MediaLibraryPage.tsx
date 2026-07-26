import { useCallback, useEffect, useState } from 'react'
import { Copy, Eye, Link2, Pencil, Trash2 } from 'lucide-react'
import { toast } from 'sonner'
import {
  delMediaService,
  getAuthHeaders,
  getMediaListService,
  renameMediaService,
} from '@/api/service'
import { ConfirmDialog } from '@/components/ConfirmDialog'
import { FileKindIcon } from '@/components/FileKindIcon'
import { FileUpload } from '@/components/FileUpload'
import { Loading } from '@/components/Loading'
import { Pagination } from '@/components/Pagination'
import { PageShell } from '@/components/PageShell'
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
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { formatDateTime, getAdminMediaUrl } from '@/lib/utils'
import type { MediaItem } from '@/types'

type FileTypeFilter = '' | 'image' | 'document' | 'video' | 'other'

const TYPE_TABS: { value: FileTypeFilter; label: string }[] = [
  { value: '', label: '全部' },
  { value: 'image', label: '图片' },
  { value: 'document', label: '文档' },
  { value: 'video', label: '视频' },
  { value: 'other', label: '其他' },
]

const TYPE_LABEL: Record<string, string> = {
  image: '图片',
  document: '文档',
  video: '视频',
  other: '其他',
}

const MEDIA_ACCEPT = [
  '.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg', '.bmp',
  '.mp4', '.webm', '.mov', '.avi', '.mkv', '.m4v',
  '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.txt', '.md', '.csv',
  '.zip', '.rar', '.7z', '.tar', '.gz',
].join(',')

function formatFileSize(bytes?: number) {
  const size = Number(bytes) || 0
  if (size < 1024) return `${size} B`
  if (size < 1024 * 1024) return `${(size / 1024).toFixed(1)} KB`
  return `${(size / (1024 * 1024)).toFixed(1)} MB`
}

function mediaPath(item: MediaItem) {
  return item.url || getAdminMediaUrl(item.file_path)
}

function mediaAbsoluteUrl(item: MediaItem) {
  const path = mediaPath(item)
  if (!path) return ''
  if (path.startsWith('http://') || path.startsWith('https://') || path.startsWith('//')) {
    return path.startsWith('//') ? `${window.location.protocol}${path}` : path
  }
  return `${window.location.origin}${path.startsWith('/') ? path : `/${path}`}`
}

async function copyText(text: string) {
  if (!text) {
    toast.error('链接为空')
    return
  }
  try {
    await navigator.clipboard.writeText(text)
    toast.success('链接已复制')
  } catch {
    toast.error('复制失败，请手动选择链接')
  }
}

function MediaUrlCell({ item }: { item: MediaItem }) {
  const path = mediaPath(item)
  const absolute = mediaAbsoluteUrl(item)
  return (
    <div className="flex min-w-[14rem] max-w-[22rem] items-center gap-1.5">
      <Link2 className="h-3.5 w-3.5 shrink-0 text-muted-foreground" />
      <a
        href={path}
        target="_blank"
        rel="noreferrer"
        className="min-w-0 flex-1 truncate text-xs text-primary hover:underline"
        title={absolute}
      >
        {path}
      </a>
      <Button
        type="button"
        variant="outline"
        size="icon"
        className="table-action-icon h-7 w-7 shrink-0"
        title="复制链接"
        onClick={() => void copyText(absolute)}
      >
        <Copy className="h-3.5 w-3.5" />
      </Button>
    </div>
  )
}

export function MediaLibraryPage() {
  const [loading, setLoading] = useState(false)
  const [list, setList] = useState<MediaItem[]>([])
  const [total, setTotal] = useState(0)
  const [pageNum, setPageNum] = useState(1)
  const [pageSize, setPageSize] = useState(20)
  const [fileType, setFileType] = useState<FileTypeFilter>('')
  const [keyword, setKeyword] = useState('')
  const [searchInput, setSearchInput] = useState('')
  const [previewItem, setPreviewItem] = useState<MediaItem | null>(null)
  const [renameItem, setRenameItem] = useState<MediaItem | null>(null)
  const [renameName, setRenameName] = useState('')
  const [deleteTarget, setDeleteTarget] = useState<MediaItem | null>(null)

  const loadList = useCallback(async () => {
    setLoading(true)
    try {
      const res = await getMediaListService({
        page_num: pageNum,
        page_size: pageSize,
        file_type: fileType,
        keyword,
      })
      if (res.code === 0) {
        setList((res.datas as MediaItem[]) || [])
        setTotal(res.total_count ?? 0)
      } else {
        toast.error(res.message || '加载媒体列表失败')
      }
    } catch (e) {
      toast.error(`加载媒体列表失败：${String(e)}`)
    } finally {
      setLoading(false)
    }
  }, [pageNum, pageSize, fileType, keyword])

  useEffect(() => {
    loadList()
  }, [loadList])

  const handleSearch = () => {
    setPageNum(1)
    setKeyword(searchInput.trim())
  }

  const handleTypeChange = (value: FileTypeFilter) => {
    setFileType(value)
    setPageNum(1)
  }

  const openRename = (item: MediaItem) => {
    setRenameItem(item)
    setRenameName(item.name || '')
  }

  const handleRename = async () => {
    if (!renameItem) return
    const name = renameName.trim()
    if (!name) {
      toast.error('请填写名称')
      return
    }
    setLoading(true)
    try {
      const res = await renameMediaService({ id: renameItem.id, name })
      if (res.code === 0 && res.ret) {
        toast.success('重命名成功')
        setRenameItem(null)
        await loadList()
      } else {
        toast.error(res.message || '重命名失败')
      }
    } catch (e) {
      toast.error(`重命名失败：${String(e)}`)
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async () => {
    if (!deleteTarget) return
    setLoading(true)
    try {
      const res = await delMediaService({ id: deleteTarget.id })
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

  const showGrid = fileType === 'image'

  return (
    <>
      <Loading loading={loading} />

      <PageShell
        title="媒体库"
        description="按类型管理站点图片、文档、视频及其他文件"
        actions={
          <FileUpload
            action="/api/upload_media/"
            headers={getAuthHeaders()}
            accept={MEDIA_ACCEPT}
            multiple
            label="上传文件"
            onSuccess={() => {
              void loadList()
            }}
          />
        }
      >
        <div className="content-panel space-y-3 p-3">
          <div className="flex flex-wrap items-center gap-2">
            {TYPE_TABS.map((tab) => (
              <Button
                key={tab.value || 'all'}
                type="button"
                size="sm"
                variant={fileType === tab.value ? 'default' : 'outline'}
                onClick={() => handleTypeChange(tab.value)}
              >
                {tab.label}
              </Button>
            ))}
            <div className="ml-auto flex min-w-[16rem] items-center gap-2">
              <Input
                value={searchInput}
                onChange={(e) => setSearchInput(e.target.value)}
                placeholder="按名称搜索"
                onKeyDown={(e) => {
                  if (e.key === 'Enter') handleSearch()
                }}
              />
              <Button type="button" variant="outline" onClick={handleSearch}>
                搜索
              </Button>
            </div>
          </div>

          {showGrid ? (
            <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5">
              {list.length === 0 ? (
                <div className="col-span-full py-12 text-center text-muted-foreground">暂无数据</div>
              ) : (
                list.map((item) => {
                  const path = mediaPath(item)
                  return (
                    <div
                      key={item.id}
                      className="group overflow-hidden rounded-xl border border-border/60 bg-background"
                    >
                      <button
                        type="button"
                        className="block aspect-video w-full overflow-hidden bg-muted/40"
                        onClick={() => setPreviewItem(item)}
                        title="预览"
                      >
                        <img src={path} alt={item.name} className="h-full w-full object-cover" />
                      </button>
                      <div className="space-y-1.5 p-2.5">
                        <div className="truncate text-sm font-medium" title={item.name}>
                          {item.name}
                        </div>
                        <div className="flex items-center gap-1 text-xs text-muted-foreground">
                          <a
                            href={path}
                            target="_blank"
                            rel="noreferrer"
                            className="min-w-0 flex-1 truncate text-primary hover:underline"
                            title={mediaAbsoluteUrl(item)}
                            onClick={(e) => e.stopPropagation()}
                          >
                            {path}
                          </a>
                          <Button
                            type="button"
                            variant="ghost"
                            size="icon"
                            className="h-6 w-6 shrink-0"
                            title="复制链接"
                            onClick={() => void copyText(mediaAbsoluteUrl(item))}
                          >
                            <Copy className="h-3 w-3" />
                          </Button>
                        </div>
                        <div className="text-xs text-muted-foreground">
                          {formatFileSize(item.file_size)}
                        </div>
                        <div className="flex gap-1">
                          <Button
                            variant="outline"
                            size="icon"
                            className="table-action-icon"
                            title="预览"
                            onClick={() => setPreviewItem(item)}
                          >
                            <Eye className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="outline"
                            size="icon"
                            className="table-action-icon"
                            title="重命名"
                            onClick={() => openRename(item)}
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
                      </div>
                    </div>
                  )
                })
              )}
            </div>
          ) : (
            <div className="table-scroll-panel overflow-hidden rounded-xl border border-border/60">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="min-w-[4rem]">序号</TableHead>
                    <TableHead className="min-w-[14rem]">名称</TableHead>
                    <TableHead className="min-w-[16rem]">链接 URL</TableHead>
                    <TableHead className="min-w-[5rem]">类型</TableHead>
                    <TableHead className="min-w-[6rem]">大小</TableHead>
                    <TableHead className="min-w-[10rem]">上传时间</TableHead>
                    <TableHead className="min-w-[8rem]">操作</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {list.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={7} className="text-center text-muted-foreground">
                        暂无数据
                      </TableCell>
                    </TableRow>
                  ) : (
                    list.map((item, index) => (
                      <TableRow key={item.id}>
                        <TableCell>{(pageNum - 1) * pageSize + index + 1}</TableCell>
                        <TableCell>
                          <div className="flex items-center gap-2.5">
                            {item.file_type === 'image' ? (
                              <img
                                src={mediaPath(item)}
                                alt={item.name}
                                className="h-10 w-12 rounded-md border object-cover"
                              />
                            ) : (
                              <FileKindIcon ext={item.ext} fileType={item.file_type} />
                            )}
                            <div className="min-w-0">
                              <div className="truncate font-medium" title={item.name}>
                                {item.name}
                              </div>
                              <div className="text-xs text-muted-foreground">.{item.ext}</div>
                            </div>
                          </div>
                        </TableCell>
                        <TableCell>
                          <MediaUrlCell item={item} />
                        </TableCell>
                        <TableCell>{TYPE_LABEL[item.file_type] || item.file_type}</TableCell>
                        <TableCell>{formatFileSize(item.file_size)}</TableCell>
                        <TableCell>{formatDateTime(item.create_time)}</TableCell>
                        <TableCell>
                          <div className="flex gap-1">
                            <Button
                              variant="outline"
                              size="icon"
                              className="table-action-icon"
                              title="预览"
                              onClick={() => setPreviewItem(item)}
                            >
                              <Eye className="h-4 w-4" />
                            </Button>
                            <Button
                              variant="outline"
                              size="icon"
                              className="table-action-icon"
                              title="复制链接"
                              onClick={() => void copyText(mediaAbsoluteUrl(item))}
                            >
                              <Copy className="h-4 w-4" />
                            </Button>
                            <Button
                              variant="outline"
                              size="icon"
                              className="table-action-icon"
                              title="重命名"
                              onClick={() => openRename(item)}
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
            </div>
          )}

          <div className="border-t border-border/60 pt-2">
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

      <Dialog open={!!previewItem} onOpenChange={(open) => !open && setPreviewItem(null)}>
        <DialogContent className="max-w-3xl">
          <DialogHeader>
            <DialogTitle className="truncate pr-6">{previewItem?.name || '预览'}</DialogTitle>
          </DialogHeader>
          {previewItem && (
            <div className="min-h-[12rem] space-y-3">
              <div className="flex items-center gap-2 rounded-lg border border-border/60 bg-muted/30 px-3 py-2">
                <Link2 className="h-4 w-4 shrink-0 text-muted-foreground" />
                <a
                  href={mediaPath(previewItem)}
                  target="_blank"
                  rel="noreferrer"
                  className="min-w-0 flex-1 truncate text-sm text-primary hover:underline"
                  title={mediaAbsoluteUrl(previewItem)}
                >
                  {mediaAbsoluteUrl(previewItem)}
                </a>
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={() => void copyText(mediaAbsoluteUrl(previewItem))}
                >
                  <Copy className="h-3.5 w-3.5" />
                  复制
                </Button>
              </div>

              {previewItem.file_type === 'image' && (
                <img
                  src={mediaPath(previewItem)}
                  alt={previewItem.name}
                  className="max-h-[70vh] w-full object-contain"
                />
              )}
              {previewItem.file_type === 'video' && (
                <video
                  src={mediaPath(previewItem)}
                  controls
                  className="max-h-[70vh] w-full bg-black"
                />
              )}
              {previewItem.file_type === 'document' && previewItem.ext === 'pdf' && (
                <iframe
                  title={previewItem.name}
                  src={mediaPath(previewItem)}
                  className="h-[70vh] w-full rounded border"
                />
              )}
              {(previewItem.file_type === 'other' ||
                (previewItem.file_type === 'document' && previewItem.ext !== 'pdf')) && (
                <div className="flex flex-col items-center gap-4 py-10 text-center">
                  <FileKindIcon
                    ext={previewItem.ext}
                    fileType={previewItem.file_type}
                    size="lg"
                  />
                  <p className="text-sm text-muted-foreground">
                    该文件类型不支持在线预览，请下载或新窗口打开。
                  </p>
                  <div className="flex gap-2">
                    <Button asChild variant="outline">
                      <a href={mediaPath(previewItem)} target="_blank" rel="noreferrer">
                        新窗口打开
                      </a>
                    </Button>
                    <Button asChild>
                      <a href={mediaPath(previewItem)} download={previewItem.name}>
                        下载
                      </a>
                    </Button>
                  </div>
                </div>
              )}
            </div>
          )}
        </DialogContent>
      </Dialog>

      <Dialog open={!!renameItem} onOpenChange={(open) => !open && setRenameItem(null)}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>重命名</DialogTitle>
          </DialogHeader>
          <div className="dialog-form-narrow space-y-2.5">
            <div className="dialog-form-row">
              <FormLabel required>名称</FormLabel>
              <Input
                value={renameName}
                onChange={(e) => setRenameName(e.target.value)}
                placeholder="请输入文件名称"
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setRenameItem(null)}>
              取消
            </Button>
            <Button onClick={handleRename}>保存</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <ConfirmDialog
        open={!!deleteTarget}
        onOpenChange={(open) => !open && setDeleteTarget(null)}
        title="删除确认"
        description={`确定要删除「${deleteTarget?.name}」吗？删除后将无法从媒体库恢复。`}
        onConfirm={handleDelete}
      />
    </>
  )
}
