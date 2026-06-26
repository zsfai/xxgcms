import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ChevronDown, Globe2, KeyRound, LogOut, RefreshCw } from 'lucide-react'
import { toast } from 'sonner'
import { getSiteListService, refreshSysService } from '@/api/service'
import { ChangePasswordDialog } from '@/components/layout/ChangePasswordDialog'
import { useAppStore } from '@/stores/app-store'
import type { SiteItem } from '@/types'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { Button } from '@/components/ui/button'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'

function getInitials(name: string) {
  const trimmed = name.trim()
  if (!trimmed) return 'U'
  return trimmed.slice(0, 1).toUpperCase()
}

export function TopBar() {
  const navigate = useNavigate()
  const siteNameX = useAppStore((s) => s.siteNameX)
  const changeSiteName = useAppStore((s) => s.changeSiteName)
  const [userName, setUserName] = useState('')
  const [domain, setDomain] = useState('')
  const [siteList, setSiteList] = useState<SiteItem[]>([])
  const [changePasswordOpen, setChangePasswordOpen] = useState(false)

  useEffect(() => {
    setUserName(sessionStorage.getItem('name') || '')
    setDomain(sessionStorage.getItem('domain') || '')
    void loadSites()
  }, [])

  useEffect(() => {
    if (siteNameX) setDomain(siteNameX)
  }, [siteNameX])

  useEffect(() => {
    if (domain && siteList.length) {
      const site = siteList.find((item) => item.name === domain)
      if (site?.root_path) {
        sessionStorage.setItem('root_path', site.root_path)
      }
    }
  }, [domain, siteList])

  const loadSites = async () => {
    const res = await getSiteListService({})
    if (res.code === 0 && res.datas) {
      setSiteList(res.datas as SiteItem[])
    } else {
      toast.error(res.message || '获取站点列表失败')
    }
  }

  const selectSite = (value: string) => {
    setDomain(value)
    changeSiteName(value)
    sessionStorage.setItem('domain', value)
    const site = siteList.find((item) => item.name === value)
    if (site?.root_path) {
      sessionStorage.setItem('root_path', site.root_path)
    } else {
      sessionStorage.removeItem('root_path')
    }
  }

  const refreshSys = async () => {
    const res = await refreshSysService({})
    if (res.code === 0 && res.ret) {
      toast.success('刷新系统配置成功')
    } else {
      toast.error(res.message || '刷新系统配置失败')
    }
  }

  const logout = () => {
    sessionStorage.removeItem('token')
    sessionStorage.removeItem('name')
    sessionStorage.removeItem('domain')
    sessionStorage.removeItem('root_path')
    changeSiteName('')
    navigate('/')
  }

  return (
    <header className="layout-header justify-between px-8">
      <div className="flex items-center gap-2">
        <Select value={domain || undefined} onValueChange={selectSite}>
          <SelectTrigger className="h-9 w-[240px] gap-2 rounded-full bg-background pl-3 text-[13px]">
            <Globe2 className="h-4 w-4 shrink-0 text-primary" strokeWidth={1.75} />
            <SelectValue placeholder="选择站点" />
          </SelectTrigger>
          <SelectContent>
            {siteList.map((item) => (
              <SelectItem key={item.id} value={item.name}>
                {item.name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        <Button
          variant="ghost"
          size="icon"
          className="h-9 w-9 text-muted-foreground hover:bg-primary/10 hover:text-primary"
          title="刷新系统配置"
          onClick={() => void refreshSys()}
        >
          <RefreshCw className="h-4 w-4" strokeWidth={1.75} />
        </Button>
      </div>

      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button
            variant="ghost"
            className="h-9 gap-2 rounded-full px-2 hover:bg-primary/5"
          >
            <span className="relative">
              <Avatar className="h-8 w-8 ring-2 ring-primary/20">
                <AvatarFallback className="bg-primary text-xs font-semibold text-primary-foreground">
                  {getInitials(userName)}
                </AvatarFallback>
              </Avatar>
              <span className="absolute bottom-0 right-0 h-2.5 w-2.5 rounded-full border-2 border-card bg-primary" />
            </span>
            <span className="max-w-[120px] truncate text-[13px] font-medium text-foreground">
              {userName || '用户'}
            </span>
            <ChevronDown className="h-4 w-4 text-muted-foreground" strokeWidth={1.75} />
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end" className="w-52 text-left">
          <DropdownMenuLabel className="font-normal">
            <div className="flex items-center gap-2.5 text-left">
              <Avatar className="h-9 w-9">
                <AvatarFallback className="bg-primary text-xs font-semibold text-primary-foreground">
                  {getInitials(userName)}
                </AvatarFallback>
              </Avatar>
              <div className="min-w-0 text-left">
                <p className="truncate text-sm font-medium">{userName || '用户'}</p>
                <p className="truncate text-xs text-muted-foreground">管理员</p>
              </div>
            </div>
          </DropdownMenuLabel>
          <DropdownMenuSeparator />
          <DropdownMenuItem onClick={() => setChangePasswordOpen(true)} className="min-h-10 gap-2 py-2.5">
            <KeyRound className="h-4 w-4" />
            修改密码
          </DropdownMenuItem>
          <DropdownMenuItem onClick={logout} className="min-h-10 gap-2 py-2.5 text-destructive focus:text-destructive">
            <LogOut className="h-4 w-4" />
            退出登录
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>

      <ChangePasswordDialog open={changePasswordOpen} onOpenChange={setChangePasswordOpen} />
    </header>
  )
}
