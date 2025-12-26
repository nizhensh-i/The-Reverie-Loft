<script setup>
import { computed } from "vue";
import { useCurrentUserStore } from "@/stores/user";
import { useOtherUserStore } from "@/stores/otherUser";
import userApi from "@/api/user/userApi.js";
import { useRouter } from "vue-router";
const props = defineProps({ scope: Object, loading: Boolean, config: Object });

const currentUser = useCurrentUserStore();
const otherUser = useOtherUserStore();

const router = useRouter();
function followUser() {
  userApi.follow(props.scope.uName).then((res) => {
    if (res.code == 200) {
      ElMessage.success("关注成功");
      currentUser.addItemFollowed({
        id: props.scope.id,
        name: props.scope.username,
        uName: props.scope.uName,
        avatar: props.scope.avatar,
      });
    }
  });
}
function unFollowUser() {
  userApi.unFollow(props.scope.uName).then((res) => {
    if (res.code == 200) {
      currentUser.delItemFollowed(props.scope.uName);
      ElMessage.success("已取消关注");
    } else {
      ElMessage.error("取消关注失败");
    }
  });
}
function chat() {
  otherUser.userInfo = props.scope;
  router.push("/chat");
}
function toUser() {
  // 接口都已改为根据用户id获取用户数据
  otherUser.userInfo.id = props.scope.id;
  router.push(`/user/${props.scope.uName}`);
}
const isF = computed(() => {
  return currentUser.userInfo.followed.some((item) => {
    return item.uName === props.scope.uName;
  });
});
</script>

<template>
  <el-skeleton
    :loading="loading"
    :throttle="{ leading: 300, trailing: 300, initVal: true }"
    animated
  >
    <template #template>
      <el-skeleton-item
        variant="image"
        style="width: 50px; height: 50px; margin-bottom: 10px"
      />
      <div>
        <el-skeleton-item variant="h3" style="width: 100px" />
        <el-skeleton-item variant="text" style="margin-right: 16px" />
        <el-skeleton-item variant="text" style="width: 100px" />
      </div>
    </template>
    <template #default>
      <div class="user-card">
        <div class="user-avatar" @click="toUser">
          <el-avatar
            alt="用户图像"
            style="margin-top: 5px"
            :size="40"
            fit="cover"
            :src="scope.avatar"
          />
        </div>
        <div class="user-content">
          <div class="user-info">
            <div href="" class="username">
              <span class="name" style="max-width: 10em">{{
                scope.username
              }}</span>
              <!-- <span blank="true" class="rank" v-if="config.show.level">
                <u-icon size="24" v-html="useLevel(scope.level)"></u-icon>
              </span> -->
            </div>
          </div>
          <div class="social-info">
            <router-link
              :to="{
                name: 'follow',
                params: { action: 'followed', userName: scope.uName || 1 },
              }"
              class="attention"
            >
              <span>{{ scope.attention }}</span>
              <span>关注</span>
            </router-link>
            <router-link
              :to="{
                name: 'follow',
                params: { action: 'follower', userName: scope.uName || 1 },
              }"
              class="follower"
            >
              <span>{{ scope.follower }}</span>
              <span>粉丝</span>
            </router-link>
            <a class="like">
              <span>{{ scope.like }}</span>
              <span>获赞</span>
            </a>
          </div>
          <div
            class="card-btn"
            v-if="scope.uName !== currentUser.userInfo.username"
          >
            <el-button v-if="isF" @click="unFollowUser">取消关注</el-button>
            <el-button v-else type="primary" @click="followUser"
              >关注</el-button
            >
            <el-button @click="chat">发消息</el-button>
          </div>
        </div>
      </div>
    </template>
  </el-skeleton>
</template>

<style lang="scss" scoped>
.user-card {
  display: flex;
  .user-content {
    flex: 1;
    margin-left: 16px;
    .user-info {
      .username {
        display: flex;
        align-items: center;
        text-decoration: none;
        .name {
          max-width: 100px;
          font-weight: 500;
          font-size: 15px;
          color: #252933;
          line-height: 32px;
          margin-right: 4px;
        }
      }
    }
    .social-info {
      font-size: 12px;
      margin-bottom: 10px;
      a {
        text-decoration: none;
      }
      a:not(:first-child) {
        margin-left: 18px;
      }
      a span:last-child {
        margin-left: 3px;
        color: #9499a0;
      }
    }
  }
}
</style>
