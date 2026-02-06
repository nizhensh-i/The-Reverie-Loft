<script>
import authApi from "@/api/auth/authApi.js";
import ButtonClick from "@/utils/components/ButtonClick.vue";
import PageHeadBack from "@/utils/components/PageHeadBack.vue";

export default {
  components: {
    ButtonClick,
    PageHeadBack,
    PageScroll,
  },
  data() {
    var validatePass = (rule, value, callback) => {
      if (value === "") {
        callback(new Error("请输入密码"));
      } else if (value.length < 3) {
        callback(new Error("密码长度不能少于3个字符"));
      } else {
        callback();
      }
    };
    return {
      form: {
        email: "",
        code: "",
        new_password: "",
      },
      rules: {
        email: [
          { required: true, message: "请输入邮箱地址", trigger: "blur" },
          {
            type: "email",
            message: "请输入正确的邮箱地址",
            trigger: ["blur", "change"],
          },
        ],
        code: [{ required: true, message: "请输入验证码", trigger: "blur" }],
        new_password: [
          { required: true, validator: validatePass, trigger: "blur" },
        ],
      },
      isEmailValid: false,
      value: "",
      showButton: true,
      loading: false,
      isChange: false,
    };
  },
  computed: {
    isSubmit() {
      return !(this.isEmailValid && this.form.code && this.form.new_password);
    },
  },
  methods: {
    applyCode() {
      this.value = Date.now() + 1000 * 60;
      this.showButton = !this.showButton;
      authApi.applyCode({ email: this.form.email }).then((res) => {
        if (res.code == 200) {
          ElMessage.success("验证码已发送");
        } else {
          ElMessage.error("验证码发送失败");
        }
      });
    },
    resetPassword() {
      authApi.resetPassword(this.form).then((res) => {
        if (res.code == 200) {
          ElMessage.success("密码重置成功");
          this.$router.push("/login");
        } else {
          ElMessage.error("密码重置失败");
        }
      });
    },
    submitForm() {
      this.loading = true;
      this.resetPassword();
      this.loading = false;
      this.isChange = false;
    },
    finish() {
      this.showButton = !this.showButton;
    },
    validateEmail() {
      if (this.$refs.formRef) {
        this.$refs.formRef.validateField("email", (errorMessage) => {
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
      <div class="password-reset-container">
        <div class="reset-header">
          <div class="reset-icon">
            <el-icon size="48" color="#409EFF">
              <i-ep-Lock />
            </el-icon>
          </div>
          <h1 class="reset-title">重置您的密码</h1>
          <p class="reset-subtitle">请按照以下步骤重置您的密码</p>
        </div>

        <div class="reset-form-wrapper">
          <el-form
            label-position="top"
            label-width="auto"
            :model="form"
            :rules="rules"
            ref="formRef"
            class="reset-form"
          >
            <div class="form-step" :class="{ 'step-completed': isEmailValid }">
              <div class="step-header">
                <div class="step-number">1</div>
                <div class="step-title">验证邮箱</div>
              </div>
              <el-form-item prop="email" label="邮箱地址">
                <div class="email-input-group">
                  <el-input
                    v-model="form.email"
                    placeholder="请输入您的邮箱地址"
                    size="large"
                    @blur="validateEmail"
                    class="email-input"
                  >
                    <template #prefix>
                      <el-icon><i-ep-Message /></el-icon>
                    </template>
                  </el-input>
                  <el-button
                    @click="applyCode"
                    type="primary"
                    size="large"
                    :disabled="!isEmailValid"
                    v-if="showButton"
                    class="send-code-btn"
                  >
                    发送验证码
                  </el-button>
                  <div v-else class="countdown-wrapper">
                    <el-countdown
                      prefix="重新发送 "
                      suffix=" 秒后可重发"
                      format="ss"
                      :value="value"
                      @finish="finish"
                    />
                  </div>
                </div>
              </el-form-item>
            </div>

            <div class="form-step" :class="{ 'step-completed': form.code }">
              <div class="step-header">
                <div class="step-number">2</div>
                <div class="step-title">输入验证码</div>
              </div>
              <el-form-item prop="code" label="验证码">
                <el-input
                  v-model="form.code"
                  placeholder="请输入6位验证码"
                  size="large"
                  maxlength="6"
                  class="code-input"
                >
                  <template #prefix>
                    <el-icon><i-ep-Key /></el-icon>
                  </template>
                </el-input>
              </el-form-item>
            </div>

            <div
              class="form-step"
              :class="{ 'step-completed': form.new_password }"
            >
              <div class="step-header">
                <div class="step-number">3</div>
                <div class="step-title">设置新密码</div>
              </div>
              <el-form-item prop="new_password" label="新密码">
                <el-input
                  v-model="form.new_password"
                  type="password"
                  show-password
                  placeholder="请输入新密码（至少3个字符）"
                  size="large"
                >
                  <template #prefix>
                    <el-icon><i-ep-Lock /></el-icon>
                  </template>
                </el-input>
              </el-form-item>
            </div>

            <el-form-item class="submit-form-item">
              <ButtonClick
                content="重置密码"
                type="primary"
                :disabled="isSubmit"
                :round="true"
                width="100%"
                :loading="loading"
                @do-search="submitForm"
                class="submit-btn"
              />
            </el-form-item>
          </el-form>
        </div>
      </div>
    </PageScroll>
  </PageHeadBack>
</template>
<style lang="scss" scoped>
.password-reset-container {
  max-width: 500px;
  margin: 0 auto;
  padding: 20px;
}

.reset-header {
  text-align: center;
  margin-bottom: 40px;

  .reset-icon {
    margin-bottom: 20px;
  }

  .reset-title {
    font-size: 28px;
    font-weight: 600;
    color: #303133;
    margin: 0 0 12px;
    line-height: 1.2;
  }

  .reset-subtitle {
    font-size: 16px;
    color: #909399;
    margin: 0;
    line-height: 1.5;
  }
}

.reset-form-wrapper {
  background: #ffffff;
  border-radius: 12px;
  padding: 32px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border: 1px solid #f0f0f0;
}

.reset-form {
  width: 100%;
}

.form-step {
  margin-bottom: 32px;
  padding: 24px;
  border-radius: 8px;
  background: #fafafa;
  border: 2px solid #e4e7ed;
  transition: all 0.3s ease;
  position: relative;
  animation: slideInUp 0.6s ease-out;

  &:last-of-type {
    margin-bottom: 24px;
  }

  &.step-completed {
    background: #f0f9ff;
    border-color: #409eff;
    animation: pulse 0.6s ease-in-out;
  }
}

.step-header {
  display: flex;
  align-items: center;
  margin-bottom: 16px;

  .step-number {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    background: #e4e7ed;
    color: #909399;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 600;
    font-size: 14px;
    margin-right: 12px;
    transition: all 0.3s ease;
  }

  .step-title {
    font-size: 16px;
    font-weight: 600;
    color: #303133;
  }
}

.step-completed .step-number {
  background: #409eff;
  color: white;
}

.step-completed .step-title {
  color: #409eff;
}

.email-input-group {
  display: flex;
  gap: 12px;
  align-items: flex-start;

  .email-input {
    flex: 1;
  }
}

.send-code-btn {
  min-width: 120px;
  height: 40px;
}

.countdown-wrapper {
  min-width: 120px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f7fa;
  border-radius: 4px;
  font-size: 14px;
  color: #909399;
  border: 1px solid #dcdfe6;
}

.code-input {
  max-width: 200px;
}

.submit-form-item {
  margin-bottom: 0;
  margin-top: 32px;
}

.submit-btn {
  height: 48px;
  font-size: 16px;
  font-weight: 600;
}

// Element Plus 组件样式覆盖
:deep(.el-form-item__label) {
  font-weight: 600;
  color: #303133;
  font-size: 14px;
  margin-bottom: 8px;
}

:deep(.el-input__wrapper) {
  border-radius: 8px;
  box-shadow: 0 0 0 1px #dcdfe6;
  transition: all 0.3s ease;

  &:hover {
    box-shadow: 0 0 0 1px #c0c4cc;
  }
}

:deep(.el-input.is-focus .el-input__wrapper) {
  box-shadow: 0 0 0 1px #409eff;
}

:deep(.el-button) {
  border-radius: 8px;
  font-weight: 500;
  transition: all 0.3s ease;

  &:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
  }
}

:deep(.el-countdown) {
  font-size: 14px;
  color: #409eff;
  font-weight: 500;
}

// 响应式设计
@media (max-width: 768px) {
  .password-reset-container {
    padding: 16px;
  }

  .reset-form-wrapper {
    padding: 24px 20px;
  }

  .form-step {
    padding: 20px 16px;
  }

  .email-input-group {
    flex-direction: column;
  }

  .send-code-btn {
    width: 100%;
    margin-top: 8px;
  }

  .countdown-wrapper {
    width: 100%;
    margin-top: 8px;
  }

  .code-input {
    max-width: 100%;
  }
}

// 动画效果
@keyframes slideInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes pulse {
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.02);
  }
  100% {
    transform: scale(1);
  }
}
</style>
