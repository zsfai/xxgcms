import { useCallback, useEffect, useState } from 'react'
import { toast } from 'sonner'
import { getChangelogService } from '@/api/service'
import { Loading } from '@/components/Loading'
import { PageShell } from '@/components/PageShell'
import { SystemSecondaryNav } from '@/pages/sys/SystemSecondaryNav'
import { Badge } from '@/components/ui/badge'

interface ChangelogEntry {
  version: string
  date: string
  items: string[]
}

export function ChangelogPage() {
  const [loading, setLoading] = useState(false)
  const [entries, setEntries] = useState<ChangelogEntry[]>([])

  const loadList = useCallback(async () => {
    setLoading(true)
    try {
      const res = await getChangelogService()
      if (res.code === 0) {
        setEntries((res.datas as ChangelogEntry[]) || [])
      } else {
        toast.error(res.message || '加载更新日志失败')
      }
    } catch (e) {
      toast.error(`加载更新日志失败：${String(e)}`)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    void loadList()
  }, [loadList])

  return (
    <>
      <Loading loading={loading} />
      <PageShell
        title="更新日志"
        description="按版本查看产品更新说明"
        sideNav={<SystemSecondaryNav />}
      >
        <div className="content-panel min-h-[240px] p-6">
          {entries.length === 0 && !loading ? (
            <p className="py-10 text-center text-sm text-muted-foreground">暂无更新日志</p>
          ) : (
            <div className="relative space-y-0">
              {entries.map((entry, index) => (
                <section
                  key={`${entry.version}-${entry.date}`}
                  className="relative flex gap-4 pb-8 last:pb-0"
                >
                  <div className="flex w-3 shrink-0 flex-col items-center">
                    <span className="mt-1.5 h-2.5 w-2.5 shrink-0 rounded-full bg-primary" />
                    {index < entries.length - 1 && (
                      <span className="mt-1 w-px flex-1 bg-border" aria-hidden />
                    )}
                  </div>
                  <div className="min-w-0 flex-1 space-y-2.5">
                    <div className="flex flex-wrap items-center gap-2.5">
                      <Badge className="font-mono text-[12px]">v{entry.version}</Badge>
                      <span className="text-sm tabular-nums text-muted-foreground">{entry.date}</span>
                    </div>
                    {entry.items.length === 0 ? (
                      <p className="text-sm text-muted-foreground">无说明条目</p>
                    ) : (
                      <ul className="list-disc space-y-1.5 pl-5 text-[13px] leading-relaxed text-foreground/90">
                        {entry.items.map((item, idx) => (
                          <li key={`${entry.version}-${idx}`}>{item}</li>
                        ))}
                      </ul>
                    )}
                  </div>
                </section>
              ))}
            </div>
          )}
        </div>
      </PageShell>
    </>
  )
}
