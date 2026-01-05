<template>
  <div class="chat-page">
    <div class="chat-container">
      <!-- 聊天头部 -->
      <div class="chat-header">
        <h1>🔍 智能搜索</h1>
        <p>用自然语言搜索你的照片</p>
      </div>

      <!-- 对话区域 -->
      <div class="chat-messages" ref="messagesRef">
        <!-- 欢迎消息 -->
        <div class="message bot">
          <div class="message-content">
            <p>👋 你好！我可以帮你搜索照片。试试说：</p>
            <div class="suggestions">
              <button 
                v-for="(s, i) in suggestions" 
                :key="i" 
                class="suggestion-btn"
                @click="sendMessage(s)"
              >{{ s }}</button>
            </div>
          </div>
        </div>

        <!-- 对话历史 -->
        <div 
          v-for="(msg, idx) in messages" 
          :key="idx" 
          class="message"
          :class="msg.type"
        >
          <div class="message-content">
            <p>{{ msg.text }}</p>
            <!-- 图片结果 -->
            <div v-if="msg.images?.length" class="image-results">
              <div 
                v-for="img in msg.images" 
                :key="img.id" 
                class="result-item"
                @click="openImage(img)"
              >
                <img :src="img.thumbnail_url" :alt="img.filename" />
                <div class="result-tags">
                  <span v-for="tag in img.tags.slice(0, 2)" :key="tag.id">{{ tag.name }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 加载中 -->
        <div v-if="loading" class="message bot">
          <div class="message-content loading">
            <span class="dot"></span>
            <span class="dot"></span>
            <span class="dot"></span>
          </div>
        </div>
      </div>

      <!-- 输入区域 -->
      <div class="chat-input">
        <input 
          v-model="inputText"
          type="text"
          placeholder="描述你想找的照片..."
          @keyup.enter="sendMessage(inputText)"
        />
        <button @click="sendMessage(inputText)" :disabled="!inputText.trim()">
          发送
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue';
import apiClient from '@/api/axios.js';

const inputText = ref('');
const messages = ref([]);
const loading = ref(false);
const messagesRef = ref(null);
const suggestions = ref([
  '帮我找风景照片',
  '显示最近的图片',
  '找有建筑的照片'
]);

const scrollToBottom = () => {
  nextTick(() => {
    if (messagesRef.value) {
      messagesRef.value.scrollTop = messagesRef.value.scrollHeight;
    }
  });
};

const sendMessage = async (text) => {
  if (!text?.trim()) return;
  
  // 添加用户消息
  messages.value.push({ type: 'user', text: text.trim() });
  inputText.value = '';
  loading.value = true;
  scrollToBottom();
  
  try {
    const response = await apiClient.post('/chat/search', { query: text.trim() });
    const data = response.data;
    
    // 添加AI回复
    messages.value.push({
      type: 'bot',
      text: data.message,
      images: data.images
    });
  } catch (error) {
    messages.value.push({
      type: 'bot',
      text: '抱歉，搜索出错了，请稍后再试。'
    });
  } finally {
    loading.value = false;
    scrollToBottom();
  }
};

const openImage = (img) => {
  window.open(img.original_url, '_blank');
};

onMounted(async () => {
  // 获取搜索建议
  try {
    const res = await apiClient.get('/chat/suggestions');
    if (res.data.suggestions?.length) {
      suggestions.value = res.data.suggestions.slice(0, 5);
    }
  } catch (e) {
    console.error('获取建议失败', e);
  }
});
</script>

<style scoped>
.chat-page {
  min-height: calc(100vh - 48px);
  background: #000;
  display: flex;
  justify-content: center;
  padding: 40px 20px;
}

.chat-container {
  width: 100%;
  max-width: 800px;
  display: flex;
  flex-direction: column;
  height: calc(100vh - 128px);
}

.chat-header {
  text-align: center;
  margin-bottom: 24px;
}

.chat-header h1 {
  font-size: 28px;
  font-weight: 300;
  color: #fff;
  letter-spacing: 4px;
  margin: 0;
}

.chat-header p {
  color: rgba(255,255,255,0.5);
  font-size: 14px;
  margin-top: 8px;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px 0;
}

.message {
  margin-bottom: 16px;
  display: flex;
}

.message.user {
  justify-content: flex-end;
}

.message-content {
  max-width: 80%;
  padding: 14px 18px;
  border-radius: 16px;
  font-size: 14px;
  line-height: 1.6;
}

.message.user .message-content {
  background: rgba(255,255,255,0.15);
  color: #fff;
  border-radius: 16px 16px 4px 16px;
}

.message.bot .message-content {
  background: rgba(255,255,255,0.05);
  color: rgba(255,255,255,0.9);
  border-radius: 16px 16px 16px 4px;
}

.message-content p {
  margin: 0;
}

.suggestions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 12px;
}

.suggestion-btn {
  padding: 8px 14px;
  background: rgba(255,255,255,0.1);
  border: 1px solid rgba(255,255,255,0.15);
  border-radius: 20px;
  color: rgba(255,255,255,0.8);
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}

.suggestion-btn:hover {
  background: rgba(255,255,255,0.2);
}

.image-results {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
  gap: 10px;
  margin-top: 12px;
}

.result-item {
  position: relative;
  aspect-ratio: 1;
  border-radius: 10px;
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.2s;
}

.result-item:hover {
  transform: scale(1.05);
}

.result-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.result-tags {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 4px;
  background: linear-gradient(transparent, rgba(0,0,0,0.8));
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.result-tags span {
  font-size: 10px;
  color: rgba(255,255,255,0.8);
  padding: 2px 6px;
  background: rgba(255,255,255,0.2);
  border-radius: 8px;
}

.loading {
  display: flex;
  gap: 6px;
  padding: 16px 20px;
}

.dot {
  width: 8px;
  height: 8px;
  background: rgba(255,255,255,0.5);
  border-radius: 50%;
  animation: bounce 1.4s ease-in-out infinite;
}

.dot:nth-child(2) { animation-delay: 0.2s; }
.dot:nth-child(3) { animation-delay: 0.4s; }

@keyframes bounce {
  0%, 80%, 100% { transform: translateY(0); }
  40% { transform: translateY(-8px); }
}

.chat-input {
  display: flex;
  gap: 12px;
  padding: 16px;
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 16px;
  margin-top: 16px;
}

.chat-input input {
  flex: 1;
  background: transparent;
  border: none;
  color: #fff;
  font-size: 15px;
  outline: none;
}

.chat-input input::placeholder {
  color: rgba(255,255,255,0.35);
}

.chat-input button {
  padding: 10px 24px;
  background: #fff;
  border: none;
  border-radius: 12px;
  color: #000;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.chat-input button:hover:not(:disabled) {
  transform: scale(1.02);
}

.chat-input button:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
</style>
