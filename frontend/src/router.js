import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/Home.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/Register.vue'),
    meta: { requiresAuth: false }
  },
  // Keycloak 认证路由
  {
    path: '/auth/callback',
    name: 'AuthCallback',
    component: () => import('@/views/AuthCallback.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/auth/success',
    name: 'AuthSuccess',
    component: () => import('@/views/AuthSuccess.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/topics',
    name: 'Topics',
    component: () => import('@/views/Topics.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/topics/new',
    name: 'NewTopic',
    component: () => import('@/views/NewTopic.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/topics/:id',
    name: 'TopicDetail',
    component: () => import('@/views/TopicDetail.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/characters',
    name: 'Characters',
    component: () => import('@/views/Characters.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/characters/new',
    name: 'NewCharacter',
    component: () => import('@/views/NewCharacter.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/characters/:id',
    name: 'CharacterDetail',
    component: () => import('@/views/CharacterDetail.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/discussions',
    name: 'Discussions',
    component: () => import('@/views/Discussions.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/discussions/new',
    name: 'NewDiscussion',
    component: () => import('@/views/NewDiscussion.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/discussions/:id',
    name: 'DiscussionDetail',
    component: () => import('@/views/DiscussionDetail.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/discussions/:id/report',
    name: 'DiscussionReport',
    component: () => import('@/views/DiscussionReport.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('@/views/Settings.vue'),
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Navigation guard
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  const requiresAuth = to.meta.requiresAuth

  if (requiresAuth && !authStore.isAuthenticated) {
    next('/login')
  } else if ((to.name === 'Login' || to.name === 'Register') && authStore.isAuthenticated) {
    next('/topics')
  } else {
    next()
  }
})

export default router
