/**
 * Route Definitions
 */

import type { RouteRecordRaw } from 'vue-router'

export const routes: RouteRecordRaw[] = [
  // Public Routes
  {
    path: '/',
    name: 'home',
    component: () => import('@/views/HomeView.vue'),
    meta: { title: 'simFocus - AI Virtual Focus Groups' }
  },
  {
    path: '/login',
    name: 'login',
    component: () => import('@/views/LoginView.vue'),
    meta: {
      title: 'Login',
      requiresGuest: true,
      layout: 'auth'
    }
  },
  {
    path: '/register',
    name: 'register',
    component: () => import('@/views/RegisterView.vue'),
    meta: {
      title: 'Create Account',
      requiresGuest: true,
      layout: 'auth'
    }
  },
  {
    path: '/forgot-password',
    name: 'forgot-password',
    component: () => import('@/views/ForgotPasswordView.vue'),
    meta: {
      title: 'Reset Password',
      requiresGuest: true,
      layout: 'auth'
    }
  },

  // Protected Routes
  {
    path: '/dashboard',
    name: 'dashboard',
    component: () => import('@/views/DashboardView.vue'),
    meta: {
      title: 'Dashboard',
      requiresAuth: true
    }
  },

  // Topic Management
  {
    path: '/topics',
    name: 'topics',
    component: () => import('@/views/TopicListView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/topics/create',
    name: 'topic-create',
    component: () => import('@/views/TopicCreateView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/topics/:id/edit',
    name: 'topic-edit',
    component: () => import('@/views/TopicEditView.vue'),
    meta: { requiresAuth: true }
  },

  // Discussion Routes
  {
    path: '/discussions',
    name: 'discussions',
    component: () => import('@/views/DiscussionListView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/discussions/:id',
    name: 'discussion-room',
    component: () => import('@/views/DiscussionRoomView.vue'),
    meta: {
      requiresAuth: true,
      title: 'Discussion Room'
    }
  },
  {
    path: '/discussions/:id/report',
    name: 'discussion-report',
    component: () => import('@/views/ReportView.vue'),
    meta: {
      requiresAuth: true,
      title: 'Discussion Report'
    }
  },

  // Settings
  {
    path: '/settings',
    name: 'settings',
    redirect: '/settings/profile',
    meta: { requiresAuth: true }
  },
  {
    path: '/settings/profile',
    name: 'settings-profile',
    component: () => import('@/views/SettingsView.vue'),
    meta: { requiresAuth: true, title: 'Profile Settings' }
  },
  {
    path: '/settings/api-keys',
    name: 'settings-api-keys',
    component: () => import('@/views/ApiKeyView.vue'),
    meta: { requiresAuth: true, title: 'API Key Management' }
  },

  // Shared Reports (Public)
  {
    path: '/share/:slug',
    name: 'shared-report',
    component: () => import('@/views/SharedReportView.vue'),
    meta: {
      title: 'Shared Discussion',
      public: true
    }
  },

  // 404 Not Found
  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    component: () => import('@/views/NotFoundView.vue'),
    meta: { title: 'Page Not Found' }
  }
]
