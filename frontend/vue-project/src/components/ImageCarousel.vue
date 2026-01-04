<template>
  <Teleport to="body">
    <div v-if="visible" class="carousel-overlay" @keydown="handleKeydown" tabindex="0" ref="overlayRef">
      <!-- 顶部工具栏 -->
      <div class="carousel-header">
        <span class="image-counter">{{ currentIndex + 1 }} / {{ images.length }}</span>
        <div class="header-controls">
          <el-button :icon="isPlaying ? 'VideoPause' : 'VideoPlay'" circle @click="toggleAutoPlay" :title="isPlaying ? '暂停' : '自动播放'" />
          <el-button icon="Close" circle @click="close" title="关闭 (ESC)" />
        </div>
      </div>

      <!-- 主图片区域 -->
      <div class="carousel-main">
        <button class="nav-btn prev" @click="prev" :disabled="currentIndex === 0">
          <el-icon size="32"><ArrowLeft /></el-icon>
        </button>
        
        <div class="image-container">
          <img :src="currentImage?.original_url" :alt="currentImage?.filename" class="main-image" />
        </div>
        
        <button class="nav-btn next" @click="next" :disabled="currentIndex === images.length - 1">
          <el-icon size="32"><ArrowRight /></el-icon>
        </button>
      </div>

      <!-- 底部缩略图导航 -->
      <div class="carousel-thumbnails">
        <div 
          v-for="(image, index) in images" 
          :key="image.id"
          class="thumbnail"
          :class="{ active: index === currentIndex }"
          @click="goTo(index)"
        >
          <img :src="image.thumbnail_url" :alt="image.filename" />
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue';
import { ArrowLeft, ArrowRight } from '@element-plus/icons-vue';

const props = defineProps({
  images: {
    type: Array,
    required: true,
    default: () => []
  },
  visible: {
    type: Boolean,
    default: false
  },
  startIndex: {
    type: Number,
    default: 0
  }
});

const emit = defineEmits(['update:visible', 'close']);

const currentIndex = ref(0);
const isPlaying = ref(false);
const overlayRef = ref(null);
let autoPlayTimer = null;

// 当前显示的图片
const currentImage = computed(() => props.images[currentIndex.value]);

// 切换到上一张
const prev = () => {
  if (currentIndex.value > 0) {
    currentIndex.value--;
  }
};

// 切换到下一张
const next = () => {
  if (currentIndex.value < props.images.length - 1) {
    currentIndex.value++;
  } else if (isPlaying.value) {
    // 自动播放时，到最后一张后回到第一张
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
  }, 3000);
};

const stopAutoPlay = () => {
  if (autoPlayTimer) {
    clearInterval(autoPlayTimer);
    autoPlayTimer = null;
  }
};

// 关闭轮播
const close = () => {
  stopAutoPlay();
  emit('update:visible', false);
  emit('close');
};

// 键盘事件处理
const handleKeydown = (e) => {
  switch (e.key) {
    case 'ArrowLeft':
      prev();
      break;
    case 'ArrowRight':
      next();
      break;
    case 'Escape':
      close();
      break;
    case ' ': // 空格键
      e.preventDefault();
      toggleAutoPlay();
      break;
  }
};

// 监听 visible 变化
watch(() => props.visible, (newVal) => {
  if (newVal) {
    currentIndex.value = props.startIndex;
    nextTick(() => {
      overlayRef.value?.focus();
    });
  } else {
    stopAutoPlay();
    isPlaying.value = false;
  }
});

// 组件卸载时清理定时器
onUnmounted(() => {
  stopAutoPlay();
});
</script>

<style scoped>
.carousel-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.95);
  z-index: 9999;
  display: flex;
  flex-direction: column;
  outline: none;
}

.carousel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  color: white;
}

.image-counter {
  font-size: 16px;
  font-weight: 500;
}

.header-controls {
  display: flex;
  gap: 12px;
}

.header-controls .el-button {
  background: rgba(255, 255, 255, 0.1);
  border: none;
  color: white;
}

.header-controls .el-button:hover {
  background: rgba(255, 255, 255, 0.2);
}

.carousel-main {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 60px;
  position: relative;
  min-height: 0;
}

.image-container {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  overflow: hidden;
}

.main-image {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.nav-btn {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  border: none;
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s;
}

.nav-btn:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.25);
}

.nav-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.nav-btn.prev {
  left: 16px;
}

.nav-btn.next {
  right: 16px;
}

.carousel-thumbnails {
  display: flex;
  justify-content: center;
  gap: 8px;
  padding: 16px;
  background: rgba(0, 0, 0, 0.5);
  overflow-x: auto;
}

.thumbnail {
  width: 60px;
  height: 60px;
  border-radius: 4px;
  overflow: hidden;
  cursor: pointer;
  opacity: 0.5;
  transition: all 0.2s;
  flex-shrink: 0;
  border: 2px solid transparent;
}

.thumbnail:hover {
  opacity: 0.8;
}

.thumbnail.active {
  opacity: 1;
  border-color: #409eff;
}

.thumbnail img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* 手机端适配 */
@media (max-width: 768px) {
  .carousel-main {
    padding: 0 16px;
  }
  
  .nav-btn {
    width: 40px;
    height: 40px;
  }
  
  .nav-btn.prev {
    left: 8px;
  }
  
  .nav-btn.next {
    right: 8px;
  }
  
  .thumbnail {
    width: 50px;
    height: 50px;
  }
}
</style>
