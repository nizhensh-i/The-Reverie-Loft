<script setup>
import { onMounted, ref, watch } from "vue";
import BanTouchMask from "./BanTouchMask.vue";
import CenterLogo from "./CenterLogo.vue";
import useMobileVhCssVar from "./hooks/useMobileVhCssVar";

defineOptions({
  name: "App",
});

const animationEnd = ref(false);
const drawerVisible = ref(false);
const backgroundLoaded = ref(false);

useMobileVhCssVar();

// 控制着中间字按钮的出现时机。
onMounted(() => {
  setTimeout(() => {
    animationEnd.value = true;
  }, 1300);
});

// 会把主页背景部分变黑，导致无法预览，故注释掉
// watch([backgroundLoaded, animationEnd], () => {
//   if (backgroundLoaded.value && animationEnd.value) {
//     document.body.style.backgroundColor = 'rgba(0,0,0,0.8)'
//   }
// })
</script>

<template>
  <div id="main-view">
    <!-- 遮罩：防止用户在动画播放期间点击屏幕 -->
    <BanTouchMask :touchable="animationEnd" />

    <!-- 中间LOGO部分 -->
    <CenterLogo
      :drawer-visible="drawerVisible"
      :touchable="animationEnd"
      @background-loaded="backgroundLoaded = true"
    />
  </div>
</template>

<style lang="scss" scoped>
#main-view {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: calc(var(--vh, 1vh) * 100);
  overflow: hidden;
}
</style>
