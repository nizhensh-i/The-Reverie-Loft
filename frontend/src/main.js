import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";
import pinia from "./stores/index.js";

import "@/asset/styles/init.css";

// 具体组件样式按需导入
import "vant/es/popover/style";
// import 'vant/es/dialog/style'
import "element-plus/es/components/message/style/css";
// import 'element-plus/es/components/notification/style/css'
// import 'element-plus/es/components/message-box/style/css'
import "element-plus/es/components/loading/style/css";

// 插件导入
import { loadingFadeOut } from "virtual:app-loading";
import vSlideIn from "@/directives/vSlideIn.js";

// 解决 Added non-passive event listener to a scroll-blocking 'touchstart' event. 问题
import "default-passive-events";
loadingFadeOut();

const app = createApp(App);

// 指令注册
app.directive("slide-in", vSlideIn);

// 插件使用
app.use(pinia);
app.use(router);

if (import.meta.env.DEV) {
  import("./main.dev.js").then(({ setupDevPlugins }) => {
    setupDevPlugins(app);
  });
}

app.mount("#app");
