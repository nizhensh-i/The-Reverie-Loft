<script setup>
import { computed } from "vue";

const props = defineProps({
  providers: {
    type: Array,
    default: () => [],
  },
  activeProvider: {
    type: String,
    default: "",
  },
});

const emit = defineEmits(["start"]);

// 按需引入 svg 组件
import githubIcon from "@/asset/svg/github.svg?component";
import googleIcon from "@/asset/svg/google.svg?component";
import qqIcon from "@/asset/svg/qqchat.svg?component";
import wechatIcon from "@/asset/svg/wechat.svg?component";
import weiboIcon from "@/asset/svg/weibo.svg?component";
const iconMap = {
  github: githubIcon,
  google: googleIcon,
  qq: qqIcon,
  wechat: wechatIcon,
  wechat_open: wechatIcon,
  wechat_mini: wechatIcon,
  weibo: weiboIcon,
};

const renderProviders = computed(() =>
  (props.providers || []).map((item) => {
    const IconComp = iconMap[item.provider];
    return {
      ...item,
      IconComp,
      label: item.name || item.provider,
    };
  })
);

function handleClick(provider) {
  emit("start", provider);
}
</script>

<template>
  <div class="oauth-block" v-if="renderProviders.length">
    <el-divider>其他登录方式</el-divider>
    <div class="oauth-row">
      <button
        v-for="item in renderProviders"
        :key="item.provider"
        class="oauth-chip"
        :class="{ loading: activeProvider === item.provider }"
        :disabled="activeProvider === item.provider"
        @click="handleClick(item.provider)"
        :title="item.label"
      >
        <span class="icon" v-if="item.IconComp">
          <component :is="item.IconComp" class="svg" />
        </span>
        <span class="fallback" v-else>{{ item.label?.[0] || "?" }}</span>
      </button>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.oauth-block {
  width: 100%;
  margin: 10px 0 4px;
}
:deep(.el-divider__text) {
  font-weight: 0;
}
.oauth-row {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.oauth-chip {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 10px;
  border: 1px solid #e5e7eb;
  border-radius: 50%;
  background: #ffffff;
  cursor: pointer;
  transition: all 0.2s ease;
  width: 48px;
  height: 48px;
  position: relative;
  overflow: hidden;

  // 图标样式
  .icon {
    width: 24px;
    height: 24px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    transition: opacity 0.3s ease;

    .svg {
      width: 100%;
      height: 100%;
    }
  }

  .fallback {
    width: 24px;
    height: 24px;
    border-radius: 50%;
    background: #f3f4f6;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-weight: 600;
    color: #374151;
    font-size: 14px;
    transition: opacity 0.3s ease;
  }

  // 加载状态
  &.loading {
    .icon,
    .fallback {
      opacity: 0.3;
    }
  }

  &:disabled {
    opacity: 0.72;
    cursor: not-allowed;
  }

  &:not(:disabled):hover {
    transform: translateY(-1px);
    box-shadow: 0 8px 18px rgba(0, 0, 0, 0.06);
    border-color: #d1d5db;
  }

  &:not(:disabled):active {
    transform: translateY(0);
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.04);
  }
}
</style>
