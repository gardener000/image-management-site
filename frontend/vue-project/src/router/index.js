import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import RegisterView from '../views/RegisterView.vue' 

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    // --- 新增注册路由 ---
    {
      path: '/register',
      name: 'register',
      component: RegisterView
    },
    // --- 预留登录路由 ---
    {
      path: '/login',
      name: 'login',
      // 暂时先指向 HomeView，后面我们会创建 LoginView.vue
      component: () => import('../views/HomeView.vue') 
    }
  ],
})

export default router
