<template>
  <div class="gallery-page">
    <!-- 页面标题 -->
    <header class="page-header">
      <h1 class="page-title">我的画廊</h1>
      <p class="page-subtitle" v-if="images.length > 0">{{ images.length }} 件作品</p>
    </header>

    <!-- 顶部工具栏 -->
    <div class="toolbar">
      <div class="toolbar-left">
        <div class="search-box">
          <input 
            v-model="searchTerm"
            type="text"
            placeholder="搜索标签..."
            @keyup.enter="performSearch"
          />
          <button class="search-btn" @click="performSearch">🔍</button>
        </div>
      </div>
      <div class="toolbar-right">
        <button 
          class="pill-btn" 
          :class="{ active: isSelectMode }"
          @click="toggleSelectMode"
        >
          {{ isSelectMode ? '✕ 退出选择' : '☑ 选择图片' }}
        </button>
      </div>
    </div>

    <!-- 选择模式工具栏 -->
    <div v-if="isSelectMode" class="selection-bar">
      <span class="selection-count">已选择 {{ selectedImages.length }} 张</span>
      <div class="selection-actions">
        <button class="ghost-btn" @click="selectAll">全选</button>
        <button class="ghost-btn" @click="clearSelection">清空</button>
        <button 
          class="pill-btn primary"
          :disabled="selectedImages.length === 0"
          @click="confirmAndPlay"
        >
          ▶ 开始播放
        </button>
      </div>
    </div>

    <!-- 上传区域 -->
    <div class="upload-zone">
      <el-upload
        class="dark-uploader"
        :action="uploadUrl"
        :headers="uploadHeaders"
        :show-file-list="false"
        :on-success="handleUploadSuccess"
        :before-upload="beforeUpload"
        drag
        multiple
      >
        <div class="upload-content">
          <span class="upload-icon">📤</span>
          <span class="upload-text">拖拽图片到此处，或 <em>点击上传</em></span>
          <span class="upload-hint">支持 JPG, PNG, GIF · 最大 10MB</span>
        </div>
      </el-upload>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-state">
      <div class="loader"></div>
      <span>加载中...</span>
    </div>

    <!-- 空状态 -->
    <div v-else-if="images.length === 0" class="empty-state">
      <span class="empty-icon">🖼️</span>
      <p v-if="isSearching">未找到 "{{ lastSearchTerm }}" 相关作品</p>
      <p v-else>还没有作品，开始上传你的第一张图片吧</p>
    </div>

    <!-- 图片网格 -->
    <div v-else class="gallery-grid">
      <div 
        v-for="image in images" 
        :key="image.id"
        class="gallery-item"
        :class="{ selected: isImageSelected(image.id) }"
        @click="handleImageClick(image)"
      >
        <div class="item-image">
          <img :src="image.thumbnail_url" :alt="image.filename" />
          <!-- 选择模式勾选 -->
          <div v-if="isSelectMode" class="select-marker">
            <span v-if="isImageSelected(image.id)">✓</span>
          </div>
          <!-- 悬停信息 -->
          <div class="item-overlay">
            <span class="item-name">{{ image.filename }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 图片详情弹窗 -->
    <ImageDetailsDialog 
      v-if="selectedImageId"
      :image-id="selectedImageId"
      v-model:visible="detailsDialogVisible"
      @close="handleDialogClose"
      @image-updated="fetchImages"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import ImageDetailsDialog from '@/components/ImageDetailsDialog.vue';
import apiClient from '@/api/axios.js';
import { ElMessage } from 'element-plus';
import { slideshowStore } from '@/stores/slideshowStore.js';
import { useAuthStore } from '@/stores/auth';

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();

// 上传相关
const uploadUrl = `http://${window.location.hostname}:5000/api/images/upload`;
const uploadHeaders = computed(() => ({
  Authorization: `Bearer ${authStore.token}`
}));

const images = ref([]);
const loading = ref(true);
const searchTerm = ref('');
const isSearching = ref(false);
const lastSearchTerm = ref('');
const selectedImageId = ref(null);
const detailsDialogVisible = ref(false);
const isSelectMode = ref(false);
const selectedImages = ref([]);

const toggleSelectMode = () => {
  isSelectMode.value = !isSelectMode.value;
  if (!isSelectMode.value) clearSelection();
};

const isImageSelected = (id) => selectedImages.value.some(img => img.id === id);

const toggleImageSelection = (image) => {
  const idx = selectedImages.value.findIndex(img => img.id === image.id);
  if (idx === -1) selectedImages.value.push(image);
  else selectedImages.value.splice(idx, 1);
};

const selectAll = () => { selectedImages.value = [...images.value]; };
const clearSelection = () => { selectedImages.value = []; };

const confirmAndPlay = () => {
  if (selectedImages.value.length > 0) {
    slideshowStore.setImages(selectedImages.value);
    router.push('/');
    ElMessage.success(`已选择 ${selectedImages.value.length} 张图片`);
  }
};

const handleImageClick = (image) => {
  if (isSelectMode.value) toggleImageSelection(image);
  else openImageDetails(image.id);
};

const fetchImages = async (tag = '') => {
  loading.value = true;
  isSearching.value = !!tag;
  lastSearchTerm.value = tag;
  try {
    const res = await apiClient.get('/images/', { params: { tag: tag || undefined } });
    images.value = res.data;
  } catch (e) {
    ElMessage.error('获取图片失败');
  } finally {
    loading.value = false;
  }
};

const performSearch = () => fetchImages(searchTerm.value);

const handleUploadSuccess = () => {
  ElMessage.success('上传成功！');
  if (!isSearching.value) fetchImages();
};

const beforeUpload = (file) => {
  const ok = ['image/jpeg', 'image/png', 'image/gif'].includes(file.type) && file.size / 1024 / 1024 < 10;
  if (!ok) ElMessage.error('请上传 10MB 以内的 JPG/PNG/GIF 图片');
  return ok;
};

const openImageDetails = (id) => {
  selectedImageId.value = id;
  detailsDialogVisible.value = true;
};

const handleDialogClose = () => {
  detailsDialogVisible.value = false;
  setTimeout(() => { selectedImageId.value = null; }, 300);
};

onMounted(() => {
  fetchImages();
  if (route.query.select === 'true') isSelectMode.value = true;
});
</script>

<style scoped>
/* 深色画廊页面 - 全屏沉浸 */
.gallery-page {
  min-height: 100vh;
  background: #000;
  padding: 100px 40px 60px;
  box-sizing: border-box;
}

/* 页面标题 */
.page-header {
  text-align: center;
  margin-bottom: 48px;
}

.page-title {
  font-size: 42px;
  font-weight: 300;
  color: #fff;
  letter-spacing: 6px;
  margin: 0;
  text-transform: uppercase;
}

.page-subtitle {
  font-size: 13px;
  color: rgba(255,255,255,0.35);
  margin-top: 12px;
  letter-spacing: 2px;
}

/* 工具栏 */
.toolbar {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-bottom: 32px;
  gap: 16px;
  flex-wrap: wrap;
}

.search-box {
  display: flex;
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 24px;
  overflow: hidden;
  backdrop-filter: blur(10px);
}

.search-box input {
  background: transparent;
  border: none;
  padding: 12px 20px;
  color: #fff;
  font-size: 13px;
  width: 240px;
  outline: none;
  letter-spacing: 0.5px;
}

.search-box input::placeholder {
  color: rgba(255,255,255,0.4);
}

.search-btn {
  background: transparent;
  border: none;
  padding: 10px 14px;
  cursor: pointer;
  font-size: 14px;
}

/* 按钮样式 */
.pill-btn {
  padding: 10px 20px;
  border-radius: 20px;
  border: 1px solid rgba(255,255,255,0.2);
  background: rgba(255,255,255,0.08);
  color: rgba(255,255,255,0.85);
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}

.pill-btn:hover {
  background: rgba(255,255,255,0.15);
}

.pill-btn.active {
  background: rgba(255,255,255,0.9);
  color: #000;
  border-color: transparent;
}

.pill-btn.primary {
  background: #fff;
  color: #000;
  border: none;
  font-weight: 600;
}

.pill-btn.primary:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.ghost-btn {
  background: transparent;
  border: none;
  color: rgba(255,255,255,0.7);
  padding: 8px 14px;
  font-size: 13px;
  cursor: pointer;
}

.ghost-btn:hover {
  color: #fff;
}

/* 选择工具栏 */
.selection-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 20px;
  background: rgba(255,255,255,0.05);
  border-radius: 12px;
  margin-bottom: 24px;
}

