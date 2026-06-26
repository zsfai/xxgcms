import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { toast } from 'sonner'
import { changePasswordService } from '@/api/service'
import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { FormLabel } from '@/components/FormLabel'

const schema = z
  .object({
    old_pwd: z.string().min(1, '请填写原密码'),
    new_pwd: z.string().min(6, '新密码长度不能小于6位'),
    confirm_pwd: z.string().min(1, '请确认新密码'),
  })
  .refine((data) => data.new_pwd === data.confirm_pwd, {
    message: '两次输入的新密码不一致',
    path: ['confirm_pwd'],
  })
  .refine((data) => data.old_pwd !== data.new_pwd, {
    message: '新密码不能与原密码相同',
    path: ['new_pwd'],
  })

type FormValues = z.infer<typeof schema>

interface ChangePasswordDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
}

export function ChangePasswordDialog({ open, onOpenChange }: ChangePasswordDialogProps) {
  const form = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: { old_pwd: '', new_pwd: '', confirm_pwd: '' },
  })

  const resetForm = () => {
    form.reset({ old_pwd: '', new_pwd: '', confirm_pwd: '' })
  }

  const handleOpenChange = (nextOpen: boolean) => {
    if (!nextOpen) {
      resetForm()
    }
    onOpenChange(nextOpen)
  }

  const onSubmit = async (values: FormValues) => {
    try {
      const res = await changePasswordService({
        old_pwd: values.old_pwd,
        new_pwd: values.new_pwd,
      })
      if (res.code === 0 && res.ret) {
        toast.success(res.message || '密码修改成功')
        handleOpenChange(false)
      } else {
        toast.error(res.message || '密码修改失败')
      }
    } catch (e) {
      toast.error(`密码修改失败：${String(e)}`)
    }
  }

  const { isSubmitting } = form.formState

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>修改密码</DialogTitle>
          <DialogDescription>修改当前登录账号的密码，修改成功后仍保持登录状态。</DialogDescription>
        </DialogHeader>
        <form className="space-y-4 py-2" onSubmit={form.handleSubmit(onSubmit)}>
          <div className="space-y-2">
            <FormLabel htmlFor="change-old-pwd" required>
              原密码
            </FormLabel>
            <Input
              id="change-old-pwd"
              type="password"
              autoComplete="current-password"
              {...form.register('old_pwd')}
            />
            {form.formState.errors.old_pwd && (
              <p className="text-xs text-destructive">{form.formState.errors.old_pwd.message}</p>
            )}
          </div>
          <div className="space-y-2">
            <FormLabel htmlFor="change-new-pwd" required>
              新密码
            </FormLabel>
            <Input
              id="change-new-pwd"
              type="password"
              autoComplete="new-password"
              {...form.register('new_pwd')}
            />
            {form.formState.errors.new_pwd && (
              <p className="text-xs text-destructive">{form.formState.errors.new_pwd.message}</p>
            )}
          </div>
          <div className="space-y-2">
            <FormLabel htmlFor="change-confirm-pwd" required>
              确认新密码
            </FormLabel>
            <Input
              id="change-confirm-pwd"
              type="password"
              autoComplete="new-password"
              {...form.register('confirm_pwd')}
            />
            {form.formState.errors.confirm_pwd && (
              <p className="text-xs text-destructive">{form.formState.errors.confirm_pwd.message}</p>
            )}
          </div>
          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => handleOpenChange(false)}>
              取消
            </Button>
            <Button type="submit" disabled={isSubmitting}>
              {isSubmitting ? '保存中…' : '保存'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}
