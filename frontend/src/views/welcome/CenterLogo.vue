<script setup>
import { GLOBAL_CONFIG } from "@/config/welcomeCfg.js";
import { randomNum } from "@/utils/common";
import { onMounted, ref } from "vue";
// import LocalLogo from '@/asset/logo.svg?component'

defineOptions({
  name: "CenterLogo",
});

defineProps({
  drawerVisible: Boolean,
  touchable: Boolean,
});

const emit = defineEmits({
  backgroundLoaded: [],
});

const bgLoaded = ref(false);
const slogan = ref("");

/**
 * 加载背景图片
 */
function loadBackground() {
  var img = new Image();
  img.src = GLOBAL_CONFIG.BACKGROUND_IMG_URL;
  img.addEventListener("load", () => {
    bgLoaded.value = true;
    emit("backgroundLoaded");
  });
}

function randomSlogan() {
  const slogans = GLOBAL_CONFIG.SLOGANS;
  slogan.value = slogans[randomNum(0, slogans.length - 1)];
}
function goHome() {
  window.location.href = "/posts";
}
onMounted(() => {
  randomSlogan();
  loadBackground();
});
</script>

<template>
  <div
    :class="['logo-area', { 'is-blur': drawerVisible }]"
    :style="{ background: `url(${GLOBAL_CONFIG.BACKGROUND_IMG_URL})` }"
  >
    <div :class="['img-shadow', { 'img-shadow-show': bgLoaded }]"></div>
    <div class="inner" style="cursor: pointer" @click="goHome">
      <!-- <LocalLogo :class="['main-logo', { 'main-logo-top': touchable }]" /> -->
      <div :class="['hello', { hello_bottom: touchable }]">
        <div>{{ slogan }}</div>
        <div class="hello_bottom_text">
          <div class="slide-up">访问 随想阁楼</div>
        </div>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
@import url("@/asset/css/animate.scss");

.logo-area {
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  background-size: cover !important;
  background-position: center !important;
  border-radius: 100%;
  animation: logoEnter 1.2s forwards;
  transition: all 0.8s;

  &.is-blur {
    filter: blur(5px);
  }

  .img-shadow {
    position: absolute;
    width: 100%;
    height: 100%;
    background-color: #fda085;
    border-radius: 100%;
    overflow: hidden;
    animation: shadowEnter 1.2s forwards;
    transition: background-color 0.5s;

    &.img-shadow-show {
      background-color: rgba(0, 0, 0, 0.5);
    }
  }

  .inner {
    position: relative;

    .main-logo {
      position: absolute;
      top: 0;
      height: 6rem;
      transform: translate(-50%, -50%);
      transition: all 1s;

      &.main-logo-top {
        top: -3.2rem;
      }
    }

    .hello {
      position: absolute;
      top: 100px;
      width: 18.75rem;
      font-size: 21px;
      color: #ffffff;
      text-align: center;
      opacity: 0;
      transform: translate(-50%, -50%);
      transition: all 1s;

      &_bottom {
        top: 3.5rem;
        opacity: 1;

        &_text {
          margin-top: 0.5rem;
          padding-top: 0.5rem;
          font-size: 14px;
          border-top: 1px solid #fff;

          .slide-up {
            margin-top: 15px;
            animation: float 4s infinite ease-in-out;
          }
        }
      }
    }
  }
}
</style>
