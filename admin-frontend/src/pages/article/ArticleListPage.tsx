import { useEffect, useMemo, useRef, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { debounce } from 'lodash-es'
import { toast } from 'sonner'
import {
  Archive,
  Layers,
  Clock,
  FolderTree,
  Image,
  Pencil,
  Plus,
  RefreshCw,
  RotateCcw,
  Search,
  Tags,
  Target,
  Trash2,
  Undo2,
  FileText,
  Images,
  Video,
  X,
} from 'lucide-react'
import {
  getArticleListService,
  getArticleCateListService,
  matchArticleKwsService,
  updateArticleCateService,
  updateArticlePrePubService,
  matchSomeArticleKwsService,
  delArticleItemService,
  renewArticleItemService,
  purgeArticleItemService,
  makeThumbPicService,
  searchArticleService,
  getArticleDetailService,
  updateArticleService,
  searchKwService,
  addKwService,
  generateArticleSlugUrlService,
  getAuthHeaders,
} from '@/api/service'
import { Loading } from '@/components/Loading'
import { RichTextEditor } from '@/components/RichTextEditor'
import { CategoryTree } from '@/components/CategoryTree'
import { Pagination } from '@/components/Pagination'
import { FileUpload } from '@/components/FileUpload'
import { ConfirmDialog } from '@/components/ConfirmDialog'
import { DateTimePicker } from '@/components/DateTimePicker'
import { ModalArticleTitles } from '@/components/ModalArticleTitles'
import { Separator } from '@/components/ui/separator'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { PageShell } from '@/components/PageShell'
import { Checkbox } from '@/components/ui/checkbox'
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { FormLabel } from '@/components/FormLabel'
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Textarea } from '@/components/ui/textarea'
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip'
import { findCategoryName, formatDateTime, listToTree, resolveSiteMediaUrl } from '@/lib/utils'
import { cleanInvisibleChars } from '@/utils/clean-text'
import type { ArticleItem, CateItem, KeywordItem } from '@/types'

interface EditForm {
  id: number | null
  title: string
  slug_url: string
  cate_id: number | null
  show_type: number
  content: string
  desc: string
  kws: string[]
  pic_url: string
}

const emptyForm: EditForm = {
  id: null,
  title: '',
  slug_url: '',
  cate_id: null,
  show_type: 1,
  content: '',
  desc: '',
  kws: [],
  pic_url: '',
}

function ArticleTableDateTime({ value }: { value?: string | null }) {
  const text = formatDateTime(value)
  if (!text) return <span className="text-sm text-muted-foreground">-</span>

  const spaceIndex = text.indexOf(' ')
  if (spaceIndex === -1) {
    return <div className="whitespace-nowrap text-sm">{text}</div>
  }

  const date = text.slice(0, spaceIndex)
  const time = text.slice(spaceIndex + 1)

  return (
    <div className="min-w-[5.5rem] text-sm leading-snug">
      <div className="whitespace-nowrap">{date}</div>
      <div className="whitespace-nowrap text-muted-foreground">{time}</div>
    </div>
  )
}

function ArticleTableKeywords({ value }: { value?: string | null }) {
  const text = value?.trim()
  if (!text) return <span className="text-sm text-muted-foreground">-</span>

  return (
    <div className="min-w-[8rem] max-w-[12rem] line-clamp-2 break-words text-sm leading-snug" title={text}>
      {text}
    </div>
  )
}

