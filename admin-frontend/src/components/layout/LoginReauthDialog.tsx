import { useEffect } from 'react'
import { toast } from 'sonner'
import { loginService } from '@/api/service'
import { useAppStore } from '@/stores/app-store'
import { Button } from '@/components/ui/button'
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { useForm } from 'react-hook-form'
import { z } from 'zod'
import { zodResolver } from '@hookform/resolvers/zod'

const schema = z.object({
  name: z.string().min(1, '请填写用户名'),
  pwd: z.string().min(6, '密码长度不能小于6位'),
})

type FormValues = z.infer<typeof schema>

export function LoginReauthDialog() {
  const loginFormShow = useAppStore((s) => s.loginFormShow)
  const hideLoginForm = useAppStore((s) => s.hideLoginForm)

  const form = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: { name: sessionStorage.getItem('name') || '', pwd: '' },
  })

  useEffect(() => {
    form.setValue('name', sessionStorage.getItem('name') || '')
  }, [loginFormShow, form])

  const onSubmit = async (values: FormValues) => {
    const res = await loginService(values)
    if (res.code === 0 && res.ret) {
      toast.success('登录成功!')
      sessionStorage.setItem('token', res.token || '')
      sessionStorage.setItem('name', values.name)
      hideLoginForm()
      window.location.reload()
    } else {
      toast.error(res.message || '登录失败')
    }
  }

  return (
    <Dialog open={loginFormShow} onOpenChange={() => undefined}>
      <DialogContent className="sm:max-w-md" onPointerDownOutside={(e) => e.preventDefault()} onEscapeKeyDown={(e) => e.preventDefault()}>
        <DialogHeader>
          <DialogTitle>登录验证</DialogTitle>
        </DialogHeader>
        <form className="space-y-4 py-2" onSubmit={form.handleSubmit(onSubmit)}>
          <div className="space-y-2">
            <Label htmlFor="reauth-name">账号</Label>
            <Input id="reauth-name" {...form.register('name')} />
            {form.formState.errors.name && <p className="text-xs text-destructive">{form.formState.errors.name.message}</p>}
          </div>
          <div className="space-y-2">
            <Label htmlFor="reauth-pwd">密码</Label>
            <Input id="reauth-pwd" type="password" {...form.register('pwd')} />
            {form.formState.errors.pwd && <p className="text-xs text-destructive">{form.formState.errors.pwd.message}</p>}
          </div>
          <DialogFooter>
            <Button type="submit">确定</Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}
