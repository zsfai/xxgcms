import { Outlet } from 'react-router-dom'
import { TopBar } from '@/components/layout/TopBar'
import { Sidebar } from '@/components/layout/Sidebar'
import { LoginReauthDialog } from '@/components/layout/LoginReauthDialog'

export function MainLayout() {
  return (
    <div className="flex h-full overflow-hidden">
      <Sidebar />
      <div className="flex min-w-0 flex-1 flex-col">
        <TopBar />
        <main className="layout-content-main">
          <Outlet />
        </main>
      </div>
      <LoginReauthDialog />
    </div>
  )
}
