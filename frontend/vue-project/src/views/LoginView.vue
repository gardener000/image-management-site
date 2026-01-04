<template>
  <div class="auth-page">
    <!-- 毛玻璃登录卡片 -->
    <div class="auth-card">
      <h1 class="auth-title">登录</h1>
      <p class="auth-subtitle">欢迎回来，继续你的相册之旅</p>
      
      <form @submit.prevent="onSubmit" class="auth-form">
        <div class="input-group">
          <span class="input-icon">👤</span>
          <input 
            v-model="form.username" 
            type="text" 
            placeholder="用户名"
            required
          />
        </div>
        
        <div class="input-group">
          <span class="input-icon">🔒</span>
          <input 
            v-model="form.password" 
            type="password" 
            placeholder="密码"
            required
          />
        </div>
        
        <button type="submit" class="submit-btn">登 录</button>
      </form>
      
      <div class="auth-footer">
        <span>还没有账号？</span>
        <router-link to="/register">立即注册</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { ElMessage } from 'element-plus';

const authStore = useAuthStore();

const form = reactive({
  username: '',
  password: ''
});

const onSubmit = async () => {
  try {
    await authStore.login(form);
    ElMessage.success('登录成功！');
  } catch (error) {
    const msg = error.response?.data?.error || '登录失败';
    ElMessage.error(msg);
  }
};
</script>

<style scoped>
.auth-page {
  min-height: calc(100vh - 48px);
  background: #000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
}

.auth-card {
  width: 100%;
  max-width: 420px;
  padding: 48px 40px;
  background: rgba(255, 255, 255, 0.03);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 28px;
}

.auth-title {
  font-size: 32px;
  font-weight: 300;
  color: #fff;
  text-align: center;
  margin: 0 0 8px;
  letter-spacing: 4px;
}

.auth-subtitle {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.4);
  text-align: center;
  margin: 0 0 40px;
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.input-group {
  display: flex;
  align-items: center;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 14px;
  padding: 0 16px;
  transition: all 0.2s;
}

.input-group:focus-within {
  background: rgba(255, 255, 255, 0.08);
  box-shadow: 0 0 0 1px rgba(255, 255, 255, 0.15);
}

.input-icon {
  font-size: 18px;
  opacity: 0.5;
  margin-right: 12px;
}

.input-group input {
  flex: 1;
  background: transparent;
  border: none;
  padding: 16px 0;
  color: #fff;
  font-size: 15px;
  outline: none;
}

.input-group input::placeholder {
  color: rgba(255, 255, 255, 0.35);
}

.submit-btn {
  width: 100%;
  padding: 16px;
  margin-top: 16px;
  background: #fff;
  border: none;
  border-radius: 14px;
  color: #000;
  font-size: 15px;
  font-weight: 600;
  letter-spacing: 2px;
  cursor: pointer;
  transition: all 0.2s;
}

.submit-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(255, 255, 255, 0.15);
}

.auth-footer {
  text-align: center;
  margin-top: 32px;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.4);
}

.auth-footer a {
  color: #fff;
  margin-left: 8px;
  text-decoration: none;
}

.auth-footer a:hover {
  text-decoration: underline;
}
</style>