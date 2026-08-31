import { createBrowserRouter, Navigate } from 'react-router-dom'
import { MainLayout } from '@/layouts/MainLayout'
import { LoginPage } from '@/pages/login/LoginPage'
import { KeywordListPage } from '@/pages/keyword/KeywordListPage'
import { ArticleListPage } from '@/pages/article/ArticleListPage'
import { CatePage } from '@/pages/article/CatePage'
import { CarouselPage } from '@/pages/article/CarouselPage'
import { FriendLinkPage } from '@/pages/article/FriendLinkPage'
import { MediaLibraryPage } from '@/pages/article/MediaLibraryPage'
import { SiteConfPage } from '@/pages/article/SiteConfPage'
import { AiTopicPage } from '@/pages/article/AiTopicPage'
import { SitePage } from '@/pages/sys/SitePage'
import { AiSettingsLayout } from '@/pages/sys/AiSettingsLayout'
import { AiConfigPage } from '@/pages/sys/AiConfigPage'
import { AiVerticalPage } from '@/pages/sys/AiVerticalPage'
import { AiTemplatePage } from '@/pages/sys/AiTemplatePage'
import { SystemLayout } from '@/pages/sys/SystemLayout'
import { LoginLogPage } from '@/pages/sys/LoginLogPage'
import { ChangelogPage } from '@/pages/sys/ChangelogPage'

const basename = import.meta.env.BASE_URL.replace(/\/$/, '') || undefined

export const router = createBrowserRouter(
  [
    {
      path: '/',
      element: <LoginPage />,
    },
    {
      path: '/',
      element: <MainLayout />,
      children: [
        { path: 'keywords', element: <KeywordListPage /> },
        { path: 'articles', element: <ArticleListPage /> },
        { path: 'ai-topics', element: <AiTopicPage /> },
        { path: 'cates', element: <CatePage /> },
        { path: 'carousels', element: <CarouselPage /> },
        { path: 'links', element: <FriendLinkPage /> },
        { path: 'media', element: <MediaLibraryPage /> },
        { path: 'conf', element: <SiteConfPage /> },
        { path: 'sites', element: <SitePage /> },
        {
          path: 'system',
          element: <SystemLayout />,
          children: [
            { index: true, element: <Navigate to="login-logs" replace /> },
            { path: 'login-logs', element: <LoginLogPage /> },
            { path: 'changelog', element: <ChangelogPage /> },
          ],
        },
        {
          path: 'ai',
          element: <AiSettingsLayout />,
          children: [
            { index: true, element: <Navigate to="config" replace /> },
            { path: 'config', element: <AiConfigPage /> },
            { path: 'verticals', element: <AiVerticalPage /> },
            { path: 'templates', element: <AiTemplatePage /> },
          ],
        },
        { path: 'ai-config', element: <Navigate to="/ai/config" replace /> },
        { path: 'ai-verticals', element: <Navigate to="/ai/verticals" replace /> },
        { path: 'ai-templates', element: <Navigate to="/ai/templates" replace /> },
      ],
    },
    { path: '*', element: <Navigate to="/" replace /> },
  ],
  { basename },
)
