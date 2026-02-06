<template>
  <div class="music-player-container">
    <el-avatar
      class="music-avatar"
      style="border-radius: 50%; width: 120px; height: 120px"
      @mouseenter="showMusicPlayer = true"
      @mouseleave="showMusicPlayer = false"
    >
      <img
        v-if="avatar"
        :src="avatar"
        alt="用户图像"
        :class="{ 'avatar-spin': isPlaying }"
        :style="{
          animation: isPlaying ? 'spin 6s linear infinite' : 'none',
          transformOrigin: 'center',
        }"
      />
      <div v-else class="avatar-placeholder" />

      <transition name="fade">
        <div
          v-show="showMusicPlayer"
          class="music-player-overlay"
          :class="{ 'fade-in': showMusicPlayer }"
        >
          <div v-if="audioLoading" class="loading-spinner">
            <el-icon class="is-loading">
              <i-ep-Loading />
            </el-icon>
          </div>

          <div class="song-info">
            <span class="song-title">{{
              currentSong?.name || "什么也没有..."
            }}</span>
            <span class="song-author">{{ currentSong?.artist || "" }}</span>
          </div>

          <div class="player-controls" v-if="currentSong?.name">
            <el-button
              :size="playButtonSize"
              circle
              @click="handlePlayMusic"
              class="play-btn"
            >
              <el-icon v-if="isPlaying"><i-ep-VideoPause /></el-icon>
              <el-icon v-else><i-ep-VideoPlay /></el-icon>
            </el-button>
          </div>
        </div>
      </transition>
    </el-avatar>
  </div>
</template>

<script setup>
import { ref, computed, watch } from "vue";
import { ElAvatar, ElButton, ElIcon } from "element-plus";
import { useMusicStore } from "@/stores/music";

// Props
const props = defineProps({
  // 头像图片URL
  avatar: {
    type: String,
    required: false,
    default: "",
  },
  musics: {
    type: Object,
    required: false,
    default: () => {
      return { name: "", artist: "", url: "" };
    },
  },
});

const musicStore = useMusicStore();

// Refs
const showMusicPlayer = ref(false);
const audioLoading = ref(false);

const isMobile = ref(/Mobi|Android|iPhone/i.test(navigator.userAgent));

// Computed
const currentSong = computed(() => {
  return props.musics;
});

const isPlaying = computed(() => {
  return (
    musicStore.isPlaying &&
    musicStore.currentMusic?.url === currentSong.value?.url
  );
});

const playButtonSize = computed(() => {
  return isMobile ? "default" : "large";
});

const handlePlayMusic = () => {
  if (!currentSong.value?.url) return;

  // 使用全局音乐播放器
  musicStore.playMusic(currentSong.value);
};

// 监听全局播放状态变化 - 优化性能
watch(
  () => musicStore.isPlaying,
  (playing) => {
    if (playing && musicStore.currentMusic?.url === currentSong.value?.url) {
      // 当前歌曲正在播放
    }
  },
  { immediate: true }
);

// 监听当前音乐变化 - 优化性能
watch(
  () => musicStore.currentMusic,
  (newMusic) => {
    if (newMusic?.url === currentSong.value?.url) {
      // 当前歌曲被选中播放
    }
  },
  { immediate: true }
);
</script>

<style lang="scss" scoped>
.music-player-container {
  display: flex;
  justify-content: center;
  align-items: center;
}

.music-avatar {
  position: relative;
  cursor: pointer;
  transition: all 0.3s ease;

  &:hover {
    transform: scale(1.05);
  }

  img {
    width: 100%;
    height: 100%;
    border-radius: 50%;
    object-fit: cover;
  }
}

.avatar-placeholder {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e7ed 100%);
}

.music-player-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  backdrop-filter: blur(10px);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 10px;
  box-sizing: border-box;
}

.song-info {
  position: absolute;
  left: 0;
  right: 0;
  text-align: center;
  color: white;
  font-size: 12px;
  pointer-events: none;

  .song-title {
    position: absolute;
    top: 1.6rem;
    left: 0;
    right: 0;
    font-weight: bold;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    padding: 0 10px;
  }

  .song-author {
    position: absolute;
    bottom: 1.4rem;
    left: 0;
    right: 0;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    padding: 0 10px;
  }
}

.player-controls {
  display: flex;
  align-items: center;
  gap: 8px;
  z-index: 1;

  .play-btn {
    background: rgba(255, 255, 255, 0.3) !important;
    border: none !important;
    color: white !important;

    &:hover {
      background: rgba(255, 255, 255, 0.4) !important;
    }
  }
}

.loading-spinner {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: 2;
}

.avatar-spin {
  animation: spin 6s linear infinite !important;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.8s;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

// 移动端适配
@media (max-width: 768px) {
  .song-info {
    .song-title {
      font-size: 10px;
      top: 1.2rem;
    }

    .song-author {
      font-size: 9px;
      bottom: 1rem;
    }
  }

  .player-controls {
    gap: 6px;
  }
}
</style>
