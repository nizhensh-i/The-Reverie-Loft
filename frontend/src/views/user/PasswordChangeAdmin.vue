<script>
import authApi from "@/api/auth/authApi.js";
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
    var validatePass = (rule, value, callback) => {
      if (value === "") {
        callback(new Error("请输入新密码"));
      } else if (value.length < 3) {
        callback(new Error("新密码长度不能少于3个字符"));
      } else {
        callback();
      }
    };
    var validateConfirmPass = (rule, value, callback) => {
      if (value !== this.form.newPassword) {
        callback(new Error("两次密码不一致"));
      } else {
        callback();
      }
    };
    return {
      form: {
        username: "",
        newPassword: "",
        confirmNewPassword: "",
      },
      rules: {
        username: [
          { required: true, message: "请输入用户账号", trigger: "blur" },
        ],
        newPassword: [
          { required: true, validator: validatePass, trigger: "blur" },
        ],
        confirmNewPassword: [
          { required: true, validator: validateConfirmPass, trigger: "blur" },
        ],
      },
      loading: false,
      isChange: false,
      dialogShow: false,
    };
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
          this.dialogShow = true;
        } else {
          ElMessage.error("请修正表单中的错误");
        }
      });
    },
    beforeClose(action) {
      if (action !== "confirm") {
        return Promise.resolve(true);
      } else {
        return authApi.helpChangePassword(this.form).then((res) => {
          this.isChange = false;
          if (res.code == 200) {
            ElMessage.success("该用户密码修改成功");
          } else {
            ElMessage.error("该用户密码修改失败");
          }
          return res;
        });
      }
    },
  },
};
</script>

<template>
  <PageHeadBack>
    <PageScroll max-height="calc(100vh - 45px - 47px)">
      <h1>找回其他用户密码</h1>
      <el-form
        :model="form"
        label-position="top"
        :rules="rules"
        ref="form"
        label-width="auto"
        style="max-width: 600px"
      >
        <el-form-item prop="username" label="用户账号">
          <el-input v-model="form.username" />
        </el-form-item>
        <el-form-item prop="newPassword" label="新密码">
          <el-input v-model="form.newPassword" type="password" show-password />
        </el-form-item>
        <el-form-item prop="confirmNewPassword" label="确认新密码">
          <el-input
            v-model="form.confirmNewPassword"
            type="password"
            show-password
          />
        </el-form-item>
        <el-form-item>
          <ButtonClick
            content="提交"
            type="primary"
            :disabled="!isChange"
            :loading="loading"
            @do-search="submitForm"
          />
        </el-form-item>
      </el-form>

      <van-dialog
        v-model:show="dialogShow"
        title="修改用户的密码？"
        width="230"
        show-cancel-button
        confirm-button-color="red"
        :beforeClose="beforeClose"
      />
    </PageScroll>
  </PageHeadBack>
</template>
<style scoped></style>
