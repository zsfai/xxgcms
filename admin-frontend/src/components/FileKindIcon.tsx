import { useId } from 'react'
import { cn } from '@/lib/utils'

type FileTone = {
  label: string
  /** 主体填充 */
  fill: string
  /** 折角内侧 */
  fold: string
  /** 折角阴影边 */
  foldEdge: string
  /** 底部标签底色 */
  badge: string
  /** 轻描边 */
  stroke: string
}

const EXT_TONE: Record<string, FileTone> = {
  pdf: {
    label: 'PDF',
    fill: '#FEF2F2',
    fold: '#FECACA',
    foldEdge: '#F87171',
    badge: '#DC2626',
    stroke: '#FCA5A5',
  },
  doc: {
    label: 'DOC',
    fill: '#EFF6FF',
    fold: '#BFDBFE',
    foldEdge: '#60A5FA',
    badge: '#2563EB',
    stroke: '#93C5FD',
  },
  docx: {
    label: 'DOCX',
    fill: '#EFF6FF',
    fold: '#BFDBFE',
    foldEdge: '#60A5FA',
    badge: '#1D4ED8',
    stroke: '#93C5FD',
  },
  xls: {
    label: 'XLS',
    fill: '#ECFDF5',
    fold: '#A7F3D0',
    foldEdge: '#34D399',
    badge: '#059669',
    stroke: '#6EE7B7',
  },
  xlsx: {
    label: 'XLSX',
    fill: '#ECFDF5',
    fold: '#A7F3D0',
    foldEdge: '#34D399',
    badge: '#047857',
    stroke: '#6EE7B7',
  },
  csv: {
    label: 'CSV',
    fill: '#F0FDF4',
    fold: '#BBF7D0',
    foldEdge: '#4ADE80',
    badge: '#16A34A',
    stroke: '#86EFAC',
  },
  ppt: {
    label: 'PPT',
    fill: '#FFF7ED',
    fold: '#FED7AA',
    foldEdge: '#FB923C',
    badge: '#EA580C',
    stroke: '#FDBA74',
  },
  pptx: {
    label: 'PPTX',
    fill: '#FFF7ED',
    fold: '#FED7AA',
    foldEdge: '#FB923C',
    badge: '#C2410C',
    stroke: '#FDBA74',
  },
  txt: {
    label: 'TXT',
    fill: '#F8FAFC',
    fold: '#E2E8F0',
    foldEdge: '#94A3B8',
    badge: '#64748B',
    stroke: '#CBD5E1',
  },
  md: {
    label: 'MD',
    fill: '#F8FAFC',
    fold: '#E2E8F0',
    foldEdge: '#64748B',
    badge: '#475569',
    stroke: '#CBD5E1',
  },
  zip: {
    label: 'ZIP',
    fill: '#FFFBEB',
    fold: '#FDE68A',
    foldEdge: '#FBBF24',
    badge: '#D97706',
    stroke: '#FCD34D',
  },
  rar: {
    label: 'RAR',
    fill: '#FFFBEB',
    fold: '#FDE68A',
    foldEdge: '#FBBF24',
    badge: '#B45309',
    stroke: '#FCD34D',
  },
  '7z': {
    label: '7Z',
    fill: '#FFFBEB',
    fold: '#FDE68A',
    foldEdge: '#FBBF24',
    badge: '#B45309',
    stroke: '#FCD34D',
  },
  tar: {
    label: 'TAR',
    fill: '#FFFBEB',
    fold: '#FDE68A',
    foldEdge: '#F59E0B',
    badge: '#D97706',
    stroke: '#FCD34D',
  },
  gz: {
    label: 'GZ',
    fill: '#FFFBEB',
    fold: '#FDE68A',
    foldEdge: '#F59E0B',
    badge: '#D97706',
    stroke: '#FCD34D',
  },
  mp4: {
    label: 'MP4',
    fill: '#EEF2FF',
    fold: '#C7D2FE',
    foldEdge: '#818CF8',
    badge: '#4F46E5',
    stroke: '#A5B4FC',
  },
  webm: {
    label: 'WEBM',
    fill: '#EEF2FF',
    fold: '#C7D2FE',
    foldEdge: '#818CF8',
    badge: '#4338CA',
    stroke: '#A5B4FC',
  },
  mov: {
    label: 'MOV',
    fill: '#EEF2FF',
    fold: '#C7D2FE',
    foldEdge: '#818CF8',
    badge: '#4F46E5',
    stroke: '#A5B4FC',
  },
  avi: {
    label: 'AVI',
    fill: '#EEF2FF',
    fold: '#C7D2FE',
    foldEdge: '#818CF8',
    badge: '#4338CA',
    stroke: '#A5B4FC',
  },
  mkv: {
    label: 'MKV',
    fill: '#EEF2FF',
    fold: '#C7D2FE',
    foldEdge: '#818CF8',
    badge: '#4338CA',
    stroke: '#A5B4FC',
  },
  m4v: {
    label: 'M4V',
    fill: '#EEF2FF',
    fold: '#C7D2FE',
    foldEdge: '#818CF8',
    badge: '#4F46E5',
    stroke: '#A5B4FC',
  },
  jpg: {
    label: 'JPG',
    fill: '#F0FDFA',
    fold: '#99F6E4',
    foldEdge: '#2DD4BF',
    badge: '#0D9488',
    stroke: '#5EEAD4',
  },
  jpeg: {
    label: 'JPEG',
    fill: '#F0FDFA',
    fold: '#99F6E4',
    foldEdge: '#2DD4BF',
    badge: '#0F766E',
    stroke: '#5EEAD4',
  },
  png: {
    label: 'PNG',
    fill: '#F0FDFA',
    fold: '#99F6E4',
    foldEdge: '#14B8A6',
    badge: '#0D9488',
    stroke: '#5EEAD4',
  },
  gif: {
    label: 'GIF',
    fill: '#F0FDFA',
    fold: '#99F6E4',
    foldEdge: '#14B8A6',
    badge: '#0F766E',
    stroke: '#5EEAD4',
  },
  webp: {
    label: 'WEBP',
    fill: '#F0FDFA',
    fold: '#99F6E4',
    foldEdge: '#14B8A6',
    badge: '#0D9488',
    stroke: '#5EEAD4',
  },
  svg: {
    label: 'SVG',
    fill: '#F0FDFA',
    fold: '#99F6E4',
    foldEdge: '#14B8A6',
    badge: '#0F766E',
    stroke: '#5EEAD4',
  },
  bmp: {
    label: 'BMP',
    fill: '#F0FDFA',
    fold: '#99F6E4',
    foldEdge: '#14B8A6',
    badge: '#0D9488',
    stroke: '#5EEAD4',
  },
}

