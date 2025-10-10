<template>
  <el-dialog
    :model-value="visible"
    title="图片详情"
    width="60%"
    @close="closeDialog"
  >
    <div v-if="loading" class="dialog-loading">加载中...</div>
    <div v-else-if="imageDetails" class="details-content">
      <div class="image-preview">
        <img :src="imageDetails.original_url" alt="Image preview" />
      </div>
      <div class="info-panel">
        <h3>信息</h3>
        <p><strong>文件名:</strong> {{ imageDetails.filename }}</p>
        <p><strong>分辨率:</strong> {{ imageDetails.resolution }}</p>
        <p><strong>上传时间:</strong> {{ new Date(imageDetails.uploaded_at).toLocaleString() }}</p>
        
        <h3>标签管理</h3>
        <div class="tags-section">
          <el-tag
            v-for="tag in imageDetails.tags"
            :key="tag.id"
            class="tag-item"
            closable
            @close="handleRemoveTag(tag.id)"
          >
            {{ tag.name }}
          </el-tag>
          
          <el-input
            v-if="inputVisible"
            ref="InputRef"
            v-model="inputValue"
            class="tag-input"
            size="small"
            @keyup.enter="handleInputConfirm"
            @blur="handleInputConfirm"
          />
          <el-button v-else class="button-new-tag" size="small" @click="showInput">
            + 添加标签
          </el-button>
        </div>
      </div>
    </div>
  </el-dialog>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue';
import apiClient from '@/api/axios.js';
import { ElMessage } from 'element-plus';

const props = defineProps({
  imageId: {
    type: Number,
    required: true,
  },
  visible: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits(['update:visible', 'close']);

const loading = ref(true);
const imageDetails = ref(null);

const inputVisible = ref(false);
const inputValue = ref('');
const InputRef = ref(null); // 用于获取 input 元素的引用

// 监听 imageId 的变化，当它有值时，获取图片详情
watch(() => props.imageId, async (newId) => {
  if (newId) {
    loading.value = true;
    try {
      const response = await apiClient.get(`/images/${newId}`);
      imageDetails.value = response.data;
    } catch (error) {
      ElMessage.error('获取图片详情失败');
      closeDialog();
    } finally {
      loading.value = false;
    }
  }
}, { immediate: true }); // immediate: true 确保组件一创建就执行一次

const closeDialog = () => {
  emit('update:visible', false);
  emit('close');
};

// --- 标签管理逻辑 ---
const handleRemoveTag = async (tagId) => {
  try {
    await apiClient.delete(`/images/${props.imageId}/tags/${tagId}`);
    // 从前端列表中移除标签
    const index = imageDetails.value.tags.findIndex(tag => tag.id === tagId);
    if (index !== -1) {
      imageDetails.value.tags.splice(index, 1);
    }
    ElMessage.success('标签已移除');
  } catch (error) {
    ElMessage.error('移除标签失败');
  }
};

const showInput = () => {
  inputVisible.value = true;
  nextTick(() => {
    InputRef.value.focus(); // 自动聚焦
  });
};

const handleInputConfirm = async () => {
  if (inputValue.value) {
    try {
      const response = await apiClient.post(`/images/${props.imageId}/tags`, { name: inputValue.value });
      // 检查返回的标签是否已存在于列表中
      const existingTag = imageDetails.value.tags.find(tag => tag.id === response.data.id);
      if (!existingTag) {
        imageDetails.value.tags.push(response.data);
      }
      ElMessage.success('标签已添加');
    } catch (error) {
      ElMessage.error('添加标签失败');
    }
  }
  inputVisible.value = false;
  inputValue.value = '';
};
</script>

<style scoped>
.details-content {
  display: flex;
  gap: 20px;
}
.image-preview {
  flex: 2;
}
.image-preview img {
  width: 100%;
  height: auto;
  border-radius: 4px;
}
.info-panel {
  flex: 1;
}
.info-panel h3 {
  margin-top: 0;
  margin-bottom: 10px;
  border-bottom: 1px solid #eee;
  padding-bottom: 5px;
}
.tags-section {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
}
.tag-item {
  margin: 0;
}
.tag-input {
  width: 90px;
}
</style>