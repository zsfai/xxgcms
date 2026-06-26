import { useRef } from 'react'
import { Upload } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { toast } from 'sonner'

interface FileUploadProps {
  action: string
  accept?: string
  headers?: Record<string, string>
  onSuccess?: (url: string) => void
  label?: string
  multiple?: boolean
}

export function FileUpload({
  action,
  accept = 'image/jpeg,image/png,image/gif,image/webp',
  headers = {},
  onSuccess,
  label = '选择文件上传',
  multiple = false,
}: FileUploadProps) {
  const inputRef = useRef<HTMLInputElement>(null)

  const handleChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files
    if (!files?.length) return

    for (const file of Array.from(files)) {
      const formData = new FormData()
      formData.append('file', file)

      try {
        const res = await fetch(action, {
          method: 'POST',
          headers,
          body: formData,
        })
        const data = await res.json()
        if (data.code === 0 && data.data) {
          toast.success('文件上传成功')
          onSuccess?.(typeof data.data === 'string' ? data.data : data.data.url || '')
        } else {
          toast.error(data.message || '文件上传失败')
        }
      } catch {
        toast.error('文件上传失败')
      }
    }

    if (inputRef.current) inputRef.current.value = ''
  }

  return (
    <>
      <input ref={inputRef} type="file" accept={accept} multiple={multiple} className="hidden" onChange={handleChange} />
      <Button type="button" variant="outline" size="sm" onClick={() => inputRef.current?.click()}>
        <Upload className="h-4 w-4" />
        {label}
      </Button>
    </>
  )
}
