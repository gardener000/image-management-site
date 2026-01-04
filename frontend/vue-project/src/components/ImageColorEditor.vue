<template>
  <el-dialog
    :model-value="visible"
    title="调整色调"
    width="80%"
    :close-on-click-modal="false"
    @close="close"
  >
    <div class="color-editor-container">
      <!-- 图片预览区 -->
      <div class="preview-section">
        <img 
          :src="imageUrl" 
          alt="Preview" 
          class="preview-image"
          :style="previewStyle"
        />
      </div>
      
      <!-- 控制面板 -->
      <div class="controls-section">
        <div class="control-item">
          <label>亮度</label>
          <el-slider 
            v-model="brightness" 
            :min="-100" 
            :max="100" 
            :show-tooltip="true"
          />
          <span class="value-display">{{ brightness }}</span>
        </div>
        
        <div class="control-item">
          <label>对比度</label>
          <el-slider 
            v-model="contrast" 
            :min="-100" 
            :max="100" 
            :show-tooltip="true"
          />
          <span class="value-display">{{ contrast }}</span>
        </div>
        
        <div class="control-item">
          <label>饱和度</label>
          <el-slider 
            v-model="saturation" 
            :min="-100" 
            :max="100" 
            :show-tooltip="true"
          />
          <span class="value-display">{{ saturation }}</span>
        </div>
        
        <el-button @click="resetValues" class="reset-btn">重置</el-button>
      </div>
    </div>
    
    <template #footer>
      <span class="dialog-footer">
        <el-button @click="close">取消</el-button>
        <el-button type="primary" @click="confirmAdjust" :loading="isSaving">
          确认调整
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed } from 'vue';
import apiClient from '@/api/axios.js';
import { ElMessage } from 'element-plus';

// --- Props and Emits ---
const props = defineProps({
  imageId: { type: Number, required: true },
  imageUrl: { type: String, required: true },
  visible: { type: Boolean, default: false },
});
const emit = defineEmits(['update:visible', 'adjust-success']);

// --- Reactive State ---
const brightness = ref(0);
const contrast = ref(0);
const saturation = ref(0);
const isSaving = ref(false);

// --- CSS filter 实时预览 ---
const previewStyle = computed(() => {
  // CSS filter 的值映射：
  // brightness: 0-200% (100% = 原始)
  // contrast: 0-200% (100% = 原始)
  // saturate: 0-200% (100% = 原始)
  const brightnessValue = 100 + brightness.value;
  const contrastValue = 100 + contrast.value;
  const saturateValue = 100 + saturation.value;
  
  return {
    filter: `brightness(${brightnessValue}%) contrast(${contrastValue}%) saturate(${saturateValue}%)`
  };
});

// --- Actions ---
const resetValues = () => {
  brightness.value = 0;
  contrast.value = 0;
  saturation.value = 0;
};

const confirmAdjust = async () => {
  // 如果没有任何调整，提示用户
  if (brightness.value === 0 && contrast.value === 0 && saturation.value === 0) {
    ElMessage.warning('请先调整色调参数');
    return;
  }
  
  isSaving.value = true;
  try {
    const response = await apiClient.post(`/images/${props.imageId}/edit`, {
      color_adjust: {
        brightness: brightness.value,
        contrast: contrast.value,
        saturation: saturation.value,
      },
    });
    
    ElMessage.success('色调调整成功！');
    emit('adjust-success', response.data.new_urls);
    close();
  } catch (error) {
    ElMessage.error('色调调整失败，请稍后再试');
    console.error(error);
  } finally {
    isSaving.value = false;
  }
};

// --- Dialog Control ---
const close = () => {
  resetValues();
  emit('update:visible', false);
};
</script>

<style scoped>
.color-editor-container {
  display: flex;
  gap: 24px;
  min-height: 400px;
}

.preview-section {
  flex: 2;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #1a1a1a;
  border-radius: 8px;
  overflow: hidden;
}

.preview-image {
  max-width: 100%;
  max-height: 60vh;
  object-fit: contain;
}

.controls-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 24px;
  padding: 16px;
  background-color: #f5f5f5;
  border-radius: 8px;
}

.control-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.control-item label {
  font-weight: 600;
  color: #333;
}

.control-item .el-slider {
  flex: 1;
}

.value-display {
  text-align: center;
  font-size: 14px;
  color: #666;
  min-width: 40px;
}

.reset-btn {
  margin-top: auto;
}

/* 响应式布局 */
@media (max-width: 768px) {
  .color-editor-container {
    flex-direction: column;
  }
  
  .preview-section {
    min-height: 250px;
  }
  
  .controls-section {
    flex: none;
  }
}
</style>
