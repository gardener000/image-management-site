<template>
  <el-dialog
    :model-value="visible"
    title="裁剪图片"
    width="80%"
    :close-on-click-modal="false"
    @close="close"
  >
    <div class="cropper-container">
      <!-- vue-cropperjs 组件 -->
      <VueCropper
        ref="cropperRef"
        :src="imageUrl"
        alt="Image to crop"
        :view-mode="1"         
        :drag-mode="'crop'"    
        :aspect-ratio="0"      
        :auto-crop="true"      
        :background="false"    
        :guides="true"         
        :center="true"         
        :movable="true"        
        :crop-box-movable="true" 
        :crop-box-resizable="true"
      
        style="width: 100%; height: 100%;"
      />
    </div>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click="close">取消</el-button>
        <el-button type="primary" @click="confirmCrop" :loading="isSaving">
          确认裁剪
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, onUnmounted } from 'vue';
import VueCropper from 'vue-cropperjs';
import 'cropperjs/dist/cropper.css'; // 关键：必须导入 cropperjs 的样式
import apiClient from '@/api/axios.js';
import { ElMessage } from 'element-plus';

// --- Props and Emits ---
const props = defineProps({
  imageId: { type: Number, required: true },
  imageUrl: { type: String, required: true },
  visible: { type: Boolean, default: false },
});
const emit = defineEmits(['update:visible', 'crop-success']);

// --- Reactive State ---
const cropperRef = ref(null);
const isSaving = ref(false);

onUnmounted(() => {
  if (cropperRef.value) {
    cropperRef.value.destroy();
  }
});

// --- Cropper Logic ---
const confirmCrop = () => {
  if (!cropperRef.value) return;

  // 2. 使用 vue-cropperjs 的 API 获取裁剪数据
  // 它直接返回一个包含坐标和尺寸的对象
  const cropData = cropperRef.value.getData(true);

  isSaving.value = true;
  apiClient.post(`/images/${props.imageId}/edit`, {
    crop: {
      x: Math.round(cropData.x),
      y: Math.round(cropData.y),
      width: Math.round(cropData.width),
      height: Math.round(cropData.height),
    },
  }).then(response => {
    ElMessage.success('裁剪成功！');
    emit('crop-success', response.data.new_urls);
    close();
  }).catch(error => {
    ElMessage.error('裁剪失败，请稍后再试');
    console.error(error);
  }).finally(() => {
    isSaving.value = false;
  });
};

// --- Dialog Control ---
const close = () => {
  emit('update:visible', false);
};
</script>

<style scoped>
.cropper-container {
  position: relative; /* 关键：为cropper提供一个定位上下文 */
  height: 60vh;
  width: 100%;
  overflow: hidden; 
  background-color: #f0f0f0; /* 添加一个背景色，方便观察容器范围 */
}
</style>