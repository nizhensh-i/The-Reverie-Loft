<script setup>
import { onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useCurrentUserStore } from "@/stores/user";

const route = useRoute();
const router = useRouter();
const store = useCurrentUserStore();
const startedAt =
  typeof performance !== "undefined" ? performance.now() : Date.now();

const state = ref({
  status: "info", // info | success | error
  title: "正在完成第三方登录...",
  subTitle: "请稍候",
});

function parseUser(raw) {
  if (!raw) return null;
  try {
    return typeof raw === "string" ? JSON.parse(raw) : raw;
  } catch (error) {
    console.warn("解析用户信息失败", error);
    return null;
  }
}

onMounted(() => {
  const {
    access_token,
    refresh_token,
    user,
    error,
    message,
    provider,
    action,
    status,
  } = route.query;

  // 处理绑定回调
  if (action === "bind") {
    if (status === "success") {
      state.value = {
        status: "success",
        title: "绑定成功",
        subTitle: `${provider} 账号绑定成功，正在跳转...`,
      };
      // 更新当前用户的绑定状态
      if (store.userInfo) {
        // 触发用户信息更新（bound_providers会在下次获取用户信息时更新）
        store.setUserInfo({
          ...store.userInfo,
          bound_providers: [
            ...(store.userInfo.bound_providers || []),
            provider,
          ],
        });
      }
    } else {
      state.value = {
        status: "error",
        title: "绑定失败",
        subTitle: decodeURIComponent(message || "授权失败"),
      };
    }

    // 跳转回设置页面
    const elapsed =
      (typeof performance !== "undefined" ? performance.now() : Date.now()) -
      startedAt;
    const delay = Math.max(1500 - elapsed, 0);
    setTimeout(() => router.replace("/settings"), delay);
    return;
  }

  // 处理登录回调
  if (error || message) {
    state.value = {
      status: "error",
      title: "登录失败",
      subTitle: decodeURIComponent(error || message || "授权失败"),
    };
    return;
  }

  if (!access_token || !refresh_token || !user) {
    state.value = {
      status: "error",
      title: "登录失败",
      subTitle: "缺少必要的授权参数",
    };
    return;
  }

  const parsedUser = parseUser(user);
  if (!parsedUser) {
    state.value = {
      status: "error",
      title: "登录失败",
      subTitle: "无法解析用户信息",
    };
    return;
  }

  // 清除旧的 token 数据，避免残留
  store.clearLocalData();

  store.access_token = access_token;
  store.refresh_token = refresh_token;
  store.setUserInfo(parsedUser);

  state.value = {
    status: "success",
    title: "登录成功",
    subTitle: provider ? `通过 ${provider} 登录，正在跳转...` : "正在跳转...",
  };

  // 至少展示 1s，避免"样式刚出现就跳走"造成闪烁
  const elapsed =
    (typeof performance !== "undefined" ? performance.now() : Date.now()) -
    startedAt;
  const delay = Math.max(1500 - elapsed, 0);
  setTimeout(() => router.replace("/posts"), delay);
});

// 返回登录页
function goToLogin() {
  router.replace("/login");
}
</script>

<template>
  <div class="oauth-callback">
    <div class="content" :class="state.status">
      <div class="status" aria-hidden="true">
        <div class="dot-spinner" v-if="state.status === 'info'">
          <span v-for="n in 3" :key="n" class="dot" />
        </div>
        <span v-else-if="state.status === 'success'" class="glyph success"
          >✓</span
        >
        <span v-else class="glyph error">!</span>
      </div>

      <h2 class="title">{{ state.title }}</h2>
      <p class="subtitle">{{ state.subTitle }}</p>

      <!-- 登录失败时显示返回按钮 -->
      <el-button
        v-if="state.status === 'error'"
        class="back-button"
        round
        type="primary"
        @click="goToLogin"
      >
        返回登录页
      </el-button>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.oauth-callback {
  min-height: 100vh;
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding: 24px;
  background: #f5f5f7;
  font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display",
    "SF Pro Text", "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans",
    "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
}

.content {
  width: min(720px, 92vw);
  text-align: center;
  margin-top: 18vh;

  .title {
    font-size: 24px;
    font-weight: 600;
    letter-spacing: -0.02em;
    color: rgba(0, 0, 0, 0.88);
    margin: 6px 0 8px;
  }

  .subtitle {
    font-size: 15px;
    line-height: 1.45;
    color: rgba(0, 0, 0, 0.56);
    margin: 0 0 24px;
  }

  .back-button {
    margin-top: 58px;
    min-width: 140px;
  }
}

.status {
  display: flex;
  justify-content: center;
  margin-bottom: 12px;
  min-height: 34px;

  .dot-spinner {
    display: flex;
    justify-content: center;
    gap: 6px;

    .dot {
      width: 8px;
      height: 8px;
      border-radius: 999px;
      background: rgba(0, 113, 227, 0.9);
      opacity: 0.35;
      animation: bounce 1s infinite ease-in-out;

      &:nth-child(2) {
        animation-delay: 0.15s;
      }

      &:nth-child(3) {
        animation-delay: 0.3s;
      }
    }
  }

  .glyph {
    width: 34px;
    height: 34px;
    border-radius: 999px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 18px;
    font-weight: 700;
    line-height: 1;
    user-select: none;
    color: rgba(0, 0, 0, 0.82);

    &.success {
      background: rgba(52, 199, 89, 0.16);
      border: 1px solid rgba(52, 199, 89, 0.28);
    }

    &.error {
      background: rgba(255, 59, 48, 0.14);
      border: 1px solid rgba(255, 59, 48, 0.26);
    }
  }
}

@keyframes bounce {
  0%,
  80%,
  100% {
    transform: translateY(0);
    opacity: 0.35;
  }

  40% {
    transform: translateY(-4px);
    opacity: 1;
  }
}
</style>