const TYPE_FALLBACK: Record<string, FileTone> = {
  image: {
    label: 'IMG',
    fill: '#F0FDFA',
    fold: '#99F6E4',
    foldEdge: '#2DD4BF',
    badge: '#0D9488',
    stroke: '#5EEAD4',
  },
  video: {
    label: 'VID',
    fill: '#EEF2FF',
    fold: '#C7D2FE',
    foldEdge: '#818CF8',
    badge: '#4F46E5',
    stroke: '#A5B4FC',
  },
  document: {
    label: 'DOC',
    fill: '#EFF6FF',
    fold: '#BFDBFE',
    foldEdge: '#60A5FA',
    badge: '#2563EB',
    stroke: '#93C5FD',
  },
  other: {
    label: 'FILE',
    fill: '#FAFAF9',
    fold: '#E7E5E4',
    foldEdge: '#A8A29E',
    badge: '#78716C',
    stroke: '#D6D3D1',
  },
}

function resolveTone(ext: string, fileType: string): FileTone {
  const key = (ext || '').toLowerCase()
  if (EXT_TONE[key]) return EXT_TONE[key]
  return TYPE_FALLBACK[fileType] || TYPE_FALLBACK.other
}

const SIZE_MAP = {
  sm: { className: 'h-9 w-[1.85rem]', badgeFs: 6.2, lines: true },
  md: { className: 'h-11 w-[2.25rem]', badgeFs: 7.2, lines: true },
  lg: { className: 'h-[4.75rem] w-[3.6rem]', badgeFs: 9.5, lines: true },
} as const