export function ArticleListPage() {
  const [searchParams, setSearchParams] = useSearchParams()
  const [loadingShow, setLoadingShow] = useState(false)
  const [tableLoading, setTableLoading] = useState(false)
  const [pageNum, setPageNum] = useState(1)
  const [pageSize, setPageSize] = useState(10)
  const [total, setTotal] = useState(0)
  const [keyword, setKeyword] = useState('')
  const [searchMode, setSearchMode] = useState(false)
  const [aiOnly, setAiOnly] = useState(() => searchParams.get('ai') === '1')
  const [selectedCateId, setSelectedCateId] = useState(-1)
  const [dataList, setDataList] = useState<ArticleItem[]>([])
  const [cateList, setCateList] = useState<CateItem[]>([])
  const [cateTreeData, setCateTreeData] = useState<CateItem[]>([])
  const [selectedRows, setSelectedRows] = useState<ArticleItem[]>([])
  const [selectIds, setSelectIds] = useState<number[]>([])

  const [selectCateOpen, setSelectCateOpen] = useState(false)
  const [selectCateId, setSelectCateId] = useState<string>('')

  const [delOpen, setDelOpen] = useState(false)
  const [delMsg, setDelMsg] = useState('')
  const [renewOpen, setRenewOpen] = useState(false)
  const [renewMsg, setRenewMsg] = useState('')
  const [purgeOpen, setPurgeOpen] = useState(false)
  const [purgeMsg, setPurgeMsg] = useState('')
  const [matchOpen, setMatchOpen] = useState(false)
  const [matchMsg, setMatchMsg] = useState('')
  const [prePubOpen, setPrePubOpen] = useState(false)
  const [prePubTime, setPrePubTime] = useState('')
  const [prePubIds, setPrePubIds] = useState<number[]>([])

  const [confirmOneKey, setConfirmOneKey] = useState<'matchAll' | 'matchNone' | 'thumb' | null>(null)

  const [editOpen, setEditOpen] = useState(false)
  const [editForm, setEditForm] = useState<EditForm>(emptyForm)
  const [originalForm, setOriginalForm] = useState<EditForm>(emptyForm)
  const [selectedCategoryName, setSelectedCategoryName] = useState('')
  const [keywordOptions, setKeywordOptions] = useState<KeywordItem[]>([])
  const [keywordLoading, setKeywordLoading] = useState(false)
  const [newKeyword, setNewKeyword] = useState('')
  const [addKeywordLoading, setAddKeywordLoading] = useState(false)
  const [generateSlugLoading, setGenerateSlugLoading] = useState(false)
  const [editorFullScreen, setEditorFullScreen] = useState(false)

  const headers = useMemo(() => getAuthHeaders(), [])
  const rootPath = sessionStorage.getItem('root_path') || ''

  const loadCates = async () => {
    const res = await getArticleCateListService({})
    if (res.code === 0 && res.datas) {
      const list = res.datas as CateItem[]
      setCateList(list)
      setCateTreeData(listToTree(list))
    }
  }

  const loadArticles = async () => {
    setTableLoading(true)
    const res = await getArticleListService({
      cate_id: selectedCateId,
      page_num: pageNum,
      page_size: pageSize,
      ai_only: aiOnly ? 1 : 0,
    })
    if (res.code === 0 && res.datas) {
      setDataList(res.datas as ArticleItem[])
      setTotal(res.total_count || 0)
    } else {
      toast.error(res.message || '获取文章列表失败')
    }
    setTableLoading(false)
  }

  useEffect(() => {
    void loadCates()
  }, [])

  useEffect(() => {
    if (searchParams.get('ai') === '1') {
      setAiOnly(true)
      setSelectedCateId(-1)
      setPageNum(1)
      setSearchMode(false)
    }
  }, [searchParams])

  useEffect(() => {
    if (!searchMode) void loadArticles()
  }, [selectedCateId, pageNum, pageSize, searchMode, aiOnly])

  const doSearch = async (page = 1) => {
    const kw = keyword.trim()
    if (!kw) {
      toast.warning('请输入关键字')
      return
    }
    if (kw.length < 2) {
      toast.warning('请输入至少2个文字')
      return
    }
    setLoadingShow(true)
    setSearchMode(true)
    setPageNum(page)
    const res = await searchArticleService({ keyword: kw, page_size: pageSize, page_num: page })
    if (res.code === 0) {
      setDataList((res.datas as ArticleItem[]) || [])
      setTotal(res.total_count || 0)
    } else {
      toast.error(res.message || '搜索失败')
    }
    setLoadingShow(false)
  }

  const resetFilter = () => {
    setPageNum(1)
    setSearchMode(false)
    setKeyword('')
    setAiOnly(false)
    if (searchParams.get('ai')) {
      setSearchParams({}, { replace: true })
    }
    void loadArticles()
  }

  const toggleRow = (row: ArticleItem, checked: boolean) => {
    setSelectedRows((prev) => (checked ? [...prev, row] : prev.filter((r) => r.id !== row.id)))
  }

  const toggleAll = (checked: boolean) => {
    setSelectedRows(checked ? [...dataList] : [])
  }

  const isRecycleBin = selectedCateId === -2

  const openPurgeConfirm = (rows: ArticleItem[]) => {
    setSelectedRows(rows)
    setPurgeMsg(rows.length === 1 ? rows[0].title : buildSelectionMsg(rows))
    setSelectIds(rows.map((r) => r.source_id))
    setPurgeOpen(true)
  }

  const openDelConfirm = (rows: ArticleItem[]) => {
    setSelectedRows(rows)
    setDelMsg(rows.length === 1 ? rows[0].title : rows.map((r) => r.title).join('\n'))
    setSelectIds(rows.map((r) => r.source_id))
    setDelOpen(true)
  }

  const requireSelection = () => {
    if (!selectedRows.length) {
      toast.warning('请先选择文章')
      return false
    }
    return true
  }

  const buildSelectionMsg = (rows: ArticleItem[], idField: 'id' | 'source_id' = 'id') => {
    setSelectIds(rows.map((r) => r[idField]))
    return rows.map((r) => r.title).join('\n')
  }

  const openEditModal = async (article?: ArticleItem) => {
    if (!article?.id) {
      const cateId = selectedCateId > 0 ? selectedCateId : null
      const form = { ...emptyForm, cate_id: cateId }
      setEditForm(form)
      setOriginalForm(form)
      setSelectedCategoryName(findCategoryName(cateTreeData, cateId))
      setEditOpen(true)
      return
    }

    setLoadingShow(true)
    try {
      const res = await getArticleDetailService({ article_id: article.id })
      if (res.code === 0 && res.data) {
        const detail = res.data as { info: EditForm; kws?: string[] }
        const form: EditForm = {
          id: detail.info.id ?? article.id ?? null,
          title: detail.info.title || article.title,
          slug_url: detail.info.slug_url || '',
          cate_id: detail.info.cate_id || article.cate_id || null,
          show_type: detail.info.show_type || 1,
          content: detail.info.content || '',
          desc: detail.info.desc || '',
          kws: [...(detail.kws || [])],
          pic_url: detail.info.pic_url || '',
        }
        setEditForm(form)
        setOriginalForm({ ...form, kws: [...form.kws] })
        setSelectedCategoryName(findCategoryName(cateTreeData, form.cate_id))
        setKeywordOptions((detail.kws || []).map((kw) => ({ id: 0, kw })))
      }
    } catch {
      toast.warning('网络错误，仅显示基本信息')
      const form = {
        ...emptyForm,
        id: article.id,
        title: article.title,
        cate_id: article.cate_id || null,
      }
      setEditForm(form)
      setOriginalForm(form)
    } finally {
      setLoadingShow(false)
      setEditOpen(true)
    }
  }

  const hasContentChanged = () => {
    return (
      editForm.title !== originalForm.title ||
      editForm.slug_url !== originalForm.slug_url ||
      editForm.cate_id !== originalForm.cate_id ||
      editForm.show_type !== originalForm.show_type ||
      editForm.content !== originalForm.content ||
      editForm.desc !== originalForm.desc ||
      editForm.pic_url !== originalForm.pic_url ||
      JSON.stringify(editForm.kws) !== JSON.stringify(originalForm.kws)
    )
  }

  const closeEditModal = () => {
    setEditOpen(false)
    setEditorFullScreen(false)
    setEditForm(emptyForm)
    setOriginalForm(emptyForm)
    setSelectedCategoryName('')
    setNewKeyword('')
    setKeywordOptions([])
  }

  const handleEditCancel = () => {
    if (hasContentChanged()) {
      if (window.confirm('文章内容已修改，是否存为草稿？点击取消将不保存直接关闭。')) {
        void handleEditSubmit(false)
      } else {
        closeEditModal()
      }
    } else {
      closeEditModal()
    }
  }

  const handleEditSubmit = async (publish = false) => {
    if (!editForm.title.trim()) {
      toast.error('请输入文章标题')
      return
    }
    if (!editForm.slug_url.trim()) {
      toast.error('请输入英文链接')
      return
    }
    setLoadingShow(true)
    const res = await updateArticleService({
      article_id: editForm.id ?? null,
      title: cleanInvisibleChars(editForm.title),
      slug_url: cleanInvisibleChars(editForm.slug_url),
      cate_id: editForm.cate_id,
      show_type: editForm.show_type,
      content: cleanInvisibleChars(editForm.content),
      desc: cleanInvisibleChars(editForm.desc),
      kws: editForm.kws,
      pic_url: editForm.pic_url,
      publish: publish === true,
    })
    if (res.code === 0 && res.ret) {
      toast.success(publish ? '文章已发布' : '草稿已保存')
      closeEditModal()
      searchMode ? void doSearch(pageNum) : void loadArticles()
    } else {
      toast.error(res.message || (publish ? '发布失败' : '保存失败'))
    }
    setLoadingShow(false)
  }

  const generateSlugUrl = async () => {
    const title = editForm.title.trim()
    if (!title) return
    setGenerateSlugLoading(true)
    const res = await generateArticleSlugUrlService({ article_title: title })
    if (res.code === 0 && res.data) {
      const data = res.data as { slug_url?: string }
      setEditForm((f) => ({ ...f, slug_url: data.slug_url || '' }))
    } else {
      toast.error(res.message || '生成失败')
    }
    setGenerateSlugLoading(false)
  }

  const searchKeywordsDebounced = useRef(
    debounce(async (query: string) => {
      if (!query) {
        setKeywordOptions([])
        return
      }
      setKeywordLoading(true)
      const res = await searchKwService({ keyword: query.trim(), page_num: 1, page_size: 10 })
      if (res.code === 0 && res.data) {
        setKeywordOptions(res.data as KeywordItem[])
      } else {
        setKeywordOptions([])
      }
      setKeywordLoading(false)
    }, 500),
  ).current

  const addNewKeyword = async () => {
    const kw = newKeyword.trim()
    if (!kw) {
      toast.warning('请输入关键词')
      return
    }
    setAddKeywordLoading(true)
    const res = await addKwService({ kw })
    if (res.code === 0 && res.ret) {
      toast.success('关键词添加成功')
      if (!editForm.kws.includes(kw)) {
        setEditForm((f) => ({ ...f, kws: [...f.kws, kw] }))
      }
      setNewKeyword('')
    } else {
      toast.error(res.message || '添加失败')
    }
    setAddKeywordLoading(false)
  }

  const getArticleUrl = (row: ArticleItem) => {
    const domain = sessionStorage.getItem('domain') || ''
    let url = `//${domain}`
    if (row.p_cate_name_en) url += `/${row.p_cate_name_en}`
    if (row.cate_name_en) url += `/${row.cate_name_en}`
    url += row.slug_url ? `/${row.slug_url}` : `/${row.source_id}.html`
    return url
  }

  const getShowTypeIcon = (type?: number) => {
    if (type === 3) return <Video className="h-4 w-4 shrink-0 text-muted-foreground" />
    if (type === 2) return <Images className="h-4 w-4 shrink-0 text-muted-foreground" />
    return <FileText className="h-4 w-4 shrink-0 text-muted-foreground" />
  }

  const handleOneKey = async () => {
    if (!confirmOneKey) return
    const key = confirmOneKey
    setConfirmOneKey(null)
    setLoadingShow(true)
    try {
      if (key === 'matchAll' || key === 'matchNone') {
        const res = await matchArticleKwsService({ flag: key === 'matchAll' ? 'all' : 'none' })
        if (res.code === 0 && res.ret) {
          toast.success('匹配关键词完成')
          void loadArticles()
        } else {
          toast.error(res.message || '匹配关键词失败')
        }
      } else if (key === 'thumb') {
        const res = await makeThumbPicService({})
        if (res.code === 0 && res.ret) {
          toast.success('生成缩略图完成')
          void loadArticles()
        } else {
          toast.error(res.message || '生成缩略图失败')
        }
      }
    } catch (e) {
      toast.error(`操作失败：${String(e)}`)
    } finally {
      setLoadingShow(false)
    }
  }

  return (
    <>
      <Loading loading={loadingShow} />
      <PageShell
        title="文章管理"
        description="按分类浏览、编辑与发布文章内容"
        actions={
          <div className="flex max-w-full flex-col items-end gap-2">
            <div className="flex flex-wrap items-center justify-end gap-2">
              <Input
                className="h-9 w-72 min-w-[18rem]"
                placeholder="请输入文章完整标题"
                value={keyword}
                onChange={(e) => setKeyword(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && void doSearch(1)}
              />
              <Button variant="outline" onClick={() => void doSearch(1)}>
                <Search className="h-4 w-4" /> 查找
              </Button>
              <Button variant="outline" onClick={resetFilter}>
                <RotateCcw className="h-4 w-4" /> 重置
              </Button>
              {aiOnly && (
                <Badge variant="secondary" className="h-9 px-3">仅 AI 文章</Badge>
              )}
            </div>
            <div className="flex flex-wrap items-center justify-end gap-2">
              <Button onClick={() => void openEditModal()}>
                <Plus className="h-4 w-4" /> 新增
              </Button>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button
                    variant="outline"
                    onClick={() => {
                      if (!requireSelection()) return
                      buildSelectionMsg(selectedRows)
                      setSelectCateId(selectedCateId > 0 ? String(selectedCateId) : '')
                      setSelectCateOpen(true)
                    }}
                  >
                    <FolderTree className="h-4 w-4" /> 归类
                  </Button>
                </TooltipTrigger>
                <TooltipContent>将文章归到指定类别</TooltipContent>
              </Tooltip>
              <Button
                variant="outline"
                onClick={() => {
                  if (!requireSelection()) return
                  setPrePubIds(selectedRows.map((r) => r.id))
                  setPrePubOpen(true)
                }}
              >
                <Clock className="h-4 w-4" /> 定时发布
              </Button>
              <Button
                variant="outline"
                onClick={() => {
                  if (!requireSelection()) return
                  setMatchMsg(buildSelectionMsg(selectedRows, 'source_id'))
                  setSelectIds(selectedRows.map((r) => r.source_id))
                  setMatchOpen(true)
                }}
              >
                <Tags className="h-4 w-4" /> 匹配关键词
              </Button>
              <Button variant="outline" onClick={() => setConfirmOneKey('thumb')}>
                <Image className="h-4 w-4" /> 生成缩略图
              </Button>
              <Button variant="outline" onClick={() => setConfirmOneKey('matchAll')}>
                <Tags className="h-4 w-4" /> 匹配全部文章关键词
              </Button>
              <Button variant="outline" onClick={() => setConfirmOneKey('matchNone')}>
                <Target className="h-4 w-4" /> 匹配未匹配文章关键词
              </Button>
              {!isRecycleBin ? (
                <>
                  <Separator orientation="vertical" className="h-5 shrink-0 self-center" />
                  <Button
                    variant="outline"
                    className="text-destructive hover:text-destructive"
                    onClick={() => {
                      if (!requireSelection()) return
                      openDelConfirm(selectedRows)
                    }}
                  >
                    <Trash2 className="h-4 w-4" /> 删除
                  </Button>
                </>
              ) : (
                <>
                  <Separator orientation="vertical" className="h-5 shrink-0 self-center" />
                  <Button
                    variant="outline"
                    className="text-destructive hover:text-destructive"
                    onClick={() => {
                      if (!requireSelection()) return
                      openPurgeConfirm(selectedRows)
                    }}
                  >
                    <Trash2 className="h-4 w-4" /> 彻底删除
                  </Button>
                </>
              )}
            </div>
          </div>
        }
      >
          <div className="grid min-w-0 grid-cols-1 gap-6 lg:grid-cols-[220px_minmax(0,1fr)]">
            <div className="content-panel p-2">
              <button
                type="button"
                className={`mb-1 flex w-full items-center gap-2 rounded-full px-3 py-2 text-sm transition-colors ${selectedCateId === -1 ? 'bg-sidebar-accent font-medium text-sidebar-accent-foreground' : 'hover:bg-sidebar-accent/80'}`}
                onClick={() => {
                  setSelectedCateId(-1)
                  setPageNum(1)
                }}
              >
                <Layers className="h-4 w-4" /> 全部
              </button>
              <CategoryTree
                data={cateTreeData}
                selectedId={selectedCateId > 0 ? selectedCateId : null}
                onSelect={(id) => {
                  setSelectedCateId(id)
                  setPageNum(1)
                  setSearchMode(false)
                }}
              />
              <button
                type="button"
                className={`mt-1 flex w-full items-center gap-2 rounded-full px-3 py-2 text-sm transition-colors ${selectedCateId === -2 ? 'bg-sidebar-accent font-medium text-sidebar-accent-foreground' : 'hover:bg-sidebar-accent/80'}`}
                onClick={() => {
                  setSelectedCateId(-2)
                  setPageNum(1)
                }}
              >
                <Archive className="h-4 w-4" /> 回收站
              </button>
            </div>

            <div className="min-w-0">
              <div className="content-panel">
                <div className="table-scroll-panel">
                  <Table className="min-w-[76rem] w-max">
                  <TableHeader>
                    <TableRow>
                      <TableHead>
                        <Checkbox
                          checked={selectedRows.length === dataList.length && dataList.length > 0}
                          onCheckedChange={(c) => toggleAll(!!c)}
                        />
                      </TableHead>
                      <TableHead className="min-w-[4rem]">ID</TableHead>
                      <TableHead className="min-w-[20rem]">标题</TableHead>
                      <TableHead className="min-w-[7rem]">类别</TableHead>
                      <TableHead className="min-w-[8rem]">关键词</TableHead>
                      <TableHead className="min-w-[5rem]">发布状态</TableHead>
                      <TableHead className="min-w-[5rem]">浏览次数</TableHead>
                      <TableHead className="min-w-[6rem]">新增时间</TableHead>
                      <TableHead className="min-w-[6rem]">发布时间</TableHead>
                      <TableHead className="table-sticky-action-head min-w-[7rem]">操作</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {tableLoading ? (
                      <TableRow>
                        <TableCell colSpan={10} className="py-8 text-center text-muted-foreground">
                          加载中...
                        </TableCell>
                      </TableRow>
                    ) : dataList.length === 0 ? (
                      <TableRow>
                        <TableCell colSpan={10} className="py-8 text-center text-muted-foreground">
                          暂无数据
                        </TableCell>
                      </TableRow>
                    ) : (
                      dataList.map((row) => (
                        <TableRow key={row.id} className="group">
                          <TableCell>
                            <Checkbox
                              checked={selectedRows.some((r) => r.id === row.id)}
                              onCheckedChange={(c) => toggleRow(row, !!c)}
                            />
                          </TableCell>
                          <TableCell>{row.source_id}</TableCell>
                          <TableCell className="min-w-[20rem] max-w-[24rem]">
                            <a
                              href={getArticleUrl(row)}
                              target="_blank"
                              rel="noreferrer"
                              className="flex items-start gap-1.5 text-primary hover:underline"
                            >
                              <span className="mt-0.5 flex h-4 w-4 shrink-0 items-center justify-center">
                                {getShowTypeIcon(row.show_type)}
                              </span>
                              <span className="line-clamp-2 break-words" title={row.title}>
                                {row.title}
                              </span>
                              {row.ai_generated === 'Y' && (
                                <Badge variant="outline" className="shrink-0 text-xs">AI</Badge>
                              )}
                            </a>
                          </TableCell>
                          <TableCell>{row.cate_name}</TableCell>
                          <TableCell>
                            <ArticleTableKeywords value={row.kws} />
                          </TableCell>
                          <TableCell>
                            <Badge variant={row.pub_status === 'Y' ? 'default' : 'secondary'}>
                              {row.pub_status === 'Y' ? '是' : '否'}
                            </Badge>
                          </TableCell>
                          <TableCell>{row.view_num || 0}</TableCell>
                          <TableCell>
                            <ArticleTableDateTime value={row.add_time} />
                          </TableCell>
                          <TableCell>
                            <ArticleTableDateTime value={row.pub_time} />
                          </TableCell>
                          <TableCell className="table-sticky-action-cell group-hover:bg-muted/50">
                            {row.del_flag === 'N' ? (
                              <div className="flex gap-1">
                                <Button
                                  variant="outline"
                                  size="icon"
                                  className="table-action-icon"
                                  title="编辑"
                                  onClick={() => void openEditModal(row)}
                                >
                                  <Pencil className="h-4 w-4" />
                                </Button>
                                <Button
                                  variant="outline"
                                  size="icon"
                                  className="table-action-icon-danger"
                                  title="删除"
                                  onClick={() => openDelConfirm([row])}
                                >
                                  <Trash2 className="h-4 w-4" />
                                </Button>
                              </div>
                            ) : (
                              <div className="flex gap-1">
                                <Button
                                  variant="outline"
                                  size="icon"
                                  className="table-action-icon"
                                  title="恢复"
                                  onClick={() => {
                                    setSelectedRows([row])
                                    setRenewMsg(row.title)
                                    setSelectIds([row.source_id])
                                    setRenewOpen(true)
                                  }}
                                >
                                  <Undo2 className="h-4 w-4" />
                                </Button>
                                <Button
                                  variant="outline"
                                  size="icon"
                                  className="table-action-icon-danger"
                                  title="彻底删除"
                                  onClick={() => openPurgeConfirm([row])}
                                >
                                  <Trash2 className="h-4 w-4" />
                                </Button>
                              </div>
                            )}
                          </TableCell>
                        </TableRow>
                      ))
                    )}
                  </TableBody>
                </Table>
                </div>
                <div className="border-t border-border/60 px-3 py-2">
                  <Pagination
                    total={total}
                    pageNum={pageNum}
                    pageSize={pageSize}
                    pageSizeOptions={[10, 20, 50, 100, 200]}
                    onPageChange={(p) => {
                      setPageNum(p)
                      if (searchMode) void doSearch(p)
                    }}
                    onPageSizeChange={(s) => {
                      setPageSize(s)
                      setPageNum(1)
                    }}
                  />
                </div>
              </div>
            </div>
          </div>
      </PageShell>

      {/* 选择分类 */}
      <Dialog open={selectCateOpen} onOpenChange={setSelectCateOpen}>
        <DialogContent className="flex flex-col gap-4 sm:max-w-lg">
          <DialogHeader><DialogTitle>选择分类</DialogTitle></DialogHeader>
          <div className="flex flex-col gap-4">
            <ModalArticleTitles titles={selectedRows.map((r) => r.title)} />
            <Select value={selectCateId} onValueChange={setSelectCateId}>
            <SelectTrigger><SelectValue placeholder="选择分类" /></SelectTrigger>
            <SelectContent>
              {cateList.map((c) => (
                <SelectItem key={c.id} value={String(c.id)}>{c.name}</SelectItem>
              ))}
            </SelectContent>
          </Select>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setSelectCateOpen(false)}>取消</Button>
            <Button
              onClick={async () => {
                const res = await updateArticleCateService({ cate_id: Number(selectCateId), aids: selectIds.join('___') })
                if (res.code === 0 && res.ret) {
                  toast.success('操作成功')
                  setSelectCateOpen(false)
                  void loadArticles()
                } else toast.error(res.message || '操作失败')
              }}
            >
              确定
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* 删除 */}
      <ConfirmDialog
        open={delOpen}
        onOpenChange={setDelOpen}
        title="删除确认"
        description={
          delMsg.includes('\n') ? (
            <div className="space-y-2 text-sm">
              <p>确认删除以下 {selectIds.length} 篇文章吗？</p>
              <p className="whitespace-pre-line text-muted-foreground">{delMsg}</p>
              <p className="text-muted-foreground">文章将移入回收站，可在回收站中恢复或彻底删除。</p>
            </div>
          ) : (
            <span>
              确认删除文章 <span className="highlight-text">{delMsg}</span> 吗？文章将移入回收站。
            </span>
          )
        }
        confirmText="删除"
        onConfirm={async () => {
          setDelOpen(false)
          setLoadingShow(true)
          const res = await delArticleItemService({ sids: selectIds })
          if (res.code === 0 && res.ret) {
            toast.success('操作成功')
            if (dataList.length === 1 && pageNum > 1) setPageNum(pageNum - 1)
            void loadArticles()
          } else toast.error(res.message || '操作失败')
          setLoadingShow(false)
        }}
      />

      {/* 恢复 */}
      <ConfirmDialog
        open={renewOpen}
        onOpenChange={setRenewOpen}
        title="恢复文章"
        description={<span>确认恢复文章 <span className="highlight-text">{renewMsg}</span> 吗？</span>}
        onConfirm={async () => {
          setRenewOpen(false)
          setLoadingShow(true)
          const res = await renewArticleItemService({ sids: selectIds })
          if (res.code === 0 && res.ret) {
            toast.success('操作成功')
            void loadArticles()
          } else toast.error(res.message || '操作失败')
          setLoadingShow(false)
        }}
      />

      {/* 彻底删除 */}
      <ConfirmDialog
        open={purgeOpen}
        onOpenChange={setPurgeOpen}
        title="彻底删除确认"
        description={
          <div className="space-y-2 text-sm">
            <p>
              确认彻底删除文章 <span className="highlight-text">{purgeMsg}</span> 吗？
            </p>
            <p className="text-destructive">删除后无法恢复，相关正文、关键词与链接数据将一并清除。</p>
          </div>
        }
        confirmText="彻底删除"
        onConfirm={async () => {
          setPurgeOpen(false)
          setLoadingShow(true)
          const res = await purgeArticleItemService({ sids: selectIds })
          if (res.code === 0 && res.ret) {
            toast.success('彻底删除成功')
            if (dataList.length === 1 && pageNum > 1) setPageNum(pageNum - 1)
            void loadArticles()
          } else {
            toast.error(res.message || '彻底删除失败')
          }
          setLoadingShow(false)
        }}
      />

      {/* 匹配关键词 */}
      <ConfirmDialog
        open={matchOpen}
        onOpenChange={setMatchOpen}
        title="匹配关键词"
        description={<p className="whitespace-pre-line">{matchMsg}</p>}
        onConfirm={async () => {
          setMatchOpen(false)
          setLoadingShow(true)
          const res = await matchSomeArticleKwsService({ sids: selectIds })
          if (res.code === 0 && res.ret) {
            toast.success('操作成功')
            void loadArticles()
          } else toast.error(res.message || '操作失败')
          setLoadingShow(false)
        }}
      />

      {/* 定时发布 */}
      <Dialog open={prePubOpen} onOpenChange={setPrePubOpen}>
        <DialogContent className="flex flex-col gap-4 sm:max-w-lg">
          <DialogHeader><DialogTitle>定时发布</DialogTitle></DialogHeader>
          <div className="flex flex-col gap-4">
            <ModalArticleTitles titles={selectedRows.filter((r) => prePubIds.includes(r.id)).map((r) => r.title)} />
            <DateTimePicker value={prePubTime} onChange={setPrePubTime} />
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setPrePubOpen(false)}>取消</Button>
            <Button
              onClick={async () => {
                setPrePubOpen(false)
                setLoadingShow(true)
                const res = await updateArticlePrePubService({
                  aids: prePubIds.join('___'),
                  pre_pub_time: prePubTime.replace('T', ' ') + ':00',
                })
                if (res.code === 0 && res.ret) {
                  toast.success('操作成功')
                  void loadArticles()
                } else {
                  toast.error(res.message || '操作失败')
                  setPrePubOpen(true)
                }
                setLoadingShow(false)
              }}
            >
              确定
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* 一键操作确认 */}
      <ConfirmDialog
        open={confirmOneKey !== null}
        onOpenChange={() => setConfirmOneKey(null)}
        description={
          confirmOneKey === 'matchAll'
            ? '一键匹配【全部文章】关键词？这将重新执行一次全部文章匹配任务，谨慎使用！'
            : confirmOneKey === 'matchNone'
              ? '一键匹配【未匹配关键词文章】关键词？'
              : '确认一键为所有没有缩略图的文章生成缩略图吗？'
        }
        onConfirm={() => void handleOneKey()}
      />

      {/* 编辑文章 — 全屏，保留左右两栏布局 */}
      <Dialog open={editOpen} onOpenChange={(open) => !open && handleEditCancel()}>
        <DialogContent fullscreen hideClose={editorFullScreen} onPointerDownOutside={(e) => e.preventDefault()}>
          <DialogHeader className="shrink-0 pb-4">
            <DialogTitle>{editForm.id ? '编辑文章' : '新增文章'}</DialogTitle>
          </DialogHeader>
          <div className="min-h-0 flex-1 overflow-y-auto pt-4 pr-6">
            <div className={`grid gap-8 ${editorFullScreen ? 'grid-cols-1' : 'grid-cols-[1fr_240px]'}`}>
              <div className="dialog-form-narrow content-panel flex flex-col gap-4 p-5">
                <div className="dialog-form-row-wide">
                  <FormLabel required>文章标题</FormLabel>
                  <Input
                    value={editForm.title}
                    onChange={(e) => setEditForm((f) => ({ ...f, title: e.target.value }))}
                    onBlur={() => void generateSlugUrl()}
                    placeholder="不超过70个字"
                  />
                </div>
                <div className="dialog-form-row-wide">
                  <FormLabel required>英文链接</FormLabel>
                  <div className="flex gap-2">
                    <Input
                      value={editForm.slug_url}
                      onChange={(e) => setEditForm((f) => ({ ...f, slug_url: e.target.value }))}
                      placeholder="不超过70个字"
                    />
                    <Button variant="outline" disabled={generateSlugLoading} onClick={() => void generateSlugUrl()}>
                      <RefreshCw className={`h-4 w-4 ${generateSlugLoading ? 'animate-spin' : ''}`} />
                    </Button>
                  </div>
                </div>
                <div className="dialog-form-row-wide">
                  <Label>关键词</Label>
                  <div className="min-w-0">
                    <div className="flex gap-2">
                      <Select
                        onValueChange={(v) => {
                          if (!editForm.kws.includes(v)) setEditForm((f) => ({ ...f, kws: [...f.kws, v] }))
                        }}
                      >
                        <SelectTrigger><SelectValue placeholder={keywordLoading ? '搜索中...' : '搜索并选择关键词'} /></SelectTrigger>
                        <SelectContent>
                          {keywordOptions.map((k) => (
                            <SelectItem key={k.id || k.kw} value={k.kw}>{k.kw}</SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                      <Input
                        className="w-40"
                        placeholder="输入新关键词"
                        value={newKeyword}
                        onChange={(e) => {
                          setNewKeyword(e.target.value)
                          searchKeywordsDebounced(e.target.value)
                        }}
                        onKeyDown={(e) => e.key === 'Enter' && void addNewKeyword()}
                      />
                      <Button disabled={addKeywordLoading} onClick={() => void addNewKeyword()}>添加</Button>
                    </div>
                    {editForm.kws.length > 0 && (
                      <div className="mt-2 flex flex-wrap gap-2">
                        {editForm.kws.map((kw) => (
                          <Badge key={kw} variant="secondary" className="cursor-pointer" onClick={() => setEditForm((f) => ({ ...f, kws: f.kws.filter((k) => k !== kw) }))}>
                            {kw} ×
                          </Badge>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
                <div className="dialog-form-row-wide-top">
                  <Label>文章描述</Label>
                  <Textarea rows={3} value={editForm.desc} onChange={(e) => setEditForm((f) => ({ ...f, desc: e.target.value }))} />
                </div>
                <div className="dialog-form-row-wide">
                  <Label>文章分类</Label>
                  <Input value={selectedCategoryName} readOnly placeholder="请从右侧选择分类" />
                </div>
                <div className="dialog-form-row-wide">
                  <Label>文章类型</Label>
                  <RadioGroup
                    value={String(editForm.show_type)}
                    onValueChange={(v) => setEditForm((f) => ({ ...f, show_type: Number(v) }))}
                    className="flex gap-4"
                  >
                    <div className="flex items-center gap-2"><RadioGroupItem value="1" id="t1" /><Label htmlFor="t1">图文</Label></div>
                    <div className="flex items-center gap-2"><RadioGroupItem value="2" id="t2" /><Label htmlFor="t2">图集</Label></div>
                    <div className="flex items-center gap-2"><RadioGroupItem value="3" id="t3" /><Label htmlFor="t3">视频</Label></div>
                  </RadioGroup>
                </div>
                <div className="dialog-form-row-wide-top">
                  <Label>封面图</Label>
                  <div className="flex items-start gap-3">
                    <FileUpload
                      action="/api/upload_file/"
                      headers={headers}
                      onSuccess={(url) => setEditForm((f) => ({ ...f, pic_url: url }))}
                      label="上传封面图"
                    />
                    {editForm.pic_url ? (
                      <div className="group relative shrink-0">
                        <img
                          src={resolveSiteMediaUrl(editForm.pic_url, rootPath)}
                          alt="封面预览"
                          className="h-16 w-24 rounded border object-cover"
                        />
                        <button
                          type="button"
                          className="absolute -right-1.5 -top-1.5 flex h-5 w-5 items-center justify-center rounded-full border bg-background text-muted-foreground shadow-sm transition-colors hover:border-destructive hover:bg-destructive hover:text-destructive-foreground"
                          title="删除封面图"
                          onClick={() => setEditForm((f) => ({ ...f, pic_url: '' }))}
                        >
                          <X className="h-3 w-3" />
                        </button>
                      </div>
                    ) : null}
                  </div>
                </div>
                <div className="dialog-form-row-wide-top">
                  <Label>文章内容</Label>
                  <RichTextEditor
                    value={editForm.content}
                    onChange={(content) => setEditForm((f) => ({ ...f, content }))}
                    uploadImageHeaders={headers}
                    height="calc(100dvh - 26rem)"
                    onFullScreenChange={setEditorFullScreen}
                  />
                </div>
              </div>
              {!editorFullScreen && (
              <div className="content-panel sticky top-0 self-start p-3">
                <h4 className="mb-2 font-medium">选择分类</h4>
                <div className="max-h-[calc(100dvh-12rem)] overflow-y-auto">
                  <CategoryTree
                    data={cateTreeData}
                    selectedId={editForm.cate_id}
                    onSelect={(id) => {
                      setEditForm((f) => ({ ...f, cate_id: id }))
                      setSelectedCategoryName(findCategoryName(cateTreeData, id))
                    }}
                    defaultExpandAll
                  />
                </div>
              </div>
              )}
            </div>
          </div>
          <DialogFooter className="shrink-0 flex-row items-center justify-center gap-2 pt-4 sm:justify-center">
            <Button type="button" variant="outline" onClick={handleEditCancel}>取消</Button>
            <Button type="button" variant="outline" onClick={() => void handleEditSubmit(false)}>存草稿</Button>
            <Separator orientation="vertical" className="h-5 shrink-0 self-center" />
            <Button type="button" onClick={() => void handleEditSubmit(true)}>发布</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  )
}
