<template>
  <PageHeadBack>
    <div class="settings-content">
      <!-- 未设置密码提示横幅 -->
      <el-alert
        v-if="!currentUser.userInfo.has_password"
        title="你尚未设置登录密码"
        type="warning"
        :closable="false"
        show-icon
        class="password-warning-banner"
      />

      <!-- 账户设置 -->
      <div class="cell-group">
        <van-cell
          v-if="currentUser.userInfo.has_password"
          title="修改密码"
          icon="lock"
          is-link
          @click="goTo('/changePassword')"
        />
        <van-cell
          v-else
          title="设置密码"
          icon="lock"
          is-link
          @click="goTo('/setPassword')"
        />
        <van-cell
          v-if="currentUser.isConfirmed"
          title="修改邮箱"
          icon="envelop-o"
          is-link
          @click="goTo('/changeEmail')"
        />
        <van-cell
          v-else
          title="绑定邮箱"
          icon="envelop-o"
          is-link
          @click="goTo('/bindEmail')"
        />
      </div>

      <!-- 第三方账号绑定 -->
      <div class="cell-group">
        <div class="cell-group-title">第三方账号绑定</div>
        <van-cell
          v-for="provider in oauthProviders"
          :key="provider.provider"
          :title="getProviderTitle(provider.provider)"
          :label="getProviderLabel(provider.provider)"
          :class="{ 'is-bound': isProviderBound(provider.provider) }"
        >
          <!-- :icon="getProviderIcon(provider.provider)" -->
          <template #right-icon>
            <el-switch
              :model-value="isProviderBound(provider.provider)"
              @update:model-value="
                (value) => handleProviderToggle(value, provider.provider)
              "
              size="small"
            />
          </template>
        </van-cell>
      </div>

      <!-- 管理员设置 -->
      <div v-if="currentUser.isCommentManage" class="cell-group">
        <van-cell
          title="评论管理"
          icon="chat-o"
          is-link
          @click="goTo('/commentManagement')"
        />
        <van-cell
          title="标签管理"
          icon="medal-o"
          is-link
          @click="goTo('/tag')"
        />
        <van-cell
          title="操作日志"
          icon="shield-o"
          is-link
          @click="goTo('/operateLog')"
        />
        <van-cell
          title="管理背景库"
          icon="photo-o"
          is-link
          @click="goTo('/uploadBg')"
        />
        <van-cell
          title="管理图像库"
          icon="user-o"
          is-link
          @click="goTo('/uploadAva')"
        />
        <van-cell
          title="找回其他用户密码"
          icon="warning-o"
          is-link
          @click="goTo('/PasswordChangeAdmin')"
        />
      </div>

      <!-- 其他设置 -->
      <!-- <div class="cell-group">
        <van-cell title="意见反馈" icon="question-o" is-link />
      </div> -->

      <div class="logout-button">
        <el-button type="danger" round @click="handleLogout"
          >退出登录</el-button
        >
      </div>
    </div>
  </PageHeadBack>
</template>

<script>
import PageHeadBack from "@/utils/components/PageHeadBack.vue";
import { useCurrentUserStore } from "@/stores/user";

import authApi from "@/api/auth/authApi.js";

