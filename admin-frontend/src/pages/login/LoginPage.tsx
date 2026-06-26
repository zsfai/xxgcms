import { useForm } from 'react-hook-form'
import { useNavigate } from 'react-router-dom'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { toast } from 'sonner'
import { Globe, Layers, Loader2, Lock, LogIn, Sparkles, User } from 'lucide-react'
import { loginService } from '@/api/service'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { FormLabel } from '@/components/FormLabel'
import { BRAND_COPYRIGHT, BRAND_LOGO_URL, BRAND_NAME } from '@/lib/brand'
import { cn } from '@/lib/utils'

const schema = z.object({
  username: z.string().min(1, '请填写用户名'),
  password: z.string().min(6, '密码长度不能小于6位'),
})

type FormValues = z.infer<typeof schema>

const FEATURES = [
  { icon: Globe, title: '多站点统一管理', desc: '一处登录，统筹全部站点内容与配置' },
  { icon: Sparkles, title: 'AI 智能创作', desc: '选题、生成、发布，内容生产更高效' },
  { icon: Layers, title: '可视化运营', desc: '文章、分类、轮播与友链，所见即所得' },
] as const

function BrandPanel({ className }: { className?: string }) {
  return (
    <div
      className={cn(
        'relative flex flex-col justify-between overflow-hidden bg-primary px-10 py-12 text-primary-foreground xl:px-14 xl:py-16',
        className,
      )}
    >
      <div
        className="pointer-events-none absolute inset-0 opacity-[0.08]"
        style={{
          backgroundImage: 'radial-gradient(circle at 1px 1px, currentColor 1px, transparent 0)',
          backgroundSize: '28px 28px',
        }}
      />
      <div className="pointer-events-none absolute -left-24 top-1/4 h-72 w-72 rounded-full bg-white/10 blur-3xl" />
      <div className="pointer-events-none absolute -right-16 bottom-0 h-96 w-96 rounded-full bg-black/10 blur-3xl" />

      <div className="relative z-10">
        <div className="mb-10 flex items-center gap-4">
          <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-white/15 ring-1 ring-white/20 backdrop-blur-sm">
            <img src={BRAND_LOGO_URL} alt={BRAND_NAME} className="h-10 w-10 object-contain drop-shadow-sm" />
          </div>
          <div>
            <p className="text-2xl font-semibold tracking-tight">{BRAND_NAME}</p>
            <p className="mt-0.5 text-sm text-primary-foreground/75">内容管理 · 一站掌控</p>
          </div>
        </div>

        <h1 className="max-w-md text-3xl font-semibold leading-tight tracking-tight xl:text-4xl">
          让内容运营
          <br />
          <span className="text-primary-foreground/90">更简单、更智能</span>
        </h1>
        <p className="mt-4 max-w-sm text-sm leading-relaxed text-primary-foreground/70">
          面向多站点 CMS 场景打造的管理平台，助力团队高效协作与规模化内容生产。
        </p>
      </div>

      <ul className="relative z-10 mt-12 space-y-4">
        {FEATURES.map(({ icon: Icon, title, desc }) => (
          <li
            key={title}
            className="flex gap-4 rounded-xl border border-white/10 bg-white/5 px-4 py-3.5 backdrop-blur-sm transition-colors hover:bg-white/10"
          >
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-white/15">
              <Icon className="h-5 w-5" aria-hidden />
            </div>
            <div className="min-w-0">
              <p className="text-sm font-medium">{title}</p>
              <p className="mt-0.5 text-xs leading-relaxed text-primary-foreground/65">{desc}</p>
            </div>
          </li>
        ))}
      </ul>

      <p className="relative z-10 mt-10 text-xs text-primary-foreground/50">
        © {new Date().getFullYear()} {BRAND_COPYRIGHT}
      </p>
    </div>
  )
}

export function LoginPage() {
  const navigate = useNavigate()
  const form = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: { username: '', password: '' },
  })

  const onSubmit = async (values: FormValues) => {
    try {
      const res = await loginService({ name: values.username, pwd: values.password })
      if (res.code === 0 && res.ret) {
        toast.success('登录成功')
        sessionStorage.setItem('token', res.token || '')
        sessionStorage.setItem('name', values.username)
        navigate('/sites')
      } else {
        toast.error(res.message || '登录失败')
      }
    } catch (e) {
      toast.error(`登录失败：${String(e)}`)
    }
  }

  const { isSubmitting } = form.formState

  return (
    <div className="relative flex min-h-screen">
      <div className="pointer-events-none absolute inset-0 bg-gradient-to-br from-primary/5 via-background to-background lg:hidden" />
      <div className="pointer-events-none absolute -right-20 top-0 h-64 w-64 rounded-full bg-primary/10 blur-3xl lg:hidden" />
      <div className="pointer-events-none absolute -bottom-16 -left-16 h-72 w-72 rounded-full bg-primary/5 blur-3xl lg:hidden" />

      <BrandPanel className="hidden w-[46%] min-w-[320px] max-w-xl shrink-0 lg:flex" />

      <div className="relative flex flex-1 flex-col items-center justify-center px-4 py-10 sm:px-8">
        <div className="mb-8 flex flex-col items-center gap-3 lg:hidden">
          <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-primary/10 ring-1 ring-primary/15">
            <img src={BRAND_LOGO_URL} alt={BRAND_NAME} className="h-10 w-10 object-contain" />
          </div>
          <p className="text-lg font-semibold tracking-tight">{BRAND_NAME}</p>
        </div>

        <Card className="w-full max-w-[420px] border-border/60 shadow-xl shadow-primary/5 backdrop-blur-sm">
          <CardHeader className="space-y-1 pb-2 pt-8">
            <CardTitle className="text-xl">欢迎回来</CardTitle>
            <CardDescription>登录管理后台，开始今天的内容工作</CardDescription>
          </CardHeader>
          <CardContent className="pb-8">
            <form className="space-y-5" onSubmit={form.handleSubmit(onSubmit)}>
              <div className="space-y-2">
                <FormLabel htmlFor="username" required>
                  账号
                </FormLabel>
                <div className="relative">
                  <User
                    className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground"
                    aria-hidden
                  />
                  <Input
                    id="username"
                    className="h-10 pl-9"
                    placeholder="请输入账号"
                    autoComplete="username"
                    {...form.register('username')}
                  />
                </div>
                {form.formState.errors.username && (
                  <p className="text-xs text-destructive">{form.formState.errors.username.message}</p>
                )}
              </div>

              <div className="space-y-2">
                <FormLabel htmlFor="password" required>
                  密码
                </FormLabel>
                <div className="relative">
                  <Lock
                    className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground"
                    aria-hidden
                  />
                  <Input
                    id="password"
                    type="password"
                    className="h-10 pl-9"
                    placeholder="请输入密码"
                    autoComplete="current-password"
                    {...form.register('password')}
                  />
                </div>
                {form.formState.errors.password && (
                  <p className="text-xs text-destructive">{form.formState.errors.password.message}</p>
                )}
              </div>

              <Button type="submit" className="mt-2 h-10 w-full gap-2 text-sm" size="lg" disabled={isSubmitting}>
                {isSubmitting ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin" aria-hidden />
                    登录中…
                  </>
                ) : (
                  <>
                    <LogIn className="h-4 w-4" aria-hidden />
                    登录
                  </>
                )}
              </Button>
            </form>
          </CardContent>
        </Card>

        <p className="mt-8 text-center text-xs text-muted-foreground lg:hidden">
          多站点 · AI 创作 · 可视化运营
        </p>
      </div>
    </div>
  )
}
