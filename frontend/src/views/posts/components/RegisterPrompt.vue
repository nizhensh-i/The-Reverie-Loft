<template>
  <div class="identity-wrapper">
    <div class="aurora-gradient"></div>

    <div class="glass-card">
      <div class="noise-overlay"></div>

      <div class="card-content">
        <div class="avatar-placeholder">
          <div class="dashed-circle">
            <el-icon class="plus-icon"><Plus /></el-icon>
          </div>
          <div class="radar-ring"></div>
        </div>

        <div class="vibe-section">
          <div class="audio-visualizer">
            <span class="bar"></span>
            <span class="bar"></span>
            <span class="bar"></span>
            <span class="bar"></span>
          </div>

          <transition name="fade" mode="out-in">
            <p :key="currentIndex" class="scene-text">
              "{{ copyList[currentIndex] }}"
            </p>
          </transition>
        </div>

        <div class="action-area">
          <el-button round class="explore-btn" @click="handleLogin">
            生成我的 ID
            <el-icon class="el-icon--right"><ArrowRight /></el-icon>
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from "vue";
import { Plus, ArrowRight } from "@element-plus/icons-vue";

// 场景化文案配置
const copyList = [
  "在这里，选一首只有你能听懂的 BGM",
  "没有算法审视，只有 10m² 的静谧",
  "此刻建立信号，等待同频率的访客",
];

const currentIndex = ref(0);
let timer: ReturnType<typeof setInterval> | null = null;

// 简单的文案轮播逻辑
const startRotation = () => {
  timer = setInterval(() => {
    currentIndex.value = (currentIndex.value + 1) % copyList.length;
  }, 4000); // 4秒切换一次
};

const handleLogin = () => {
  console.log("触发登录/注册流程");
  // 这里调用你的登录弹窗逻辑
};

onMounted(() => {
  startRotation();
});

onUnmounted(() => {
  if (timer) clearInterval(timer);
});
</script>

<style lang="scss" scoped>
// 变量定义 - 方便调整主题色
$glass-bg: rgba(255, 255, 255, 0.1);
$glass-border: rgba(255, 255, 255, 0.2);
$blur-amount: 16px;
$primary-glow: #70a1ff; // 你的品牌主色偏亮版
$secondary-glow: #ff6b81; // 撞色

.identity-wrapper {
  position: relative;
  width: 100%;
  max-width: 380px; // 移动端合适宽度，PC端限制最大宽
  margin: 24px auto; // 上下留白
  padding: 2px; // 为边框留空间
  border-radius: 24px;
  overflow: hidden;

  // 3D 视差透视感 (可选)
  perspective: 1000px;
}

// 1. 流光背景动画
.aurora-gradient {
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(
    circle at 50% 50%,
    rgba($primary-glow, 0.4),
    rgba($secondary-glow, 0.3),
    transparent 60%
  );
  animation: rotateGradient 10s linear infinite;
  z-index: 0;
  filter: blur(30px);
}

// 2. 毛玻璃卡片主体
.glass-card {
  position: relative;
  background: $glass-bg;
  backdrop-filter: blur($blur-amount);
  -webkit-backdrop-filter: blur($blur-amount); // Safari 支持
  border-radius: 22px;
  border: 1px solid $glass-border;
  box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.15); // 柔和阴影
  z-index: 1;
  padding: 24px 20px;
  display: flex;
  flex-direction: column;
  align-items: center;

  // 呼吸动画
  animation: floatCard 6s ease-in-out infinite;
}

// 3. 内部元素样式

.avatar-placeholder {
  position: relative;
  width: 72px;
  height: 72px;
  margin-bottom: 16px;
  display: flex;
  justify-content: center;
  align-items: center;

  .dashed-circle {
    width: 100%;
    height: 100%;
    border-radius: 50%;
    border: 2px dashed rgba(255, 255, 255, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
    color: white;
    z-index: 2;
  }

  // 扩散的雷达波纹
  .radar-ring {
    position: absolute;
    width: 100%;
    height: 100%;
    border-radius: 50%;
    border: 1px solid rgba(255, 255, 255, 0.3);
    animation: radarRipple 2s linear infinite;
    z-index: 1;
  }
}

.vibe-section {
  text-align: center;
  margin-bottom: 20px;
  min-height: 70px; // 防止文字切换高度抖动
  display: flex;
  flex-direction: column;
  align-items: center;

  .audio-visualizer {
    display: flex;
    gap: 4px;
    height: 16px;
    align-items: flex-end;
    margin-bottom: 10px;

    .bar {
      width: 3px;
      background: white;
      border-radius: 2px;
      animation: soundWave 1s ease-in-out infinite;

      // 让每个条跳动节奏不同
      &:nth-child(1) {
        height: 40%;
        animation-delay: 0.1s;
      }
      &:nth-child(2) {
        height: 80%;
        animation-delay: 0.3s;
      }
      &:nth-child(3) {
        height: 60%;
        animation-delay: 0s;
      }
      &:nth-child(4) {
        height: 50%;
        animation-delay: 0.2s;
      }
    }
  }

  .scene-text {
    font-size: 14px;
    color: rgba(255, 255, 255, 0.9);
    line-height: 1.5;
    font-weight: 300;
    margin: 0;
    font-family: "Times New Roman", serif; // 使用衬线体增加高级感
    font-style: italic;
  }
}

// Element Plus 按钮深度定制
.explore-btn {
  background: rgba(255, 255, 255, 0.9);
  color: #333;
  border: none;
  font-weight: 600;
  padding: 10px 24px;
  transition: all 0.3s ease;

  &:hover {
    transform: scale(1.05);
    background: #fff;
    box-shadow: 0 0 15px rgba(255, 255, 255, 0.5);
  }
}

// --- Keyframe 动画定义 ---

@keyframes rotateGradient {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

@keyframes floatCard {
  0%,
  100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-6px);
  }
}

@keyframes radarRipple {
  0% {
    transform: scale(1);
    opacity: 0.8;
  }
  100% {
    transform: scale(1.6);
    opacity: 0;
  }
}

@keyframes soundWave {
  0%,
  100% {
    height: 30%;
  }
  50% {
    height: 100%;
  }
}

// Vue Transition for Text
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.5s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
