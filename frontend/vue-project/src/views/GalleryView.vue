<template>
  <div class="gallery-page">
    <div class="header-section">
      <h1>我的画廊</h1>
      <!-- 1. 添加搜索框 -->
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
    </div>
    
    <ImageUpload @upload-success="handleUploadSuccess" />

    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="images.length === 0" class="empty">
      <span v-if="isSearching">未找到匹配 "{{ lastSearchTerm }}" 的图片</span>
      <span v-else>这里空空如也，快去上传你的第一张图片吧！</span>
    </div>
    <div v-else class="image-grid">
      <!-- 2. 修改点击事件 -->
      <el-card v-for="image in images" :key="image.id" class="image-card" shadow="hover" @click="openImageDetails(image.id)">
        <img :src="image.thumbnail_url" class="image" />
        <div class="image-info">
          <span>{{ image.filename }}</span>
        </div>
      </el-card>
    </div>

    <!-- 3. 图片详情对话框 -->
    <ImageDetailsDialog 
      v-if="selectedImageId"
      :image-id="selectedImageId"
      v-model:visible="detailsDialogVisible"
      @close="handleDialogClose"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import ImageUpload from '@/components/ImageUpload.vue';
import ImageDetailsDialog from '@/components/ImageDetailsDialog.vue'; // 稍后创建
import apiClient from '@/api/axios.js';
import { ElMessage } from 'element-plus';

const images = ref([]);
const loading = ref(true);
const searchTerm = ref('');
const isSearching = ref(false);
const lastSearchTerm = ref('');

const selectedImageId = ref(null);
const detailsDialogVisible = ref(false);

// 获取图片列表的函数（已重构）
const fetchImages = async (tag = '') => {
  loading.value = true;
  isSearching.value = !!tag; // 如果 tag 不为空，则认为是搜索状态
  lastSearchTerm.value = tag;

  try {
    const response = await apiClient.get('/images/', {
      params: { tag: tag || undefined } // 如果tag为空，则不发送该参数
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
  // 如果当前正在搜索，则不刷新列表，让用户保持在搜索结果页
  // 如果不在搜索，则刷新列表显示最新图片
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
  // 使用 setTimeout 延迟清空ID，避免在弹窗关闭动画完成前组件被销毁
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
</style>