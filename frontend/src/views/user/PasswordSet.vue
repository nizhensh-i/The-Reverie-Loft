<script>
import authApi from "@/api/auth/authApi.js";
import ButtonClick from "@/utils/components/ButtonClick.vue";
import PageHeadBack from "@/utils/components/PageHeadBack.vue";
import PageScroll from "@/utils/components/PageScroll.vue";
import { useCurrentUserStore } from "@/stores/user";

export default {
  components: {
    ButtonClick,
    PageHeadBack,
    PageScroll,
  },
  data() {
    var validateNewPassword = (rule, value, callback) => {
      if (!value) {
        callback(new Error("请输入新密码"));
      } else if (value.length < 3) {
        callback(new Error("密码长度不能少于3个字符"));
      } else {
        callback();
      }
    };

    var validateConfirmPassword = (rule, value, callback) => {
      if (value !== this.form.new_password) {
        callback(new Error("两次输入的密码不一致"));
      } else {
        callback();
      }
    };

    return {
      form: {
        new_password: "",
        confirm_password: "",
      },
      rules: {
        new_password: [
          { required: true, validator: validateNewPassword, trigger: "blur" },
        ],
        confirm_password: [
          {
            required: true,
            validator: validateConfirmPassword,
            trigger: "blur",
          },
        ],
      },
      loading: false,
      isChange: false,
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
  methods: {
    submitForm() {
      this.$refs.form.validate((valid) => {
        if (valid) {
          this.loading = true;
          authApi
            .setPassword({ new_password: this.form.new_password })
            .then((res) => {
              this.loading = false;
              this.isChange = false;
              if (res.code == 200) {
                ElMessage.success("密码设置成功，请使用新密码重新登录");
                this.logout();
              } else {
                ElMessage.error(res.message || "设置密码失败");
              }
            })
            .catch((err) => {
              this.loading = false;
              ElMessage.error("设置密码失败，请稍后重试");
            });
        } else {
          ElMessage.error("请检查表单填写");
        }
      });
    },
    logout() {
      this.currentUser.logOut();
      this.$router.push("/login");
    },
  },
};
</script>

<template>
  <PageHeadBack>
    <PageScroll max-height="calc(100vh - 45px - 47px)">
      <div class="password-set-container">
        <div class="password-header">
          <div class="password-icon">
            <i class="el-icon-lock"></i>
          </div>
          <h1>设置登录密码</h1>
          <p class="subtitle">设置密码后，您可以使用账号密码登录</p>
        </div>

        <div class="form-card">
          <el-form
            :model="form"
            label-position="top"
            :rules="rules"
            ref="form"
            label-width="auto"
          >
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

            <el-form-item prop="confirm_password" label="确认密码">
              <el-input
                v-model="form.confirm_password"
                type="password"
                show-password
                prefix-icon="el-icon-check"
                placeholder="请再次输入新密码"
              />
            </el-form-item>

            <el-form-item>
              <ButtonClick
                content="设置密码"
                type="primary"
                :disabled="!isChange"
                :loading="loading"
                @do-search="submitForm"
                class="submit-btn"
              />
            </el-form-item>
          </el-form>

          <div class="password-tips">
            <h4><i class="el-icon-info-filled"></i> 密码安全提示</h4>
            <ul>
              <li>密码长度至少3个字符</li>
              <li>建议混合使用字母、数字和特殊字符</li>
              <li>避免使用容易猜到的信息</li>
            </ul>
          </div>
        </div>
      </div>
    </PageScroll>
  </PageHeadBack>
</template>

<style scoped>
.password-set-container {
  max-width: 600px;
  margin: 0 auto;
  padding: 20px 0;
}

.password-header {
  text-align: center;
  margin-bottom: 30px;
}

.password-icon {
  background: linear-gradient(135deg, #409eff, #67c23a);
  width: 70px;
  height: 70px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 15px;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
}

.password-icon i {
  font-size: 32px;
  color: white;
}

.password-header h1 {
  margin: 10px 0;
  font-size: 28px;
  color: #303133;
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

.password-strength {
  margin-top: 10px;
  display: flex;
  align-items: center;
  gap: 10px;
}

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
}

.strength-bar {
  height: 100%;
  transition: width 0.3s, background-color 0.3s;
}

.strength-bar.weak {
  background-color: #f56c6c;
}

.strength-bar.medium {
  background-color: #e6a23c;
}

.strength-bar.strong {
  background-color: #67c23a;
}

.strength-text {
  font-size: 12px;
  font-weight: bold;
  width: 20px;
}

.weak-text {
  color: #f56c6c;
}

.medium-text {
  color: #e6a23c;
}

.strong-text {
  color: #67c23a;
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
}

.password-tips h4 {
  color: #303133;
  font-weight: 500;
  margin: 0 0 10px;
  display: flex;
  align-items: center;
  gap: 5px;
}

.password-tips ul {
  padding-left: 20px;
  margin: 8px 0 0;
}

.password-tips li {
  color: #606266;
  margin-bottom: 5px;
  font-size: 13px;
}
</style>
