<template>
  <div class="theater-page" v-if="images.length > 0">
    <!-- 顶部控制栏 (Apple 风格) -->
    <header class="top-nav">
      <div class="nav-left">
        <span class="mode-badge" v-if="isCustomMode">自定义播放</span>
        <span class="mode-badge" v-else>随机播放</span>
      </div>
      <div class="nav-center">
        <span class="nav-title">我的相册</span>
      </div>
      <div class="nav-right">
        <button v-if="isCustomMode" class="nav-btn" @click="switchToRandomMode">🎲 随机</button>
        <button class="nav-btn" :class="{ active: isPlaying }" @click="toggleAutoPlay">
          {{ isPlaying ? '⏸ 暂停' : '▶ 播放' }}
        </button>
        <button class="nav-btn primary" @click="goToGallery">✏️ 选择图片</button>
      </div>
    </header>

    <!-- 剧场式轮播主体 -->
    <main class="theater-stage">
      <div class="carousel-viewport">
        <!-- 左侧预览 -->
        <div class="slide-peek left" @click="prev">
          <div class="slide-inner" v-if="prevImage">
            <img :src="prevImage.original_url" :alt="prevImage.filename" />
          </div>
        </div>

        <!-- 中心主图 -->
        <div class="slide-main">
          <div class="slide-inner">
            <img :src="currentImage?.original_url" :alt="currentImage?.filename" />
          </div>
          
          <!-- 底部信息叠加 -->
          <div class="slide-overlay">
            <button class="pill-btn" @click="goToGallery">选择图片</button>
            <div class="slide-info">
              <span class="slide-title">{{ currentImage?.filename }}</span>
              <div class="slide-tags" v-if="currentImage?.tags?.length">
                <span class="tag-item" v-for="tag in currentImage.tags" :key="tag.id">
                  📍 {{ tag.name }}
                </span>
              </div>
              <span class="slide-meta">{{ formatDate(currentImage?.uploaded_at) }}</span>
            </div>
          </div>
        </div>

        <!-- 右侧预览 -->
        <div class="slide-peek right" @click="next">
          <div class="slide-inner" v-if="nextImage">
            <img :src="nextImage.original_url" :alt="nextImage.filename" />
          </div>
        </div>
      </div>

      <!-- 指示器 -->
      <div class="stage-indicators">
        <span 
          v-for="(_, idx) in Math.min(images.length, 8)" 
          :key="idx"
          class="indicator-dot"
          :class="{ active: idx === currentIndex % 8 }"
        ></span>
        <span class="indicator-count">{{ currentIndex + 1 }}/{{ images.length }}</span>
      </div>
    </main>
  </div>

  <!-- 空状态 -->
  <div class="theater-page empty-state" v-else>
    <div class="empty-box">
      <span class="empty-icon">📷</span>
      <h2>开始你的相册</h2>
      <p>上传照片，开启沉浸式浏览体验</p>
      <button class="pill-btn large" @click="goToGallery">前往画廊</button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import apiClient from '@/api/axios.js';
import { slideshowStore } from '@/stores/slideshowStore.js';

const router = useRouter();
const images = ref([]);
const currentIndex = ref(0);
const isPlaying = ref(true);
const isCustomMode = ref(false);
let timer = null;

const currentImage = computed(() => images.value[currentIndex.value]);
const prevImage = computed(() => images.value.length > 1 
  ? images.value[(currentIndex.value - 1 + images.value.length) % images.value.length] 
  : null);
const nextImage = computed(() => images.value.length > 1 
  ? images.value[(currentIndex.value + 1) % images.value.length] 
  : null);

const formatDate = (d) => d ? new Date(d).toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric' }) : '';

const init = async () => {
  const custom = slideshowStore.getImages();
  if (custom?.length) {
    images.value = custom;
    isCustomMode.value = true;
  } else {
    const res = await apiClient.get('/images/').catch(() => ({ data: [] }));
    images.value = res.data.sort(() => Math.random() - 0.5);
    isCustomMode.value = false;
  }
  if (images.value.length) startPlay();
};

const switchToRandomMode = async () => {
  slideshowStore.clearImages();
  currentIndex.value = 0;
  const res = await apiClient.get('/images/').catch(() => ({ data: [] }));
  images.value = res.data.sort(() => Math.random() - 0.5);
  isCustomMode.value = false;
  isPlaying.value = true;
  startPlay();
};

const prev = () => { currentIndex.value = (currentIndex.value - 1 + images.value.length) % images.value.length; };
const next = () => { currentIndex.value = (currentIndex.value + 1) % images.value.length; };

const toggleAutoPlay = () => {
  isPlaying.value = !isPlaying.value;
  isPlaying.value ? startPlay() : stopPlay();
};

const startPlay = () => { stopPlay(); timer = setInterval(next, 4000); };
const stopPlay = () => { if (timer) { clearInterval(timer); timer = null; } };

