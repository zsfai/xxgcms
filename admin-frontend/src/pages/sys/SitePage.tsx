import { useCallback, useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Plus, Trash2, Settings2, LayoutDashboard } from 'lucide-react'
import { toast } from 'sonner'
import {
  addSiteService,
  delSiteService,
  getAuthHeaders,
  getSitePageListService,
  testSiteDbService,
  updateSiteService,
} from '@/api/service'
import { ConfirmDialog } from '@/components/ConfirmDialog'
import { FileUpload } from '@/components/FileUpload'
import { Loading } from '@/components/Loading'
import { Pagination } from '@/components/Pagination'
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
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { Textarea } from '@/components/ui/textarea'
import { formatDateTime, getAdminMediaUrl } from '@/lib/utils'
import { useAppStore } from '@/stores/app-store'
import type { SiteItem } from '@/types'
import { SiteSslPanel } from '@/pages/sys/SiteSslPanel'

interface SiteForm {
  id?: number
  name: string
  root_path: string
  sort_num: number
  desc: string
  pic_url: string
  db_host: string
  db_port: number
  db_name: string
  db_user: string
  db_pwd: string
  db_x_host: string
  db_x_port: number
  db_x_name: string
  db_x_user: string
  db_x_pwd: string
}

const emptyForm: SiteForm = {
  name: '',
  root_path: '',
  sort_num: 9999,
  desc: '',
  pic_url: '',
  db_host: '127.0.0.1',
  db_port: 3306,
  db_name: '',
  db_user: '',
  db_pwd: '',
  db_x_host: '127.0.0.1',
  db_x_port: 3306,
  db_x_name: '',
  db_x_user: '',
  db_x_pwd: '',
}

