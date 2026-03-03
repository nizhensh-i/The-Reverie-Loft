import { fileURLToPath, URL } from "node:url";
import { include, exclude } from "./build/optimize";
import { loadEnv } from "vite";
import { getPluginsList } from "./build/plugins";
import { root, wrapperEnv } from "./build/utils";
import { getLocalIP } from "./src/utils/ipUtil.js";

export default ({ mode }) => {
  const { VITE_COMPRESSION, VITE_PORT } = wrapperEnv(loadEnv(mode, root));

  const backendAddr = `http://${getLocalIP()}:4289`;
  const sokcetIOAddr = `http://${getLocalIP()}:4290`;
  return {
    plugins: getPluginsList(VITE_COMPRESSION, mode),
    resolve: {
      alias: {
        "@": fileURLToPath(new URL("./src", import.meta.url)),
      },
    },
    server: {
      host: "0.0.0.0",
      port: VITE_PORT,
      proxy: {
        // 后端接口代理
        "/api": {
          target: backendAddr,
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\/api/, ""),
        },
        // websocket代理
        "/socket.io/": {
          target: sokcetIOAddr,
          changeOrigin: true,
          // 启用 WebSocket 代理
          ws: true,
        },
      },
    },
    define: {
      // enable hydration mismatch details in production build
      __VUE_PROD_HYDRATION_MISMATCH_DETAILS__: "true",
    },
    optimizeDeps: {
      include,
      exclude,
    },
    build: {
      rollupOptions: {
        // 静态资源分类打包
        output: {
          chunkFileNames: "static/js/[name]-[hash].js",
          entryFileNames: "static/js/[name]-[hash].js",
          assetFileNames: "static/[ext]/[name]-[hash].[ext]",
        },
      },
    },
  };
};
