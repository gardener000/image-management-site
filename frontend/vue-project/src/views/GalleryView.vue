<template>
    <div class="gallery-page">
    <h1>我的画廊</h1>
    
    <!-- 1. 引入上传组件 -->
    <ImageUpload @upload-success="fetchImages" />

    <!-- 2. 图片展示区 -->
    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="images.length === 0" class="empty">
        这里空空如也，快去上传你的第一张图片吧！
    </div>
    <div v-else class="image-grid">
        <el-card v-for="image in images" :key="image.id" class="image-card" shadow="hover">
        <img :src="image.thumbnail_url" class="image" @click="previewImage(image.original_url)" />
        <div class="image-info">
            <span>{{ image.filename }}</span>
        </div>
        </el-card>
    </div>

    <!-- 3. 图片预览对话框 -->
    <el-dialog v-model="dialogVisible" title="图片预览" width="70%">
        <img :src="previewImageUrl" style="width: 100%" />
    </el-dialog>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import ImageUpload from '@/components/ImageUpload.vue';
import apiClient from '@/api/axios.js';
import { ElMessage } from 'element-plus';

const images = ref([]);
const loading = ref(true);
const dialogVisible = ref(false);
const previewImageUrl = ref('');

// 获取图片列表的函数
const fetchImages = async () => {
    loading.value = true;
    try {
    const response = await apiClient.get('/images/');
    images.value = response.data;
    } catch (error) {
    ElMessage.error('获取图片列表失败');
    console.error(error);
    } finally {
    loading.value = false;
    }
};

// 点击缩略图时，显示原图预览
const previewImage = (url) => {
    previewImageUrl.value = url;
    dialogVisible.value = true;
};

// 组件挂载后（即页面加载后），立即获取图片列表
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