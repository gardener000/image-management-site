<template>
    <div class="upload-container">
    <el-upload
        class="uploader"
        :action="uploadUrl"
        :headers="uploadHeaders"
        :show-file-list="false"
        :on-success="handleSuccess"
        :on-error="handleError"
        :before-upload="beforeUpload"
        drag
    >
        <el-icon class="el-icon--upload"><upload-filled /></el-icon>
        <div class="el-upload__text">
        将文件拖到此处，或 <em>点击上传</em>
        </div>
        <template #tip>
        <div class="el-upload__tip">
            只能上传 jpg/png/gif 文件，且不超过 10MB
        </div>
        </template>
    </el-upload>
    </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { ElMessage } from 'element-plus';
import { UploadFilled } from '@element-plus/icons-vue';

// 定义一个 emit 事件，当上传成功后通知父组件
const emit = defineEmits(['upload-success']);

const authStore = useAuthStore();

// 上传的目标 URL
const uploadUrl = ref('http://localhost:5000/api/images/upload');

// 上传时需要携带的请求头，包含我们的 JWT Token
const uploadHeaders = computed(() => {
    return {
    Authorization: `Bearer ${authStore.token}`
    };
});

// 上传成功的回调函数
const handleSuccess = (response, file) => {
    ElMessage.success('图片上传成功！');
    // 触发 'upload-success' 事件，并把新图片的信息传给父组件
    emit('upload-success', response);
};

// 上传失败的回调函数
const handleError = (error, file) => {
    const errorMessage = JSON.parse(error.message)?.error || '上传失败';
    ElMessage.error(errorMessage);
};

// 上传前的校验
const beforeUpload = (file) => {
    const isAllowedType = ['image/jpeg', 'image/png', 'image/gif'].includes(file.type);
    const isLt10M = file.size / 1024 / 1024 < 10;

    if (!isAllowedType) {
    ElMessage.error('只能上传 JPG, PNG, GIF 格式的图片!');
    }
    if (!isLt10M) {
    ElMessage.error('图片大小不能超过 10MB!');
    }
    return isAllowedType && isLt10M;
};
</script>

<style scoped>
.upload-container {
    margin-bottom: 20px;
}
</style>