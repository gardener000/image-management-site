// frontend/vue-project/src/api/axios.js
import axios from 'axios';

// 根据环境决定 API 地址
// 开发环境：使用当前主机名 + 5000 端口
// 生产环境（Docker）：使用相对路径，由 nginx 代理
const isDev = import.meta.env.DEV;
const API_HOST = window.location.hostname;
const baseURL = isDev ? `http://${API_HOST}:5000/api` : '/api';

const apiClient = axios.create({
  baseURL,
  headers: {
    'Content-Type': 'application/json'
  }
});

// 请求拦截器：自动添加 JWT Token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器：处理认证错误
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token 失效，可以在这里处理登出逻辑
      console.warn('认证失败，请重新登录');
    }
    return Promise.reject(error);
  }
);

export default apiClient;