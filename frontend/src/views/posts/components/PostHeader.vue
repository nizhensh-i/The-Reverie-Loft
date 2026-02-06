<script>
import date from "@/utils/date.js";
import { useOtherUserStore } from "@/stores/otherUser";
export default {
  props: {
    post: {
      type: Object,
      default() {
        return {
          id: 1,
          content: "",
          post_type: "text",
          timestamp: "",
          author: "--",
          nick_name: "",
          user_id: 1,
          commentCount: 20,
          disabled: false,
          image: "",
          comment_count: 0,
          praise_num: 0,
          has_praised: false,
          post_images: [],
        };
      },
    },
  },
  data() {
    return {
      touchTimer: null,
    };
  },
  setup() {
    const otherUser = useOtherUserStore();
    return { otherUser };
  },
  computed: {
    from_now() {
      return date.dateShow(this.post.timestamp);
    },
  },
  methods: {
    handleUserClick(event) {
      // 阻止事件冒泡和默认行为
      if (event) {
        event.preventDefault();
        event.stopPropagation();
      }
      this.toUser(false);
    },

    handleMusicClick(event) {
      // 阻止事件冒泡和默认行为
      if (event) {
        event.preventDefault();
        event.stopPropagation();
      }
      this.toUser(true);
    },

    handleTouchStart(event) {
      if (this.touchTimer) {
        clearTimeout(this.touchTimer);
      }
      this.touchTimer = setTimeout(() => {
        // 长按逻辑（如果需要）
      }, 300);
    },

    handleTouchEnd(event) {
      if (this.touchTimer) {
        clearTimeout(this.touchTimer);
      }
    },

    toUser(playMusic = false) {
      this.otherUser.userInfo.id = this.post.user_id;
      const url = playMusic
        ? `/user/${this.post.author}?playMusic=true`
        : `/user/${this.post.author}`;
      this.$router.push(url);
    },
  },
};
</script>

<template>
  <el-row class="head" justify="space-between" align="middle">
    <div class="user-info">
      <el-avatar
        alt="用户图像"
        :src="post.image"
        @click="handleUserClick"
        @touchstart="handleTouchStart"
        @touchend="handleTouchEnd"
      />
      <div class="user-mata">
        <span
          @click="handleUserClick"
          @touchstart="handleTouchStart"
          @touchend="handleTouchEnd"
          class="nickname"
          >{{ post.nick_name ? post.nick_name : post.author }}</span
        >
        <div
          v-if="post.music?.name"
          @click="handleMusicClick"
          @touchstart="handleTouchStart"
          @touchend="handleTouchEnd"
          class="music"
        >
          <el-icon><i-ep-Headset /></el-icon>
          <span>{{ post.music.name }}-{{ post.music.artist }}</span>
        </div>
      </div>
    </div>
    <div>
      <el-text size="small" class="head-time">{{ from_now }}</el-text>
    </div>
  </el-row>
</template>

<style lang="scss" scoped>
$primary-color: #409eff;
$text-main: #2c3e50;
$text-light: #909399;

.head {
  height: 40px;
  margin-bottom: 10px;

  .user-info {
    display: flex;
    align-items: center;
    gap: 12px;
    cursor: pointer;

    .el-avatar {
      cursor: pointer;
      border: 1px solid #f0f0f0;
      transition: opacity 0.2s ease;

      &:hover {
        opacity: 0.8;
      }
      &:active {
        transform: scale(0.95);
      }
    }

    .user-mata {
      display: flex;
      flex-direction: column;

      .nickname {
        font-size: 14px;
        font-weight: 550;
        color: $text-main;

        &:hover {
          color: $primary-color;
        }
      }

      .music {
        display: flex;
        align-items: center;
        gap: 4px;
        margin-top: 2px;
        font-size: 11px;
        color: $text-light;
      }
    }
  }

  .head-time {
    margin-right: 1px;
  }
}
</style>