export function SitePage() {
  const navigate = useNavigate()
  const changeSiteName = useAppStore((s) => s.changeSiteName)
  const [loading, setLoading] = useState(false)
  const [loadingText, setLoadingText] = useState('加载中...')
  const [list, setList] = useState<SiteItem[]>([])
  const [total, setTotal] = useState(0)
  const [pageNum, setPageNum] = useState(1)
  const [pageSize, setPageSize] = useState(10)
  const [dialogOpen, setDialogOpen] = useState(false)
  const [form, setForm] = useState<SiteForm>(emptyForm)
  const [deleteTarget, setDeleteTarget] = useState<SiteItem | null>(null)
  const [dialogTab, setDialogTab] = useState<'basic' | 'ssl'>('basic')

  const loadList = useCallback(async () => {
    setLoading(true)
    try {
      const res = await getSitePageListService({ page_num: pageNum, page_size: pageSize })
      if (res.code === 0) {
        setList((res.datas as SiteItem[]) || [])
        setTotal(res.total_count ?? 0)
      } else {
        toast.error(res.message || '加载站点列表失败')
      }
    } catch (e) {
      toast.error(`加载站点列表失败：${String(e)}`)
    } finally {
      setLoading(false)
    }
  }, [pageNum, pageSize])

  useEffect(() => {
    loadList()
  }, [loadList])

  const openAdd = () => {
    setForm(emptyForm)
    setDialogTab('basic')
    setDialogOpen(true)
  }

  const openEdit = (item: SiteItem) => {
    setDialogTab('basic')
    setForm({
      id: item.id,
      name: item.name || '',
      root_path: item.root_path || '',
      sort_num: item.sort_num ?? 9999,
      desc: item.desc || '',
      pic_url: item.pic_url || '',
      db_host: item.db_host || '127.0.0.1',
      db_port: item.db_port ?? 3306,
      db_name: item.db_name || '',
      db_user: item.db_user || '',
      db_pwd: item.db_pwd || '',
      db_x_host: item.db_x_host || '127.0.0.1',
      db_x_port: item.db_x_port ?? 3306,
      db_x_name: item.db_x_name || '',
      db_x_user: item.db_x_user || '',
      db_x_pwd: item.db_x_pwd || '',
    })
    setDialogOpen(true)
  }

  const validateCmsDb = () => {
    if (!form.db_x_host.trim()) {
      toast.error('请填写数据库主机')
      return false
    }
    if (!form.db_x_name.trim()) {
      toast.error('请填写数据库名')
      return false
    }
    if (!form.db_x_user.trim()) {
      toast.error('请填写数据库用户名')
      return false
    }
    return true
  }

  const handleTestDb = async () => {
    if (!validateCmsDb()) return

    setLoading(true)
    setLoadingText('正在测试数据库连接...')
    try {
      const res = await testSiteDbService({
        db_x_host: form.db_x_host.trim(),
        db_x_port: form.db_x_port,
        db_x_name: form.db_x_name.trim(),
        db_x_user: form.db_x_user.trim(),
        db_x_pwd: form.db_x_pwd,
      })
      if (res.code === 0 && res.data) {
        const { database_exists, has_cms_tables, table_count } = res.data
        if (has_cms_tables) {
          toast.success(`连接成功：库「${form.db_x_name}」已存在 CMS 表（共 ${table_count} 张表），保存时将跳过建表`)
        } else if (database_exists) {
          toast.success(`连接成功：库「${form.db_x_name}」已存在但尚无 CMS 表，保存时将自动初始化`)
        } else {
          toast.success(`连接成功：将自动创建库「${form.db_x_name}」并初始化 CMS 数据表`)
        }
      } else {
        toast.error(res.message || '数据库连接测试失败')
      }
    } catch (e) {
      toast.error(`数据库连接测试失败：${String(e)}`)
    } finally {
      setLoading(false)
      setLoadingText('加载中...')
    }
  }

  const handleSave = async () => {
    if (!form.name.trim()) {
      toast.error('请填写域名')
      return
    }
    if (!form.root_path.trim()) {
      toast.error('请填写站点根目录')
      return
    }
    if (!form.id && !validateCmsDb()) {
      return
    }

    setLoading(true)
    setLoadingText(form.id ? '正在保存...' : '正在创建数据库并初始化 CMS 表...')
    try {
      const payload = { ...form, name: form.name.trim(), root_path: form.root_path.trim() }
      const res = form.id ? await updateSiteService(payload) : await addSiteService(payload)

      if (res.code === 0 && res.ret) {
        toast.success(res.message || (form.id ? '更新成功' : '添加成功'))
        setDialogOpen(false)
        await loadList()
      } else {
        toast.error(res.message || '保存失败')
      }
    } catch (e) {
      toast.error(`保存失败：${String(e)}`)
    } finally {
      setLoading(false)
      setLoadingText('加载中...')
    }
  }

  const handleDelete = async () => {
    if (!deleteTarget) return
    setLoading(true)
    try {
      const res = await delSiteService({ id: deleteTarget.id })
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

  const handleManageSite = (item: SiteItem) => {
    sessionStorage.setItem('domain', item.name)
    if (item.root_path) {
      sessionStorage.setItem('root_path', item.root_path)
    } else {
      sessionStorage.removeItem('root_path')
    }
    changeSiteName(item.name)
    navigate('/articles')
  }

  const updateField = <K extends keyof SiteForm>(key: K, value: SiteForm[K]) => {
    setForm((prev) => ({ ...prev, [key]: value }))
  }

  return (
    <>
      <Loading loading={loading} loadingText={loadingText} />

      <PageShell
        title="站点管理"
        description="配置多站点域名、目录及 CMS 数据库；新增站点时将自动建库并初始化数据表"
        actions={
          <Button onClick={openAdd}>
            <Plus className="h-4 w-4" />
            新增站点
          </Button>
        }
      >
        <div className="content-panel">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="min-w-[4rem]">序号</TableHead>
                <TableHead className="min-w-[8rem]">域名</TableHead>
                <TableHead className="min-w-[5rem]">站点图片</TableHead>
                <TableHead className="min-w-[10rem]">根目录</TableHead>
                <TableHead className="min-w-[4rem]">排序</TableHead>
                <TableHead className="min-w-[10rem]">描述</TableHead>
                <TableHead className="min-w-[10rem]">添加时间</TableHead>
                <TableHead className="min-w-[11rem]">操作</TableHead>
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
                    <TableCell>{(pageNum - 1) * pageSize + index + 1}</TableCell>
                    <TableCell>{item.name}</TableCell>
                    <TableCell>
                      {item.pic_url ? (
                        <img
                          src={getAdminMediaUrl(item.pic_url)}
                          alt={item.name}
                          className="h-10 w-16 rounded border object-cover"
                        />
                      ) : (
                        '-'
                      )}
                    </TableCell>
                    <TableCell>{item.root_path || '-'}</TableCell>
                    <TableCell>{item.sort_num ?? '-'}</TableCell>
                    <TableCell className="max-w-[200px] truncate">{item.desc || '-'}</TableCell>
                    <TableCell>{formatDateTime(item.add_time)}</TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        <Button variant="outline" size="sm" onClick={() => handleManageSite(item)}>
                          <LayoutDashboard className="h-4 w-4" />
                          管理
                        </Button>
                        <Button variant="outline" size="sm" onClick={() => openEdit(item)}>
                          <Settings2 className="h-4 w-4" />
                          配置
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
        <DialogContent
          className="max-w-3xl max-h-[90vh] overflow-y-auto"
          onPointerDownOutside={(e) => e.preventDefault()}
          onInteractOutside={(e) => e.preventDefault()}
          onEscapeKeyDown={(e) => e.preventDefault()}
        >
          <DialogHeader>
            <DialogTitle>{form.id ? '配置站点' : '新增站点'}</DialogTitle>
          </DialogHeader>
          {form.id && (
            <div className="flex gap-2 border-b pb-2">
              <Button
                type="button"
                size="sm"
                variant={dialogTab === 'basic' ? 'default' : 'ghost'}
                onClick={() => setDialogTab('basic')}
              >
                基本信息
              </Button>
              <Button
                type="button"
                size="sm"
                variant={dialogTab === 'ssl' ? 'default' : 'ghost'}
                onClick={() => setDialogTab('ssl')}
              >
                域名与证书
              </Button>
            </div>
          )}
          {dialogTab === 'ssl' && form.id ? (
            <SiteSslPanel siteId={form.id} siteName={form.name} />
          ) : (
          <div className="dialog-form-narrow space-y-5">
            <div className="space-y-3">
              <h4 className="text-sm font-medium text-muted-foreground">基本信息</h4>
              <div className="space-y-2.5">
                <div className="dialog-form-row">
                  <FormLabel required>域名</FormLabel>
                  <Input
                    value={form.name}
                    onChange={(e) => updateField('name', e.target.value)}
                    placeholder="请输入域名，如 www.example.com"
                    autoFocus={!form.id}
                  />
                </div>
                <div className="dialog-form-row">
                  <Label>站点图片</Label>
                  <div className="flex items-center gap-3">
                    {form.pic_url && (
                      <img
                        src={getAdminMediaUrl(form.pic_url)}
                        alt="站点图片预览"
                        className="h-16 w-28 rounded border object-cover"
                      />
                    )}
                    <FileUpload
                      action="/api/upload_site_pic/"
                      headers={getAuthHeaders()}
                      label="上传图片"
                      onSuccess={(url) => updateField('pic_url', url)}
                    />
                  </div>
                </div>
                <div className="dialog-form-row">
                  <FormLabel required>根目录</FormLabel>
                  <Input
                    value={form.root_path}
                    onChange={(e) => updateField('root_path', e.target.value)}
                    placeholder="请输入站点根目录"
                  />
                </div>
                <div className="dialog-form-row">
                  <Label>排序</Label>
                  <Input
                    type="number"
                    value={form.sort_num}
                    onChange={(e) => updateField('sort_num', Number(e.target.value) || 0)}
                  />
                </div>
                <div className="dialog-form-row-top">
                  <Label>描述</Label>
                  <Textarea
                    value={form.desc}
                    onChange={(e) => updateField('desc', e.target.value)}
                    placeholder="请输入站点描述"
                    rows={2}
                  />
                </div>
              </div>
            </div>

            <div className="space-y-3">
              <div className="flex items-center justify-between gap-3">
                <h4 className="text-sm font-medium text-muted-foreground">数据库配置</h4>
                <Button type="button" variant="outline" size="sm" onClick={() => void handleTestDb()}>
                  测试连接
                </Button>
              </div>
              <div className="space-y-2.5">
                <div className="dialog-form-row">
                  <FormLabel required>数据库主机</FormLabel>
                  <Input
                    value={form.db_x_host}
                    onChange={(e) => updateField('db_x_host', e.target.value)}
                    placeholder="如 127.0.0.1"
                  />
                </div>
                <div className="dialog-form-row">
                  <Label>端口</Label>
                  <Input
                    type="number"
                    className="max-w-[8rem]"
                    value={form.db_x_port}
                    onChange={(e) => updateField('db_x_port', Number(e.target.value) || 3306)}
                  />
                </div>
                <div className="dialog-form-row">
                  <FormLabel required>数据库名</FormLabel>
                  <Input
                    value={form.db_x_name}
                    onChange={(e) => updateField('db_x_name', e.target.value)}
                    placeholder="新建或已有空库均可"
                  />
                </div>
                <div className="dialog-form-row">
                  <FormLabel required>用户名</FormLabel>
                  <Input value={form.db_x_user} onChange={(e) => updateField('db_x_user', e.target.value)} />
                </div>
                <div className="dialog-form-row">
                  <Label>密码</Label>
                  <Input
                    type="password"
                    value={form.db_x_pwd}
                    onChange={(e) => updateField('db_x_pwd', e.target.value)}
                  />
                </div>
              </div>
            </div>
          </div>
          )}
          {dialogTab === 'basic' && (
            <DialogFooter>
              <Button variant="outline" onClick={() => setDialogOpen(false)}>
                取消
              </Button>
              <Button onClick={handleSave}>保存</Button>
            </DialogFooter>
          )}
        </DialogContent>
      </Dialog>

      <ConfirmDialog
        open={!!deleteTarget}
        onOpenChange={(open) => !open && setDeleteTarget(null)}
        title="删除确认"
        description={`确定要删除站点「${deleteTarget?.name}」吗？`}
        onConfirm={handleDelete}
      />
    </>
  )
}
