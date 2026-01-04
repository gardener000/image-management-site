// 简单的轮播状态存储，用于在首页和画廊之间传递选中的图片
const STORAGE_KEY = 'slideshow_images';

export const slideshowStore = {
    // 保存选中的图片到 sessionStorage
    setImages(images) {
        sessionStorage.setItem(STORAGE_KEY, JSON.stringify(images));
    },

    // 获取选中的图片
    getImages() {
        const data = sessionStorage.getItem(STORAGE_KEY);
        return data ? JSON.parse(data) : null;
    },

    // 清除选中的图片（恢复随机模式）
    clearImages() {
        sessionStorage.removeItem(STORAGE_KEY);
    },

    // 检查是否有自定义图片
    hasCustomImages() {
        return sessionStorage.getItem(STORAGE_KEY) !== null;
    }
};
