<template>
  <el-card
    class="pure-text-card"
    shadow="hover"
    :body-style="{ padding: '24px' }"
    @click="handleGoDetail"
  >
    <div class="header-row">
      <div class="user-info" @click.stop="handleGoProfile">
        <el-avatar :size="32" :src="cardData.avatar" class="avatar-shadow">
          {{ cardData.nickname.charAt(0) }}
        </el-avatar>
        <div class="meta-data">
          <span class="nickname">{{ cardData.nickname }}</span>
          <div v-if="cardData.music" class="music-info">
            <el-icon><Headset /></el-icon>
            <span>{{ cardData.music }}</span>
          </div>
        </div>
      </div>

      <div class="vibe-indicator">
        <span class="bar"></span>
        <span class="bar"></span>
        <span class="bar"></span>
      </div>
    </div>

    <div class="body-row">
      <p class="main-content">
        {{ cardData.content }}
      </p>
    </div>

    <div class="footer-row">
      <div class="left-footer">
        <span class="time-stamp">{{ cardData.timeAgo }}</span>
      </div>

      <div class="right-actions">
        <el-button link class="action-btn" @click.stop="handleComment">
          <el-icon><ChatDotRound /></el-icon>
        </el-button>
        <el-button link class="action-btn" @click.stop="handleLike">
          <el-icon><Star /></el-icon>
        </el-button>
        <el-button link class="enter-link" @click.stop="handleGoChannel">
          进入频道 <el-icon><Right /></el-icon>
        </el-button>
      </div>
    </div>
  </el-card>
</template>

<script>
import { Headset, Right, ChatDotRound, Star } from "@element-plus/icons-vue";

export default {
  name: "AtmosphereTextCard",
  components: { Headset, Right, ChatDotRound, Star },
  props: {
    data: {
      type: Object,
      default: () => ({
        id: 1,
        userId: 1001,
        nickname: "深夜诗人",
        avatar:
          "https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png",
        music: "Bach: Cello Suite No.1",
        content:
          "我们坐在长椅上，看落日一点点沉入地平线。那一刻，时间仿佛不是流逝的，而是凝固的。白色的背景里，连呼吸都变得清晰可见。",
        timeAgo: "2小时前",
      }),
    },
  },
  computed: {
    cardData() {
      return this.data;
    },
  },
  methods: {
    // 1. 点击卡片整体：进入文章详情
    handleGoDetail() {
      console.log("跳转至文章详情，ID:", this.cardData.id);
      // TODO: 在此处编写你的跳转逻辑（如 this.$router.push）
    },

    // 2. 点击头像或昵称：进入个人资料页
    handleGoProfile() {
      console.log("跳转至用户资料页，用户ID:", this.cardData.userId);
      // TODO: 在此处编写你的跳转逻辑
    },

    // 3. 点击点赞按钮
    handleLike() {
      console.log("执行点赞逻辑");
      // TODO: 在此处编写点赞 API 调用
    },

    // 4. 点击评论按钮
    handleComment() {
      console.log("打开评论面板或跳转至评论区");
      // TODO: 在此处编写逻辑
    },

    // 5. 点击进入频道按钮
    handleGoChannel() {
      console.log("跳转至特定频道");
      // TODO: 在此处编写跳转逻辑
    },
  },
};
</script>

<style lang="scss" scoped>
$primary-color: #409eff;
$text-main: #2c3e50;
$text-light: #909399;
$serif-font: "Times New Roman", "Source Han Serif SC", "Songti SC", serif;

.pure-text-card {
  border: 1px solid #f0f0f0 !important;
  border-radius: 16px;
  background-color: #fff;
  margin-bottom: 20px;
  transition: all 0.3s ease;
  overflow: hidden;
  //   position: relative;
  cursor: pointer;

  // 白色背景下的轻柔阴影
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 12px 24px rgba(0, 0, 0, 0.04) !important;
    border-color: #e4e7ed !important;
  }

  /* 文章卡片装饰元素 */
  //   &::before {
  //     content: '';
  //     position: absolute;
  //     top: 0;
  //     left: 0;
  //     width: 4px;
  //     height: 100%;
  //     background: linear-gradient(to bottom, #09c8ce, #eb2f96);
  //     border-radius: 4px 0 0 4px;
  //   }
}

// --- Header ---
.header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;

  .user-info {
    display: flex;
    align-items: center;
    gap: 12px;
    cursor: pointer; // 明确提示可点击

    .avatar-shadow {
      border: 1px solid #f0f0f0;
    }

    .meta-data {
      display: flex;
      flex-direction: column;

      .nickname {
        font-size: 14px;
        font-weight: 600;
        color: $text-main;
      }

      &:hover .nickname {
        color: #409eff; // 悬浮反馈
      }
      .music-info {
        display: flex;
        align-items: center;
        gap: 4px;
        font-size: 11px;
        color: $text-light;
        margin-top: 2px;
      }
    }
  }
}

// 信号律动（灰色版）
.vibe-indicator {
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

// --- Body ---
.body-row {
  margin-bottom: 24px;

  .main-content {
    font-family: $serif-font;
    font-size: 17px;
    line-height: 1.8;
    color: #333;
    margin: 0;
    // 适当增加字间距
    letter-spacing: 0.3px;

    // 多行省略
    display: -webkit-box;
    -webkit-line-clamp: 4;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }
}

// --- Footer ---
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

  .right-actions {
    display: flex;
    align-items: center;
    gap: 12px;

    .action-btn {
      padding: 0;
      color: $text-light;
      font-size: 18px;
      &:hover {
        color: $primary-color;
      }
    }

    .enter-link {
      font-size: 12px;
      color: $primary-color;
      font-weight: 500;
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
