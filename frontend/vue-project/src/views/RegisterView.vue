<template>
  <div class="register-container">
    <el-card class="register-card">
      <template #header>
        <div class="card-header">
          <span>用户注册</span>
        </div>
      </template>
      <el-form :model="form" label-width="80px">
        <el-form-item label="用户名">
          <el-input v-model="form.username" placeholder="请输入至少6位用户名"></el-input>
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="form.email" placeholder="请输入有效的邮箱地址"></el-input>
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="form.password" type="password" show-password placeholder="请输入至少6位密码"></el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="onSubmit">立即注册</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { reactive } from 'vue';
import { useRouter } from 'vue-router';
import apiClient from '@/api/axios.js';
import { ElMessage } from 'element-plus';

const router = useRouter();

// 使用 reactive 创建一个响应式对象来存储表单数据
const form = reactive({
  username: '',
  email: '',
  password: ''
});

const onSubmit = async () => {
  try {
    // 调用我们封装的 apiClient 来发送 POST 请求
    const response = await apiClient.post('/auth/register', {
      username: form.username,
      email: form.email,
      password: form.password
    });
    
    // 使用 Element Plus 的 ElMessage 显示成功提示
    ElMessage.success('注册成功！即将跳转到登录页面...');
    
    // 1.5秒后跳转到登录页
    setTimeout(() => {
      router.push('/login');
    }, 1500);

  } catch (error) {
    // 如果请求失败，显示错误信息
    const errorMessage = error.response?.data?.error || '注册失败，请稍后再试';
    ElMessage.error(errorMessage);
    console.error('注册失败:', error.response);
  }
};
</script>

<style scoped>
.register-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #f5f7fa;
}
.register-card {
  width: 400px;
}
.card-header {
  text-align: center;
  font-size: 20px;
}
</style>