<template>
  <div class="scroll-container">
    <el-text v-if="text.length <= 18" class="mx-1 scroll-text">{{
      text
    }}</el-text>
    <el-text
      v-else
      class="mx-1 scroll-text"
      :style="{ animationDuration: `${animationDuration}s` }"
      @mouseenter="pauseAnimation"
      @mouseleave="resumeAnimation"
    >
      {{ text }}
    </el-text>
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
    default: 2,
  },
});

const scrollTextRef = ref(null);
const animationDuration = computed(() => 10 / props.speed);

function pauseAnimation() {
  if (scrollTextRef.value) {
    scrollTextRef.value.style.animationPlayState = "paused";
  }
}

function resumeAnimation() {
  if (scrollTextRef.value) {
    scrollTextRef.value.style.animationPlayState = "running";
  }
}
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
