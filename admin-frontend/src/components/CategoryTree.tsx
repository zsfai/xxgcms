import { ChevronDown, ChevronRight, Folder, FolderOpen, Home, Menu } from 'lucide-react'
import { cn } from '@/lib/utils'
import type { CateItem } from '@/types'
import { useState } from 'react'
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip'

interface CategoryTreeProps {
  data: CateItem[]
  selectedId?: number | null
  onSelect?: (id: number) => void
  renderActions?: (item: CateItem) => React.ReactNode
  defaultExpandAll?: boolean
  /** 分类管理页：展示主菜单 / 首页可见状态 */
  showVisibility?: boolean
}

function VisibilityIcon({
  active,
  label,
  icon: Icon,
}: {
  active: boolean
  label: string
  icon: typeof Menu
}) {
  return (
    <Tooltip>
      <TooltipTrigger asChild>
        <span
          className={cn(
            'inline-flex h-6 w-6 items-center justify-center rounded-md transition-colors',
            active
              ? 'bg-primary/12 text-primary'
              : 'bg-transparent text-muted-foreground/35',
          )}
          aria-label={`${label}：${active ? '展示' : '隐藏'}`}
        >
          <Icon className="h-3.5 w-3.5" strokeWidth={active ? 2.25 : 1.75} />
        </span>
      </TooltipTrigger>
      <TooltipContent side="top">
        {label}：{active ? '展示' : '隐藏'}
      </TooltipContent>
    </Tooltip>
  )
}

function CateVisibilityIcons({ item }: { item: CateItem }) {
  const navVisible = item.visiable === 'Y'
  const homeVisible = item.home_visiable === 'Y'
  return (
    <span
      className="inline-flex h-8 shrink-0 items-center gap-0.5 rounded-lg border border-border/50 bg-background/80 px-0.5 shadow-sm"
      onClick={(e) => e.stopPropagation()}
    >
      <VisibilityIcon active={navVisible} label="主菜单" icon={Menu} />
      <span className="h-3 w-px bg-border/70" aria-hidden />
      <VisibilityIcon active={homeVisible} label="首页" icon={Home} />
    </span>
  )
}

function TreeNode({
  item,
  selectedId,
  onSelect,
  renderActions,
  defaultExpandAll,
  showVisibility,
  level = 0,
}: {
  item: CateItem
  selectedId?: number | null
  onSelect?: (id: number) => void
  renderActions?: (item: CateItem) => React.ReactNode
  defaultExpandAll?: boolean
  showVisibility?: boolean
  level?: number
}) {
  const hasChildren = !!item.children?.length
  const [expanded, setExpanded] = useState(defaultExpandAll ?? true)
  const isSelected = selectedId === item.id

  return (
    <div>
      <div
        className={cn(
          'flex min-h-9 items-center gap-1 rounded-lg py-0.5 pr-1 transition-colors',
          isSelected
            ? 'bg-sidebar-accent font-medium text-sidebar-accent-foreground'
            : 'hover:bg-sidebar-accent/80',
        )}
        style={{ paddingLeft: `${level * 12 + 4}px` }}
      >
        {hasChildren ? (
          <button
            type="button"
            className="flex h-8 w-[1.125rem] shrink-0 items-center justify-center rounded text-muted-foreground hover:bg-muted"
            onClick={() => setExpanded(!expanded)}
          >
            {expanded ? <ChevronDown className="h-3.5 w-3.5" /> : <ChevronRight className="h-3.5 w-3.5" />}
          </button>
        ) : (
          <span className="inline-flex h-8 w-[1.125rem] shrink-0 items-center justify-center" />
        )}
        <button
          type="button"
          className={cn(
            'flex h-8 min-w-0 flex-1 items-center gap-1.5 rounded-lg text-left text-sm',
            isSelected ? 'font-semibold' : '',
          )}
          onClick={() => onSelect?.(item.id)}
        >
          {hasChildren ? (
            expanded ? (
              <FolderOpen className="h-4 w-4 shrink-0 opacity-80" />
            ) : (
              <Folder className="h-4 w-4 shrink-0 opacity-80" />
            )
          ) : (
            <Folder className="h-4 w-4 shrink-0 opacity-80" />
          )}
          <span className="truncate">{item.name}</span>
        </button>
        {(showVisibility || renderActions) && (
          <div className="flex shrink-0 items-center gap-2">
            {showVisibility && <CateVisibilityIcons item={item} />}
            {renderActions?.(item)}
          </div>
        )}
      </div>
      {hasChildren && expanded && (
        <div>
          {item.children!.map((child) => (
            <TreeNode
              key={child.id}
              item={child}
              selectedId={selectedId}
              onSelect={onSelect}
              renderActions={renderActions}
              defaultExpandAll={defaultExpandAll}
              showVisibility={showVisibility}
              level={level + 1}
            />
          ))}
        </div>
      )}
    </div>
  )
}

export function CategoryTree({
  data,
  selectedId,
  onSelect,
  renderActions,
  defaultExpandAll,
  showVisibility,
}: CategoryTreeProps) {
  return (
    <TooltipProvider delayDuration={300}>
      <div className="space-y-0.5">
        {data.map((item) => (
          <TreeNode
            key={item.id}
            item={item}
            selectedId={selectedId}
            onSelect={onSelect}
            renderActions={renderActions}
            defaultExpandAll={defaultExpandAll}
            showVisibility={showVisibility}
          />
        ))}
      </div>
    </TooltipProvider>
  )
}
