import { useCallback, useEffect, useState } from 'react'
import { Search, RotateCcw } from 'lucide-react'
import { toast } from 'sonner'
import { getLoginLogListService } from '@/api/service'
import { DateTimePicker } from '@/components/DateTimePicker'
import { Loading } from '@/components/Loading'
import { Pagination } from '@/components/Pagination'
import { PageShell } from '@/components/PageShell'
import { SystemSecondaryNav } from '@/pages/sys/SystemSecondaryNav'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { formatDateTime } from '@/lib/utils'

interface LoginLogRow {
  id: number
  user_name: string
  action: string
  ip?: string
  user_agent?: string
  message?: string
  create_time?: string
}

const ACTION_LABEL: Record<string, string> = {
  login_success: '登录成功',
  login_fail: '登录失败',
  logout: '登出',
}

const ACTION_VARIANT: Record<string, 'default' | 'secondary' | 'destructive' | 'outline'> = {
  login_success: 'default',
  login_fail: 'destructive',
  logout: 'secondary',
}

export function LoginLogPage() {
  const [loading, setLoading] = useState(false)
  const [list, setList] = useState<LoginLogRow[]>([])
  const [total, setTotal] = useState(0)
  const [pageNum, setPageNum] = useState(1)
  const [pageSize, setPageSize] = useState(20)
  const [userName, setUserName] = useState('')
  const [action, setAction] = useState('all')
  const [startTime, setStartTime] = useState('')
  const [endTime, setEndTime] = useState('')
  const [query, setQuery] = useState({
    user_name: '',
    action: '',
    start_time: '',
    end_time: '',
  })

  const loadList = useCallback(async () => {
    setLoading(true)
    try {
      const res = await getLoginLogListService({
        page_num: pageNum,
        page_size: pageSize,
        user_name: query.user_name,
        action: query.action,
        start_time: query.start_time ? query.start_time.replace('T', ' ') : '',
        end_time: query.end_time ? query.end_time.replace('T', ' ') : '',
      })
      if (res.code === 0) {
        setList((res.datas as LoginLogRow[]) || [])
        setTotal(res.total_count ?? 0)
      } else {
        toast.error(res.message || '加载登录日志失败')
      }
    } catch (e) {
      toast.error(`加载登录日志失败：${String(e)}`)
    } finally {
      setLoading(false)
    }
  }, [pageNum, pageSize, query])

  useEffect(() => {
    void loadList()
  }, [loadList])

  const applyFilter = () => {
    setPageNum(1)
    setQuery({
      user_name: userName.trim(),
      action: action === 'all' ? '' : action,
      start_time: startTime,
      end_time: endTime,
    })
  }

  const resetFilter = () => {
    setUserName('')
    setAction('all')
    setStartTime('')
    setEndTime('')
    setPageNum(1)
    setQuery({ user_name: '', action: '', start_time: '', end_time: '' })
  }

  return (
    <>
      <Loading loading={loading} />
      <PageShell
        title="登录日志"
        description="查看管理后台登录成功、失败与登出记录"
        sideNav={<SystemSecondaryNav />}
      >
        <div className="content-panel mb-4 space-y-3 p-4">
          <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
            <div className="space-y-1.5">
              <Label htmlFor="login-log-user">账号</Label>
              <Input
                id="login-log-user"
                className="h-9"
                value={userName}
                onChange={(e) => setUserName(e.target.value)}
                placeholder="用户名"
                onKeyDown={(e) => e.key === 'Enter' && applyFilter()}
              />
            </div>
            <div className="space-y-1.5">
              <Label>结果</Label>
              <Select value={action} onValueChange={setAction}>
                <SelectTrigger className="h-9">
                  <SelectValue placeholder="全部" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">全部</SelectItem>
                  <SelectItem value="login_success">登录成功</SelectItem>
                  <SelectItem value="login_fail">登录失败</SelectItem>
                  <SelectItem value="logout">登出</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <DateTimePicker
              label="开始时间"
              placeholder="选择开始时间"
              value={startTime}
              onChange={setStartTime}
              triggerClassName="h-9 rounded-md"
            />
            <DateTimePicker
              label="结束时间"
              placeholder="选择结束时间"
              value={endTime}
              onChange={setEndTime}
              triggerClassName="h-9 rounded-md"
            />
          </div>
          <div className="flex flex-wrap gap-2">
            <Button className="h-9" onClick={applyFilter}>
              <Search className="h-4 w-4" />
              查询
            </Button>
            <Button className="h-9" variant="outline" onClick={resetFilter}>
              <RotateCcw className="h-4 w-4" />
              重置
            </Button>
          </div>
        </div>

        <div className="content-panel">
          <div className="table-scroll-panel">
            <Table className="min-w-[56rem]">
              <TableHeader>
                <TableRow>
                  <TableHead className="w-16">ID</TableHead>
                  <TableHead className="min-w-[7rem]">账号</TableHead>
                  <TableHead className="min-w-[6rem]">结果</TableHead>
                  <TableHead className="min-w-[8rem]">IP</TableHead>
                  <TableHead className="min-w-[14rem]">User-Agent</TableHead>
                  <TableHead className="min-w-[8rem]">说明</TableHead>
                  <TableHead className="min-w-[10rem]">时间</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {list.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={7} className="h-24 text-center text-muted-foreground">
                      暂无登录日志
                    </TableCell>
                  </TableRow>
                ) : (
                  list.map((row) => (
                    <TableRow key={row.id}>
                      <TableCell className="tabular-nums text-muted-foreground">{row.id}</TableCell>
                      <TableCell>{row.user_name || '—'}</TableCell>
                      <TableCell>
                        <Badge variant={ACTION_VARIANT[row.action] || 'outline'}>
                          {ACTION_LABEL[row.action] || row.action}
                        </Badge>
                      </TableCell>
                      <TableCell className="font-mono text-xs">{row.ip || '—'}</TableCell>
                      <TableCell
                        className="max-w-[18rem] truncate text-xs text-muted-foreground"
                        title={row.user_agent}
                      >
                        {row.user_agent || '—'}
                      </TableCell>
                      <TableCell className="max-w-[10rem] truncate text-sm text-muted-foreground" title={row.message}>
                        {row.message || '—'}
                      </TableCell>
                      <TableCell className="whitespace-nowrap tabular-nums text-sm">
                        {formatDateTime(row.create_time)}
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </div>
        </div>

        <Pagination
          pageNum={pageNum}
          pageSize={pageSize}
          total={total}
          onPageChange={setPageNum}
          onPageSizeChange={(size) => {
            setPageSize(size)
            setPageNum(1)
          }}
        />
      </PageShell>
    </>
  )
}
