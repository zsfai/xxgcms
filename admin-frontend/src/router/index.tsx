import { createBrowserRouter, Navigate } from 'react-router-dom'
import { MainLayout } from '@/layouts/MainLayout'
import { LoginPage } from '@/pages/login/LoginPage'
import { KeywordListPage } from '@/pages/keyword/KeywordListPage'
import { ArticleListPage } from '@/pages/article/ArticleListPage'
import { CatePage } from '@/pages/article/CatePage'
import { CarouselPage } from '@/pages/article/CarouselPage'
import { FriendLinkPage } from '@/pages/article/FriendLinkPage'
import { SiteConfPage } from '@/pages/article/SiteConfPage'
import { AiTopicPage } from '@/pages/article/AiTopicPage'
import { SitePage } from '@/pages/sys/SitePage'
import { AiConfigPage } from '@/pages/sys/AiConfigPage'
import { AiVerticalPage } from '@/pages/sys/AiVerticalPage'
import { AiTemplatePage } from '@/pages/sys/AiTemplatePage'

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
        { path: 'conf', element: <SiteConfPage /> },
        { path: 'sites', element: <SitePage /> },
        { path: 'ai-config', element: <AiConfigPage /> },
        { path: 'ai-verticals', element: <AiVerticalPage /> },
        { path: 'ai-templates', element: <AiTemplatePage /> },
      ],
    },
    { path: '*', element: <Navigate to="/" replace /> },
  ],
  { basename },
)
