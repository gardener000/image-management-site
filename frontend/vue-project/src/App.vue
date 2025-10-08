<script setup>
import { RouterLink, RouterView } from 'vue-router'
import { useAuthStore } from '@/stores/auth';// 1. 导入 auth store

const authStore = useAuthStore(); // 2. 获取 store 实例
</script>

<template>
  <header>
    <div class="wrapper">
      <nav>
        <RouterLink to="/">首页</RouterLink>

        <!-- 3. 使用 v-if 和 v-else 来根据登录状态显示不同链接 -->
        <template v-if="authStore.isAuthenticated">
          <RouterLink to="/gallery">我的画廊</RouterLink>
          <a href="#" @click.prevent="authStore.logout()">退出</a>
        </template>
        <template v-else>
          <RouterLink to="/login">登录</RouterLink>
          <RouterLink to="/register">注册</RouterLink>
        </template>
      </nav>
    </div>
  </header>

  <RouterView />
</template>

<style scoped>
    nav a {
      display: inline-block;
      padding: 0 1rem;
      border-left: 1px solid var(--color-border);
    }
    nav a:first-of-type {
      border: 0;
    }
</style>
