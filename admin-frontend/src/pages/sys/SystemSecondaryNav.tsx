import { NavLink, useLocation } from 'react-router-dom'
import { ScrollText, History, type LucideIcon } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'

const secondaryNav: { to: string; label: string; end: boolean; icon: LucideIcon }[] = [
  { to: '/system/login-logs', label: '登录日志', end: true, icon: ScrollText },
  { to: '/system/changelog', label: '更新日志', end: true, icon: History },
]

function isNavActive(pathname: string, to: string, end: boolean) {
  if (end) return pathname === to
  return pathname === to || pathname.startsWith(`${to}/`)
}

/** 系统管理二级菜单：放在 PageShell 标题下方，与右侧卡片对齐 */
export function SystemSecondaryNav() {
  const { pathname } = useLocation()

  return (
    <nav className="flex flex-col gap-2" aria-label="系统管理二级菜单">
      {secondaryNav.map((item) => {
        const Icon = item.icon
        const active = isNavActive(pathname, item.to, item.end)
        return (
          <Button
            key={item.to}
            asChild
            variant={active ? 'default' : 'outline'}
            className={cn(
              'h-auto justify-start gap-2.5 rounded-xl px-3 py-2.5 text-[13px] font-normal shadow-none',
              active && 'font-medium',
            )}
          >
            <NavLink to={item.to} end={item.end}>
              <Icon className="h-4 w-4 shrink-0" strokeWidth={1.75} />
              <span className="truncate">{item.label}</span>
            </NavLink>
          </Button>
        )
      })}
    </nav>
  )
}
