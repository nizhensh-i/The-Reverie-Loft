<template>
  <header class="atmosphere-header" :class="{ 'is-scrolled': hasScrolled }">
    <div class="brand-zone" @click="handleLogoClick">
      <div class="logo-wrapper">
        <el-image :src="appLogo" class="app-logo" fit="contain">
          <template #error>
            <el-icon><s-promotion /></el-icon>
          </template>
        </el-image>
      </div>

      <div class="text-wrapper">
        <h1 class="app-name">ECHO SPACE</h1>
        <transition name="fade" mode="out-in">
          <span :key="currentGreeting" class="greeting-text">
            {{ currentGreeting }}
          </span>
        </transition>
      </div>
    </div>

    <div class="user-zone" @click="handleAvatarClick">
      <div v-if="!isLoggedIn" class="avatar-container guest-mode">
        <div class="mystery-ring"></div>
        <el-icon class="guest-icon"><User /></el-icon>
      </div>

      <div v-else class="avatar-container user-mode">
        <el-avatar :size="36" :src="userInfo.avatar" class="user-avatar">
          {{ userInfo.nickname ? userInfo.nickname.charAt(0) : "U" }}
        </el-avatar>
        <span class="status-dot"></span>
      </div>
    </div>
  </header>
</template>

<script>
import { User, Promotion } from "@element-plus/icons-vue";

export default {
  name: "AtmosphereHeader",
  components: {
    User,
    "s-promotion": Promotion, // 只是做个示例Logo图标
  },
  props: {
    // 接收外部状态
    isLoggedIn: {
      type: Boolean,
      default: false, // 默认未登录，方便看效果
    },
    userInfo: {
      type: Object,
      default: () => ({
        nickname: "Explorer",
        avatar:
          "https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png",
      }),
    },
  },
  data() {
    return {
      hasScrolled: false,
      appLogo: "/static/logo.png", // 替换你的真实Logo路径
      currentGreeting: "",
      timer: null,
    };
  },
  created() {
    this.updateGreeting();
  },
  mounted() {
    // 监听滚动，实现毛玻璃渐变效果
    window.addEventListener("scroll", this.handleScroll);
    // 每小时更新一次问候语
    this.timer = setInterval(this.updateGreeting, 1000 * 60 * 60);
  },
  beforeUnmount() {
    window.removeEventListener("scroll", this.handleScroll);
    if (this.timer) clearInterval(this.timer);
  },
  methods: {
    handleScroll() {
      const scrollTop =
        window.pageYOffset || document.documentElement.scrollTop;
      // 滚动超过 50px 就变色
      this.hasScrolled = scrollTop > 50;
    },
    updateGreeting() {
      const hour = new Date().getHours();
      if (hour >= 5 && hour < 11) {
        this.currentGreeting = "早安，世界醒了";
      } else if (hour >= 11 && hour < 14) {
        this.currentGreeting = "午安，休息片刻";
      } else if (hour >= 14 && hour < 18) {
        this.currentGreeting = "下午好，捕捉灵感";
      } else if (hour >= 18 && hour < 23) {
        this.currentGreeting = "晚上好，把心事放下";
      } else {
        this.currentGreeting = "夜深了，我们在听";
      }
    },
    handleAvatarClick() {
      if (!this.isLoggedIn) {
        console.log("触发登录引导");
        this.$emit("open-login");
      } else {
        console.log("前往个人中心");
        this.$emit("go-profile");
      }
    },
    handleLogoClick() {
      // 点击Logo刷新或回到顶部
      window.scrollTo({ top: 0, behavior: "smooth" });
    },
  },
};
</script>

<style lang="scss" scoped>
// === 变量定义 ===
$header-height: 60px;
$padding-x: 20px;
$transition-speed: 0.4s;
$font-serif: "Times New Roman", serif; // 保持一致的衬线体风格

.atmosphere-header {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: $header-height;
  padding: 0 $padding-x;
  box-sizing: border-box;
  display: flex;
  justify-content: space-between;
  align-items: center;
  z-index: 1000; // 保证在最上层

  // 初始状态：完全透明背景
  background: transparent;
  transition: all $transition-speed ease;

  // 滚动后的状态：毛玻璃 + 深色半透明底
  &.is-scrolled {
    background: rgba(20, 20, 20, 0.75); // 深色底
    backdrop-filter: blur(12px); // 强模糊
    -webkit-backdrop-filter: blur(12px);
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
  }
}

// === 左侧品牌区 ===
.brand-zone {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;

  .logo-wrapper {
    width: 32px;
    height: 32px;
    display: flex;
    justify-content: center;
    align-items: center;
    color: #fff;
    // Logo 的呼吸光晕
    filter: drop-shadow(0 0 5px rgba(255, 255, 255, 0.4));

    .app-logo {
      width: 100%;
      height: 100%;
    }
  }

  .text-wrapper {
    display: flex;
    flex-direction: column;
    justify-content: center;

    .app-name {
      font-size: 14px;
      font-weight: 700;
      color: #fff;
      margin: 0;
      line-height: 1.2;
      letter-spacing: 1px;
    }

    .greeting-text {
      font-size: 11px;
      color: rgba(255, 255, 255, 0.7);
      font-family: $font-serif; // 使用衬线体增加温度
      font-style: italic;
    }
  }
}

// === 右侧用户区 ===
.user-zone {
  cursor: pointer;

  // A. 游客模式样式
  .guest-mode {
    position: relative;
    width: 36px;
    height: 36px;
    display: flex;
    justify-content: center;
    align-items: center;

    .guest-icon {
      color: rgba(255, 255, 255, 0.8);
      font-size: 18px;
      z-index: 2;
    }

    // 神秘的旋转光环 (Undefined Ring)
    .mystery-ring {
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      border: 1px dashed rgba(255, 255, 255, 0.4);
      border-radius: 50%;
      animation: rotateRing 10s linear infinite;
    }

    // 增加 hover 效果提示可点击
    &:hover .mystery-ring {
      border-color: rgba(255, 255, 255, 0.9);
      animation-duration: 4s; // 加速旋转
    }
  }

  // B. 用户模式样式
  .user-mode {
    position: relative;

    .user-avatar {
      border: 1px solid rgba(255, 255, 255, 0.3);
      transition: transform 0.3s ease;

      &:hover {
        transform: scale(1.1);
        border-color: #fff;
      }
    }

    // 绿色在线点
    .status-dot {
      position: absolute;
      bottom: 2px;
      right: 2px;
      width: 8px;
      height: 8px;
      background-color: #67c23a; // Element Green
      border-radius: 50%;
      border: 1px solid #1a1a1a;
      animation: pulse 2s infinite;
    }
  }
}

// === 动画定义 ===
@keyframes rotateRing {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

@keyframes pulse {
  0% {
    box-shadow: 0 0 0 0 rgba(103, 194, 58, 0.7);
  }
  70% {
    box-shadow: 0 0 0 4px rgba(103, 194, 58, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(103, 194, 58, 0);
  }
}

// Vue Transition Fade
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.5s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
