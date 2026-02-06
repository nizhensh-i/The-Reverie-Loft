<script>
import dragVerifyImgRotate from "./components/dragVerifyImgRotate.vue";
import authApi from "@/api/auth/authApi.js";
import { useCurrentUserStore } from "@/stores/user";
import imageCfg from "@/config/image.js";
import SocialOAuthButtons from "./components/SocialOAuthButtons.vue";

export default {
  components: {
    dragVerifyImgRotate,
    SocialOAuthButtons,
  },
  data() {
    const validateUser = (rule, value, callback) => {
      if (value === "") {
        callback(new Error("请输入账户"));
      } else {
        callback();
      }
    };
    const validatePass = (rule, value, callback) => {
      if (value === "") {
        callback(new Error("请输入密码"));
      } else {
        callback();
      }
    };

    const isDev = import.meta.env.DEV;
    const initialData = {
      ruleForm: {
        user: "",
        pass: "",
      },
      rules: {
        user: [{ validator: validateUser, trigger: "blur" }],
        pass: [{ validator: validatePass, trigger: "blur" }],
      },
      isRemember: false,
      loading: false,
      oauthProviders: [],
      oauthLoading: false,
    };

    if (!isDev) {
      initialData.ruleForm.isPassing2 = false;
      initialData.imgPic = imageCfg.login;
    }

    return initialData;
  },
  setup() {
    const currentUser = useCurrentUserStore();
    return { currentUser };
  },
  computed: {
    formHasValue() {
      return this.ruleForm.user !== "" && this.ruleForm.pass !== "";
    },
    isDev() {
      return import.meta.env.DEV;
    },
  },
  beforeRouteEnter(to, from, next) {
    next((vm) => {
      if (to.query?.username) {
        vm.ruleForm.user = to.query.username;
      } else if (vm.isDev) {
        // 开发环境在路由进入时获取账号
        vm.getAccount();
      }
    });
  },
  mounted() {
    // 生产环境在 mounted 时获取账号
    if (!this.isDev) {
      this.getAccount();
    }
    this.loadProviders();
  },
  methods: {
    login() {
      this.$refs.ruleForm.validate((valid) => {
        if (valid) {
          // 生产环境需要验证通过
          if (!this.isDev && !this.ruleForm.isPassing2) {
            ElMessage("请先完成验证");
            return;
          }

          this.loading = true;
          authApi
            .login(this.ruleForm.user, this.ruleForm.pass)
            .then((res) => {
              this.loading = false;
              if (res.code === 200) {
                this.hasRemember();
                const u = res.data;
                this.currentUser.setUserInfo(u);
                this.currentUser.access_token = res.access_token;
                this.currentUser.refresh_token = res.refresh_token;

                // 根据环境显示不同的消息
                if (this.isDev) {
                  ElMessage.success("登录成功");
                } else {
                  ElMessage({
                    message: "登录成功",
                    type: "success",
                    duration: 1700,
                  });
                }

                this.$router.replace({ path: "/posts" });
              } else {
                if (this.isDev) {
                  ElMessage.error(res.message || "账号或密码错误");
                } else {
                  ElMessage({
                    message: res.message || "账号或密码错误",
                    type: "error",
                    duration: 1700,
                  });
                }
              }
            })
            .catch(() => {
              this.loading = false;
            });
        } else {
          ElMessage.error("请修正表单中的错误");
        }
      });
    },
    getAccount() {
      const savedUsername = localStorage.getItem("loginUsername");
      const savedPassword = localStorage.getItem("loginPassword");
      if (savedUsername && savedPassword) {
        this.ruleForm.user = savedUsername;
        this.ruleForm.pass = savedPassword;
        this.isRemember = true;
      }
    },
    hasRemember() {
      if (this.isRemember) {
        localStorage.setItem("loginUsername", this.ruleForm.user);
        localStorage.setItem("loginPassword", this.ruleForm.pass);
      } else {
        localStorage.removeItem("loginUsername");
        localStorage.removeItem("loginPassword");
      }
    },
    handleImageError() {
      if (!this.isDev) {
        this.imgPic = imageCfg.loginFail;
      }
    },
    async loadProviders() {
      try {
        const res = await authApi.oauthProviders();
        this.oauthProviders = res.data?.providers || [];
      } catch (error) {
        console.warn("加载第三方登录配置失败", error);
      }
    },
    async startOAuth(provider) {
      this.oauthLoading = provider;
      try {
        const res = await authApi.oauthAuthorize(provider);
        const url = res.data?.authorize_url;
        if (url) {
          window.location.href = url;
        } else {
          ElMessage.error(res.message || "获取授权链接失败");
        }
      } catch (error) {
        ElMessage.error("获取授权链接失败");
      } finally {
        this.oauthLoading = false;
      }
    },
  },
};
</script>

