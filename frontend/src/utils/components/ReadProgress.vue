<template>
  <div class="read-progress">
    <el-progress :percentage="read" :show-text="false" :stroke-width="3" />
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from "vue";

const props = defineProps({
  tartget: {
    type: String,
    default: ".el-scrollbar__wrap",
  },
});

const read = ref(0);
let scrollEl = null;
let throttleTimer = null;

const updateReadProgress = () => {
  if (!scrollEl) return;

  const total = scrollEl.scrollHeight - scrollEl.clientHeight;
  if (total <= 0) {
    read.value = 0;
    return;
  }

  const percent = ((scrollEl.scrollTop / total) * 100).toFixed(2);
  read.value = Math.min(Math.max(Number(percent), 0), 100);
};

// 100ms 节流
const throttledUpdate = () => {
  if (throttleTimer) return;

  throttleTimer = setTimeout(() => {
    updateReadProgress();
    throttleTimer = null;
  }, 100);
};

onMounted(() => {
  scrollEl = document.querySelector(props.tartget);
  if (scrollEl) {
    scrollEl.addEventListener("scroll", throttledUpdate);
    updateReadProgress();
  }
});

onUnmounted(() => {
  if (scrollEl) {
    scrollEl.removeEventListener("scroll", throttledUpdate);
  }
  if (throttleTimer) {
    clearTimeout(throttleTimer);
    throttleTimer = null;
  }
});
</script>

<style lang="scss" scoped>
.read-progress {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;

  :deep(.el-progress--line) {
    max-width: 600px;
    margin-bottom: 15px;
  }
}
</style>
