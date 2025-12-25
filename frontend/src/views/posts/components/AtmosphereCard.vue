<!-- <template>
  <el-card 
    class="vibe-card" 
    shadow="hover" 
    :body-style="{ padding: '0px', height: '100%' }"
    @click="onCardClick"
  >
    <div class="bg-layer">
      <el-image 
        :src="cardData.bgImage" 
        fit="cover" 
        class="bg-img" 
        lazy
      >
        <template #placeholder>
          <div class="image-slot loading"></div>
        </template>
        <template #error>
          <div class="image-slot error">
            <el-icon><Picture /></el-icon>
          </div>
        </template>
      </el-image>
      <div class="mask-overlay"></div>
    </div>

    <div class="content-layer">
      
      <div class="header-row">
        <div class="user-block">
          <div @click.stop="onAvatarClick">
            <el-avatar :size="32" :src="cardData.avatar" class="avatar-border">
              {{ cardData.nickname.charAt(0) }}
            </el-avatar>
          </div>
          <div class="user-meta">
            <span class="nickname">{{ cardData.nickname }}</span>
            <div v-if="cardData.music" class="music-mini-tag">
              <el-icon><Headset /></el-icon>
              <span>{{ cardData.music }}</span>
            </div>
          </div>
        </div>

        <div class="vibe-signal">
          <span class="bar"></span>
          <span class="bar"></span>
          <span class="bar"></span>
        </div>
      </div>

      <div class="body-row">
        <p class="mood-content">
          {{ cardData.content }}
        </p>
      </div>

      <div class="footer-row">
        <span class="time-stamp">{{ cardData.timeAgo }}</span>
        
        <el-button link class="explore-btn">
          进入频道
          <el-icon class="el-icon--right"><i-ep-Right /></el-icon>
        </el-button>
      </div>
    </div>
  </el-card>
</template>

<script>
import { Picture, Headset, Right } from '@element-plus/icons-vue'

export default {
  name: 'AtmosphereCard',
  components: {
    Picture,
    Headset,
    Right
  },
  props: {
    // 接收父组件数据，带完整默认值以便直接预览
    data: {
      type: Object,
      default: () => ({
        id: 101,
        nickname: 'Lost_In_Tokyo',
        avatar: 'https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png',
        // 默认一张有氛围感的城市夜景或自然图
        bgImage: 'https://images.unsplash.com/photo-1519681393784-d120267933ba?q=80&w=800&auto=format&fit=crop',
        music: 'Midnight City - M83',
        content: '城市里的灯光并不是为了照亮谁，只是为了证明黑夜的存在。今晚的风很适合散步。',
        timeAgo: '15分钟前',
        // 虽然界面不显示，但数据里可能有
        likes: 120,
        comments: 45
      })
    }
  },
  computed: {
    cardData() {
      return this.data || {}
    }
  },
  methods: {
    onCardClick() {
      // 点击卡片整体，进入详情或个人主页
      console.log('Explore world:', this.cardData.id)
      this.$emit('click-card', this.cardData.id)
    },
    onAvatarClick() {
      console.log('Click avatar:', this.cardData.nickname)
      this.$emit('click-avatar', this.cardData.id)
    }
  }
}
</script>

<style lang="scss" scoped>
// === 变量定义 ===
$card-height: 240px;
$padding: 16px;
$radius: 16px;
// 衬线字体栈：增强文学感和高级感
$serif-font: 'Times New Roman', 'Georgia', 'Songti SC', serif;

// 深度覆盖 el-card
:deep(.el-card) {
  border: none !important;
  background-color: transparent !important;
  overflow: visible; // 允许阴影溢出
}

.vibe-card {
  position: relative;
  height: $card-height;
  border-radius: $radius;
  overflow: hidden; // 圆角裁剪
  margin-bottom: 24px;
  cursor: pointer;
  background: #1c1c1c; // 加载前的底色
  
  // 3D 悬浮阴影
//   box-shadow: 0 8px 24px -6px rgba(0, 0, 0, 0.5);
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);

  // PC 端 Hover 效果
  @media (min-width: 768px) {
    &:hover {
      transform: translateY(-4px);
      box-shadow: 0 16px 32px -8px rgba(0, 0, 0, 0.6);
      
      .bg-img {
        transform: scale(1.08); // 背景微放
      }
      .explore-btn {
        color: #fff;
        text-shadow: 0 0 8px rgba(255,255,255,0.6);
      }
    }
  }
}

