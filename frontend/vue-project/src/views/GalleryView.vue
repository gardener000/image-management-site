<template>
  <div class="gallery-page">
    <div class="header-section">
      <h1>我的画廊</h1>
      <div class="header-controls">
        <!-- 搜索框 -->
        <el-input
          v-model="searchTerm"
          placeholder="按标签搜索..."
          class="search-input"
          @keyup.enter="performSearch"
          clearable
          @clear="performSearch"
        >
          <template #append>
            <el-button @click="performSearch">搜索</el-button>
          </template>
        </el-input>
        
        <!-- 选择模式切换 -->
        <el-button 
          :type="isSelectMode ? 'primary' : 'default'" 
          @click="toggleSelectMode"
        >
          {{ isSelectMode ? '退出选择' : '选择图片' }}
        </el-button>
      </div>
    </div>
    
    <!-- 选择模式工具栏 -->
    <div v-if="isSelectMode" class="selection-toolbar">
      <span>已选择 {{ selectedImages.length }} 张图片</span>
      <div class="selection-actions">
        <el-button @click="selectAll">全选</el-button>
        <el-button @click="clearSelection">取消全选</el-button>
        <el-button 
          type="success" 
          :disabled="selectedImages.length === 0"
          @click="startCarousel"
        >
          🎬 开始轮播
        </el-button>
      </div>
    </div>
    
    <ImageUpload @upload-success="handleUploadSuccess" />

    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="images.length === 0" class="empty">
      <span v-if="isSearching">未找到匹配 "{{ lastSearchTerm }}" 的图片</span>
      <span v-else>这里空空如也，快去上传你的第一张图片吧！</span>
    </div>
    <div v-else class="image-grid">
      <el-card 
        v-for="image in images" 
        :key="image.id" 
        class="image-card" 
        :class="{ selected: isImageSelected(image.id) }"
        shadow="hover" 
        @click="handleImageClick(image)"
      >
        <!-- 选择模式下的勾选框 -->
        <div v-if="isSelectMode" class="select-checkbox" @click.stop>
          <el-checkbox 
            :model-value="isImageSelected(image.id)"
            @change="toggleImageSelection(image)"
          />
        </div>
        <img :src="image.thumbnail_url" class="image" />
        <div class="image-info">
          <span>{{ image.filename }}</span>
        </div>
      </el-card>
    </div>

    <!-- 图片详情对话框 -->
    <ImageDetailsDialog 
      v-if="selectedImageId"
      :image-id="selectedImageId"
      v-model:visible="detailsDialogVisible"
      @close="handleDialogClose"
      @image-updated="fetchImages"
    />
    
    <!-- 轮播组件 -->
    <ImageCarousel
      :images="carouselImages"
      v-model:visible="carouselVisible"
      :start-index="0"
      @close="carouselVisible = false"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import ImageUpload from '@/components/ImageUpload.vue';
import ImageDetailsDialog from '@/components/ImageDetailsDialog.vue';
import ImageCarousel from '@/components/ImageCarousel.vue';
import apiClient from '@/api/axios.js';
import { ElMessage } from 'element-plus';

const images = ref([]);
const loading = ref(true);
const searchTerm = ref('');
const isSearching = ref(false);
const lastSearchTerm = ref('');

const selectedImageId = ref(null);
const detailsDialogVisible = ref(false);

// --- 选择模式相关状态 ---
const isSelectMode = ref(false);
const selectedImages = ref([]); // 存储选中的图片对象

// --- 轮播相关状态 ---
const carouselVisible = ref(false);
const carouselImages = computed(() => selectedImages.value);

// 切换选择模式
const toggleSelectMode = () => {
  isSelectMode.value = !isSelectMode.value;
  if (!isSelectMode.value) {
    clearSelection();
  }
};

// 检查图片是否被选中
const isImageSelected = (imageId) => {
  return selectedImages.value.some(img => img.id === imageId);
};

// 切换单个图片的选中状态
const toggleImageSelection = (image) => {
  const index = selectedImages.value.findIndex(img => img.id === image.id);
  if (index === -1) {
    selectedImages.value.push(image);
  } else {
    selectedImages.value.splice(index, 1);
  }
};

// 全选
const selectAll = () => {
  selectedImages.value = [...images.value];
};

// 取消全选
const clearSelection = () => {
  selectedImages.value = [];
};

// 开始轮播
const startCarousel = () => {
  if (selectedImages.value.length > 0) {
    carouselVisible.value = true;
  }
};

// 处理图片点击
const handleImageClick = (image) => {
  if (isSelectMode.value) {
    toggleImageSelection(image);
  } else {
    openImageDetails(image.id);
  }
};

// 获取图片列表的函数
const fetchImages = async (tag = '') => {
  loading.value = true;
  isSearching.value = !!tag;
  lastSearchTerm.value = tag;

  try {
    const response = await apiClient.get('/images/', {
      params: { tag: tag || undefined }
    });
    images.value = response.data;
  } catch (error) {
    ElMessage.error('获取图片列表失败');
    console.error(error);
  } finally {
    loading.value = false;
  }
};

// 执行搜索
const performSearch = () => {
  fetchImages(searchTerm.value);
};

// 上传成功后的处理
const handleUploadSuccess = () => {
  if (!isSearching.value) {
    fetchImages();
  } else {
    ElMessage.info('上传成功！清空搜索框可查看所有图片。');
  }
};

// 打开详情弹窗
const openImageDetails = (id) => {
  selectedImageId.value = id;
  detailsDialogVisible.value = true;
};

// 关闭详情弹窗
const handleDialogClose = () => {
  detailsDialogVisible.value = false;
  setTimeout(() => {
    selectedImageId.value = null;
  }, 300);
};

onMounted(() => {
  fetchImages();
});
</script>

<style scoped>
.gallery-page {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}
.header-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.search-input {
  width: 300px;
}
.image-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 15px;
}
.image-card {
  cursor: pointer;
}
.image {
  width: 100%;
  height: 180px;
  object-fit: cover;
  display: block;
}
.image-info {
  padding: 10px;
  font-size: 14px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.loading, .empty {
  text-align: center;
  margin-top: 50px;
  color: #888;
}

/* 头部控件容器 */
.header-controls {
  display: flex;
  gap: 12px;
  align-items: center;
}

/* 选择模式工具栏 */
.selection-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 8px;
  margin-bottom: 16px;
  color: white;
}

.selection-actions {
  display: flex;
  gap: 8px;
}

/* 选中状态的图片卡片 */
.image-card.selected {
  outline: 3px solid #409eff;
  outline-offset: -3px;
}

.image-card {
  position: relative;
}

/* 勾选框 */
.select-checkbox {
  position: absolute;
  top: 8px;
  left: 8px;
  z-index: 10;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 4px;
  padding: 2px;
}

/* 手机端响应式 */
@media (max-width: 768px) {
  .header-section {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }
  
  .header-controls {
    flex-direction: column;
    gap: 8px;
  }
  
  .search-input {
    width: 100%;
  }
  
  .selection-toolbar {
    flex-direction: column;
    gap: 12px;
    text-align: center;
  }
  
  .selection-actions {
    flex-wrap: wrap;
    justify-content: center;
  }
  
  .image-grid {
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  }
}
</style>