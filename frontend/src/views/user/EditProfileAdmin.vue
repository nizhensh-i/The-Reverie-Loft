<script>
import editApi from "@/api/user/editApi.js";
import userApi from "@/api/user/userApi.js";
import imageApi from "@/api/user/imageApi.js";
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
      formLabelAlign: {
        email: "",
        username: "",
        confirmed: "",
        role: "",
        name: "",
        location: "",
        about_me: "",
        image: "",
      },
      user: {},
      userId: -1,
      roles: [
        {
          value: 1,
          label: "普通用户",
        },
        {
          value: 2,
          label: "内容协调员",
        },
        {
          value: 3,
          label: "管理员",
        },
      ],
      confirm: [
        {
          value: false,
          label: "未认证",
        },
        {
          value: true,
          label: "已认证",
        },
      ],
      originalForm: {},
      loading: false,
      isChange: false,
      dialogShow: false,
    };
  },
  beforeRouteEnter(to, from, next) {
    next((vm) => {
      vm.userId = to.params.id;
      vm.getUserInfo(vm.userId);
      vm.$nextTick(() => {});
    });
  },
  watch: {
    formLabelAlign: {
      deep: true,
      handler(newVal) {
        this.isChange = JSON.stringify(newVal) !== this.originalForm;
      },
    },
  },
  methods: {
    getUserInfo(userId) {
      userApi.getUser(userId).then((res) => {
        if (res.code == 200) {
          this.user = res.data;
          this.originalForm = JSON.stringify(res.data);
          this.formLabelAlign = res.data;
        }
      });
    },
    submit() {
      this.loading = true;
      editApi.editProfileAdmin(this.formLabelAlign).then((res) => {
        this.loading = false;
        this.isChange = false;
        if (res.code == 200) {
          ElMessage.success("修改成功");
          this.$router.push(`/user/${this.formLabelAlign.username}`);
        } else {
          ElMessage.error("修改失败");
        }
      });
    },
    resetToDefaultAvatar() {
      this.dialogShow = true;
    },

    beforeReset(action) {
      if (action !== "confirm") {
        return Promise.resolve(true);
      } else {
        return imageApi
          .saveImageUrl(this.formLabelAlign.id, {
            image: "",
          })
          .then((res) => {
            if (res.code === 200) {
              this.formLabelAlign.image = res.data.image;
              ElMessage.success("已设置为随机头像");
            } else {
              ElMessage.error(res.message || "操作失败");
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
      <div
        style="
          display: flex;
          align-items: center;
          gap: 20px;
          margin-bottom: 20px;
        "
      >
        <div style="display: flex; align-items: center; gap: 16px">
          <el-avatar
            :src="formLabelAlign.image"
            :size="80"
            style="border: 2px solid #e4e7ed"
          />
          <div>
            <div style="font-weight: bold; margin-bottom: 4px">用户头像</div>
            <div style="font-size: 12px; color: #909399">
              当前用户：{{ formLabelAlign.nickname || formLabelAlign.username }}
            </div>
          </div>
        </div>
        <div style="display: flex; gap: 8px">
          <el-upload
            ref="avatarUpload"
            action=""
            :show-file-list="false"
            :before-upload="beforeAvatarUpload"
            :http-request="uploadAvatar"
            accept="image/*"
          >
            <!-- <el-button type="primary" size="small" :loading="avatarLoading">
            上传头像
          </el-button> -->
          </el-upload>
          <el-button type="danger" size="small" @click="resetToDefaultAvatar">
            恢复默认图像
          </el-button>
        </div>
      </div>
      <el-form
        :model="formLabelAlign"
        ref="formLabelAlign"
        label-position="top"
        label-width="auto"
        style="max-width: 600px"
      >
        <el-form-item
          prop="email"
          label="邮件"
          :rules="[
            {
              type: 'email',
              message: '请输入正确的邮件地址',
              trigger: ['blur', 'change'],
            },
          ]"
        >
          <el-input v-model="formLabelAlign.email" />
        </el-form-item>
        <el-form-item label="用户名">
          <el-input v-model="formLabelAlign.username" />
        </el-form-item>
        <el-form-item label="认证状态">
          <el-select
            v-model="formLabelAlign.confirmed"
            placeholder="Select"
            style="width: 240px"
          >
            <el-option
              v-for="item in confirm"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="角色">
          <el-select
            v-model="formLabelAlign.roleId"
            placeholder="Select"
            style="width: 240px"
          >
            <el-option
              v-for="item in roles"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="昵称">
          <el-input v-model="formLabelAlign.nickname" />
        </el-form-item>
        <el-form-item label="城市">
          <el-input v-model="formLabelAlign.location" />
        </el-form-item>
        <el-form-item label="关于我">
          <el-input
            v-model="formLabelAlign.about_me"
            show-word-limit
            maxlength="30"
          />
        </el-form-item>
        <el-form-item>
          <ButtonClick
            content="提交"
            type="primary"
            :disabled="!isChange"
            :loading="loading"
            @do-search="submit"
          />
        </el-form-item>
      </el-form>

      <van-dialog
        v-model:show="dialogShow"
        title="将用户图像设置为随机图像？"
        width="230"
        show-cancel-button
        :beforeClose="beforeReset"
      />
    </PageScroll>
  </PageHeadBack>
</template>
<style lang="scss" scoped></style>
