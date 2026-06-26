import { useCallback, useLayoutEffect, useRef, useState } from 'react'
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip'
import { cn } from '@/lib/utils'

interface ClampedTextWithTooltipProps {
  text?: string
  lines?: 1 | 2 | 3
  emptyText?: string
  className?: string
}

export function ClampedTextWithTooltip({
  text,
  lines = 2,
  emptyText = '-',
  className,
}: ClampedTextWithTooltipProps) {
  const ref = useRef<HTMLDivElement>(null)
  const [overflow, setOverflow] = useState(false)

  const checkOverflow = useCallback(() => {
    const el = ref.current
    if (!el) return
    setOverflow(el.scrollHeight > el.clientHeight + 1)
  }, [])

  useLayoutEffect(() => {
    checkOverflow()
    const el = ref.current
    if (!el) return
    const observer = new ResizeObserver(checkOverflow)
    observer.observe(el)
    return () => observer.disconnect()
  }, [text, checkOverflow])

  if (!text) {
    return <span className="text-sm text-muted-foreground">{emptyText}</span>
  }

  const clampClass = lines === 1 ? 'line-clamp-1' : lines === 3 ? 'line-clamp-3' : 'line-clamp-2'

  const body = (
    <div
      ref={ref}
      className={cn(clampClass, 'break-words text-sm leading-snug', overflow && 'cursor-help', className)}
    >
      {text}
    </div>
  )

  if (!overflow) return body

  return (
    <Tooltip>
      <TooltipTrigger asChild>
        <span className="block text-left">{body}</span>
      </TooltipTrigger>
      <TooltipContent side="top" className="max-w-sm whitespace-normal">
        {text}
      </TooltipContent>
    </Tooltip>
  )
}