.selection-count {
  color: rgba(255,255,255,0.7);
  font-size: 14px;
}

.selection-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

/* 上传区域 - 极简毛玻璃 */
.upload-zone {
  max-width: 600px;
  margin: 0 auto 48px;
}

:deep(.dark-uploader .el-upload-dragger) {
  background: rgba(255,255,255,0.02);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 20px;
  padding: 48px;
  transition: all 0.3s;
}

:deep(.dark-uploader .el-upload-dragger:hover) {
  background: rgba(255,255,255,0.05);
  border-color: rgba(255,255,255,0.15);
}

.upload-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.upload-icon {
  font-size: 32px;
  opacity: 0.6;
}

.upload-text {
  color: rgba(255,255,255,0.7);
  font-size: 14px;
}

.upload-text em {
  color: #fff;
  font-style: normal;
}

.upload-hint {
  color: rgba(255,255,255,0.4);
  font-size: 12px;
}

/* 加载状态 */
.loading-state {
  text-align: center;
  padding: 60px 0;
  color: rgba(255,255,255,0.5);
}

.loader {
  width: 32px;
  height: 32px;
  border: 2px solid rgba(255,255,255,0.1);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin: 0 auto 16px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 空状态 */
.empty-state {
  text-align: center;
  padding: 80px 20px;
  color: rgba(255,255,255,0.5);
}

.empty-icon {
  font-size: 64px;
  display: block;
  margin-bottom: 16px;
  opacity: 0.5;
}

/* 图片网格 - 多列布局 */
.gallery-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 20px;
}