export default {
  name: "Settings",
  components: {
    PageHeadBack,
  },
  data() {
    return {
      oauthProviders: [],
    };
  },
  computed: {
    boundProviders() {
      return this.currentUser.userInfo.bound_providers || [];
    },
  },
  setup() {
    const currentUser = useCurrentUserStore();
    return { currentUser };
  },
  mounted() {
    this.loadOAuthProviders();
  },
  methods: {
    checkLastProviderAndPassword(provider) {
      if (
        !this.currentUser.userInfo.has_password &&
        this.boundProviders.length <= 1 &&
        this.isProviderBound(provider)
      ) {
        ElMessage.warning("为保证账号安全，请先设置密码");
        this.$forceUpdate();
        return false;
      }
      return true;
    },
    goTo(route) {
      this.$router.push(route);
    },
    async loadOAuthProviders() {
      try {
        const res = await authApi.oauthProviders();
        if (res.code === 200) {
          this.oauthProviders = res.data.providers || [];
        }
      } catch (error) {
        console.error("加载OAuth平台列表失败:", error);
      }
    },
    isProviderBound(provider) {
      return this.boundProviders.includes(provider);
    },
    getProviderTitle(provider) {
      const providerMap = {
        github: "GitHub",
        google: "Google",
        qq: "QQ",
        wechat: "微信",
        weibo: "微博",
      };
      return providerMap[provider] || provider.toUpperCase();
    },
    // getProviderIcon(provider) {
    //   const iconMap = {
    //     github: "github",
    //     google: "google",
    //     qq: "qq",
    //     wechat: "wechat",
    //     weibo: "weibo",
    //   };
    //   return iconMap[provider] || "link-o";
    // },
    getProviderLabel(provider) {
      if (this.isProviderBound(provider)) {
        return "已绑定";
      }
      return "未绑定";
    },
    async handleProviderToggle(value, provider) {
      if (value) {
        // 绑定
        await this.bindProvider(provider);
      } else {
        // 解绑
        if (!this.checkLastProviderAndPassword(provider)) {
          return;
        }
        await this.unbindProvider(provider);
      }
    },
    async bindProvider(provider) {
      try {
        const res = await authApi.oauthBind(provider);
        if (res.code === 200 && res.data.authorize_url) {
          // 跳转到第三方授权页面
          window.location.href = res.data.authorize_url;
        } else {
          ElMessage.error("发起绑定失败");
        }
      } catch (error) {
        console.error("绑定失败:", error);
        ElMessage.error(error.message || "绑定失败");
      }
    },
    unbindProvider(provider) {
      try {
        const providerName = this.getProviderTitle(provider);

        showConfirmDialog({
          title: "确认解绑",
          message: `确定要解绑 ${providerName} 账号吗？`,
          confirmButtonText: "解绑",
          cancelButtonText: "取消",
          beforeClose: this.unBindBeforeClose.bind(null, provider),
        });
      } catch (error) {
        console.error("解绑失败:", error);
        ElMessage.error(error.message || "解绑失败");
        // 恢复switch状态
        this.$forceUpdate();
      }
    },

    //（自定义参数在前，action在后）
    unBindBeforeClose(provider, action) {
      if (action !== "confirm") {
        return Promise.resolve(true);
      }
      return authApi
        .oauthUnbind(provider)
        .then((res) => {
          if (res.code === 200) {
            ElMessage.success("解绑成功");
            // 直接从Pinia store中更新bound_providers
            const updatedProviders = this.boundProviders.filter(
              (p) => p !== provider
            );
            this.currentUser.setUserInfo({
              bound_providers: updatedProviders,
            });
          } else {
            ElMessage.error(res.message || "解绑失败");
          }
          return true;
        })
        .catch((err) => {
          return true;
        });
    },
    handleLogout() {
      showConfirmDialog({
        title: "提示",
        message: "是否退出登录？",
        width: "280px",
        beforeClose: this.beforeClose,
      });
    },
    beforeClose(action) {
      if (action !== "confirm") {
        return Promise.resolve(true);
      } else {
        this.currentUser.disconnectSocket();
        return Promise.all([
          authApi.revokeToken("access_token"),
          authApi.revokeToken("refresh_token"),
        ])
          .then((res) => {
            this.currentUser.logOut();
            this.$router.push("/posts");
            return res;
          })
          .catch((err) => {
            console.error("撤销令牌失败:", err);
            this.currentUser.logOut();
            this.$router.push("/posts");
            return err;
          });
      }
    },
  },
};
</script>

<style scoped>
.settings-content {
  padding: 12px;
}

.cell-group {
  margin-bottom: 16px;
}

.cell-group-title {
  padding: 8px 16px;
  font-size: 14px;
  color: #969799;
  background-color: #f7f8fa;
}

.logout-button {
  margin-top: 24px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}
.el-button {
  width: 92%;
}

:deep(.van-cell.is-bound) {
  --van-cell-label-color: #07c160;
}

.password-warning-banner {
  margin-bottom: 16px;
}
</style>
