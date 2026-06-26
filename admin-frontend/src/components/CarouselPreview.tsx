import { useEffect, useState } from 'react'
import { ChevronLeft, ChevronRight } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { cn, getMediaUrl } from '@/lib/utils'
import type { CarouselItem } from '@/types'

interface CarouselPreviewProps {
  items: CarouselItem[]
  domain: string
  interval?: number
}

export function CarouselPreview({ items, domain, interval = 4000 }: CarouselPreviewProps) {
  const [activeIndex, setActiveIndex] = useState(0)
  const [paused, setPaused] = useState(false)

  useEffect(() => {
    setActiveIndex(0)
  }, [items])

  useEffect(() => {
    if (items.length <= 1 || paused) return
    const timer = window.setInterval(() => {
      setActiveIndex((prev) => (prev + 1) % items.length)
    }, interval)
    return () => window.clearInterval(timer)
  }, [items.length, interval, paused])

  const goTo = (index: number) => {
    setActiveIndex((index + items.length) % items.length)
  }

  if (items.length === 0) return null

  const current = items[activeIndex]

  return (
    <div
      className="relative mx-auto w-full max-w-2xl overflow-hidden rounded-lg border bg-muted/20 shadow-sm"
      onMouseEnter={() => setPaused(true)}
      onMouseLeave={() => setPaused(false)}
    >
      <div className="relative h-[194px] w-full bg-muted sm:h-[210px]">
        {items.map((item, index) => (
          <div
            key={item.id}
            className={cn(
              'absolute inset-0 transition-opacity duration-500 ease-in-out',
              index === activeIndex ? 'z-10 opacity-100' : 'pointer-events-none z-0 opacity-0',
            )}
          >
            <a
              href={item.click_url || '#'}
              target="_blank"
              rel="noreferrer"
              className="block h-full w-full"
              tabIndex={index === activeIndex ? 0 : -1}
            >
              <img
                src={getMediaUrl(domain, item.pic_url)}
                alt={item.title}
                className="h-full w-full object-cover"
              />
            </a>
          </div>
        ))}

        {items.length > 1 && (
          <>
            <Button
              type="button"
              variant="outline"
              size="icon"
              className="absolute left-2 top-1/2 z-20 h-7 w-7 -translate-y-1/2 bg-background/80 shadow-sm backdrop-blur-sm"
              onClick={() => goTo(activeIndex - 1)}
              aria-label="上一张"
            >
              <ChevronLeft className="h-4 w-4" />
            </Button>
            <Button
              type="button"
              variant="outline"
              size="icon"
              className="absolute right-2 top-1/2 z-20 h-7 w-7 -translate-y-1/2 bg-background/80 shadow-sm backdrop-blur-sm"
              onClick={() => goTo(activeIndex + 1)}
              aria-label="下一张"
            >
              <ChevronRight className="h-4 w-4" />
            </Button>
          </>
        )}
      </div>

      <div className="flex items-center justify-between gap-3 border-t border-border/60 px-3 py-2">
        <p className="min-w-0 truncate text-xs font-medium sm:text-sm">{current?.title}</p>
        {items.length > 1 && (
          <div className="flex shrink-0 items-center gap-1.5">
            {items.map((item, index) => (
              <button
                key={item.id}
                type="button"
                aria-label={`切换到第 ${index + 1} 张`}
                className={cn(
                  'h-2 rounded-full transition-all',
                  index === activeIndex
                    ? 'w-5 bg-primary shadow-sm ring-1 ring-primary/40'
                    : 'w-2 border border-foreground/25 bg-foreground/30 hover:bg-foreground/45',
                )}
                onClick={() => setActiveIndex(index)}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
