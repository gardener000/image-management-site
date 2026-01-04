<template>
  <div class="home-slideshow" v-if="images.length > 0">
    <!-- 轮播主体 -->
    <div class="slideshow-container">
      <transition name="fade" mode="out-in">
        <img 
          :key="currentIndex"
          :src="currentImage?.original_url" 
          :alt="currentImage?.filename" 
          class="slideshow-image"
        />
      </transition>
      
      <!-- 左右切换按钮 -->
      <button class="nav-btn prev" @click="prev">
        <el-icon size="24"><ArrowLeft /></el-icon>
      </button>
      <button class="nav-btn next" @click="next">
        <el-icon size="24"><ArrowRight /></el-icon>
      </button>
      
      <!-- 右上角控制按钮 -->
      <div class="slideshow-controls">
        <!-- 自定义模式时显示随机模式按钮 -->
        <el-button 
          v-if="isCustomMode" 
          size="small" 
          type="info"
          @click="switchToRandomMode"
        >
          🎲 随机模式
        </el-button>
        <el-button 
          size="small" 
          :type="isPlaying ? 'warning' : 'primary'"
          @click="toggleAutoPlay"
        >
          {{ isPlaying ? '⏸ 暂停' : '▶ 播放' }}
        </el-button>
        <el-button size="small" type="success" @click="goToGallery">
          📷 选择图片
        </el-button>
      </div>
      
      <!-- 模式指示器 -->
      <div class="mode-indicator" v-if="isCustomMode">
        <el-tag type="success" size="small">自定义播放中 ({{ images.length }} 张)</el-tag>
      </div>
      
      <!-- 底部指示器 -->
      <div class="slideshow-indicators">
        <span 
          v-for="(_, index) in images" 
          :key="index"
          class="indicator"
          :class="{ active: index === currentIndex }"
          @click="goTo(index)"
        ></span>
      </div>
      
      <!-- 图片信息 -->
      <div class="image-info">
        <span>{{ currentImage?.filename }}</span>
      </div>
    </div>
  </div>
  
  <!-- 无图片时的占位 -->
  <div v-else class="empty-slideshow">
    <div class="empty-content">
      <el-icon size="64" color="#ccc"><Picture /></el-icon>
      <p>还没有图片，快去上传吧！</p>
      <el-button type="primary" @click="goToGallery">前往画廊上传</el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import { ArrowLeft, ArrowRight, Picture } from '@element-plus/icons-vue';
import apiClient from '@/api/axios.js';
import { slideshowStore } from '@/stores/slideshowStore.js';

const router = useRouter();

const images = ref([]);
const currentIndex = ref(0);
const isPlaying = ref(true); // 默认自动播放
const isCustomMode = ref(false); // 是否为自定义模式
let autoPlayTimer = null;

// 当前显示的图片
const currentImage = computed(() => images.value[currentIndex.value]);

// 初始化图片列表
const initImages = async () => {
  // 检查是否有自定义图片
  const customImages = slideshowStore.getImages();
  
  if (customImages && customImages.length > 0) {
    // 自定义模式
    images.value = customImages;
    isCustomMode.value = true;
  } else {
    // 随机模式
    await fetchRandomImages();
  }
  
  // 开始播放
  if (images.value.length > 0) {
    startAutoPlay();
  }
};

// 获取随机图片列表
const fetchRandomImages = async () => {
  try {
    const response = await apiClient.get('/images/');
    images.value = response.data;
    // 随机打乱顺序
    images.value = images.value.sort(() => Math.random() - 0.5);
    isCustomMode.value = false;
  } catch (error) {
    console.error('获取图片失败', error);
  }
};

// 切换到随机模式
const switchToRandomMode = async () => {
  // 清除自定义图片
  slideshowStore.clearImages();
  // 重新加载随机图片
  currentIndex.value = 0;
  await fetchRandomImages();
  // 重启自动播放
  if (images.value.length > 0) {
    isPlaying.value = true;
    startAutoPlay();
  }
};

// 切换到上一张
const prev = () => {
  if (currentIndex.value > 0) {
    currentIndex.value--;
  } else {
    currentIndex.value = images.value.length - 1;
  }
};

// 切换到下一张
const next = () => {
  if (currentIndex.value < images.value.length - 1) {
    currentIndex.value++;
  } else {
    currentIndex.value = 0;
  }
};

// 跳转到指定图片
const goTo = (index) => {
  currentIndex.value = index;
};

// 切换自动播放
const toggleAutoPlay = () => {
  isPlaying.value = !isPlaying.value;
  if (isPlaying.value) {
    startAutoPlay();
  } else {
    stopAutoPlay();
  }
};

const startAutoPlay = () => {
  stopAutoPlay();
  autoPlayTimer = setInterval(() => {
    next();
  }, 4000); // 4秒切换
};

const stopAutoPlay = () => {
  if (autoPlayTimer) {
    clearInterval(autoPlayTimer);
    autoPlayTimer = null;
  }
};

// 跳转到画廊（直接进入选择模式）
const goToGallery = () => {
  router.push({ path: '/gallery', query: { select: 'true' } });
};

onMounted(() => {
  initImages();
});

onUnmounted(() => {
  stopAutoPlay();
});
</script>

<style scoped>
.home-slideshow {
  width: 100%;
  height: calc(100vh - 60px); /* 减去导航栏高度 */
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
}

.slideshow-container {
  position: relative;
  width: 90%;
  max-width: 1200px;
  height: 80%;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
}

.slideshow-image {
  width: 100%;
  height: 100%;
  object-fit: contain;
  background: #000;
}

/* 淡入淡出动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.5s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 导航按钮 */
.nav-btn {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  border: none;
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s;
}

.nav-btn:hover {
  background: rgba(255, 255, 255, 0.4);
  transform: translateY(-50%) scale(1.1);
}

.nav-btn.prev {
  left: 16px;
}

.nav-btn.next {
  right: 16px;
}

/* 右上角控制按钮 */
.slideshow-controls {
  position: absolute;
  top: 16px;
  right: 16px;
  display: flex;
  gap: 8px;
}

/* 模式指示器 */
.mode-indicator {
  position: absolute;
  top: 16px;
  left: 16px;
}

/* 底部指示器 */
.slideshow-indicators {
  position: absolute;
  bottom: 60px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 8px;
}

.indicator {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.4);
  cursor: pointer;
  transition: all 0.3s;
}

.indicator:hover {
  background: rgba(255, 255, 255, 0.7);
}

.indicator.active {
  background: #409eff;
  transform: scale(1.2);
}

/* 图片信息 */
.image-info {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 16px;
  background: linear-gradient(transparent, rgba(0, 0, 0, 0.7));
  color: white;
  text-align: center;
  font-size: 14px;
}

/* 空状态 */
.empty-slideshow {
  width: 100%;
  height: calc(100vh - 60px);
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
}

.empty-content {
  text-align: center;
  color: white;
}

.empty-content p {
  margin: 20px 0;
  font-size: 18px;
  color: #aaa;
}

/* 手机端适配 */
@media (max-width: 768px) {
  .slideshow-container {
    width: 95%;
    height: 70%;
  }
  
  .nav-btn {
    width: 36px;
    height: 36px;
  }
  
  .slideshow-controls {
    top: 8px;
    right: 8px;
    flex-direction: column;
  }
  
  .slideshow-indicators {
    bottom: 50px;
  }
  
  .indicator {
    width: 8px;
    height: 8px;
  }
}
</style>
