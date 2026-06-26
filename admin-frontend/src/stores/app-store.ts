import { create } from 'zustand'

interface AppState {
  loginFormShow: boolean
  siteNameX: string
  sidebarCollapsed: boolean
  showLoginForm: () => void
  hideLoginForm: () => void
  changeSiteName: (name: string) => void
  toggleSidebar: () => void
}

const readSidebarCollapsed = () => {
  try {
    return localStorage.getItem('sidebar-collapsed') === 'true'
  } catch {
    return false
  }
}

const readSelectedDomain = () => {
  try {
    return sessionStorage.getItem('domain') || ''
  } catch {
    return ''
  }
}

export const useAppStore = create<AppState>((set) => ({
  loginFormShow: false,
  siteNameX: readSelectedDomain(),
  sidebarCollapsed: readSidebarCollapsed(),
  showLoginForm: () => set({ loginFormShow: true }),
  hideLoginForm: () => set({ loginFormShow: false }),
  changeSiteName: (name) => set({ siteNameX: name }),
  toggleSidebar: () =>
    set((state) => {
      const sidebarCollapsed = !state.sidebarCollapsed
      try {
        localStorage.setItem('sidebar-collapsed', String(sidebarCollapsed))
      } catch {
        // ignore storage errors
      }
      return { sidebarCollapsed }
    }),
}))
