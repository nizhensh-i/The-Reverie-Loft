<template>
  <van-cell :border="false" :to="`/user/${follows.username}`">
    <template #icon>
      <el-avatar alt="用户图像" :src="follows.image" />
    </template>
    <template #title>
      <div class="title-text">
        {{ follows.nickname ? follows.nickname : follows.username }}
      </div>
    </template>
    <template #right-icon v-if="showFollowButton">
      <van-icon
        class="icon"
        name="add"
        color="blue"
        :size="25"
        v-if="!isFollowed"
        @click.stop="followUser"
      />
      <van-icon
        class="icon"
        name="checked"
        color="gray"
        :size="25"
        v-if="isFollowed && !isMutualFollow"
        @click.stop="unFollowUser"
      />
      <van-icon
        class="icon"
        name="sort"
        color="gray"
        :size="25"
        v-if="isMutualFollow"
        @click.stop="unFollowUser"
      />
    </template>
  </van-cell>

  <van-dialog
    v-model:show="dialogShow"
    title="取消对该用户的关注"
    width="230"
    show-cancel-button
    :beforeClose="beforeClose"
    teleport="html"
  />
</template>

<script>
import userApi from "@/api/user/userApi.js";
import { useCurrentUserStore } from "@/stores/user";

export default {
  props: {
    follows: {
      type: Object,
      default() {
        return {
          username: "123",
          image: "/src/asset/image_7.ico",
          is_following: false,
          is_following_back: false,
        };
      },
    },
    tabAction: {
      type: String,
      default: "fan",
    },
    showFollowButton: {
      type: Boolean,
      default: true,
    },
  },
  emits: ["remove"],
  data() {
    return {
      isFollowed: this.tabAction == "fan" ? this.follows.is_following : true,
      isMutualFollow: false,
      dialogShow: false,
    };
  },
  setup() {
    const currentUser = useCurrentUserStore();
    return { currentUser };
  },
  mounted() {
    // 初始状态 是否互关
    if (this.tabAction == "fan" && this.follows.is_following) {
      this.isMutualFollow = true;
    } else if (this.tabAction == "followed" && this.follows.is_following_back) {
      this.isMutualFollow = true;
    } else {
      this.isMutualFollow = false;
    }
  },
  methods: {
    followUser() {
      userApi.follow(this.follows.username).then((res) => {
        if (res.code == 200) {
          this.isFollowed = true;
          this.isMutualFollow = true;
          this.currentUser.addItemFollowed({
            id: this.follows.id,
            name: this.follows.nickname
              ? this.follows.nickname
              : this.follows.username,
            uName: this.follows.username,
            avatar: this.follows.image,
          });
          ElMessage.success("关注成功");
        }
      });
    },
    unFollowUser() {
      this.dialogShow = true;
    },
    beforeClose(action) {
      if (action !== "confirm") {
        return Promise.resolve(true);
      } else {
        return userApi.unFollow(this.follows.username).then((res) => {
          if (res.code == 200) {
            this.currentUser.delItemFollowed(this.follows.username);
            ElMessage.success("已取消关注");
            if (this.tabAction == "followed") {
              this.$emit("remove", this.follows.username);
            } else {
              this.isFollowed = false;
              this.isMutualFollow = false;
            }
          }
          return res;
        });
      }
    },
  },
};
</script>
<style lang="scss" scoped>
.van-cell:active {
  background: #f5f7fa;
}

.title-text {
  line-height: 40px;
  margin-left: 20px;
}

.icon {
  line-height: 40px;
}
</style>
