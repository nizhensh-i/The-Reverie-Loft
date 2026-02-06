<!-- 
 文字水平滚动
 <MarQuee text="美国作家杰罗姆·大卫·塞林格创作的唯一一部长篇小说" :speed="0.7"/>
-->
<template>
  <div class="scroll-container">
    <el-text class="mx-1 scroll-text" v-if="text.length <= 18">{{
      text
    }}</el-text>
    <el-text
      class="mx-1 scroll-text"
      :style="{ 'animation-duration': `${animationDuration}s` }"
      @mouseenter="pauseAnimation"
      @mouseleave="resumeAnimation"
      v-else
      >{{ text }}</el-text
    >
  </div>
</template>

<script setup>
import { ref, computed } from "vue";

const props = defineProps({
  text: {
    type: String,
    required: true,
  },
  speed: {
    type: Number,
    default: 2, // 文字移动速度，值越小越快
  },
});
const isPaused = ref(false);
// 计算动画持续时间，速度越快，持续时间越短
const animationDuration = computed(() => {
  return 10 / props.speed;
});
const pauseAnimation = () => {
  isPaused.value = true;
  document.querySelector(".scroll-text").style.animationPlayState = "paused";
};

const resumeAnimation = () => {
  isPaused.value = false;
  document.querySelector(".scroll-text").style.animationPlayState = "running";
};
</script>

<style lang="scss" scoped>
.scroll-container {
  position: relative;
  display: grid;
  align-content: center;
  width: 90%;
  height: 40px;
  overflow: hidden;
  white-space: nowrap;
}

.scroll-text {
  display: inline-block;
  margin-top: 8px;
  margin-left: 5px;
  color: #303133;
  white-space: nowrap;
  letter-spacing: 0.02rem;
  animation: scroll-left linear infinite;
}

@keyframes scroll-left {
  0% {
    transform: translateX(3%);
  }
  100% {
    transform: translateX(-100%);
  }
}
</style>