const goToGallery = () => router.push({ path: '/gallery', query: { select: 'true' } });

onMounted(init);
onUnmounted(stopPlay);
</script>

<style scoped>
/* 剧场页面 - 全屏深色 */
.theater-page {
  width: 100%;
  min-height: calc(100vh - 48px);
  background: #000;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.theater-page.empty-state {
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, #0f0f1a 0%, #1a1a2e 100%);
}

/* 顶部导航栏 */
.top-nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 24px;
  background: rgba(0,0,0,0.6);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  z-index: 100;
}

.nav-left, .nav-center, .nav-right {
  flex: 1;
}

.nav-center {
  text-align: center;
}

.nav-right {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

.nav-title {
  color: rgba(255,255,255,0.9);
  font-size: 14px;
  font-weight: 500;
  letter-spacing: 0.5px;
}

.mode-badge {
  font-size: 12px;
  color: rgba(255,255,255,0.5);
}

.nav-btn {
  padding: 6px 14px;
  background: rgba(255,255,255,0.1);
  border: none;
  border-radius: 16px;
  color: rgba(255,255,255,0.85);
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.nav-btn:hover {
  background: rgba(255,255,255,0.2);
}

.nav-btn.active {
  background: rgba(255,193,7,0.25);
  color: #ffd54f;
}

.nav-btn.primary {
  background: rgba(255,255,255,0.95);
  color: #000;
  font-weight: 500;
}

.nav-btn.primary:hover {
  background: #fff;
}

/* 剧场舞台 */
.theater-stage {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 20px 0;
}

/* 轮播视口 */
.carousel-viewport {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 75vh;
  gap: 20px;
  padding: 0 40px;
}

/* 侧边预览图 */
.slide-peek {
  width: 8%;
  height: 70%;
  flex-shrink: 0;
  cursor: pointer;
  opacity: 0.4;
  filter: brightness(0.5);
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.slide-peek:hover {
  opacity: 0.6;
  filter: brightness(0.7);
}

.slide-peek .slide-inner {
  width: 100%;
  height: 100%;
  overflow: hidden;
  border-radius: 12px;
}

.slide-peek img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* 主图 */
.slide-main {
  flex: 1;
  max-width: 80%;
  height: 100%;
  position: relative;
}

.slide-main .slide-inner {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 20px;
  overflow: hidden;
  background: #111;
  box-shadow: 0 30px 80px rgba(0,0,0,0.6);
}

.slide-main img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

/* 底部叠加信息 */
.slide-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 30px;
  background: linear-gradient(transparent, rgba(0,0,0,0.85));
  border-radius: 0 0 20px 20px;
  display: flex;
  align-items: center;
  gap: 20px;
}

.pill-btn {
  padding: 10px 22px;
  background: #fff;
  border: none;
  border-radius: 20px;
  color: #000;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s;
  white-space: nowrap;
}

.pill-btn:hover {
  transform: scale(1.03);
}

.pill-btn.large {
  padding: 14px 32px;
  font-size: 15px;
  border-radius: 25px;
}

.slide-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.slide-title {
  color: #fff;
  font-size: 15px;
  font-weight: 600;
}

.slide-meta {
  color: rgba(255,255,255,0.6);
  font-size: 13px;
}

.slide-tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin: 4px 0;
}

.tag-item {
  display: inline-flex;
  align-items: center;
  padding: 4px 10px;
  background: rgba(255,255,255,0.15);
  border-radius: 12px;
  font-size: 12px;
  color: rgba(255,255,255,0.9);
}

/* 指示器 */
.stage-indicators {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 8px;
  padding-top: 20px;
}

.indicator-dot {
  width: 8px;
  height: 8px;
  background: rgba(255,255,255,0.25);
  border-radius: 50%;
  transition: all 0.3s;
}

.indicator-dot.active {
  background: #fff;
  transform: scale(1.3);
}

.indicator-count {
  color: rgba(255,255,255,0.4);
  font-size: 12px;
  margin-left: 8px;
}

/* 空状态 */
.empty-box {
  text-align: center;
  color: #fff;
}

.empty-icon {
  font-size: 72px;
  display: block;
  margin-bottom: 24px;
}

.empty-box h2 {
  font-size: 26px;
  font-weight: 600;
  margin-bottom: 10px;
}

.empty-box p {
  color: rgba(255,255,255,0.5);
  margin-bottom: 30px;
}

/* 响应式 */
@media (max-width: 768px) {
  .top-nav {
    padding: 10px 16px;
  }
  
  .nav-left, .nav-center {
    display: none;
  }
  
  .nav-right {
    flex: 1;
    justify-content: center;
  }
  
  .slide-peek {
    display: none;
  }
  
  .slide-main {
    max-width: 95%;
  }
  
  .carousel-viewport {
    padding: 0 12px;
    height: 65vh;
  }
  
  .slide-overlay {
    padding: 20px;
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
}
</style>
