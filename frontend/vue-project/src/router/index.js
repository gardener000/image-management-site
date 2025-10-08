import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import RegisterView from '../views/RegisterView.vue' 
import LoginView from '../views/LoginView.vue'
import GalleryView from '../views/GalleryView.vue' // 1. 导入画廊视图
import { useAuthStore } from '@/stores/auth' // 导入 auth store

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/register',
      name: 'register',
      component: RegisterView
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView 
    },
    {
      path: '/gallery',
      name: 'gallery',
      component: GalleryView,
      meta: { requiresAuth: true } // 2. 添加一个元信息，表示这个路由需要认证
    }
  ],
})
// 3. 创建一个全局前置守卫
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  // 检查路由是否需要认证，以及用户是否已登录
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    // 如果用户未登录，则重定向到登录页
    next({ name: 'login' })
  } else {
    // 否则，正常放行
    next()
  }
})

export default router
