import { Loader2 } from 'lucide-react'

interface LoadingProps {
  loading?: boolean
  loadingText?: string
}

export function Loading({ loading = false, loadingText = '加载中...' }: LoadingProps) {
  if (!loading) return null

  return (
    <div className="fixed inset-0 z-[1001] flex items-center justify-center bg-black/35">
      <div className="flex flex-col items-center gap-2 rounded-lg border bg-background p-6 shadow-sm">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
        <div className="text-xs text-muted-foreground">{loadingText}</div>
      </div>
    </div>
  )
}