.gallery-item {
  position: relative;
  cursor: pointer;
  border-radius: 12px;
  overflow: hidden;
  aspect-ratio: 1 / 1;
  background: #111;
  transition: transform 0.3s, box-shadow 0.3s;
}

.gallery-item:hover {
  transform: translateY(-4px);
  box-shadow: 0 20px 40px rgba(0,0,0,0.4);
}

.item-image {
  width: 100%;
  height: 100%;
  position: relative;
}

.item-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s;
}

.gallery-item:hover .item-image img {
  transform: scale(1.05);
}

/* 选中标记 */
.select-marker {
  position: absolute;
  top: 12px;
  left: 12px;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: rgba(255,255,255,0.2);
  border: 2px solid rgba(255,255,255,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 14px;
  font-weight: bold;
}

.gallery-item.selected .select-marker {
  background: #fff;
  border-color: #fff;
  color: #000;
}

/* 悬停信息 */
.item-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 30px 12px 12px;
  background: linear-gradient(transparent, rgba(0,0,0,0.8));
  opacity: 0;
  transition: opacity 0.3s;
}

.gallery-item:hover .item-overlay {
  opacity: 1;
}

.item-name {
  color: #fff;
  font-size: 12px;
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* 响应式 */
@media (max-width: 1400px) {
  .gallery-grid {
    grid-template-columns: repeat(4, 1fr);
  }
}

@media (max-width: 1024px) {
  .gallery-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 768px) {
  .gallery-page {
    padding: 80px 20px 40px;
  }
  
  .page-title {
    font-size: 28px;
    letter-spacing: 4px;
  }
  
  .toolbar {
    flex-direction: column;
  }
  
  .search-box input {
    width: 100%;
  }
  
  .gallery-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
  }
  
  .gallery-item {
    border-radius: 8px;
  }
}
</style>