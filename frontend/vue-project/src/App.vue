<script setup>
import { RouterLink, RouterView } from 'vue-router'
import { useAuthStore } from '@/stores/auth';

const authStore = useAuthStore();
</script>

<template>
  <header class="global-nav">
    <nav class="nav-container">
      <RouterLink to="/" class="nav-link">
        <span class="nav-icon">🏠</span>
        <span>首页</span>
      </RouterLink>

      <template v-if="authStore.isAuthenticated">
        <RouterLink to="/gallery" class="nav-link">
          <span class="nav-icon">🖼️</span>
          <span>我的画廊</span>
        </RouterLink>
        <a href="#" class="nav-link" @click.prevent="authStore.logout()">
          <span class="nav-icon">👋</span>
          <span>退出</span>
        </a>
      </template>
      <template v-else>
        <RouterLink to="/login" class="nav-link">登录</RouterLink>
        <RouterLink to="/register" class="nav-link">注册</RouterLink>
      </template>
    </nav>
  </header>

  <RouterView />
</template>

<style scoped>
/* Apple 风格全局导航 */
.global-nav {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 48px;
  background: rgba(22, 22, 23, 0.8);
  backdrop-filter: saturate(180%) blur(20px);
  -webkit-backdrop-filter: saturate(180%) blur(20px);
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
}

.nav-container {
  display: flex;
  align-items: center;
  gap: 4px;
}

.nav-link {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  color: rgba(255, 255, 255, 0.85);
  text-decoration: none;
  font-size: 12px;
  font-weight: 400;
  letter-spacing: 0.5px;
  border-radius: 4px;
  transition: all 0.2s ease;
}

.nav-link:hover {
  color: #fff;
  background: rgba(255, 255, 255, 0.08);
}

.nav-link.router-link-active {
  color: #fff;
}

.nav-icon {
  font-size: 14px;
  opacity: 0.8;
}

/* 响应式 - 手机端隐藏图标文字，只显示图标 */
@media (max-width: 480px) {
  .nav-link span:not(.nav-icon) {
    display: none;
  }
  
  .nav-link {
    padding: 10px 14px;
  }
  
  .nav-icon {
    font-size: 18px;
  }
}
</style>
