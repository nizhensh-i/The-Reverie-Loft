<script>
import authApi from "@/api/auth/authApi.js";
import { useCurrentUserStore } from "@/stores/user";
import ButtonClick from "@/utils/components/ButtonClick.vue";
import PageHeadBack from "@/utils/components/PageHeadBack.vue";
import PageScroll from "@/utils/components/PageScroll.vue";
export default {
  components: {
    ButtonClick,
    PageHeadBack,
    PageScroll,
  },
  data() {
    return {
      form: {
        email: "",
        code: "",
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
      },
      isEmailValid: false,
      value: "",
      showButton: true,
      loading: false,
      isChange: false,
    };
  },
  setup() {
    const currentUser = useCurrentUserStore();
    return { currentUser };
  },
  computed: {
    isSubmit() {
      return !(this.isEmailValid && this.form.code);
    },
  },
  mounted() {},
  methods: {
    applyCode() {
      this.value = Date.now() + 1000 * 60;
      this.showButton = !this.showButton;
      const loadingInstance = this.$loading({
        lock: true,
        text: "Loading",
        background: "rgba(0, 0, 0, 0.7)",
      });
      authApi
        .applyCode(this.form)
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
    bindEmail() {
      authApi
        .checkCode(this.form)
        .then((res) => {
          if (res.code == 200) {
            this.currentUser.userInfo.confirmed = res.data.isConfirmed;
            this.currentUser.userInfo.roleId = res.data.roleId;
            ElMessage.success("邮箱绑定成功！");
            this.$router.push("/posts");
          } else {
            ElMessage.error(res.message || "邮箱绑定失败");
          }
        })
        .catch((err) => {
          // 如果是因为需要fresh token，catch已经被request.js处理了
          if (err.message !== "该操作需要重新登录以验证身份") {
            ElMessage.error("邮箱绑定失败，请稍后重试");
          }
        });
    },
    submitForm() {
      this.loading = true;
      this.bindEmail();
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
      <div class="email-binding-container">
        <div class="email-header">
          <div class="email-icon">
            <i class="el-icon-message"></i>
          </div>
          <h1>邮箱绑定</h1>
          <p class="subtitle">绑定邮箱可以提高账户安全性，并接收重要通知</p>
        </div>

        <div class="form-card">
          <el-form
            label-position="top"
            label-width="auto"
            :model="form"
            :rules="rules"
            ref="formRef"
          >
            <el-form-item prop="email" label="邮箱地址">
              <div class="input-group">
                <el-input
                  v-model="form.email"
                  placeholder="请输入您的邮箱地址"
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
            </el-form-item>

            <el-form-item>
              <ButtonClick
                content="绑定邮箱"
                type="primary"
                :disabled="isSubmit"
                :loading="loading"
                @do-search="submitForm"
                class="submit-btn"
              />
            </el-form-item>
          </el-form>

          <div class="tips">
            <p><i class="el-icon-info"></i> 绑定邮箱后，您可以：</p>
            <ul>
              <!-- <li>接收系统通知和重要提醒</li> -->
              <li>使用邮箱找回密码</li>
              <li>提高账户安全性</li>
            </ul>
          </div>
        </div>
      </div>
    </PageScroll>
  </PageHeadBack>
</template>

<style lang="scss" scoped>
.email-binding-container {
  max-width: 600px;
  margin: 0 auto;
  padding: 20px 0;
}

.email-header {
  text-align: center;
  margin-bottom: 30px;

  .email-icon {
    background: linear-gradient(135deg, #409eff, #007bff);
    width: 70px;
    height: 70px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto 15px;
    box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);

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

.submit-btn {
  width: 100%;
  margin-top: 10px;
  height: 44px;
  font-size: 16px;
  font-weight: 500;
  border-radius: 6px;
}

.tips {
  margin-top: 25px;
  padding: 15px;
  background: #f0f9ff;
  border-radius: 8px;
  border-left: 4px solid #409eff;

  p {
    color: #303133;
    font-weight: 500;
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    gap: 5px;
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
</style>
