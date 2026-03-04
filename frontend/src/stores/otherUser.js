import { defineStore } from "pinia";
import {
  LOCAL_USER_BG_MOBILE,
  LOCAL_USER_BG_PC,
  qiniuUrl,
} from "@/config/fallbackAssets.js";

export const useOtherUserStore = defineStore("otherUser", {
  state: () => ({
    userInfo: {
      id: 1,
      username: "",
      nickname: "",
      bg_image: "",
      pc_bg_image: "",
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
    },
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
    isCommentManage: (state) => state.userInfo.roleId >= 2,
    isConfirmed: (state) => state.userInfo.confirmed == true,
    isAdmin: (state) => state.userInfo.isAdmin == true,
    priorityName: (state) =>
      state.userInfo.nickname
        ? state.userInfo.nickname
        : state.userInfo.username,
    backGroundUrl: (state) =>
      state.userInfo.bg_image
        ? state.userInfo.bg_image
        : state.defaultBackground,
    pcBackGroundUrl: (state) =>
      state.userInfo.pc_bg_image
        ? state.userInfo.pc_bg_image
        : state.defaultPcBackground,
  },
  actions: {
    setUserInfo(val) {
      this.userInfo = val;
    },
  },
  persist: {
    key: "blogOtherUser",
    storage: localStorage,
  },
});
