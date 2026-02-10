<script setup>
import { ref, computed, onActivated, onMounted } from "vue";
import { useRoute } from "vue-router";

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

const route = useRoute();
// 判断是否为 用户资料页面
const noPadding = computed(() => route.name === "user");

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
    <div :class="['page-container', { 'no-padding': noPadding }]">
      <slot />
    </div>
  </el-scrollbar>
</template>

<style lang="scss" scoped>
.page-scroll {
  :deep(.el-scrollbar__thumb) {
    width: 0;
    background-color: rgba(0, 0, 0, 0.3);
  }
}

.page-container {
  padding: 0 20px;
  &.no-padding {
    padding: 0;
  }
}
</style>
