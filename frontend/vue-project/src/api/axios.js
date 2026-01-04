// frontend/vue-project/src/api/axios.js
import axios from 'axios';

// 动态获取当前主机名，支持 localhost 和局域网 IP 访问
const API_HOST = window.location.hostname;

const apiClient = axios.create({
  baseURL: `http://${API_HOST}:5000/api`,
  headers: {
    'Content-Type': 'application/json'
  }
});

export default apiClient;