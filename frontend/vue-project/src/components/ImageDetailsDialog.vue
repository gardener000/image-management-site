<template>
  <div> <!-- 唯一的根元素 -->
    <!-- 主对话框 -->
    <el-dialog
      :model-value="visible"
      title="图片详情"
      width="60%"
      @close="closeDialog"
    >
      <div v-if="loading" class="dialog-loading">加载中...</div>
      <div v-else-if="imageDetails" class="details-content">
        <div class="image-preview">
          <img :src="imageDetails.original_url" alt="Image preview" ref="imagePreviewRef" />
        </div>
        <div class="info-panel">
          
          <!-- 信息部分 -->
          <h3>信息</h3>
          <p><strong>文件名:</strong> {{ imageDetails.filename }}</p>
          <p><strong>分辨率:</strong> {{ imageDetails.resolution }}</p>
          <p><strong>上传时间:</strong> {{ new Date(imageDetails.uploaded_at).toLocaleString() }}</p>
          
          <!-- 标签管理部分 -->
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
          
          <!-- 操作部分 -->
          <h3>操作</h3>
          <div class="actions-section">
            <el-button type="primary" @click="openCropper">裁剪</el-button>
            <el-button type="primary" @click="openColorEditor">调整色调</el-button>
            <el-button type="danger" @click="handleDeleteImage">删除</el-button>
          </div>
          
        </div> <!-- info-panel div 结束 -->
      </div> <!-- details-content div 结束 -->
    </el-dialog>

    <!-- 裁剪器组件 -->
    <ImageCropper
      v-if="cropperVisible"
      :image-id="imageId"
      :image-url="imageDetails.original_url"
      v-model:visible="cropperVisible"
      @crop-success="handleCropSuccess"
    />
    
    <!-- 色调调整组件 -->
    <ImageColorEditor
      v-if="colorEditorVisible"
      :image-id="imageId"
      :image-url="imageDetails.original_url"
      v-model:visible="colorEditorVisible"
      @adjust-success="handleColorAdjustSuccess"
    />
  </div> <!-- 根 div 结束 -->
</template>

<script setup>
import { ref, watch, nextTick } from 'vue';
import apiClient from '@/api/axios.js';
import { ElMessage , ElMessageBox} from 'element-plus';
import ImageCropper from './ImageCropper.vue'; // 引入裁剪器组件
import ImageColorEditor from './ImageColorEditor.vue'; // 引入色调调整组件

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

const emit = defineEmits(['update:visible', 'close','image-updated']);

const loading = ref(true);
const imageDetails = ref(null);
const imagePreviewRef = ref(null); // 对预览图的引用
const cropperVisible = ref(false);
const colorEditorVisible = ref(false);
const inputVisible = ref(false);
const inputValue = ref('');
const InputRef = ref(null); // 用于获取 input 元素的引用
const handleDeleteImage = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要删除这张图片吗？此操作不可恢复。',
      '警告',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning',
      }
    );
    
    // 用户确认后执行删除
    await apiClient.delete(`/images/${props.imageId}`);
    ElMessage.success('图片已删除');
    emit('image-updated'); // 通知父组件数据已更新
    closeDialog();
  } catch (error) {
    // 如果 error 是 'cancel'，说明是用户点击了取消，不用提示
    if (error !== 'cancel') {
      ElMessage.error('删除失败');
    }
  }
};

// --- 4. 新增编辑逻辑 ---
const openCropper = () => {
  cropperVisible.value = true;
};

const handleCropSuccess = (newUrls) => {
  // 裁剪成功后，后端返回了新的图片URL
  // 我们直接更新当前组件中的图片URL，让用户立刻看到变化
  if (imageDetails.value) {
    imageDetails.value.original_url = newUrls.original_url;
  }
  emit('image-updated'); // 同时通知父组件刷新列表（因为缩略图也变了）
};

// --- 5. 色调调整逻辑 ---
const openColorEditor = () => {
  colorEditorVisible.value = true;
};

const handleColorAdjustSuccess = (newUrls) => {
  // 色调调整成功后，更新图片URL
  if (imageDetails.value) {
    imageDetails.value.original_url = newUrls.original_url;
  }
  emit('image-updated'); // 通知父组件刷新列表
};

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
  /* 增加一个最大高度，确保它不会撑爆弹窗 */
  max-height: 70vh; 
  height: auto;
  object-fit: contain; /* 保持图片比例 */
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
.actions-section {
  margin-top: 20px;
}
</style>