<script>
import authApi from "@/api/auth/authApi.js";
import ButtonClick from "@/utils/components/ButtonClick.vue";
import PageHeadBack from "@/utils/components/PageHeadBack.vue";
import PageScroll from "@/utils/components/PageScroll.vue";
import { ElLoading } from "element-plus";

export default {
  components: {
    ButtonClick,
    PageHeadBack,
    PageScroll,
  },
  data() {
    return {
      form: {
        new_email: "",
        code: "",
        password: "",
      },
      rules: {
        new_email: [
          { required: true, message: "请输入邮箱地址", trigger: "blur" },
          {
            type: "email",
            message: "请输入正确的邮箱地址",
            trigger: ["blur", "change"],
          },
        ],
        code: [{ required: true, message: "请输入验证码", trigger: "blur" }],
        password: [{ required: true, message: "请输入密码", trigger: "blur" }],
      },
      isEmailValid: false,
      value: "",
      showButton: true,
      loading: false,
      isChange: false,
      // 新增状态标记
      isCheckingFreshness: true,
      allowOperation: false,
    };
  },
  computed: {
    isSubmit() {
      return !(this.isEmailValid && this.form.code && this.form.password);
    },
  },
  async mounted() {
    // 页面进入时立即检测令牌新鲜度
    await this.checkTokenFreshnessOnEnter();
  },
  methods: {
    async checkTokenFreshnessOnEnter() {
      this.isCheckingFreshness = true;
      const loading = ElLoading.service({
        lock: true,
        text: "正在验证您的身份...",
        background: "rgba(0, 0, 0, 0.7)",
      });
      try {
        const res = await authApi.checkTokenFreshness();
        if (res.code === 200) {
          this.allowOperation = true;
        } else {
          await this.showReauthConfirmDialog();
        }
      } catch (error) {
        await this.showReauthConfirmDialog();
      } finally {
        // 确保至少显示1秒加载状态,避免页面闪烁
        setTimeout(() => {
          loading.close();
          this.isCheckingFreshness = false;
        }, 1000);
      }
    },

    async showReauthConfirmDialog() {
      try {
        await showConfirmDialog({
          title: "提示",
          message: "为确保账户安全,请重新登录后继续操作",
          width: "280px",
        });
        // 用户点击确认
        this.currentUser.logOut();
        this.$router.push("/login");
      } catch (error) {
        // 用户点击取消,返回上一页
        this.$router.back();
      }
    },

    async applyCode() {
      // 发送验证码前额外检测令牌新鲜度(兜底策略)
      try {
        const res = await authApi.checkTokenFreshness();
        if (res.code !== 200) {
          await this.showReauthConfirmDialog();
          return;
        }
      } catch (error) {
        await this.showReauthConfirmDialog();
        return;
      }
      this.value = Date.now() + 1000 * 60;
      this.showButton = !this.showButton;
      const loadingInstance = this.$loading({
        lock: true,
        text: "Loading",
        background: "rgba(0, 0, 0, 0.7)",
      });
      authApi
        .applyCode({ email: this.form.new_email })
        .then((res) => {
          if (res.code == 200) {
            ElMessage.success("验证码已发送");
          } else {
            ElMessage.error("验证码发送失败");
          }
          loadingInstance.close();
        })
        .catch(() => {
          ElMessage.error("网络错误，请稍后再试");
          loadingInstance.close();
        });
    },
    changeEmail() {
      if (!this.allowOperation) {
        this.showReauthConfirmDialog();
        return;
      }

      authApi
        .changeEmail(this.form)
        .then((res) => {
          if (res.code == 200) {
            ElMessage.success("邮箱更换成功!");
            this.$router.push("/posts");
          } else {
            ElMessage.error(res.message || "邮箱更换失败");
          }
        })
        .catch((err) => {
          // 如果是因为需要fresh token，catch已经被request.js处理了
          if (err.message !== "该操作需要重新登录以验证身份") {
            ElMessage.error("邮箱更换失败，请稍后重试");
          }
        });
    },
    submitForm() {
      this.loading = true;
      this.changeEmail();
      this.loading = false;
      this.isChange = false;
    },
    finish() {
      this.showButton = !this.showButton;
    },
    validateEmail() {
      if (this.$refs.formRef) {
        this.$refs.formRef.validateField("new_email", (errorMessage) => {
          this.isEmailValid = errorMessage;
        });
      }
    },
  },
};
</script>

