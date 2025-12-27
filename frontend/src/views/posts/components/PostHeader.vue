<script>
import date from "@/utils/date.js";
import { useOtherUserStore } from "@/stores/otherUser";
import PostContent from "@/views/posts/components/PostContent.vue";

export default {
  props: {
    post: {
      type: Object,
      default() {
        return {
          id: 1,
          body: "",
          body_html: null,
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
  components:{
    PostContent
  },
  data() {
    return {};
  },
  setup() {
    const otherUser = useOtherUserStore();
    return { otherUser };
  },
  mounted() { },
  computed: {
    from_now() {
      return date.dateShow(this.post.timestamp);
    },
  },
  data() {
    return {
      touchTimer: null,
    };
  },
  methods: {
    handleUserClick(event) {
      // 阻止事件冒泡和默认行为
      if (event) {
        event.preventDefault();
        event.stopPropagation();
      }
      this.toUser();
    },

    handleTouchStart(event) {
      // 为移动端提供更好的响应
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

    toUser() {
      // 接口都已改为根据用户id获取用户数据
      this.otherUser.userInfo.id = this.post.user_id;
      this.$router.push(`/user/${this.post.author}`);
    },
  },
};
</script>

<template>
  <div>
    <div class="head-row">
      <div class="user-info">
        <el-avatar alt="用户图像" :src="post.image" @click="handleUserClick" @touchstart="handleTouchStart"
          @touchend="handleTouchEnd" />
        <div class="user-mata">
          <span @click="handleUserClick" @touchstart="handleTouchStart" @touchend="handleTouchEnd" class="nickname">{{
            post.nick_name ? post.nick_name : post.author }}</span>
          <div v-if="post.music" class="music">
            <el-icon><i-ep-Headset /></el-icon>
            <span>{{ post.music.name }}-{{ post.music.artist }}</span>
          </div>

        </div>
      </div>
      <div class="music-logo" v-if="post.music">
        <span class="bar"></span>
        <span class="bar"></span>
        <span class="bar"></span>
      </div>
    </div>

    <div class="body-row">
      <!-- <p class="main-content is-normal-text">
        {{ post.summary }}
      </p> -->
      <PostContent :postContent="post.summary" :preview="true" />
    </div>

    <div class="footer-row">
      <div><span class="time-stamp">{{ from_now }}</span></div>
      <div class="right-action">
        <el-button link class="action-btn"><el-icon><i-ep-ChatDotRound /></el-icon></el-button>
        <el-button link class="action-btn"><el-icon></el-icon><i-ep-Star /></el-button>
        <el-button link class="enter-link">进入频道<el-icon><i-ep-Right /></el-icon></el-button>
      </div>
    </div>
  </div>
</template>
<style lang="scss" scoped>
$primary-color: #409eff;
$text-main: #2c3e50;
$text-light: #909399;
$serif-font: "Times New Roman", "Source Han Serif SC", "Songti SC", serif;

.head-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;

  // margin-bottom: 20px;
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
        font-weight: 600;
        color: $text-main;

        &:hover {
          color: $primary-color;
        }
      }

      .music {
        display: flex;
        align-items: center;
        gap: 4px;

        font-size: 11px;
        color: $text-light;
        margin-top: 2px;
      }
    }
  }

  // 信号律动（灰色版）
  .music-logo {
    display: flex;
    gap: 3px;
    height: 12px;
    align-items: flex-end;

    .bar {
      width: 2px;
      background: #dcdfe6;
      border-radius: 1px;
      animation: pulse 1.2s infinite;

      &:nth-child(2) {
        animation-delay: 0.2s;
      }

      &:nth-child(3) {
        animation-delay: 0.4s;
      }
    }
  }

}

.body-row {
  margin-bottom: 24px;

  .main-content {
    // font-family: $serif-font;
    // font-size: 17px;
    // line-height: 1.8;
    color: #333;
    margin: 0;
    word-spacing: 0.3px;

    display: -webkit-box;
    -webkit-line-clamp: 4;
    -webkit-box-orient: vertical;
    overflow: hidden;

    // 普通文本：纯衬线体，字号可以稍微大一点点
    &.is-normal-text {
      font-family: $serif-font;
      font-size: 17px;
      line-height: 1.8;
    }

    // Markdown 预览：使用无衬线体，稍微紧凑一点，更专业
    &.is-markdown-preview {
      font-family: -apple-system, sans-serif;
      font-size: 14px;
      line-height: 1.6;
      color: #444;
    }
  }
}


.footer-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 16px;
  border-top: 1px solid #f8f8f8;

  .time-stamp {
    font-size: 12px;
    color: $text-light;
  }

  .right-action {
    display: flex;
    align-items: center;
    gap: 12px;

    .action-btn {
      padding: 0px;
      font-size: 18px;
      color: $text-light;

      &:hover {
        color: $primary-color;
      }
    }

    .enter-link {
      font-size: 12px;
      font-weight: 500;
      color: $primary-color;
      margin-left: 8px;

      .el-icon {
        vertical-align: middle;
        transition: transform 0.2s;
      }

      &:hover .el-icon {
        transform: translateX(4px);
      }
    }

  }
}


@keyframes pulse {

  0%,
  100% {
    height: 40%;
  }

  50% {
    height: 100%;
  }
}
</style>
