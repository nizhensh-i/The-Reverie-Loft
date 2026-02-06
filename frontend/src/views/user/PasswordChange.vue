<script>
import authApi from "@/api/auth/authApi.js";
import ButtonClick from "@/utils/components/ButtonClick.vue";
import PageHeadBack from "@/utils/components/PageHeadBack.vue";
import PageScroll from "@/utils/components/PageScroll.vue";
import { useCurrentUserStore } from "@/stores/user";
import { ElLoading } from "element-plus";

export default {
  components: {
    ButtonClick,
    PageHeadBack,
    PageScroll,
  },
  data() {
    var validateOldPassword = (rule, value, callback) => {
      if (!value) {
        callback(new Error("请输入原密码"));
      } else {
        callback();
      }
    };

    var validateNewPassword = (rule, value, callback) => {
      if (!value) {
        callback(new Error("请输入新密码"));
      } else if (value.length < 3) {
        callback(new Error("新密码长度不能少于3个字符"));
      } else {
        callback();
      }
    };

    var validateConfirmPassword = (rule, value, callback) => {
      if (value !== this.form.new_password) {
        callback(new Error("两次密码不一致"));
      } else {
        callback();
      }
    };

    return {
      form: {
        old_password: "",
        new_password: "",
        confirmNewPassword: "",
      },
      rules: {
        old_password: [
          { required: true, validator: validateOldPassword, trigger: "blur" },
        ],
        new_password: [
          { required: true, validator: validateNewPassword, trigger: "blur" },
        ],
        confirmNewPassword: [
          {
            required: true,
            validator: validateConfirmPassword,
            trigger: "blur",
          },
        ],
      },
      loading: false,
      isChange: false,
      // 新增状态标记
      isCheckingFreshness: true,
      allowOperation: false,
      // 是否显示旧密码输入框（根据token新鲜度）
      showOldPassword: true,
    };
  },
  setup() {
    const currentUser = useCurrentUserStore();
    return { currentUser };
  },
  watch: {
    form: {
      deep: true,
      handler() {
        this.isChange = true;
      },
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
          // token是新鲜的，不需要输入旧密码
          this.showOldPassword = false;
          // 从rules中移除old_password验证（Vue 3使用原生delete）
          delete this.rules.old_password;
        } else {
          // token不新鲜，需要输入旧密码
          this.showOldPassword = true;
          await this.showReauthConfirmDialog();
        }
      } catch (error) {
        // 已经过期或令牌无效,统一处理为需要重新登录
        this.showOldPassword = true;
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

    submitForm() {
      if (!this.allowOperation) {
        this.showReauthConfirmDialog();
        return;
      }

      this.$refs.form.validate((valid) => {
        if (valid) {
          this.loading = true;
          const params = {
            new_password: this.form.new_password,
          };
          // 如果显示了旧密码输入框，才添加旧密码参数
          if (this.showOldPassword) {
            params.old_password = this.form.old_password;
          }
          authApi
            .changePassword(params)
            .then((res) => {
              this.loading = false;
              this.isChange = false;
              if (res.code == 200) {
                ElMessage.success("修改密码成功");
                this.log_out();
              } else {
                ElMessage.error(res.message || "修改密码失败");
              }
            })
            .catch((err) => {
              this.loading = false;
              // 如果是因为需要fresh token，catch已经被request.js处理了
              if (err.message !== "该操作需要重新登录以验证身份") {
                ElMessage.error("修改密码失败，请稍后重试");
              }
            });
        } else {
          ElMessage.error("请修正表单中的错误");
        }
      });
    },
    log_out() {
      this.currentUser.logOut();
      this.$router.push("/login");
    },
  },
};
</script>

