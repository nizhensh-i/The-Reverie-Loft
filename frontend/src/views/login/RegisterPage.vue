<template>
  <PageHeadBack>
    <div class="container">
      <div class="header">
        <h2>创建账号 ✨</h2>
        <p>加入我们，开启您的创作之旅</p>
      </div>

      <el-form
        :model="ruleForm"
        status-icon
        :rules="rules"
        ref="ruleForm"
        style="max-width: 600px"
      >
        <el-form-item prop="user">
          <el-input
            type="text"
            v-model="ruleForm.user"
            autocomplete="off"
            size="large"
            placeholder="用户名"
          ></el-input>
        </el-form-item>
        <el-form-item prop="password">
          <el-input
            type="password"
            v-model="ruleForm.password"
            autocomplete="off"
            show-password
            size="large"
            placeholder="密码"
          ></el-input>
        </el-form-item>
        <el-form-item prop="confirmPass">
          <el-input
            type="password"
            v-model="ruleForm.confirmPass"
            autocomplete="off"
            show-password
            size="large"
            placeholder="确认密码"
          ></el-input>
        </el-form-item>

        <div class="security-info">
          <el-icon><i-ep-Lock /></el-icon>
          <span>密码通过加密签名(SHA-256)保护</span>
        </div>

        <el-form-item>
          <el-button
            type="primary"
            round
            :disabled="!isChange"
            :loading="loading"
            @click="register"
            >创建账号</el-button
          >
        </el-form-item>
      </el-form>

      <div class="login-container">
        <el-text class="login-account">已有账号?</el-text>
        <el-link class="login" @click="$router.push('/login')"
          >立即登录</el-link
        >
      </div>
    </div>
  </PageHeadBack>
</template>

<script>
import authApi from "@/api/auth/authApi.js";
import confetti from "canvas-confetti";
import PageHeadBack from "@/utils/components/PageHeadBack.vue";
import imageCfg from "@/config/image.js";

export default {
  components: {
    PageHeadBack,
  },
  name: "RegisterPage",
  data() {
    const validateUser = (rule, value, callback) => {
      const reg = /^[a-zA-Z0-9_@.\-]{3,16}$/;
      if (value === "") {
        callback(new Error("请输入用户名"));
      } else if (value.length < 3) {
        callback(new Error("账号长度不能少于3个字符"));
      } else if (!reg.test(value)) {
        callback(new Error("账号只能包含大小写字母、数字和_@.-字符"));
      } else {
        callback();
      }
    };
    const validatePass = (rule, value, callback) => {
      const reg = /^[a-zA-Z0-9_@.\-]{3,16}$/;
      if (value === "") {
        callback(new Error("请输入密码"));
      } else if (value.length < 3) {
        callback(new Error("密码长度应该在3到16个字符之间"));
      } else if (!reg.test(value)) {
        callback(new Error("密码只能包含大小写字母、数字和_@.-字符"));
      } else {
        callback();
      }
    };
    const validateConfirmPass = (rule, value, callback) => {
      if (value !== this.ruleForm.password) {
        callback(new Error("两次密码不一致"));
      } else {
        callback();
      }
    };
    return {
      ruleForm: {
        user: "",
        password: "",
        confirmPass: "",
        email: "",
      },
      rules: {
        user: [{ required: true, validator: validateUser, trigger: "blur" }],
        password: [
          { required: true, validator: validatePass, trigger: "blur" },
        ],
        confirmPass: [
          { required: true, validator: validateConfirmPass, trigger: "blur" },
        ],
      },
      isChange: false,
      loading: false,
    };
  },
  watch: {
    ruleForm: {
      deep: true,
      handler() {
        this.isChange = true;
      },
    },
  },
  methods: {
    // 封装验证方法为 Promise
    validateForm() {
      return new Promise((resolve) => {
        this.$refs.ruleForm.validate((valid) => {
          resolve(valid);
        });
      });
    },
    async register() {
      const valid = await this.validateForm();
      if (valid) {
        this.loading = true;
        authApi
          .register({
            email: this.ruleForm.email,
            username: this.ruleForm.user,
            password: this.ruleForm.password,
          })
          .then((res) => {
            this.loading = false;
            // 适配新的统一接口返回格式
            if (res.code === 200) {
              this.congratulation();
              ElMessage.success(res.message || "注册成功");
              setTimeout(() => {
                this.$router.push({
                  path: "/login",
                  query: {
                    username: this.ruleForm.user,
                  },
                  hash: false,
                });
              }, 700);
            } else {
              ElMessage.error(res.message || "注册失败");
            }
          })
          .catch((error) => {
            this.loading = false;
            ElMessage.error(error.message || "注册失败，请稍后重试");
          });
      } else {
        ElMessage.error("请修正表单中的错误");
      }
    },
    congratulation() {
      confetti({
        particleCount: 100,
        spread: 70,
        origin: { y: 0.6 },
      });
    },
  },
};
</script>

<style lang="scss" scoped>
* {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
    "Helvetica Neue", Arial, "Noto Sans", sans-serif, "Apple Color Emoji",
    "Segoe UI Emoji", "Segoe UI Symbol", "Noto Color Emoji";
  font-size: 14px;
  -webkit-tap-highlight-color: transparent;
}
.container {
  padding: 0 20px;
}

.header {
  margin: 5vh 0 2rem;

  h2 {
    font-size: 30px;
    color: #323639;
    margin: 0 0 12px;
  }

  p {
    color: #71717a;
  }
}

.el-form {
  width: 95%;

  .el-form-item {
    padding-bottom: 0.8rem;
  }

  .el-input {
    height: 38px;

    :deep(.el-input__wrapper) {
      border-radius: 7px;
    }
  }

  .el-button {
    width: 95%;
    letter-spacing: 2px;
    margin-left: 9px;
    margin-top: 1rem;
  }
}

.security-info {
  display: flex;
  align-items: center;
  color: #71717a;
  font-size: 0.9rem;
  margin-bottom: 1rem;

  .el-icon {
    margin-right: 8px;
    font-size: 16px;
  }
}

.login-container {
  width: 95%;
  display: flex;
  justify-content: center;
  margin-top: 3vh;

  .login-account {
    color: #323639;
  }

  .login {
    color: #006be6;
  }
}
</style>
