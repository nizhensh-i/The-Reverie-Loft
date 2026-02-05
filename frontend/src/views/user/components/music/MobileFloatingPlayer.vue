<template>
  <transition name="bounce">
    <div
      v-show="isVisible && hasMusic"
      class="mobile-floating-player"
      @click="handleClick"
    >
      <!-- 主播放按钮 -->
      <div class="floating-btn" :class="{ playing: isPlaying }">
        <div class="btn-content">
          <!-- 旋转的专辑封面 -->
          <div class="floating-cover" :class="{ 'cover-spin': isPlaying }">
            <el-image
              :src="currentSongInfo.cover"
              fit="cover"
              class="cover-image"
              :preview-src-list="
                currentSongInfo.cover ? [currentSongInfo.cover] : []
              "
              :preview-teleported="true"
              :hide-on-click-modal="true"
            >
              <template #error>
                <div class="cover-error">
                  <el-icon><i-ep-Headset /></el-icon>
                </div>
              </template>
            </el-image>
          </div>

          <!-- 播放/暂停图标 -->
          <div class="play-icon">
            <el-icon v-if="!isPlaying">
              <i-ep-VideoPlay />
            </el-icon>
            <el-icon v-else>
              <i-ep-VideoPause />
            </el-icon>
          </div>
        </div>
      </div>

      <!-- 歌曲信息弹窗（长按时显示） -->
      <div
        v-show="showTooltip"
        class="song-tooltip"
        :class="{ 'tooltip-visible': showTooltip }"
      >
        <div class="tooltip-content">
          <div class="song-title" :title="currentSongInfo.name">
            {{ currentSongInfo.name || "暂无歌曲" }}
          </div>
          <div class="song-artist" :title="currentSongInfo.artist">
            {{ currentSongInfo.artist || "未知艺术家" }}
          </div>
        </div>
      </div>

      <!-- 关闭按钮 -->
      <div v-show="showCloseBtn" class="close-btn" @click.stop="hidePlayer">
        <el-icon><i-ep-Close /></el-icon>
      </div>
    </div>
  </transition>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from "vue";
import { useMusicStore } from "@/stores/music";

const musicStore = useMusicStore();

// 响应式数据
const showTooltip = ref(false);
const showCloseBtn = ref(false);
const touchStartTime = ref(0);
const tooltipTimer = ref(null);
const closeBtnTimer = ref(null);
const windowWidth = ref(window.innerWidth);

// 监听窗口大小变化
const handleResize = () => {
  windowWidth.value = window.innerWidth;
};

// 计算属性
const isMobile = computed(() => windowWidth.value <= 768);
const isVisible = computed(
  () => musicStore.isMiniPlayerVisible && isMobile.value
);
const hasMusic = computed(() => musicStore.hasMusic);
const isPlaying = computed(() => musicStore.isPlaying);
const currentSongInfo = computed(() => musicStore.currentSongInfo);
const position = computed(() => musicStore.position);
const duration = computed(() => musicStore.duration);

// 方法
const handleClick = () => {
  musicStore.togglePlay();
};

const hidePlayer = () => {
  musicStore.hideMiniPlayer();
};

const handleTouchStart = (event) => {
  touchStartTime.value = Date.now();
  showCloseBtn.value = true;

  // 清除之前的定时器
  if (tooltipTimer.value) {
    clearTimeout(tooltipTimer.value);
  }

  // 延迟显示tooltip
  tooltipTimer.value = setTimeout(() => {
    showTooltip.value = true;
  }, 500);

  // 设置关闭按钮隐藏定时器
  if (closeBtnTimer.value) {
    clearTimeout(closeBtnTimer.value);
  }

  closeBtnTimer.value = setTimeout(() => {
    showCloseBtn.value = false;
  }, 3000);
};

const handleTouchEnd = () => {
  const touchDuration = Date.now() - touchStartTime.value;

  // 清除定时器
  if (tooltipTimer.value) {
    clearTimeout(tooltipTimer.value);
    tooltipTimer.value = null;
  }

  // 如果触摸时间短于500ms，可能是点击而非长按
  if (touchDuration < 500) {
    showTooltip.value = false;
  } else {
    // 长按后延迟隐藏tooltip
    setTimeout(() => {
      showTooltip.value = false;
    }, 2000);
  }

  // 延迟隐藏关闭按钮
  setTimeout(() => {
    showCloseBtn.value = false;
  }, 2000);
};

// 生命周期
onMounted(() => {
  // 添加窗口大小监听
  window.addEventListener("resize", handleResize);

  // 添加触摸事件监听
  const playerElement = document.querySelector(".mobile-floating-player");
  if (playerElement) {
    playerElement.addEventListener("touchstart", handleTouchStart, {
      passive: true,
    });
    playerElement.addEventListener("touchend", handleTouchEnd, {
      passive: true,
    });
    playerElement.addEventListener("touchcancel", handleTouchEnd, {
      passive: true,
    });
  }
});

