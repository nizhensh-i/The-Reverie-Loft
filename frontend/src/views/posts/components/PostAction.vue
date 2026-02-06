<script>
import { useCurrentUserStore } from "@/stores/user";
import { loginReminder } from "@/utils/common.js";
import { copy } from "@/utils/common.js";
import praise from "@/api/praise/praiseApi.js";
import postApi from "@/api/posts/postApi.js";
import emitter from "@/utils/emitter.js";

export default {
  props: {
    post: {
      type: Object,
      default() {
        return {
          id: 1,
          content: "文章",
          post_type: "text",
          timestamp: "",
          author: "张三",
          nick_name: "",
          commentCount: 20,
          disabled: false,
          image: "",
          comment_count: 0,
          praise_num: 0,
          has_praised: false,
          post_images: [],
        };
      },
    },
    showShare: {
      type: Boolean,
      default: false,
    },
    showEdit: {
      type: Boolean,
      default: false,
    },
    showDelete: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      iconSize: 15,
      praiseNum: 0,
      hasPraised: false,
      show: false,
      dialogShow: false,
      shareOptions: [
        { name: "微信", icon: "wechat" },
        { name: "朋友圈", icon: "wechat-moments" },
        { name: "微博", icon: "weibo" },
        { name: "QQ", icon: "qq" },
        { name: "复制链接", icon: "link" },
      ],
    };
  },
  setup() {
    const currentUser = useCurrentUserStore();
    return { currentUser };
  },
  mounted() {},
  watch: {
    "post.praise_num": {
      handler(newValue) {
        this.praiseNum = newValue;
      },
      immediate: true,
    },
    "post.has_praised": {
      handler(newValue) {
        this.hasPraised = newValue;
      },
      immediate: true,
    },
  },
  computed: {
    isUserRoute() {
      return this.$route.path.startsWith("/user");
    },
  },
  methods: {
    comment() {
      this.$router.push(`/postDetail/${this.post.id}`);
    },

    handlePraiseClick(event) {
      // 阻止事件冒泡和默认行为
      if (event) {
        event.preventDefault();
        event.stopPropagation();
      }

      // 如果已经点赞，可以选择取消点赞或什么都不做
      if (this.hasPraised) {
        // 这里可以添加取消点赞的逻辑，或者什么都不做
        // 暂时保持已点赞状态，不做任何操作
        return;
      }

      this.praise();
    },

    handleEditClick(event) {
      if (event) {
        event.preventDefault();
        event.stopPropagation();
      }
      this.edit();
    },

    handleDeleteClick(event) {
      if (event) {
        event.preventDefault();
        event.stopPropagation();
      }
      this.dialogShow = true;
    },

    handleShareClick(event) {
      if (event) {
        event.preventDefault();
        event.stopPropagation();
      }
      this.show = !this.show;
    },

    handleCommentClick(event) {
      if (event) {
        event.preventDefault();
        event.stopPropagation();
      }
      this.comment();
    },

    praise() {
      if (!this.currentUser.isLogin) {
        loginReminder("快去登录再点赞吧");
        return;
      }
      praise.submitPraise(this.post.id).then((res) => {
        if (res.code == 200) {
          this.praiseNum = res.data.praise_total;
          this.hasPraised = res.data.has_praised;
        } else {
          ElMessage.error(res.data.detail);
        }
      });
    },

    edit() {
      this.$router.push(`/editPost/${this.post.id}`);
    },
    shareSelect(option) {
      if (option.name === "复制链接") {
        copy(`${import.meta.env.VITE_DOMAIN}/postDetail/${this.post.id}`);
      } else {
        ElMessage.info(option.name);
      }
      this.show = false;
    },

    beforeDelete(action) {
      if (action !== "confirm") {
        return Promise.resolve(true);
      } else {
        return postApi.deletePost(this.post.id).then((res) => {
          if (res.code === 200) {
            ElMessage.success("文章删除成功");
            // 发送删除事件，通知文章列表页刷新
            emitter.emit("postDeleted");
            // 跳转到首页或文章列表页
            this.$router.push("/posts");
          } else {
            ElMessage.error(res.message || "删除文章失败");
          }
          return res;
        });
      }
    },
  },
};
</script>

<template>
  <div class="post-action-container">
    <div class="action-left">
      <div
        class="action-item"
        v-if="
          showEdit &&
          (post.author == currentUser.userInfo.username || currentUser.isAdmin)
        "
      >
        <van-icon
          name="edit"
          @click="handleEditClick"
          :size="iconSize"
          class="action-icon"
        />
      </div>

      <div class="action-item" v-if="showDelete && currentUser.isAdmin">
        <van-icon
          name="delete-o"
          @click="handleDeleteClick"
          :size="iconSize"
          color="#f56c6c"
          class="action-icon delete-icon"
          title="删除文章"
        />
      </div>
      <div class="action-item" v-if="showShare && !isUserRoute">
        <van-icon
          name="share-o"
          @click="handleShareClick"
          :size="iconSize"
          class="action-icon"
        />
      </div>
    </div>

    <div class="action-right">
      <div class="action-item comment" @click.stop>
        <van-icon
          name="comment-o"
          @click="handleCommentClick"
          :size="iconSize"
          class="action-icon"
        />
        <span class="action-count">{{ post.comment_count }}</span>
      </div>

      <div class="action-item like" @click.stop="handlePraiseClick">
        <transition :name="hasPraised ? 'praise' : ''" mode="out-in">
          <van-icon
            name="good-job"
            :size="iconSize"
            v-if="hasPraised"
            key="praised"
            class="action-icon praised"
          />
          <van-icon
            name="good-job-o"
            :size="iconSize"
            v-else
            key="unPraise"
            class="action-icon"
          />
        </transition>
        <span class="action-count">{{ praiseNum }}</span>
      </div>
    </div>
  </div>

  <van-share-sheet
    v-model:show="show"
    title="立即分享给好友"
    :options="shareOptions"
    @select="shareSelect"
  />
  <van-dialog
    v-model:show="dialogShow"
    title="确定删除这篇文章吗？"
    width="230"
    show-cancel-button
    :beforeClose="beforeDelete"
  />
</template>

<style scoped lang="scss">
.post-action-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  padding: 8px 0;
}

.action-left,
.action-right {
  display: flex;
  align-items: center;
}

.action-item {
  display: flex;
  align-items: center;
  margin-right: 16px;
  cursor: pointer;

  &:last-child {
    margin-right: 0;
  }
}

.action-icon {
  margin-right: 4px;
  transition: all 0.2s ease;

  &:hover {
    transform: scale(1.1);
  }

  &.delete-icon:hover {
    transform: scale(1.2);
    filter: brightness(1.1);
  }
}

.action-count {
  font-size: 14px;
  color: #666;
}

// 点赞动画
.praise-enter-active,
.praise-leave-active {
  transition: all 0.3s ease;
}

.praise-enter-from,
.praise-leave-to {
  opacity: 0;
  transform: scale(0.5);
}

// 响应式
@media (max-width: 768px) {
  .post-action-container {
    padding: 6px 0;
  }

  .action-item {
    margin-right: 12px;
  }
}
</style>
