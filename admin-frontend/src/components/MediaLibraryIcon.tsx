import { Images } from 'lucide-react'
import { cn } from '@/lib/utils'

/**
 * 与侧栏「媒体库」同源的 Lucide Images。
 * 默认 18px（侧栏）；富文本工具栏传更小尺寸以对齐其它按钮。
 */
export function MediaLibraryIcon({
  className = 'h-[18px] w-[18px]',
}: {
  className?: string
}) {
  return <Images className={cn(className)} strokeWidth={1.75} aria-hidden />
}