<template>
  <PageHeadBack>
    <PageScroll max-height="calc(100vh - 45px - 47px)">
      <!-- 加载状态 -->
      <div v-if="isCheckingFreshness" class="loading-state"></div>

      <!-- 主表单 -->
      <div v-else class="email-change-container">
        <div class="email-header">
          <div class="email-icon">
            <i class="el-icon-refresh"></i>
          </div>
          <h1>更换邮箱地址</h1>
          <p class="subtitle">更新您的联系方式，保持信息畅通</p>
        </div>

        <div class="form-card">
          <div class="steps-container">
            <div class="step active">
              <div class="step-number">1</div>
              <div class="step-text">填写新邮箱</div>
            </div>
            <div class="step-line"></div>
            <div class="step" :class="{ active: form.new_email && form.code }">
              <div class="step-number">2</div>
              <div class="step-text">验证身份</div>
            </div>
            <div class="step-line"></div>
            <div class="step" :class="{ active: !isSubmit }">
              <div class="step-number">3</div>
              <div class="step-text">完成更换</div>
            </div>
          </div>

          <el-form
            label-position="top"
            label-width="auto"
            :model="form"
            :rules="rules"
            ref="formRef"
          >
            <el-form-item prop="new_email" label="新的邮箱地址">
              <div class="input-group">
                <el-input
                  v-model="form.new_email"
                  placeholder="请输入新的邮箱地址"
                  @blur="validateEmail"
                  prefix-icon="el-icon-message"
                />
                <div class="code-button">
                  <el-button
                    @click="applyCode"
                    type="primary"
                    :disabled="!isEmailValid"
                    v-if="showButton"
                    class="send-code-btn"
                  >
                    发送验证码
                  </el-button>
                  <el-countdown
                    prefix="重新发送"
                    format="ss秒"
                    :value="value"
                    @finish="finish"
                    v-else
                    class="countdown"
                  />
                </div>
              </div>
            </el-form-item>

            <el-form-item prop="code" label="验证码">
              <el-input
                v-model="form.code"
                placeholder="请输入收到的验证码"
                prefix-icon="el-icon-key"
              />
              <div class="verification-hint">
                验证码已发送至您的新邮箱，请查收
              </div>
            </el-form-item>

            <div class="security-section">
              <div class="security-header">
                <i class="el-icon-lock"></i>
                <span>安全验证</span>
              </div>
              <el-form-item prop="password" label="当前账户密码">
                <el-input
                  v-model="form.password"
                  type="password"
                  show-password
                  prefix-icon="el-icon-lock"
                  placeholder="请输入当前账户密码"
                />
              </el-form-item>
            </div>

            <el-form-item>
              <ButtonClick
                content="确认更换邮箱"
                type="primary"
                :disabled="isSubmit"
                :loading="loading"
                @do-search="submitForm"
                class="submit-btn"
              />
            </el-form-item>
          </el-form>

          <div class="notice">
            <div class="notice-title">
              <i class="el-icon-warning"></i>
              <span>注意事项</span>
            </div>
            <ul>
              <!-- <li>更换邮箱后，系统通知将发送至新邮箱</li> -->
              <li>新邮箱将用于密码找回等安全操作</li>
              <li>请确保新邮箱真实有效且为您本人所有</li>
            </ul>
          </div>
        </div>
      </div>
    </PageScroll>
  </PageHeadBack>
</template>

<style lang="scss" scoped>
.email-change-container {
  max-width: 600px;
  margin: 0 auto;
  padding: 20px 0;
}

.email-header {
  text-align: center;
  margin-bottom: 30px;

  .email-icon {
    background: linear-gradient(135deg, #e6a23c, #f56c6c);
    width: 70px;
    height: 70px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto 15px;
    box-shadow: 0 4px 12px rgba(230, 162, 60, 0.3);

    i {
      font-size: 32px;
      color: white;
    }
  }

  h1 {
    margin: 10px 0;
    font-size: 28px;
    color: #303133;
  }
}

.subtitle {
  color: #606266;
  font-size: 14px;
  margin-bottom: 20px;
}

.form-card {
  background: white;
  border-radius: 12px;
  padding: 30px;
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.08);
}

.steps-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 30px;

  .step {
    display: flex;
    flex-direction: column;
    align-items: center;
    width: 80px;

    .step-number {
      width: 30px;
      height: 30px;
      border-radius: 50%;
      background-color: #ebeef5;
      color: #909399;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: bold;
      margin-bottom: 8px;
      transition: all 0.3s;
    }

    .step-text {
      font-size: 12px;
      color: #909399;
      text-align: center;
      transition: all 0.3s;
    }

    &.active .step-number {
      background-color: #409eff;
      color: white;
    }

    &.active .step-text {
      color: #409eff;
      font-weight: 500;
    }
  }

  .step-line {
    flex: 1;
    height: 2px;
    background-color: #ebeef5;
    margin: 0 10px 20px;
  }
}

.input-group {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.code-button {
  display: flex;
  justify-content: flex-end;
}

.send-code-btn {
  width: 100%;
  border-radius: 6px;
  font-weight: 500;
}

.countdown {
  width: 100%;
  text-align: center;
  padding: 10px 0;
  background: #f5f7fa;
  border-radius: 6px;

  :deep(.el-statistic__content) {
    font-size: 14px;
    color: #909399;
    font-weight: 500;
  }
}

.verification-hint {
  margin-top: 5px;
  font-size: 12px;
  color: #909399;
  padding-left: 5px;
}

.security-section {
  margin: 20px 0;
  padding: 20px;
  background: #f9f9f9;
  border-radius: 8px;
  border: 1px dashed #dcdfe6;

  .security-header {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 15px;
    color: #606266;
    font-weight: 500;

    i {
      color: #f56c6c;
    }
  }
}

.submit-btn {
  width: 100%;
  margin-top: 10px;
  height: 44px;
  font-size: 16px;
  font-weight: 500;
  border-radius: 6px;
}

.notice {
  margin-top: 25px;
  padding: 15px;
  background: #fff9f9;
  border-radius: 8px;
  border-left: 4px solid #f56c6c;

  .notice-title {
    display: flex;
    align-items: center;
    gap: 8px;
    color: #f56c6c;
    font-weight: 500;
    margin-bottom: 10px;
  }

  ul {
    padding-left: 20px;
    margin: 8px 0 0;

    li {
      color: #606266;
      margin-bottom: 5px;
      font-size: 13px;
    }
  }
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 300px;
}
</style>
