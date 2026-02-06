<template>
  <!-- 社交链接 -->
  <div class="social">
    <div class="link">
      <template v-for="item in value" :key="item.name">
        <component
          v-if="item.url"
          :is="getSvgComponent(item.name)"
          class="icon"
          @mouseenter="socialTip = item.tip"
          @click="handleSocialClick(item)"
        />
      </template>
    </div>
    <!-- <span class="tip">{{ socialTip }}</span> -->
  </div>

  <van-dialog
    v-model:show="dialogShow"
    :title="dialogData.title"
    :message="dialogData.url"
    confirm-button-text="复制链接"
    cancel-button-text="取消"
    width="230"
    show-cancel-button
    :beforeClose="beforeClose"
    close-on-click-overlay
    teleport="html"
  />
</template>

<script setup>
import { ref, computed } from "vue";
import { copy } from "@/utils/common.js";
import github from "@/asset/svg/github.svg?component";
import email from "@/asset/svg/email.svg?component";
import qqchat from "@/asset/svg/qqchat.svg?component";
import wechat from "@/asset/svg/wechat.svg?component";
import bilibili from "@/asset/svg/bilibili.svg?component";
import twitter from "@/asset/svg/twitter.svg?component";

const props = defineProps({
  links: {
    type: Object,
    default: () => ({
      github: "",
      email: "",
      qq: "",
      wechat: "",
      bilibili: "",
      twitter: "",
    }),
  },
});

const socialLinks = [
  { name: "Github", tip: "去 Github 看看" },
  { name: "Email", tip: "来封 Email ~" },
  { name: "QQ", tip: "有什么事吗" },
  { name: "WeChat", tip: "你懂的 ~" },
  { name: "BiliBili", tip: "(゜-゜)つロ 干杯 ~" },
  { name: "Twitter", tip: "你懂的 ~" },
];

const value = computed(() =>
  socialLinks.map((item) => ({
    ...item,
    url: props.links[item.name.toLowerCase()],
  }))
);

const dialogShow = ref(false);
const dialogData = ref({ title: "", url: "" });
const socialTip = ref("通过这里联系我吧");

const componentMap = {
  Github: github,
  Email: email,
  QQ: qqchat,
  WeChat: wechat,
  BiliBili: bilibili,
  Twitter: twitter,
};

function handleSocialClick(item) {
  if (item === value.value[0]) {
    window.open(item.url, "_blank");
  } else {
    openDialog(item);
  }
}

function openDialog(item) {
  dialogData.value = {
    title: ` ${item.name} 地址`,
    url: item.url,
  };
  dialogShow.value = true;
}

function beforeClose(action) {
  if (action === "confirm") {
    copy(dialogData.value.url);
  }
  return Promise.resolve(true);
}

function getSvgComponent(name) {
  return componentMap[name];
}
</script>

<style lang="scss" scoped>
.social {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  max-width: 460px;
  height: 42px;
  margin: 0 auto;
  background-color: transparent;
  border-radius: 6px;
  backdrop-filter: blur(0);
  animation: fade 0.5s;
  transition: background-color 0.3s, backdrop-filter 0.3s;

  @media (max-width: 840px) {
    max-width: 100%;
  }

  .link {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 20px;

    @media (max-width: 840px) {
      width: 80%;
    }

    .icon {
      width: 20px;
      height: 20px;
      cursor: pointer;
      transition: transform 0.3s;

      &:hover {
        transform: scale(1.2);
      }

      &:active {
        transform: scale(1);
      }
    }
  }

  // .tip {
  //   position: absolute;
  //   right: 0;
  //   display: none;
  //   margin-right: 12px;
  //   animation: fade 0.5s;

  //   @media (max-width: 840px) {
  //     display: none !important;
  //   }
  // }

  @media (min-width: 768px) {
    &:hover {
      backdrop-filter: blur(5px);

      // .tip {
      //   display: block;
      // }
    }
  }
}
</style>
