import { defineStore } from "pinia";

/**
 * 全局音乐播放器状态管理
 */
export const useMusicStore = defineStore("music", {
  state: () => ({
    // 状态
    isPlaying: false,
    currentMusic: null,
    aplayerInstance: null,
    // 底部迷你播放器显示状态（移动端和PC端）
    isMiniPlayerVisible: false,
    volume: 1,
  }),
  getters: {
    // 计算属性
    hasMusic: (state) => !!state.currentMusic?.url,
    currentSongInfo: (state) => ({
      name: state.currentMusic?.name || "",
      artist: state.currentMusic?.artist || "",
      cover: state.currentMusic?.pic || "",
      url: state.currentMusic?.url || "",
      lrc: state.currentMusic?.lrc || "",
    }),
  },
  actions: {
    setAplayerInstance(instance) {
      this.aplayerInstance = instance;
    },
    setCurrentMusic(music) {
      this.currentMusic = music;
      this.showMiniPlayer();
    },
    playMusic(music) {
      if (!music?.url) return;

      // 如果是同一首歌，切换播放/暂停状态
      if (this.currentMusic?.url === music.url) {
        this.togglePlay();
        return;
      }

      // 设置新音乐，但不自动播放
      this.setCurrentMusic(music);

      // 如果APlayer实例存在，只更新播放列表，不自动播放
      // 播放由GlobalPlayer中的监听器控制
      if (this.aplayerInstance) {
        this.aplayerInstance.list.clear();
        this.aplayerInstance.list.add([this.currentSongInfo]);
        // 不在这里调用play()，避免循环调用
      }
    },
    togglePlay() {
      if (!this.aplayerInstance || !this.hasMusic) return;

      if (this.isPlaying) {
        this.aplayerInstance.pause();
      } else {
        this.aplayerInstance.play();
        // 用户关闭了（底部或悬浮）迷你播放器，播放时自动显示
        if (!this.isMiniPlayerVisible) {
          this.showMiniPlayer();
        }
      }
    },
    stop() {
      if (this.aplayerInstance) {
        this.aplayerInstance.pause();
      }
      this.isPlaying = false;
    },
    setPlayingState(playing) {
      this.isPlaying = playing;
    },
    setVolume(newVolume) {
      this.volume = Math.max(0, Math.min(1, newVolume));
      if (this.aplayerInstance) {
        this.aplayerInstance.volume(this.volume);
      }
    },
    hideMiniPlayer() {
      this.isMiniPlayerVisible = false;
      if (this.aplayerInstance) {
        this.aplayerInstance.pause();
      }
    },
    showMiniPlayer() {
      if (this.hasMusic) {
        this.isMiniPlayerVisible = true;
      }
    },
  },
});
