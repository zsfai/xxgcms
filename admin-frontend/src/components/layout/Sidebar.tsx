import { NavLink, useLocation } from 'react-router-dom'
import {
  Globe2,
  Newspaper,
  Layers,
  Tag,
  GalleryHorizontal,
  Link,
  SlidersHorizontal,
  PanelLeftClose,
  PanelLeftOpen,
  Sparkles,
  Bot,
  Images,
  Info,
  type LucideIcon,
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { APP_VERSION, BRAND_LOGO_URL, BRAND_NAME } from '@/lib/brand'
import { useAppStore } from '@/stores/app-store'
import { Button } from '@/components/ui/button'

const iconProps = { strokeWidth: 1.75 }

type MenuItem = { to: string; label: string; icon: LucideIcon }

type MenuSection = {
  title: string
  items: MenuItem[]
  requiresSite?: boolean
}

const menuSections: MenuSection[] = [
  {
    title: '全局',
    items: [
      { to: '/sites', label: '站点管理', icon: Globe2 },
      { to: '/ai', label: 'AI 配置', icon: Bot },
    ],
  },
  {
    title: '当前站点',
    requiresSite: true,
    items: [
      { to: '/ai-topics', label: 'AI 选题', icon: Sparkles },
      { to: '/articles', label: '文章管理', icon: Newspaper },
      { to: '/cates', label: '分类管理', icon: Layers },
      { to: '/keywords', label: '关键词', icon: Tag },
      { to: '/carousels', label: '轮播配置', icon: GalleryHorizontal },
      { to: '/links', label: '友链管理', icon: Link },
      { to: '/media', label: '媒体库', icon: Images },
      { to: '/conf', label: '网站配置', icon: SlidersHorizontal },
    ],
  },
]

function SidebarBrand() {
  return (
    <div className="flex min-w-0 items-center gap-2.5">
      <img
        src={BRAND_LOGO_URL}
        alt={BRAND_NAME}
        className="h-8 w-8 shrink-0 rounded-xl object-contain"
      />
      <span className="truncate text-[15px] font-semibold tracking-tight text-foreground">
        {BRAND_NAME}
      </span>
    </div>
  )
}

function pathMatchesMenu(pathname: string, to: string) {
  if (to === '/ai') {
    // 仅匹配 AI 配置子页，避免与 /ai-topics 冲突
    return pathname === '/ai' || pathname.startsWith('/ai/')
  }
  return pathname === to
}

function isSystemPath(pathname: string) {
  return pathname === '/system' || pathname.startsWith('/system/')
}

function SidebarNavItem({
  item,
  collapsed,
  disabled,
}: {
  item: MenuItem
  collapsed: boolean
  disabled?: boolean
}) {
  const location = useLocation()
  const isActive = pathMatchesMenu(location.pathname, item.to)
  const Icon = item.icon
  const title = collapsed ? item.label : disabled ? '请先选择站点' : undefined

  const className = cn(
    'group flex rounded-xl transition-colors duration-150',
    collapsed
      ? 'flex-col items-center gap-1 px-1 py-2'
      : 'items-center gap-3 px-3 py-2 text-[13px]',
    disabled
      ? 'cursor-not-allowed opacity-45'
      : isActive
        ? 'sidebar-nav-active'
        : 'text-muted-foreground hover:bg-primary/5 hover:text-primary',
  )

  const content = (
    <>
      <span
        className={cn(
          'flex shrink-0 items-center justify-center rounded-md transition-colors',
          collapsed ? 'h-8 w-8' : 'h-7 w-7',
          disabled
            ? 'text-muted-foreground/70'
            : isActive
              ? 'bg-primary-foreground/15 text-primary-foreground'
              : 'text-muted-foreground group-hover:bg-primary/10 group-hover:text-primary',
        )}
      >
        <Icon className="h-[18px] w-[18px]" {...iconProps} />
      </span>
      <span
        className={cn(
          collapsed
            ? 'line-clamp-2 text-center text-[10px] leading-tight'
            : 'truncate leading-none',
          !disabled && isActive && 'text-primary-foreground',
        )}
      >
        {item.label}
      </span>
    </>
  )

  if (disabled) {
    return (
      <div className={className} title={title}>
        {content}
      </div>
    )
  }

  return (
    <NavLink key={item.to} to={item.to} title={title} className={className}>
      {content}
    </NavLink>
  )
}

function SystemFooterLink({ collapsed }: { collapsed: boolean }) {
  const location = useLocation()
  const isActive = isSystemPath(location.pathname)

  return (
    <NavLink
      to="/system"
      title="关于"
      className={cn(
        'group flex rounded-xl transition-colors duration-150',
        collapsed
          ? 'flex-col items-center gap-1 px-1 py-2'
          : 'items-center justify-between gap-2 px-3 py-2 text-[13px]',
        isActive
          ? 'sidebar-nav-active'
          : 'text-muted-foreground hover:bg-primary/5 hover:text-primary',
      )}
    >
      <span className={cn('flex min-w-0 items-center', collapsed ? 'flex-col gap-1' : 'gap-2.5')}>
        <span
          className={cn(
            'flex shrink-0 items-center justify-center rounded-md transition-colors',
            collapsed ? 'h-8 w-8' : 'h-7 w-7',
            isActive
              ? 'bg-primary-foreground/15 text-primary-foreground'
              : 'text-muted-foreground group-hover:bg-primary/10 group-hover:text-primary',
          )}
        >
          <Info className="h-[18px] w-[18px]" {...iconProps} />
        </span>
        {!collapsed && (
          <span className={cn('truncate leading-none', isActive && 'text-primary-foreground')}>
            关于
          </span>
        )}
      </span>
      <span
        className={cn(
          'shrink-0 tabular-nums leading-none',
          collapsed ? 'text-[10px]' : 'text-[11px]',
          isActive ? 'text-primary-foreground/80' : 'text-muted-foreground/70',
        )}
      >
        v{APP_VERSION}
      </span>
    </NavLink>
  )
}

export function Sidebar() {
  const collapsed = useAppStore((s) => s.sidebarCollapsed)
  const toggleSidebar = useAppStore((s) => s.toggleSidebar)
  const selectedDomain = useAppStore((s) => s.siteNameX)

  return (
    <aside
      className={cn(
        'flex shrink-0 flex-col border-r border-border bg-card transition-[width] duration-200 ease-out',
        collapsed ? 'w-[4.5rem]' : 'w-60',
      )}
    >
      <div
        className={cn(
          'layout-header',
          collapsed ? 'justify-center px-2' : 'justify-between px-4',
        )}
      >
        {!collapsed && <SidebarBrand />}
        <Button
          variant="ghost"
          size="icon"
          className="h-8 w-8 shrink-0 text-muted-foreground hover:bg-primary/10 hover:text-primary"
          onClick={toggleSidebar}
          title={collapsed ? '展开菜单' : '收起菜单'}
        >
          {collapsed ? (
            <PanelLeftOpen className="h-[18px] w-[18px]" {...iconProps} />
          ) : (
            <PanelLeftClose className="h-[18px] w-[18px]" {...iconProps} />
          )}
        </Button>
      </div>

      <nav className="flex-1 space-y-4 overflow-y-auto p-2">
        {menuSections.map((section) => {
          const sectionDisabled = section.requiresSite && !selectedDomain

          return (
            <div key={section.title} className="space-y-0.5">
              {!collapsed && (
                <div className="px-3 pb-1 pt-1 text-[11px] font-medium uppercase tracking-wider text-muted-foreground/70">
                  {section.title}
                </div>
              )}
              {collapsed && section.requiresSite && (
                <div className="mx-auto mb-1 h-px w-6 bg-border" aria-hidden />
              )}
              {section.items.map((item) => (
                <SidebarNavItem
                  key={item.to}
                  item={item}
                  collapsed={collapsed}
                  disabled={sectionDisabled}
                />
              ))}
            </div>
          )
        })}
      </nav>

      <div className={cn('mt-auto shrink-0 border-t border-border px-2 py-2', collapsed && 'px-1.5')}>
        <SystemFooterLink collapsed={collapsed} />
      </div>
    </aside>
  )
}