// === 1. 背景层样式 ===
.bg-layer {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 0;

  .bg-img {
    width: 100%;
    height: 100%;
    transition: transform 0.8s ease;
    filter: brightness(0.85); // 降低亮度，突出文字
  }

  .image-slot {
    width: 100%;
    height: 100%;
    display: flex;
    justify-content: center;
    align-items: center;
    background: #333;
    color: #666;
    
    &.loading {
      background: #222; // 可以在这里加个骨架屏动画
    }
  }

  // 遮罩：为了让底部和顶部的文字清晰
  .mask-overlay {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: linear-gradient(
      to bottom,
      rgba(0, 0, 0, 0.3) 0%,   /* 顶部稍微暗一点 */
      rgba(0, 0, 0, 0.1) 40%,  /* 中间透亮，展示图片 */
      rgba(0, 0, 0, 0.8) 100%  /* 底部深黑，保证按钮和时间清晰 */
    );
  }
}

// === 2. 内容层布局 ===
.content-layer {
  position: relative;
  z-index: 1;
  height: 80%;
  padding: $padding;
  display: flex;
  flex-direction: column;
  justify-content: space-between; // 撑开布局：头-中-底
}

// --- 第一行：用户信息 ---
.header-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;

  .user-block {
    display: flex;
    align-items: center;
    gap: 10px;

    .avatar-border {
      border: 1px solid rgba(255, 255, 255, 0.8);
      box-shadow: 0 2px 8px rgba(0,0,0,0.3);
    }

    .user-meta {
      display: flex;
      flex-direction: column;
      
      .nickname {
        color: #fff;
        font-size: 14px;
        font-weight: 600;
        text-shadow: 0 1px 2px rgba(0,0,0,0.8);
        line-height: 1.2;
      }

      .music-mini-tag {
        display: flex;
        align-items: center;
        gap: 4px;
        margin-top: 2px;
        font-size: 10px;
        color: rgba(255, 255, 255, 0.8);
        
        .el-icon { font-size: 10px; }
      }
    }
  }

  // 氛围波形（右上角装饰）
  .vibe-signal {
    display: flex;
    gap: 3px;
    height: 12px;
    align-items: flex-end;
    padding-bottom: 4px;

    .bar {
      width: 2px;
      background: #67C23A; // Element 绿色，代表在线/活跃
      border-radius: 2px;
      animation: vibeJump 1.2s ease-in-out infinite;
      
      &:nth-child(1) { height: 40%; animation-delay: 0s; }
      &:nth-child(2) { height: 80%; animation-delay: 0.2s; }
      &:nth-child(3) { height: 50%; animation-delay: 0.4s; }
    }
  }
}

// --- 中间行：文字内容 ---
.body-row {
  flex: 1; // 占据剩余空间
  display: flex;
  align-items: center; // 垂直居中
  padding-right: 12px;

  .mood-content {
    margin: 0;
    color: #fff;
    font-family: $serif-font; // 关键：衬线体
    font-size: 17px;
    line-height: 1.5;
    letter-spacing: 0.5px;
    font-weight: 400;
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.6);
    
    // 限制最多显示3行
    display: -webkit-box;
    -webkit-box-orient: vertical;
    -webkit-line-clamp: 3;
    overflow: hidden;
  }
}

// --- 最后一行：底部信息 ---
.footer-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;

  .time-stamp {
    font-size: 12px;
    color: rgba(255, 255, 255, 0.6);
    font-weight: 300;
  }

  .explore-btn {
    padding: 0;
    height: auto;
    font-size: 12px;
    color: rgba(255, 255, 255, 0.9);
    
    &:hover {
      color: #409EFF; // 品牌色悬浮
    }
    
    :deep(.el-icon) {
      font-size: 12px;
      margin-left: 2px;
      transition: transform 0.3s;
    }

    &:hover :deep(.el-icon) {
      transform: translateX(3px);
    }
  }
}

// === 动画 Keyframes ===
@keyframes vibeJump {
  0%, 100% { height: 30%; opacity: 0.7; }
  50% { height: 100%; opacity: 1; }
}
</style> -->

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