<template>
  <div class="login-container">
    <!-- PC端左侧插画区域 -->
    <div class="login-illustration">
      <div class="illustration-content">
        <div class="illustration-image">
          <div class="floating-shapes">
            <div class="shape shape-1"></div>
            <div class="shape shape-2"></div>
            <div class="shape shape-3"></div>
          </div>
          <div class="brand-icon">🏠</div>
        </div>
        <h1>云端阁楼</h1>
        <p>记录生活点滴，分享美好时光<br />在这里，每一刻都值得被珍藏</p>
      </div>
    </div>

    <!-- 右侧登录表单区域 -->
    <div class="login-form-area">
      <div class="form-wrapper">
        <div class="header">
          <h2>欢迎回来 👋🏻</h2>
          <p>云端阁楼，随想悠悠，静候时光</p>
        </div>

        <el-form
          :model="ruleForm"
          label-position="left"
          status-icon
          :rules="rules"
          ref="ruleForm"
        >
          <el-form-item prop="user">
            <el-input
              v-model="ruleForm.user"
              size="large"
              placeholder="请输入用户名"
            />
          </el-form-item>
          <el-form-item prop="pass">
            <el-input
              v-model="ruleForm.pass"
              show-password
              size="large"
              placeholder="密码"
            />
          </el-form-item>
          <!-- 生产环境显示拖拽验证 -->
          <el-form-item class="pic" v-if="!isDev">
            <drag-verify-img-rotate
              ref="dragVerify"
              :imgsrc="imgPic"
              v-model:isPassing="ruleForm.isPassing2"
              text="请按住滑块拖动"
              successText="验证通过"
              :width="200"
              :height="36"
              @img-error="handleImageError"
            >
            </drag-verify-img-rotate>
          </el-form-item>
        </el-form>
        <el-row justify="space-between">
          <el-col :span="4"
            ><el-checkbox label="记住密码" v-model="isRemember"></el-checkbox
          ></el-col>
          <el-col :span="6"
            ><div class="text">
              <el-link
                class="forget-pass"
                @click="$router.push('/resetPassword')"
                >忘记密码？</el-link
              >
            </div></el-col
          >
        </el-row>
        <div class="login-button">
          <el-button
            type="primary"
            round
            :disabled="!formHasValue"
            @click="login"
            :loading="loading"
            >登录</el-button
          >
        </div>

        <SocialOAuthButtons
          :providers="oauthProviders"
          :loading="oauthLoading"
          @start="startOAuth"
        />

        <div class="register-container">
          <el-text class="register-account">还没有账号?</el-text>
          <el-link class="register" @click="$router.push('/register')"
            >创建账号
          </el-link>
        </div>
        <div class="visit">
          <el-text class="register" @click="$router.push('/posts')"
            >游客访问</el-text
          >
        </div>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
// 基础变量
$font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
  "Helvetica Neue", Arial, "Noto Sans", sans-serif, "Apple Color Emoji",
  "Segoe UI Emoji", "Segoe UI Symbol", "Noto Color Emoji";
$primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
$form-gradient: linear-gradient(135deg, #f5f7fa 0%, #e4e7f1 100%);
$button-gradient: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
$button-hover-gradient: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);

// 基础样式
* {
  font-family: $font-family;
  -webkit-tap-highlight-color: transparent;
}

// 主容器 - PC端双栏布局
.login-container {
  display: flex;
  min-height: 100vh;
  background: $form-gradient;

  // 左侧插画区域
  .login-illustration {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    background: $primary-gradient;
    position: relative;
    overflow: hidden;

    .illustration-content {
      text-align: center;
      color: white;
      z-index: 1;
      position: relative;
      padding: 40px;
      max-width: 500px;

      .illustration-image {
        margin-bottom: 40px;
        position: relative;
        height: 200px;
        display: flex;
        align-items: center;
        justify-content: center;

        .floating-shapes {
          position: absolute;
          width: 100%;
          height: 100%;

          .shape {
            position: absolute;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 50%;
            animation: float 6s ease-in-out infinite;

            &.shape-1 {
              width: 80px;
              height: 80px;
              top: 0;
              left: 20%;
            }

            &.shape-2 {
              width: 60px;
              height: 60px;
              top: 40%;
              right: 10%;
              animation-delay: 2s;
            }

            &.shape-3 {
              width: 100px;
              height: 100px;
              bottom: 0;
              left: 30%;
              animation-delay: 4s;
            }
          }
        }

        .brand-icon {
          font-size: 80px;
          filter: drop-shadow(0 10px 20px rgba(0, 0, 0, 0.2));
          animation: pulse 2s ease-in-out infinite;
        }
      }

      h1 {
        font-size: 48px;
        font-weight: 700;
        margin: 0 0 16px;
        text-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
      }

      > p {
        font-size: 20px;
        line-height: 1.6;
        margin: 0 0 40px;
        opacity: 0.9;
      }
    }

    // 背景装饰
    &::before {
      content: "";
      position: absolute;
      top: -50%;
      right: -50%;
      width: 200%;
      height: 200%;
      background: radial-gradient(
        circle,
        rgba(255, 255, 255, 0.1) 0%,
        transparent 70%
      );
      animation: rotate 20s linear infinite;
    }
  }

  // 右侧表单区域
  .login-form-area {
    width: 480px;
    background: white;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: -10px 0 30px rgba(0, 0, 0, 0.05);

    .form-wrapper {
      width: 100%;
      max-width: 380px;
      padding: 40px 20px;
    }
  }
}

