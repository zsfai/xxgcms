import { useCallback, useEffect, useState } from 'react'
import { toast } from 'sonner'
import { getAuthHeaders, getMediaListService } from '@/api/service'
import { FileKindIcon } from '@/components/FileKindIcon'
import { FileUpload } from '@/components/FileUpload'
import { Loading } from '@/components/Loading'
import { Pagination } from '@/components/Pagination'
import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { cn, getAdminMediaUrl } from '@/lib/utils'
import type { MediaItem } from '@/types'

type FileTypeFilter = '' | 'image' | 'document' | 'video' | 'other'

const TYPE_TABS: { value: FileTypeFilter; label: string }[] = [
  { value: '', label: '全部' },
  { value: 'image', label: '图片' },
  { value: 'document', label: '文档' },
  { value: 'video', label: '视频' },
  { value: 'other', label: '其他' },
]

const MEDIA_ACCEPT = [
  '.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg', '.bmp',
  '.mp4', '.webm', '.mov', '.avi', '.mkv', '.m4v',
  '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.txt', '.md', '.csv',
  '.zip', '.rar', '.7z', '.tar', '.gz',
].join(',')

function mediaPath(item: MediaItem) {
  return item.url || getAdminMediaUrl(item.file_path)
}

interface MediaPickerDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onConfirm: (items: MediaItem[]) => void
  /** 打开时默认类型筛选 */
  defaultFileType?: FileTypeFilter
}

export function MediaPickerDialog({
  open,
  onOpenChange,
  onConfirm,
  defaultFileType = '',
}: MediaPickerDialogProps) {
  const [loading, setLoading] = useState(false)
  const [list, setList] = useState<MediaItem[]>([])
  const [total, setTotal] = useState(0)
  const [pageNum, setPageNum] = useState(1)
  const [pageSize, setPageSize] = useState(24)
  const [fileType, setFileType] = useState<FileTypeFilter>(defaultFileType)
  const [keyword, setKeyword] = useState('')
  const [searchInput, setSearchInput] = useState('')
  const [selected, setSelected] = useState<Record<number, MediaItem>>({})

  const loadList = useCallback(async () => {
    if (!open) return
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
  }, [open, pageNum, pageSize, fileType, keyword])

  useEffect(() => {
    if (!open) return
    setFileType(defaultFileType)
    setKeyword('')
    setSearchInput('')
    setPageNum(1)
    setSelected({})
  }, [open, defaultFileType])

  useEffect(() => {
    void loadList()
  }, [loadList])

  const selectedList = Object.values(selected)
  const selectedCount = selectedList.length

  const toggleSelect = (item: MediaItem) => {
    setSelected((prev) => {
      const next = { ...prev }
      if (next[item.id]) delete next[item.id]
      else next[item.id] = item
      return next
    })
  }

  const handleConfirm = () => {
    if (!selectedCount) {
      toast.error('请先选择文件')
      return
    }
    onConfirm(selectedList)
    onOpenChange(false)
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="flex max-h-[85vh] max-w-4xl flex-col gap-0 overflow-hidden p-0">
        <DialogHeader className="border-b px-5 py-4">
          <DialogTitle>从媒体库选择</DialogTitle>
        </DialogHeader>

        <div className="relative flex min-h-0 flex-1 flex-col gap-3 px-5 py-3">
          <Loading loading={loading} />

          <div className="flex flex-wrap items-center gap-2">
            {TYPE_TABS.map((tab) => (
              <Button
                key={tab.value || 'all'}
                type="button"
                size="sm"
                variant={fileType === tab.value ? 'default' : 'outline'}
                onClick={() => {
                  setFileType(tab.value)
                  setPageNum(1)
                }}
              >
                {tab.label}
              </Button>
            ))}
            <div className="ml-auto flex min-w-[14rem] items-center gap-2">
              <Input
                value={searchInput}
                onChange={(e) => setSearchInput(e.target.value)}
                placeholder="按名称搜索"
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    setPageNum(1)
                    setKeyword(searchInput.trim())
                  }
                }}
              />
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={() => {
                  setPageNum(1)
                  setKeyword(searchInput.trim())
                }}
              >
                搜索
              </Button>
              <FileUpload
                action="/api/upload_media/"
                headers={getAuthHeaders()}
                accept={MEDIA_ACCEPT}
                multiple
                label="上传"
                onSuccess={() => {
                  void loadList()
                }}
              />
            </div>
          </div>

          <div className="min-h-0 flex-1 overflow-y-auto rounded-xl border border-border/60 p-3">
            {list.length === 0 ? (
              <div className="py-16 text-center text-sm text-muted-foreground">暂无文件，请先上传</div>
            ) : (
              <div className="grid grid-cols-3 gap-3 sm:grid-cols-4 md:grid-cols-5 lg:grid-cols-6">
                {list.map((item) => {
                  const active = !!selected[item.id]
                  const path = mediaPath(item)
                  return (
                    <button
                      key={item.id}
                      type="button"
                      onClick={() => toggleSelect(item)}
                      className={cn(
                        'group flex flex-col overflow-hidden rounded-xl border text-left transition-all',
                        active
                          ? 'border-primary ring-2 ring-primary/30'
                          : 'border-border/60 hover:border-primary/40',
                      )}
                    >
                      <div className="flex aspect-square items-center justify-center bg-muted/30">
                        {item.file_type === 'image' ? (
                          <img src={path} alt={item.name} className="h-full w-full object-cover" />
                        ) : (
                          <FileKindIcon ext={item.ext} fileType={item.file_type} size="lg" />
                        )}
                      </div>
                      <div className="truncate px-2 py-1.5 text-xs" title={item.name}>
                        {item.name}
                      </div>
                    </button>
                  )
                })}
              </div>
            )}
          </div>

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

        <DialogFooter className="border-t px-5 py-3 sm:justify-between">
          <span className="text-sm text-muted-foreground">
            {selectedCount > 0 ? `已选 ${selectedCount} 项` : '点击文件可选中，支持多选'}
          </span>
          <div className="flex gap-2">
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              取消
            </Button>
            <Button type="button" onClick={handleConfirm} disabled={!selectedCount}>
              插入到编辑器
            </Button>
          </div>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
