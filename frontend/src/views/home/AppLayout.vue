<script setup>
import Header from "./components/Header.vue";
import AtmosphereHeader from "./components/AtmosphereHeader.vue";
import GlobalPlayer from "@/views/user/components/music/GlobalPlayer.vue";
import MiniPlayer from "@/views/user/components/music/MiniPlayer.vue";
import MobileFloatingPlayer from "@/views/user/components/music/MobileFloatingPlayer.vue";
import { useRoute } from "vue-router";
import { computed } from "vue";
import zhCn from "element-plus/es/locale/lang/zh-cn";

const route = useRoute();
// 判断是否为 用户资料页面
const isUserPage = computed(() => route.name === "user");
</script>

<template>
  <el-config-provider :locale="zhCn">
    <el-container>
      <el-header>
        <Header />
        <!-- <AtmosphereHeader/> -->
      </el-header>
      <el-divider />
      <el-main :class="{ 'no-padding': isUserPage }">
        <el-scrollbar ref="scrollbar" class="Scrollbar">
          <router-view v-slot="{ Component, route }">
            <keep-alive>
              <component
                v-if="route.meta.keepAlive"
                :is="Component"
                :key="route.name"
              />
            </keep-alive>
            <component
              v-if="!route.meta.keepAlive"
              :is="Component"
              :key="route.name"
            />
          </router-view>
        </el-scrollbar>
      </el-main>

      <!-- 全局音乐播放器 -->
      <GlobalPlayer />
      <!-- PC端底部迷你播放器 -->
      <MiniPlayer />
      <!-- 移动端悬浮播放按钮 -->
      <MobileFloatingPlayer />
    </el-container>
  </el-config-provider>
</template>

<style scoped>
body {
  /* 移动端点击可点击元素时，出现蓝色默认背景色 */
  -webkit-tap-highlight-color: transparent;
}
.el-container {
  width: 100%;
  height: 100%;
}
.el-header {
  height: 45px;
  padding: 0px;
}
.el-main {
  padding: 10px 20px 0px 20px;
}
.el-main.no-padding {
  padding: 0 !important;
}

/* 10px是随机添加的，出现阻尼效果 并且页头不会消失 */
.el-scrollbar {
  height: calc(100vh - var(--el-main-padding) * 2 - 10px);
}
.el-scrollbar :deep(.el-scrollbar__thumb) {
  background-color: rgba(0, 0, 0, 0);
}
.el-divider--horizontal {
  margin: 2px 0px 0px 0px;
  height: 0px;
}
</style>