// 头部区域
.header {
  margin-bottom: 32px;
  text-align: center;

  h2 {
    font-size: 32px;
    color: #323639;
    margin: 0 0 12px;
    font-weight: 700;
  }

  p {
    color: #6b7280;
    font-size: 16px;
    margin: 0;
    line-height: 1.5;
  }
}

// 登录表单
.el-form {
  width: 100%;
  margin: 24px 0;

  .el-form-item {
    padding-bottom: 0;
    margin-bottom: 20px;

    &.pic {
      display: grid;
      justify-content: center;
      margin-bottom: 24px;
    }
  }

  .el-input {
    height: 44px;

    :deep(.el-input__wrapper) {
      border-radius: 8px;
      box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
    }

    :deep(.el-input__inner) {
      font-size: 16px;
    }
  }
}

// 记住密码行
.el-row {
  margin-bottom: 24px;

  .text {
    height: 32px;
    display: grid;
    align-content: center;
  }

  .el-checkbox {
    color: #374151;
    font-size: 14px;

    :deep(.el-checkbox__input.is-checked + .el-checkbox__label) {
      color: #374151;
    }
  }
}

// 忘记密码链接
.forget-pass {
  color: #3b82f6;
  font-size: 14px;
  font-weight: 500;

  &:hover {
    color: #2563eb;
  }
}

// 登录按钮
.login-button {
  margin-bottom: 24px;

  .el-button {
    width: 100%;
    letter-spacing: 1px;
    font-size: 16px;
    height: 44px;
    margin: 0;
    background: $button-gradient;
    border: none;
    font-weight: 600;

    &:hover {
      background: $button-hover-gradient;
      transform: translateY(-1px);
      box-shadow: 0 10px 15px -3px rgba(59, 130, 246, 0.3);
    }

    &:active {
      transform: translateY(0);
    }
  }
}

// 第三方登录
:deep(.oauth-block) {
  margin: 24px 0;
}

// 注册和访问区域
.register-container,
.visit {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 8px;
}

.register-container {
  margin-top: 24px;

  .register-account {
    color: #6b7280;
    font-size: 14px;
  }

  .register {
    color: #3b82f6;
    font-size: 14px;
    font-weight: 600;

    &:hover {
      color: #2563eb;
    }
  }
}

.visit {
  margin-top: 16px;

  .register {
    color: #6b7280;
    font-size: 14px;
    transition: color 0.2s;

    &:hover {
      color: #3b82f6;
      cursor: pointer;
    }
  }
}

// 动画定义
@keyframes float {
  0%,
  100% {
    transform: translateY(0) rotate(0deg);
  }

  33% {
    transform: translateY(-20px) rotate(120deg);
  }

  66% {
    transform: translateY(20px) rotate(240deg);
  }
}

@keyframes pulse {
  0%,
  100% {
    transform: scale(1);
  }

  50% {
    transform: scale(1.05);
  }
}

@keyframes rotate {
  from {
    transform: rotate(0deg);
  }

  to {
    transform: rotate(360deg);
  }
}

// 响应式设计
@media screen and (max-width: 768px) {
  .login-container {
    flex-direction: column;
    background: white;

    .login-illustration {
      display: none;
    }

    .login-form-area {
      width: 100%;
      box-shadow: none;

      .form-wrapper {
        max-width: 100%;
        padding: 20px;
      }
    }
  }

  .el-form,
  .el-row,
  .login-button,
  .register-container,
  .visit {
    padding: 0 20px;
  }

  .el-form {
    width: 90%;
    margin: 20px 0;
  }

  .header {
    margin-bottom: 24px;

    h2 {
      font-size: 28px;
    }

    p {
      font-size: 16px;
    }
  }
}

@media screen and (max-width: 1024px) and (min-width: 769px) {
  .login-container .login-form-area {
    width: 400px;
  }
}
</style>
