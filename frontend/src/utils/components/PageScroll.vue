<script setup>
import { ref, onActivated, onDeactivated, onMounted } from "vue";

const props = defineProps({
  maxHeight: {
    type: String,
    default: "100%",
  },
  native: {
    type: Boolean,
    default: false,
  },
});

const scrollbarRef = ref();
const scrollTop = ref(0);

// 保存滚动位置
const handleScroll = ({ scrollTop: top }) => {
  scrollTop.value = top;
};

// 当组件被 keep-alive 激活时，恢复滚动位置
onActivated(() => {
  if (scrollbarRef.value && scrollTop.value > 0) {
    scrollbarRef.value.setScrollTop(scrollTop.value);
  }
});

// 组件停用时，滚动位置会自动保存在 scrollTop 中
onDeactivated(() => {
  // 可以在这里添加额外的清理逻辑
});

// 滚动到顶部的方法，供父组件调用
const scrollToTop = () => {
  if (scrollbarRef.value) {
    scrollbarRef.value.setScrollTop(0);
  }
};

// 新页面进入时自动滚动到顶部
onMounted(() => {
  scrollToTop();
});

// 暴露方法给父组件
defineExpose({
  scrollToTop,
  setScrollTop: (top) => {
    if (scrollbarRef.value) {
      scrollbarRef.value.setScrollTop(top);
    }
  },
});
</script>

<template>
  <el-scrollbar
    ref="scrollbarRef"
    :max-height="maxHeight"
    :native="native"
    @scroll="handleScroll"
    class="page-scroll"
  >
    <slot></slot>
  </el-scrollbar>
</template>

<style scoped>
.page-scroll :deep(.el-scrollbar__thumb) {
  background-color: rgba(0, 0, 0, 0.3);
  width: 0px;
}
</style>
