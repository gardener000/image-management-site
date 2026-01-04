<template>
  <div class="auth-page">
    <!-- 毛玻璃注册卡片 -->
    <div class="auth-card">
      <h1 class="auth-title">注册</h1>
      <p class="auth-subtitle">创建账号，开启你的相册之旅</p>
      
      <form @submit.prevent="onSubmit" class="auth-form">
        <div class="input-group">
          <span class="input-icon">👤</span>
          <input 
            v-model="form.username" 
            type="text" 
            placeholder="用户名（至少6位）"
            required
          />
        </div>
        
        <div class="input-group">
          <span class="input-icon">📧</span>
          <input 
            v-model="form.email" 
            type="email" 
            placeholder="邮箱地址"
            required
          />
        </div>
        
        <div class="input-group">
          <span class="input-icon">🔒</span>
          <input 
            v-model="form.password" 
            type="password" 
            placeholder="密码（至少6位）"
            required
          />
        </div>
        
        <button type="submit" class="submit-btn">立即注册</button>
      </form>
      
      <div class="auth-footer">
        <span>已有账号？</span>
        <router-link to="/login">立即登录</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive } from 'vue';
import { useRouter } from 'vue-router';
import apiClient from '@/api/axios.js';
import { ElMessage } from 'element-plus';

const router = useRouter();

const form = reactive({
  username: '',
  email: '',
  password: ''
});

const onSubmit = async () => {
  try {
    await apiClient.post('/auth/register', form);
    ElMessage.success('注册成功！');
    setTimeout(() => router.push('/login'), 1500);
  } catch (error) {
    const msg = error.response?.data?.error || '注册失败';
    ElMessage.error(msg);
  }
};
</script>

<style scoped>
.auth-page {
  min-height: calc(100vh - 48px);
  background: radial-gradient(ellipse at center, #1a1a1a 0%, #000 70%);
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
  font-size: 36px;
  font-weight: 200;
  color: #fff;
  text-align: center;
  margin: 0 0 8px;
  letter-spacing: 12px;
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
  background: rgba(255, 255, 255, 0.03) !important;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  padding: 0 18px;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
}

.input-group:focus-within {
  background: rgba(255, 255, 255, 0.05) !important;
  border-color: rgba(255, 255, 255, 0.18);
}

.input-icon {
  font-size: 15px;
  opacity: 0.4;
  margin-right: 14px;
  line-height: 1;
}

.input-group input {
  flex: 1;
  background: transparent !important;
  border: none !important;
  padding: 18px 0;
  color: #fff !important;
  font-size: 15px;
  outline: none !important;
  box-shadow: none !important;
}

.input-group input::placeholder {
  color: rgba(255, 255, 255, 0.3);
}

/* 覆盖浏览器自动填充样式 */
.input-group input:-webkit-autofill,
.input-group input:-webkit-autofill:hover,
.input-group input:-webkit-autofill:focus,
.input-group input:-webkit-autofill:active {
  -webkit-box-shadow: 0 0 0 1000px rgba(30, 30, 30, 1) inset !important;
  -webkit-text-fill-color: #fff !important;
  transition: background-color 5000s ease-in-out 0s;
  caret-color: #fff;
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