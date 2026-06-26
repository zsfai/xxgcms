import { cn } from '@/lib/utils'

interface ModalArticleTitlesProps {
  titles: string[]
  /** 超过该数量才出现滚动条 */
  scrollThreshold?: number
}

export function ModalArticleTitles({ titles, scrollThreshold = 10 }: ModalArticleTitlesProps) {
  if (titles.length === 0) return null
  const scrollable = titles.length > scrollThreshold
  return (
    <ul
      className={cn(
        'space-y-1.5 rounded-lg border border-border/60 bg-muted/30 px-3 py-2.5',
        scrollable && 'max-h-[min(50vh,480px)] overflow-y-auto',
      )}
    >
      {titles.map((title, index) => (
        <li key={index} className="text-sm font-medium leading-relaxed text-orange-500">
          {title}
        </li>
      ))}
    </ul>
  )
}