export function FileKindIcon({
  ext,
  fileType,
  size = 'md',
  className,
}: {
  ext: string
  fileType: string
  size?: keyof typeof SIZE_MAP
  className?: string
}) {
  const tone = resolveTone(ext, fileType)
  const dim = SIZE_MAP[size]
  const label = tone.label.length > 4 ? tone.label.slice(0, 4) : tone.label
  const uid = useId().replace(/:/g, '')

  return (
    <span
      className={cn('inline-flex shrink-0 select-none', dim.className, className)}
      title={`.${(ext || tone.label).toLowerCase()}`}
      aria-hidden
    >
      <svg viewBox="0 0 40 48" className="h-full w-full drop-shadow-[0_1px_2px_rgba(15,23,42,0.12)]">
        <defs>
          <linearGradient id={`${uid}-body`} x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#FFFFFF" />
            <stop offset="55%" stopColor={tone.fill} />
            <stop offset="100%" stopColor={tone.fill} />
          </linearGradient>
          <linearGradient id={`${uid}-fold`} x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stopColor={tone.fold} />
            <stop offset="100%" stopColor={tone.foldEdge} />
          </linearGradient>
          <filter id={`${uid}-soft`} x="-20%" y="-10%" width="140%" height="130%">
            <feDropShadow dx="0" dy="0.6" stdDeviation="0.5" floodColor="#0f172a" floodOpacity="0.08" />
          </filter>
        </defs>

        {/* 纸张主体（带折角缺口） */}
        <path
          d="M6.5 2.5 H26 L35.5 12 V42.5 C35.5 44.2 34.2 45.5 32.5 45.5 H6.5 C4.8 45.5 3.5 44.2 3.5 42.5 V5.5 C3.5 3.8 4.8 2.5 6.5 2.5 Z"
          fill={`url(#${uid}-body)`}
          stroke={tone.stroke}
          strokeWidth="1"
          filter={`url(#${uid}-soft)`}
        />

        {/* 折角面 */}
        <path d="M26 2.5 V10.5 C26 11.6 26.9 12.5 28 12.5 H35.5 Z" fill={`url(#${uid}-fold)`} />
        <path
          d="M26 2.5 L35.5 12 H28 C26.9 12 26 11.1 26 10 V2.5 Z"
          fill="none"
          stroke={tone.foldEdge}
          strokeWidth="0.75"
          opacity="0.55"
        />

        {/* 正文假线条（文档感） */}
        {dim.lines && fileType !== 'video' && (
          <g opacity="0.35" stroke={tone.badge} strokeWidth="1.1" strokeLinecap="round">
            <line x1="9" y1="18" x2="24" y2="18" />
            <line x1="9" y1="22.2" x2="28" y2="22.2" />
            <line x1="9" y1="26.4" x2="26" y2="26.4" />
          </g>
        )}

        {/* 视频播放点缀 */}
        {fileType === 'video' && (
          <circle cx="20" cy="22" r="5.2" fill={tone.badge} opacity="0.92" />
        )}
        {fileType === 'video' && (
          <path d="M18.2 19.4 L23.4 22 L18.2 24.6 Z" fill="#FFFFFF" />
        )}

        {/* 底部扩展名胶囊 */}
        <rect x="6.5" y="32.5" width="27" height="9.2" rx="2.4" fill={tone.badge} />
        <text
          x="20"
          y="39.1"
          textAnchor="middle"
          fill="#FFFFFF"
          fontSize={dim.badgeFs}
          fontWeight="700"
          fontFamily="ui-sans-serif, system-ui, -apple-system, Segoe UI, sans-serif"
          letterSpacing="0.4"
        >
          {label}
        </text>
      </svg>
    </span>
  )
}
