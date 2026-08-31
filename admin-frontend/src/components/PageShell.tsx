import type { ReactNode } from 'react'
import { cn } from '@/lib/utils'

interface PageShellProps {
  title: string
  description?: ReactNode
  actions?: ReactNode
  /** 标题下方与右侧卡片顶对齐的侧栏（如二级菜单） */
  sideNav?: ReactNode
  children: ReactNode
  className?: string
}

function PageHeader({
  title,
  description,
  actions,
}: {
  title: string
  description?: ReactNode
  actions?: ReactNode
}) {
  return (
    <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
      <div className="space-y-1">
        <h1 className="text-[20px] font-semibold leading-tight tracking-tight text-foreground">
          {title}
        </h1>
        {description && (
          <div className="text-[13px] leading-relaxed text-muted-foreground">{description}</div>
        )}
      </div>
      {actions && <div className="flex shrink-0 flex-wrap items-center gap-2">{actions}</div>}
    </div>
  )
}

export function PageShell({ title, description, actions, sideNav, children, className }: PageShellProps) {
  if (sideNav) {
    return (
      <div className={cn('w-full max-w-[1400px] space-y-5', className)}>
        {/* 标题仅占右侧主栏宽度，与下方卡片左对齐 */}
        <div className="flex items-start gap-6">
          <div className="w-48 shrink-0" aria-hidden />
          <div className="min-w-0 flex-1">
            <PageHeader title={title} description={description} actions={actions} />
          </div>
        </div>
        {/* 二级菜单顶对齐右侧卡片主区域 */}
        <div className="flex items-start gap-6">
          <aside className="sticky top-0 w-48 shrink-0">{sideNav}</aside>
          <div className="min-w-0 flex-1 space-y-5">{children}</div>
        </div>
      </div>
    )
  }

  return (
    <div className={cn('w-full max-w-[1400px] space-y-5', className)}>
      <PageHeader title={title} description={description} actions={actions} />
      <div className="space-y-5">{children}</div>
    </div>
  )
}
