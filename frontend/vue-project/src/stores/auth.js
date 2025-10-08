    // frontend/vue-project/src/stores/auth.js
    import { defineStore } from 'pinia';
    import { ref, computed } from 'vue';
    import apiClient from '@/api/axios';
    import router from '@/router';

    export const useAuthStore = defineStore('auth', () => {
      // --- State ---
      // 从浏览器的 localStorage 读取 token，这样即使用户刷新页面，登录状态也能保持
      const token = ref(localStorage.getItem('token') || null);

      // --- Getters ---
      // 一个计算属性，方便地判断用户是否已登录
      const isAuthenticated = computed(() => !!token.value);

      // --- Actions ---
      async function login(credentials) {
        try {
          const response = await apiClient.post('/auth/login', credentials);
          const newToken = response.data.access_token;
          
          // 1. 更新 store 中的 token
          token.value = newToken;
          
          // 2. 将 token 存入 localStorage 以便持久化
          localStorage.setItem('token', newToken);

          // 3. 配置 apiClient，让后续所有请求都自动带上 token
          apiClient.defaults.headers.common['Authorization'] = `Bearer ${newToken}`;

          // 4. 跳转到首页
          router.push('/');
          
          return true; // 表示登录成功
        } catch (error) {
          console.error('登录失败:', error);
          // 登录失败时，确保 token 是空的
          logout();
          throw error; // 抛出错误，让组件可以捕获
        }
      }

      function logout() {
        // 1. 清空 store 中的 token
        token.value = null;
        
        // 2. 从 localStorage 移除 token
        localStorage.removeItem('token');

        // 3. 移除 apiClient 的认证头
        delete apiClient.defaults.headers.common['Authorization'];

        // 4. 跳转到登录页
        router.push('/login');
      }

      // 初始化时，如果localStorage里有token，也设置一下apiClient的默认请求头
      if (token.value) {
          apiClient.defaults.headers.common['Authorization'] = `Bearer ${token.value}`;
      }


      // 将 state, getters, actions return 出去
      return {
        token,
        isAuthenticated,
        login,
        logout
      };
    });