import { useCallback, useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Sparkles, Loader2 } from 'lucide-react'
import { toast } from 'sonner'
import {
  getTopicSessionService,
  getTopicSessionsService,
  topicConfirmGenerateService,
  topicSuggestService,
} from '@/api/service'
import { Loading } from '@/components/Loading'
import { Button } from '@/components/ui/button'
import { Checkbox } from '@/components/ui/checkbox'
import { PageShell } from '@/components/PageShell'
import { Input } from '@/components/ui/input'
import { FormLabel } from '@/components/FormLabel'
import { Label } from '@/components/ui/label'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { formatDateTime } from '@/lib/utils'

interface TopicSuggestion {
  id: number
  title: string
  angle?: string
  timeliness?: string
  summary?: string
  status?: string
  refs?: Array<{ title: string; url: string; snippet?: string }>
}

interface TopicSessionEntry {
  session: {
    id: number
    seed_keyword: string
    status: string
    add_time?: string
  }
  suggestions: TopicSuggestion[]
}

export function AiTopicPage() {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [seed, setSeed] = useState('')
  const [wordCount, setWordCount] = useState('800')
  const [imageMode, setImageMode] = useState('ai')
  const [sessionId, setSessionId] = useState<number | null>(null)
  const [suggestions, setSuggestions] = useState<TopicSuggestion[]>([])
  const [selected, setSelected] = useState<Set<number>>(new Set())
  const [jobProgress, setJobProgress] = useState<{ done: number; total: number; status?: string } | null>(null)
  const [historySessions, setHistorySessions] = useState<TopicSessionEntry[]>([])

  const loadHistory = useCallback(async () => {
    const res = await getTopicSessionsService({ limit: 10 })
    if (res.code === 0 && Array.isArray(res.data)) {
      setHistorySessions(res.data as TopicSessionEntry[])
    }
  }, [])

  useEffect(() => {
    void loadHistory()
  }, [loadHistory])

  const pollSession = useCallback(async (sid: number) => {
    const res = await getTopicSessionService({ session_id: sid })
    if (res.code !== 0 || !res.data) return
    const data = res.data as {
      suggestions?: TopicSuggestion[]
      job?: { status: string; done: number; total: number }
    }
    if (data.suggestions) setSuggestions(data.suggestions)
    if (data.job) {
      setJobProgress({ done: data.job.done, total: data.job.total, status: data.job.status })
      if (data.job.status === 'done' || data.job.status === 'partial') {
        setLoading(false)
        void loadHistory()
        if (data.job.status === 'partial') {
          toast.warning('部分文章写稿完成，请查看列表')
        } else {
          toast.success('写稿任务已完成')
        }
        navigate('/articles?ai=1')
        return
      }
      if (data.job.status === 'failed') {
        setLoading(false)
        void loadHistory()
        toast.error('写稿失败，请查看任务进度或重试')
        return
      }
    }
    setTimeout(() => pollSession(sid), 2000)
  }, [navigate, loadHistory])

  const handleSuggest = async () => {
    if (!seed.trim()) {
      toast.error('请输入种子词，如：张家界')
      return
    }
    setLoading(true)
    setJobProgress(null)
    setSelected(new Set())
    try {
      const res = await topicSuggestService({
        seed_keyword: seed.trim(),
        suggest_count: 10,
      })
      if (res.code === 0 && res.data) {
        const data = res.data as { session: { id: number }; suggestions: TopicSuggestion[] }
        setSessionId(data.session?.id)
        setSuggestions(data.suggestions || [])
        void loadHistory()
        toast.success('选题建议已生成')
      } else {
        toast.error(res.message || '获取选题失败')
      }
    } catch (e) {
      toast.error(String(e))
    } finally {
      setLoading(false)
    }
  }

  const toggleSelect = (id: number, checked: boolean) => {
    setSelected((prev) => {
      const next = new Set(prev)
      if (checked) next.add(id)
      else next.delete(id)
      return next
    })
  }

  const handleConfirmGenerate = async () => {
    if (!sessionId || selected.size === 0) {
      toast.error('请先勾选选题')
      return
    }
    if (selected.size > 10) {
      toast.error('最多选择 10 条')
      return
    }
    setLoading(true)
    try {
      const res = await topicConfirmGenerateService({
        session_id: sessionId,
        suggestion_ids: Array.from(selected),
        word_count: Number(wordCount),
        image_mode: imageMode,
      })
      if (res.code === 0) {
        toast.info('正在写稿，请稍候…')
        setJobProgress({ done: 0, total: selected.size, status: 'running' })
        pollSession(sessionId)
      } else {
        toast.error(res.message || '提交失败')
        setLoading(false)
      }
    } catch (e) {
      toast.error(String(e))
      setLoading(false)
    }
  }

  return (
    <>
      <Loading loading={loading && !jobProgress} />
      <PageShell
        title="AI 选题助手"
        description="输入种子词获取选题建议；确认后自动生成文章草稿"
      >
        <div className="content-panel space-y-6 p-6">
          <div className="space-y-2.5">
            <div className="dialog-form-row">
              <FormLabel required>种子词</FormLabel>
              <Input
                placeholder="如：张家界"
                value={seed}
                onChange={(e) => setSeed(e.target.value)}
              />
            </div>
          </div>
          <div className="dialog-form-row">
            <span aria-hidden="true" />
            <Button
              size="lg"
              className="w-44 justify-self-start"
              onClick={handleSuggest}
              disabled={loading}
            >
              <Sparkles className="h-4 w-4" />
              获取选题建议
            </Button>
          </div>

          {suggestions.length > 0 && (
            <div className="dialog-form-row-top">
              <span aria-hidden="true" />
              <div className="min-w-0 space-y-3">
                <h4 className="text-sm font-medium text-muted-foreground">
                  选题列表（已选 {selected.size} / {suggestions.length}）
                </h4>
                {suggestions.map((s) => (
                  <div key={s.id} className="rounded-lg border p-4 space-y-2">
                    <div className="flex items-start gap-3">
                      <Checkbox
                        checked={selected.has(s.id)}
                        onCheckedChange={(c) => toggleSelect(s.id, c === true)}
                      />
                      <div className="min-w-0 flex-1">
                        <p className="font-medium">{s.title}</p>
                        {s.angle && (
                          <p className="text-sm text-muted-foreground">角度：{s.angle}</p>
                        )}
                        {s.timeliness && (
                          <p className="text-sm text-muted-foreground">{s.timeliness}</p>
                        )}
                        {s.summary && <p className="text-sm mt-1">{s.summary}</p>}
                        {s.refs && s.refs.length > 0 && (
                          <details className="mt-2 text-xs text-muted-foreground">
                            <summary>参考来源 ({s.refs.length})</summary>
                            <ul className="mt-1 space-y-1">
                              {s.refs.map((r, i) => (
                                <li key={i}>
                                  <a href={r.url} target="_blank" rel="noreferrer" className="underline">
                                    {r.title || r.url}
                                  </a>
                                </li>
                              ))}
                            </ul>
                          </details>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {suggestions.length > 0 && (
            <div className="space-y-2.5 border-t pt-4">
              <div className="dialog-form-row">
                <Label>字数</Label>
                <Select value={wordCount} onValueChange={setWordCount}>
                  <SelectTrigger className="w-[120px]"><SelectValue /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="600">600</SelectItem>
                    <SelectItem value="800">800</SelectItem>
                    <SelectItem value="1200">1200</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="dialog-form-row">
                <Label>封面</Label>
                <Select value={imageMode} onValueChange={setImageMode}>
                  <SelectTrigger className="w-[140px]"><SelectValue /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="ai">AI 生图</SelectItem>
                    <SelectItem value="default">默认图</SelectItem>
                    <SelectItem value="none">无封面</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="dialog-form-row">
                <span aria-hidden="true" />
                <div className="flex flex-wrap items-center gap-3">
                  <Button onClick={handleConfirmGenerate} disabled={loading || selected.size === 0}>
                    {loading && jobProgress ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <Sparkles className="h-4 w-4" />
                    )}
                    确认选题并开始写稿
                  </Button>
                  {jobProgress && (
                    <span className="text-sm text-muted-foreground whitespace-nowrap">
                      写稿进度 {jobProgress.done}/{jobProgress.total}
                    </span>
                  )}
                </div>
              </div>
            </div>
          )}

          <div className="dialog-form-row-top mt-12 pt-10">
            <span aria-hidden="true" />
            <div className="min-w-0 space-y-3">
              <h4 className="text-xs font-medium text-muted-foreground">历史写稿（最近 10 次）</h4>
              {historySessions.length === 0 ? (
                <p className="text-xs text-muted-foreground">
                  暂无已写稿选题，确认选题并生成文章后将显示在这里
                </p>
              ) : (
                <div className="space-y-4">
                  {historySessions.map((entry) => {
                    const sess = entry.session
                    const generatedCount = entry.suggestions.length
                    return (
                      <div key={sess.id} className="space-y-1.5">
                        <div className="flex flex-wrap items-center gap-x-2 gap-y-1 text-xs text-muted-foreground">
                          <span>{sess.seed_keyword}</span>
                          <span>·</span>
                          <span>{generatedCount} 篇</span>
                          {sess.add_time && (
                            <>
                              <span>·</span>
                              <span>{formatDateTime(sess.add_time)}</span>
                            </>
                          )}
                        </div>
                        <ul className="space-y-1">
                          {entry.suggestions.map((s) => (
                            <li key={s.id} className="text-xs text-muted-foreground/90 leading-relaxed">
                              {s.title}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )
                  })}
                </div>
              )}
            </div>
          </div>
        </div>
      </PageShell>
    </>
  )
}