<template>
  <PageHeadBack>
    <PageScroll max-height="calc(100vh - 45px - 47px)">
      <div v-if="isCheckingFreshness" class="loading-state"></div>

      <div v-else class="password-change-container">
        <div class="password-header">
          <div class="password-icon">
            <i class="el-icon-lock"></i>
          </div>
          <h1>修改密码</h1>
          <p class="subtitle">定期更换密码可以提高您的账户安全性</p>
        </div>

        <div class="form-card">
          <el-form
            :model="form"
            label-position="top"
            :rules="rules"
            ref="form"
            label-width="auto"
          >
            <el-form-item
              v-if="showOldPassword"
              prop="old_password"
              label="当前密码"
            >
              <el-input
                v-model="form.old_password"
                type="password"
                show-password
                prefix-icon="el-icon-key"
                placeholder="请输入当前密码"
              />
            </el-form-item>

            <div v-if="showOldPassword" class="divider">
              <span><i class="el-icon-refresh"></i> 设置新密码</span>
            </div>

            <el-form-item prop="new_password" label="新密码">
              <el-input
                v-model="form.new_password"
                type="password"
                show-password
                prefix-icon="el-icon-lock"
                placeholder="请输入新密码"
              />
              <div class="password-strength" v-if="form.new_password">
                <div class="strength-label">密码强度:</div>
                <div class="strength-meter">
                  <div
                    class="strength-bar"
                    :class="[
                      form.new_password.length < 6
                        ? 'weak'
                        : form.new_password.length < 10
                        ? 'medium'
                        : 'strong',
                    ]"
                    :style="{
                      width: `${Math.min(100, form.new_password.length * 10)}%`,
                    }"
                  ></div>
                </div>
                <div
                  class="strength-text"
                  :class="[
                    form.new_password.length < 6
                      ? 'weak-text'
                      : form.new_password.length < 10
                      ? 'medium-text'
                      : 'strong-text',
                  ]"
                >
                  {{
                    form.new_password.length < 6
                      ? "弱"
                      : form.new_password.length < 10
                      ? "中"
                      : "强"
                  }}
                </div>
              </div>
            </el-form-item>

            <el-form-item prop="confirmNewPassword" label="确认新密码">
              <el-input
                v-model="form.confirmNewPassword"
                type="password"
                show-password
                prefix-icon="el-icon-check"
                placeholder="请再次输入新密码"
              />
            </el-form-item>

            <el-form-item>
              <ButtonClick
                content="更新密码"
                type="primary"
                :disabled="!isChange || !allowOperation"
                :loading="loading"
                @do-search="submitForm"
                class="submit-btn"
              />
            </el-form-item>
          </el-form>

          <div class="password-tips">
            <h4><i class="el-icon-info-filled"></i> 密码安全提示</h4>
            <ul>
              <!-- <li>使用至少8个字符的密码</li> -->
              <li>混合使用字母、数字和特殊字符</li>
              <li>避免使用容易猜到的信息，如生日或姓名</li>
              <li>定期更换密码以提高安全性</li>
            </ul>
          </div>
        </div>
      </div>
    </PageScroll>
  </PageHeadBack>
</template>

<style lang="scss" scoped>
.password-change-container {
  max-width: 600px;
  margin: 0 auto;
  padding: 20px 0;
}

.password-header {
  text-align: center;
  margin-bottom: 30px;

  .password-icon {
    background: linear-gradient(135deg, #67c23a, #409eff);
    width: 70px;
    height: 70px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto 15px;
    box-shadow: 0 4px 12px rgba(103, 194, 58, 0.3);

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

.divider {
  position: relative;
  height: 20px;
  text-align: center;
  margin: 20px 0;
  border-bottom: 1px solid #ebeef5;

  span {
    position: relative;
    top: 10px;
    background: white;
    padding: 0 10px;
    color: #909399;
    font-size: 14px;
    display: inline-flex;
    align-items: center;
    gap: 5px;
  }
}

.password-strength {
  margin-top: 10px;
  display: flex;
  align-items: center;
  gap: 10px;

  .strength-label {
    font-size: 12px;
    color: #909399;
    width: 60px;
  }

  .strength-meter {
    flex: 1;
    height: 6px;
    background: #ebeef5;
    border-radius: 3px;
    overflow: hidden;

    .strength-bar {
      height: 100%;
      transition: width 0.3s, background-color 0.3s;

      &.weak {
        background-color: #f56c6c;
      }

      &.medium {
        background-color: #e6a23c;
      }

      &.strong {
        background-color: #67c23a;
      }
    }
  }

  .strength-text {
    font-size: 12px;
    font-weight: bold;
    width: 20px;

    &.weak-text {
      color: #f56c6c;
    }

    &.medium-text {
      color: #e6a23c;
    }

    &.strong-text {
      color: #67c23a;
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

.password-tips {
  margin-top: 25px;
  padding: 15px;
  background: #f0f9eb;
  border-radius: 8px;
  border-left: 4px solid #67c23a;

  h4 {
    color: #303133;
    font-weight: 500;
    margin: 0 0 10px;
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

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 300px;
}
</style>
