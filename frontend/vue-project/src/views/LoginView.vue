    <template>
      <div class="login-container">
        <el-card class="login-card">
          <template #header>
            <div class="card-header">
              <span>用户登录</span>
            </div>
          </template>
          <el-form :model="form" label-width="80px">
            <el-form-item label="用户名">
              <el-input v-model="form.username" placeholder="请输入用户名"></el-input>
            </el-form-item>
            <el-form-item label="密码">
              <el-input v-model="form.password" type="password" show-password placeholder="请输入密码"></el-input>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="onSubmit">登 录</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </div>
    </template>
    
    <script setup>
    import { reactive } from 'vue';
    import { useAuthStore } from '@/stores/auth'; // 1. 导入我们的 auth store
    import { ElMessage } from 'element-plus';

    const authStore = useAuthStore(); // 2. 获取 store 实例

    const form = reactive({
      username: '',
      password: ''
    });

    const onSubmit = async () => {
      try {
        // 3. 调用 store 中的 login action
        await authStore.login(form);
        ElMessage.success('登录成功！');
      } catch (error) {
        const errorMessage = error.response?.data?.error || '登录失败，请检查用户名和密码';
        ElMessage.error(errorMessage);
      }
    };
    </script>
    
    <style scoped>
    .login-container {
      display: flex;
      justify-content: center;
      align-items: center;
      height: 100vh;
      background-color: #f5f7fa;
    }
    .login-card {
      width: 400px;
    }
    .card-header {
      text-align: center;
      font-size: 20px;
    }
    </style>