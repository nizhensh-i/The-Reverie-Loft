<template>
  <header class="header-container">
    <!-- 左侧区域 -->
    <div class="header-left">
      <div class="home-icon" @click="goHomePage">
        <homeIcon />
      </div>
      <div class="daily-sentence">
        <MarQuee :text="daySentence" :speed="0.7" />
      </div>
    </div>

    <!-- 中间空白区域 -->
    <div class="header-center"></div>

    <!-- 右侧区域 -->
    <div class="header-right">
      <BellCom class="notification-icon" />
      <div class="user-avatar">
        <van-popover
          v-model:show="showPopover"
          :show-arrow="false"
          placement="bottom-end"
          :offset="[12, 8]"
          :actions="actions"
          @select="onSelect"
        >
          <template #reference>
            <el-avatar
              alt="用户图像"
              :size="32"
              :src="currentUser.avatarsUrl"
              @error="errorImage"
            />
          </template>
          <template #default v-if="currentUser.isLogin">
            <van-cell
              :title="currentUser.priorityName"
              :label="currentUser.userInfo.username"
              title-style="margin-left:10px"
            >
              <template #icon>
                <el-avatar
                  alt="用户图像"
                  :src="currentUser.avatarsUrl"
                  :size="47"
                />
              </template>
            </van-cell>
            <van-cell
              title="个人资料"
              icon="manager-o"
              clickable
              @click="handleCellClick(`/user/${currentUser.userInfo.username}`)"
            />
            <van-cell
              title="设置"
              icon="setting-o"
              clickable
              @click="handleCellClick('/settings')"
            />
          </template>
        </van-popover>
      </div>
    </div>
  </header>
</template>

<script>
import { useCurrentUserStore } from "@/stores/user";
import MarQuee from "@/utils/components/MarQuee.vue";
import daysApi from "@/api/days/daysApi.js";
import emitter from "@/utils/emitter.js";
import imageCfg from "@/config/image.js";
import homeIcon from "@/asset/svg/homeIcon.svg?component";
import BellCom from "./BellCom.vue";
import authApi from "@/api/auth/authApi.js";

export default {
  name: "BurgerMenu",
  components: {
    MarQuee,
    homeIcon,
    BellCom,
  },
  data() {
    return {
      windowWidth: window.innerWidth,
      menuItems: [
        { label: "About", href: "#" },
        { label: "Services", href: "#" },
        { label: "Contact", href: "#" },
      ],
      isContactDropdownActive: false,
      accountLabel: "账户",
      daySentence: "",
      photo: {
        Avatar: "",
        default:
          "https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png",
      },
      showPopover: false,
      actions: [
        { text: "登录", icon: "user-o" },
        { text: "注册", icon: "add-o" },
      ],
    };
  },
  setup() {
    const currentUser = useCurrentUserStore();
    return { currentUser };
  },
  computed: {
    isHomePage() {
      return this.$route.path === "/posts";
    },
  },
  mounted() {
    this.initImage();
    this.daySentence = daysApi.fetchQuote();
    emitter.on("image", (url) => {
      this.photo.Avatar = url;
    });
  },
  created() {
    window.addEventListener("resize", this.updateWindowWidth);
  },
  beforeUnmount() {
    window.removeEventListener("resize", this.updateWindowWidth);
  },
  methods: {
    handleCellClick(route) {
      // 关闭弹出框
      this.closeToggleMenu();
      this.$router.push(route);
    },
    closeToggleMenu() {
      if (this.showPopover) {
        this.showPopover = false;
      }
    },
    updateWindowWidth() {
      this.windowWidth = window.innerWidth;
    },
    toggleContactDropdown() {
      this.isContactDropdownActive = !this.isContactDropdownActive;
      this.accountLabel = this.isContactDropdownActive ? "关闭" : "账户";
    },
    log_out() {
      showConfirmDialog({
        title: "提示",
        message: "是否退出登陆？",
        width: "280px",
        beforeClose: this.beforeClose,
      });
    },

    beforeClose(action) {
      if (action !== "confirm") {
        return Promise.resolve(true);
      } else {
        this.currentUser.disconnectSocket();
        // 同时撤销访问令牌和刷新令牌
        return Promise.all([
          authApi.revokeToken("access_token"),
          authApi.revokeToken("refresh_token"),
        ])
          .then((res) => {
            this.closeToggleMenu();
            this.currentUser.logOut();
            this.initImage();
            return res;
          })
          .catch((err) => {
            console.error("撤销令牌失败:", err);
            // 即使撤销失败也执行登出
            this.closeToggleMenu();
            this.currentUser.logOut();
            this.initImage();
            return err;
          });
      }
    },

    goHomePage() {
      if (this.isHomePage) {
        return;
      }
      this.$router.push("/posts");
    },
    errorImage() {
      this.photo.Avatar = imageCfg.logOut;
    },
    initImage() {
      if (!this.currentUser.userInfo.image) {
        this.photo.Avatar = imageCfg.logOut;
        return;
      }
      this.photo.Avatar = this.currentUser.userInfo.image;
    },
    onSelect(action) {
      if (action.text == "登录") {
        this.$router.push("/login");
      } else if (action.text == "注册") {
        this.$router.push("/register");
      }
    },
  },
};
</script>

<style lang="scss" scoped>
.header-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  height: 48px;
  padding: 0 24px;
  box-sizing: border-box;
}

.header-left {
  display: flex;
  flex-shrink: 0;
  align-items: center;
}

.home-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: 8px 0 0 8px;
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    transform: translateY(-1px);
  }
}

.daily-sentence {
  height: 40px;
  min-width: 250px;
  padding: 0 12px;
  font-size: 14px;
  line-height: 40px;
  white-space: nowrap;
  overflow: hidden;
  border-radius: 0 8px 8px 0;
}

.header-center {
  flex: 1;
  min-width: 0;
}

.header-right {
  display: flex;
  flex-shrink: 0;
  align-items: center;
}

.notification-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: 8px 0 0 8px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.user-avatar {
  display: flex;
  align-items: center;
  height: 40px;
  padding: 0 8px;
  border-radius: 0 8px 8px 0;

  .el-avatar {
    cursor: pointer;
    transition: all 0.2s ease;

    &:hover {
      transform: scale(1.05);
    }
  }
}

.van-cell {
  width: 200px;
}

.van-divider {
  margin: 10px 0 0;
}

@media (max-width: 768px) {
  .header-container {
    height: 48px;
    padding: 0 16px;
  }

  .daily-sentence {
    max-width: 200px;
    height: 36px;
    padding: 0 8px 0 0;
    font-size: 13px;
    line-height: 36px;
  }

  .header-right {
    margin-top: 6px;
  }

  .home-icon,
  .notification-icon {
    width: 36px;
    height: 36px;
  }

  .user-avatar {
    height: 36px;
    padding: 0 6px;
  }
}
</style>
