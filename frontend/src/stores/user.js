import { defineStore } from "pinia";
import { io } from "socket.io-client";
import imageCfg from "@/config/image.js";
import {
  LOCAL_USER_BG_MOBILE,
  LOCAL_USER_BG_PC,
  qiniuUrl,
} from "@/config/fallbackAssets.js";
import cityUtil from "@/utils/cityUtil.js";
import { areaList } from "@vant/area-data";
import router from "@/router/index.js";
import {
  getToken,
  isJwtLike,
  isTokenExpired,
  refreshAccessToken,
} from "@/utils/tokenService.js";

export const useCurrentUserStore = defineStore("currentUser", {
  state: () => ({
    socket: null,
    activeChat: null,
    heartbeatInterval: null,
    access_token: "",
    refresh_token: "",
    userInfo: {
      id: "1",
      username: "",
      nickname: "",
      roleId: 0,
      confirmed: false,
      bg_image: "",
      pc_bg_image: "",
      image: "",
      about_me: "",
      location: "",
      // 已点赞的评论id
      likeIds: [],
      // 关注的用户
      followed: [
        {
          id: -1,
          name: "",
          uName: "",
          avatar: "",
        },
      ],
      interest: {
        movies: [],
        books: [],
      },
      social_account: {
        github: "",
        email: "",
        qq: "",
        wechat: "",
        bilibili: "",
        twitter: "",
      },
      music: {
        name: "",
        aitist: "",
        url: "",
        pic: "",
        lrc: "",
      },
      tags: [],
      // 第三方账号绑定状态
      bound_providers: [],
      // 是否有密码
      has_password: true,
    },
    notice: {
      Notification_data: [],
      // NOTIFICATION_KEY: `user_notifications_${userInfo.id}`,
      NOTIFICATION_KEY: `user_notifications_1`,
      MAX_ITEM: 50,
    },
    devUploadBaseUrl: "dev/",
    // 主页移动端背景库地址
    userBackgroundUrl: "userBackground/mobile/",
    // 主页PC端背景库地址
    userPcBackgroundUrl: "userBackground/pc/",
    // 用户头像库地址
    userAvatars: "userAvatars/",
    defaultBackground: qiniuUrl(
      "userBackground/mobile/image-pre3.webp-slim",
      LOCAL_USER_BG_MOBILE
    ),
    defaultPcBackground: qiniuUrl(
      "userBackground/pc/image.png-slim",
      LOCAL_USER_BG_PC
    ),
  }),
  getters: {
    isLogin: (state) => state.access_token != "",
    isCommentManage: (state) => state.userInfo.roleId >= 2,
    isConfirmed: (state) => state.userInfo.confirmed == true,
    isAdmin: (state) => state.userInfo.roleId == 3,
    priorityName: (state) =>
      state.userInfo.nickname
        ? state.userInfo.nickname
        : state.userInfo.username,
    avatarsUrl: (state) =>
      state.userInfo.image ? state.userInfo.image : imageCfg.logOut,
    backGroundUrl: (state) =>
      state.userInfo.bg_image
        ? state.userInfo.bg_image
        : state.defaultBackground,
    pcBackGroundUrl: (state) =>
      state.userInfo.pc_bg_image
        ? state.userInfo.pc_bg_image
        : state.defaultPcBackground,
    cityName: (state) => {
      if (!state.userInfo.location) return "";
      return cityUtil.getCodeToName(state.userInfo.location, areaList);
    },
    // 图片上传目录
    uploadArticlesBaseUrl: (state) =>
      import.meta.env.DEV == true
        ? state.devUploadBaseUrl
        : `user_image/user_${state.userInfo.id}/articles/`,
    uploadAvatarsBaseUrl: (state) =>
      import.meta.env.DEV == true
        ? state.devUploadBaseUrl
        : `user_image/user_${state.userInfo.id}/avatars/`,
    uploadCommentsBaseUrl: (state) =>
      import.meta.env.DEV == true
        ? state.devUploadBaseUrl
        : `user_image/user_${state.userInfo.id}/comments/`,
    uploadInterestBaseUrl: (state) =>
      import.meta.env.DEV == true
        ? state.devUploadBaseUrl
        : `user_image/user_${state.userInfo.id}/interest/`,
    uploadMarkdownBaseUrl: (state) =>
      import.meta.env.DEV == true
        ? state.devUploadBaseUrl
        : `user_image/user_${state.userInfo.id}/markdown/`,
  },
  actions: {
    addItemLikeIds(value) {
      this.userInfo.likeIds.push(value);
    },
    addItemFollowed(value) {
      this.userInfo.followed.push(value);
    },
    delItemFollowed(username) {
      this.userInfo.followed = this.userInfo.followed.filter(
        (item) => item.uName != username
      );
    },
    // 保存通知
    saveNotifications(notifications) {
      const trimmed = notifications.slice(0, this.notice.MAX_ITEM);
      this.notice.Notification_data = trimmed;
    },
    // 读取通知
    loadNotifications() {
      return this.notice.Notification_data;
    },
    // 清空通知（可选）
    clearNotifications() {},
    clearLocalData() {
      localStorage.removeItem("blog");
      localStorage.removeItem("blogOtherUser");
    },
    logOut() {
      this.clearLocalData();
      this.$reset();
    },
    async ensureSocketAuth() {
      const token = this.access_token;
      if (!token) return "";
      if (!isTokenExpired(token, 30)) return token;
      console.log("⚠️ access_token即将过期，正在刷新...");

      try {
        const refreshToken = getToken("refresh_token");
        if (!refreshToken) {
          console.warn("⚠️ 缺少refresh_token，无法刷新");
          this.logOut();
          router.push("/login");
          return "";
        }
        if (isJwtLike(refreshToken) && isTokenExpired(refreshToken, 0)) {
          console.warn("⚠️ refresh_token已过期，需要重新登录");
          this.logOut();
          router.push("/login");
          return "";
        }

        const newToken = await refreshAccessToken();
        this.access_token = newToken;
        if (this.socket) {
          this.socket.io.opts.query = {
            ...(this.socket.io.opts.query || {}),
            access_token: newToken,
          };
          if (this.socket.connected) this.socket.disconnect();
          this.socket.connect();
        }
        return newToken;
      } catch (err) {
        console.error("❌ token刷新失败，需要重新登录", err);
        this.logOut();
        router.push("/login");
        return "";
      }
    },
    async connectSocket() {
      if (this.socket) return;
      const token = await this.ensureSocketAuth();
      if (!token) {
        console.warn("⚠️ 缺少有效token，跳过WebSocket连接");
        return;
      }
      this.socket = io(import.meta.env.DEV ? "" : import.meta.env.VITE_DOMAIN, {
        path: "/socket.io",
        query: { access_token: token },
        transports: ["websocket"],
        withCredentials: true,
        reconnectionAttempts: 5,
        reconnectionDelay: 5000,
        // 与后端ping_timeout一致
        pingTimeout: 30000,
        pingInterval: 60000,
      });

      // 监听连接成功事件
      this.socket.on("connect", () => {
        console.log("已连接到WebSocket服务器", this.socket.id);
      });
      this.socket.on("connect_error", (err) => {
        const msg = String(
          err?.data?.message || err?.data || err?.message || ""
        );
        const isTokenExpired =
          msg.includes("token已过期") || msg.toLowerCase().includes("expired");

        if (isTokenExpired) {
          console.warn("⚠️ WebSocket token过期，尝试刷新并重连");
          this.ensureSocketAuth();
          return;
        }

        console.error("❌ WebSocket连接失败：", {
          message: err.message,
          code: err.code,
          data: err.data,
        });
      });

      this.socket.on("error", (err) => {
        const msg = String(err?.message || err || "");
        if (
          msg.includes("token已过期") ||
          msg.toLowerCase().includes("expired")
        ) {
          console.warn("⚠️ WebSocket鉴权失效，尝试刷新并重连");
          this.ensureSocketAuth();
        }
      });

      this.socket.on("disconnect", (reason) => {
        console.warn("⚠️ WebSocket断开连接：", reason);
      });

      this.socket.on("message_sent", (msg) => {
        console.log("📤 消息发送成功（后端确认）：", msg);
        // 前端消息发送成功后的逻辑（比如清空输入框、更新聊天记录）
      });

      this.socket.on("heartbeat", () => {
        console.log("💓 心跳响应正常");
      });

      // 初始化心跳定时器
      this.heartbeatInterval = setInterval(() => {
        if (!this.socket) return;
        this.ensureSocketAuth().then(() => {
          if (this.socket?.connected) {
            this.socket.emit("heartbeat");
          }
        });
      }, 60000);
    },
    disconnectSocket() {
      if (!this.socket) return;

      // 监听new_notification，new_message事件， 在具体组件中写了

      this.socket.off("connect");
      this.socket.off("connect_error");

      this.socket.off("disconnect");
      // 清理业务事件
      this.socket.off("new_message");
      this.socket.off("message_sent");
      this.socket.off("new_notification");
      this.socket.off("heartbeat");

      this.cleanup();
      this.socket = null;
      console.log("前端主动断开WebSocket连接");
    },
    cleanup() {
      // 清理定时器
      if (this.heartbeatInterval) {
        clearInterval(this.heartbeatInterval);
        this.heartbeatInterval = null;
      }

      // 断开Socket连接
      if (this.socket) {
        this.socket.disconnect();
        this.socket = null;
      }
    },
    async enterChat(targetId) {
      this.activeChat = targetId;
      const token = await this.ensureSocketAuth();
      if (!token) return;

      // 确保socket已连接再发送事件
      if (this.socket?.connected) {
        this.socket.emit("enter_chat", { targetId: targetId });
        console.log("🗨️ 进入聊天:", targetId);
        return;
      }
      console.error("❌ 未连接WebSocket，无法进入聊天。正在重试");
      this.connectSocket();
      setTimeout(() => this.enterChat(targetId), 1000);
    },

    async sendMessage(chat, func) {
      let content = chat.content;
      if (this.activeChat && content.trim()) {
        const token = await this.ensureSocketAuth();
        if (!token) return;
        if (this.socket?.connected) {
          this.socket.emit("send_message", {
            receiver_id: this.activeChat,
            content: content.trim(),
          });
          console.log("📤 发送消息:", content.trim());
          // 前端临时处理（最终以后端message_sent为准）
          if (func) func(chat);
        } else {
          console.error("❌ 未连接WebSocket，无法发送消息");
          // 重连后重试（可选）
          this.connectSocket();
          setTimeout(() => this.sendMessage(chat, func), 1000);
        }
      }
    },
    setUserInfo(val) {
      this.userInfo = { ...this.userInfo, ...val };
    },
  },
  persist: {
    key: "blog",
    storage: localStorage,
    pick: ["access_token", "refresh_token", "userInfo", "notice"],
  },
});
