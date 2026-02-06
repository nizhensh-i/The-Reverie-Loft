<!-- 修改昵称，签名，社交账号 -->
<script setup>
import { useCurrentUserStore } from "@/stores/user";
import { useOtherUserStore } from "@/stores/otherUser";
import { cloneDeep } from "@pureadmin/utils";
import { useRouter, useRoute } from "vue-router";
import editApi from "@/api/user/editApi.js";
import PageHeadBack from "@/utils/components/PageHeadBack.vue";
import PageScroll from "@/utils/components/PageScroll.vue";
import { useChange } from "@/utils/composedFunc/change.js";

import github from "@/asset/svg/github.svg?component";
import email from "@/asset/svg/email.svg?component";
import qqchat from "@/asset/svg/qqchat.svg?component";
import wechat from "@/asset/svg/wechat.svg?component";
import bilibili from "@/asset/svg/bilibili.svg?component";
import twitter from "@/asset/svg/twitter.svg?component";

const user = useCurrentUserStore();
const other = useOtherUserStore();
const router = useRouter();
const route = useRoute();

const data = reactive({
  type: 1,
  localUserInfo: {
    nickname: "",
    about_me: "",
    social_account: {
      qq: "",
      wechat: "",
      bilibili: "",
      github: "",
      twitter: "",
      email: "",
    },
  },
});

data.type = Number(route.query.type);
data.localUserInfo = cloneDeep(user.userInfo);

const { isChange } = useChange(data, getAttr(data.type));

async function saveNickname() {
  await editApi.editUser(user.userInfo.id, {
    nickname: data.localUserInfo.nickname,
  });
}
async function saveAboutMe() {
  await editApi.editUser(user.userInfo.id, {
    about_me: data.localUserInfo.about_me,
  });
}
async function saveSocialLinks() {
  await editApi.editUser(user.userInfo.id, {
    social_account: data.localUserInfo.social_account,
  });
}
async function save() {
  const loading = ElLoading.service({
    lock: true,
    text: "正在保存",
    background: "rgba(0, 0, 0, 0.7)",
  });
  if (data.type === 1) {
    await saveNickname();
  } else if (data.type === 2) {
    await saveAboutMe();
  } else if (data.type === 3) {
    await saveSocialLinks();
  }
  user.setUserInfo(data.localUserInfo);
  other.setUserInfo(data.localUserInfo);
  loading.close();
  router.back();
}
function getAttr(type) {
  switch (type) {
    case 1:
      return "localUserInfo.nickname";
    case 2:
      return "localUserInfo.about_me";
    case 3:
      return "localUserInfo.social_account";
    default:
      return "";
  }
}
</script>
<template>
  <PageHeadBack>
    <template #action>
      <el-button :disabled="!isChange" @click="save">保存</el-button>
    </template>
    <PageScroll max-height="calc(100vh - 45px - 47px)">
      <div v-if="data.type === 1">
        <div class="title">修改昵称</div>
        <el-input v-model="data.localUserInfo.nickname" />
      </div>

      <div v-if="data.type === 2">
        <div class="title">修改签名</div>
        <el-input
          v-model="data.localUserInfo.about_me"
          autosize
          type="textarea"
          show-word-limit
          maxlength="30"
        />
      </div>

      <div v-if="data.type === 3">
        <div class="title">修改社交账号</div>
        <van-cell-group inset>
          <van-field
            v-model="data.localUserInfo.social_account.github"
            label="github"
          >
            <template #left-icon>
              <component :is="github" class="icon" />
            </template>
          </van-field>
          <van-field
            v-model="data.localUserInfo.social_account.email"
            label="邮箱"
          >
            <template #left-icon>
              <component :is="email" class="icon" />
            </template>
          </van-field>
          <van-field
            v-model="data.localUserInfo.social_account.qq"
            type="digit"
            label="qq"
          >
            <template #left-icon>
              <component :is="qqchat" class="icon" />
            </template>
          </van-field>
          <van-field
            v-model="data.localUserInfo.social_account.wechat"
            label="微信"
          >
            <template #left-icon>
              <component :is="wechat" class="icon" />
            </template>
          </van-field>
          <van-field
            v-model="data.localUserInfo.social_account.bilibili"
            label="bilibili"
          >
            <template #left-icon>
              <component :is="bilibili" class="icon" />
            </template>
          </van-field>
          <van-field
            v-model="data.localUserInfo.social_account.twitter"
            label="twitter"
          >
            <template #left-icon>
              <component :is="twitter" class="icon" />
            </template>
          </van-field>
        </van-cell-group>
      </div>
    </PageScroll>
  </PageHeadBack>
</template>

<style lang="scss" scoped>
.title {
  text-align: center;
  margin-bottom: 20px;
}

img {
  background-color: black;
}

.icon {
  width: 32px;
  height: 32px;
}
</style>
