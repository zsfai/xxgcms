import type { ReactNode } from 'react'
import { cn } from '@/lib/utils'

interface PageShellProps {
  title: string
  description?: ReactNode
  actions?: ReactNode
  children: ReactNode
  className?: string
}

export function PageShell({ title, description, actions, children, className }: PageShellProps) {
  return (
    <div className={cn('w-full max-w-[1400px] space-y-5', className)}>
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
      <div className="space-y-5">{children}</div>
    </div>
  )
}