onUnmounted(() => {
  // 清理定时器
  if (tooltipTimer.value) {
    clearTimeout(tooltipTimer.value);
  }
  if (closeBtnTimer.value) {
    clearTimeout(closeBtnTimer.value);
  }

  // 移除窗口大小监听
  window.removeEventListener("resize", handleResize);

  // 移除事件监听
  const playerElement = document.querySelector(".mobile-floating-player");
  if (playerElement) {
    playerElement.removeEventListener("touchstart", handleTouchStart, {
      passive: true,
    });
    playerElement.removeEventListener("touchend", handleTouchEnd, {
      passive: true,
    });
    playerElement.removeEventListener("touchcancel", handleTouchEnd, {
      passive: true,
    });
  }
});
</script>

<style lang="scss" scoped>
.mobile-floating-player {
  position: fixed;
  bottom: 80px;
  right: 20px;
  z-index: 1999;
  cursor: pointer;

  .floating-btn {
    width: 60px;
    height: 60px;
    border-radius: 50%;
    background: linear-gradient(135deg, #409eff 0%, #67c23a 100%);
    box-shadow: 0 4px 20px rgba(64, 158, 255, 0.4);
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;

    &.playing {
      box-shadow: 0 4px 25px rgba(103, 194, 58, 0.6);
      transform: scale(1.05);
    }

    .btn-content {
      position: relative;
      width: 100%;
      height: 100%;

      .floating-cover {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        overflow: hidden;
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        transition: all 0.3s ease;

        &.cover-spin {
          animation: spin 8s linear infinite;
        }

        .cover-image {
          width: 100%;
          height: 100%;
          border-radius: 50%;
        }

        .cover-error {
          width: 100%;
          height: 100%;
          display: flex;
          align-items: center;
          justify-content: center;
          background: rgba(255, 255, 255, 0.2);
          backdrop-filter: blur(10px);
          color: rgba(255, 255, 255, 0.8);
          border-radius: 50%;

          .el-icon {
            font-size: 20px;
          }
        }
      }

      .play-icon {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        z-index: 2;
        opacity: 0;
        transition: opacity 0.3s ease;

        .el-icon {
          color: white;
          font-size: 24px;
          filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.3));
        }
      }
    }

    &:hover .play-icon {
      opacity: 1;
    }
  }

  .song-tooltip {
    position: absolute;
    bottom: 70px;
    right: 0;
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(20px);
    border-radius: 12px;
    padding: 12px;
    min-width: 160px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
    border: 1px solid rgba(255, 255, 255, 0.2);
    opacity: 0;
    transform: translateY(10px);
    transition: all 0.3s ease;
    pointer-events: none;

    &.tooltip-visible {
      opacity: 1;
      transform: translateY(0);
    }

    .tooltip-content {
      .song-title {
        font-size: 14px;
        font-weight: 600;
        color: #303133;
        margin-bottom: 4px;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        line-height: 1.2;
      }

      .song-artist {
        font-size: 12px;
        color: #606266;
        margin-bottom: 8px;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        line-height: 1.2;
      }
    }

    &::after {
      content: "";
      position: absolute;
      bottom: -6px;
      right: 20px;
      width: 12px;
      height: 12px;
      background: inherit;
      transform: rotate(45deg);
      border-right: 1px solid rgba(255, 255, 255, 0.2);
      border-bottom: 1px solid rgba(255, 255, 255, 0.2);
    }
  }

  .close-btn {
    position: absolute;
    top: -8px;
    right: -8px;
    width: 24px;
    height: 24px;
    border-radius: 50%;
    background: #f56c6c;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 2px 8px rgba(245, 108, 108, 0.4);
    cursor: pointer;
    z-index: 3;
    transition: all 0.3s ease;

    .el-icon {
      color: white;
      font-size: 12px;
    }

    &:hover {
      transform: scale(1.1);
      background: #f78989;
    }
  }
}

// 动画
.bounce-enter-active {
  animation: bounce-in 0.5s;
}

.bounce-leave-active {
  animation: bounce-out 0.3s;
}

@keyframes bounce-in {
  0% {
    transform: scale(0);
    opacity: 0;
  }
  50% {
    transform: scale(1.1);
  }
  100% {
    transform: scale(1);
    opacity: 1;
  }
}

@keyframes bounce-out {
  0% {
    transform: scale(1);
    opacity: 1;
  }
  100% {
    transform: scale(0);
    opacity: 0;
  }
}

@keyframes spin {
  0% {
    transform: translate(-50%, -50%) rotate(0deg);
  }
  100% {
    transform: translate(-50%, -50%) rotate(360deg);
  }
}

// 响应式适配
@media (max-width: 768px) {
  .mobile-floating-player {
    bottom: 185px;
    right: 16px;

    .floating-btn {
      width: 56px;
      height: 56px;

      .btn-content {
        .floating-cover {
          width: 36px;
          height: 36px;
        }

        .play-icon .el-icon {
          font-size: 22px;
        }
      }
    }

    .song-tooltip {
      min-width: 140px;
      padding: 10px;

      .tooltip-content {
        .song-title {
          font-size: 13px;
        }

        .song-artist {
          font-size: 11px;
        }

        .progress-info {
          font-size: 10px;
        }
      }
    }
  }
}

@media (min-width: 769px) {
  .mobile-floating-player {
    display: none; // 桌面端不显示悬浮按钮
  }
}
</style>
