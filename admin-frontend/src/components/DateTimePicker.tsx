import { useMemo } from 'react'
import { format } from 'date-fns'
import { zhCN as dateFnsZhCN } from 'date-fns/locale'
import { CalendarIcon } from 'lucide-react'
import { zhCN } from 'react-day-picker/locale'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/button'
import { Calendar } from '@/components/ui/calendar'
import { Label } from '@/components/ui/label'
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'

/** datetime-local 格式：YYYY-MM-DDTHH:mm */
function parseDateTimeLocal(value: string): Date | undefined {
  if (!value) return undefined
  const d = new Date(value)
  return Number.isNaN(d.getTime()) ? undefined : d
}

function toDateTimeLocal(date: Date): string {
  const pad = (n: number) => String(n).padStart(2, '0')
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}`
}

function mergeDateAndTime(date: Date, hour: number, minute: number): Date {
  const merged = new Date(date)
  merged.setHours(hour, minute, 0, 0)
  return merged
}

interface DateTimePickerProps {
  value: string
  onChange: (value: string) => void
  placeholder?: string
  className?: string
}

export function DateTimePicker({
  value,
  onChange,
  placeholder = '选择发布时间',
  className,
}: DateTimePickerProps) {
  const selected = parseDateTimeLocal(value)
  const hour = selected?.getHours() ?? 9
  const minute = selected?.getMinutes() ?? 0

  const hourOptions = useMemo(() => Array.from({ length: 24 }, (_, i) => i), [])
  const minuteOptions = useMemo(() => Array.from({ length: 60 }, (_, i) => i), [])

  const updateTime = (h: number, m: number) => {
    const base = selected ?? new Date()
    onChange(toDateTimeLocal(mergeDateAndTime(base, h, m)))
  }

  const displayText = selected
    ? format(selected, 'yyyy年M月d日 HH:mm', { locale: dateFnsZhCN })
    : placeholder

  return (
    <div className={cn('space-y-2', className)}>
      <Label className="text-sm text-muted-foreground">发布时间</Label>
      <Popover>
        <PopoverTrigger asChild>
          <Button
            variant="outline"
            className={cn(
              'w-full justify-start rounded-xl text-left font-normal',
              !value && 'text-muted-foreground',
            )}
          >
            <CalendarIcon className="mr-2 h-4 w-4 shrink-0" />
            {displayText}
          </Button>
        </PopoverTrigger>
        <PopoverContent className="w-auto p-0" align="start" sideOffset={8}>
          <Calendar
            mode="single"
            locale={zhCN}
            selected={selected}
            defaultMonth={selected}
            onSelect={(date) => {
              if (!date) return
              onChange(toDateTimeLocal(mergeDateAndTime(date, hour, minute)))
            }}
            className="p-3"
          />
          <div className="flex items-center gap-2 border-t px-3 py-3">
            <span className="shrink-0 text-sm text-muted-foreground">时间</span>
            <Select value={String(hour)} onValueChange={(v) => updateTime(Number(v), minute)}>
              <SelectTrigger className="w-[100px]">
                <SelectValue />
              </SelectTrigger>
              <SelectContent className="z-[110]">
                {hourOptions.map((h) => (
                  <SelectItem key={h} value={String(h)}>
                    {String(h).padStart(2, '0')} 时
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <span className="text-muted-foreground">:</span>
            <Select value={String(minute)} onValueChange={(v) => updateTime(hour, Number(v))}>
              <SelectTrigger className="w-[100px]">
                <SelectValue />
              </SelectTrigger>
              <SelectContent className="z-[110] max-h-48">
                {minuteOptions.map((m) => (
                  <SelectItem key={m} value={String(m)}>
                    {String(m).padStart(2, '0')} 分
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </PopoverContent>
      </Popover>
    </div>
  )
}
