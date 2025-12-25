<script>
import date from "@/utils/date.js";
import { useOtherUserStore } from "@/stores/otherUser";
export default {
  props: {
    post: {
      type: Object,
      default() {
        return {
          id: 1,
          body: "",
          body_html: null,
          timestamp: "",
          author: "--",
          nick_name: "",
          user_id: 1,
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
  },
  data() {
    return {};
  },
  setup() {
    const otherUser = useOtherUserStore();
    return { otherUser };
  },
  mounted() {},
  computed: {
    from_now() {
      return date.dateShow(this.post.timestamp);
    },
  },
  data() {
    return {
      touchTimer: null,
    };
  },
  methods: {
    handleUserClick(event) {
      // 阻止事件冒泡和默认行为
      if (event) {
        event.preventDefault();
        event.stopPropagation();
      }
      this.toUser();
    },

    handleTouchStart(event) {
      // 为移动端提供更好的响应
      if (this.touchTimer) {
        clearTimeout(this.touchTimer);
      }
      this.touchTimer = setTimeout(() => {
        // 长按逻辑（如果需要）
      }, 300);
    },

    handleTouchEnd(event) {
      if (this.touchTimer) {
        clearTimeout(this.touchTimer);
      }
    },

    toUser() {
      // 接口都已改为根据用户id获取用户数据
      this.otherUser.userInfo.id = this.post.user_id;
      this.$router.push(`/user/${this.post.author}`);
    },
  },
};
</script>

<template>
  <el-row class="head" justify="space-between" align="middle">
    <div class="head-name">
      <el-avatar
        alt="用户图像"
        :src="post.image"
        @click="handleUserClick"
        @touchstart="handleTouchStart"
        @touchend="handleTouchEnd"
      />
      <el-text
        @click="handleUserClick"
        @touchstart="handleTouchStart"
        @touchend="handleTouchEnd"
        >{{ post.nick_name ? post.nick_name : post.author }}</el-text
      >
    </div>
    <div>
      <el-text size="small" class="head-time">{{ from_now }}</el-text>
    </div>
  </el-row>
</template>
<style lang="scss" scoped>
.head {
  height: 40px;
  margin: 0px 0px 10px 0px;
}
.head-name {
  display: flex;
  align-items: center;

  .el-avatar {
    cursor: pointer;
    transition: opacity 0.2s ease;

    &:hover {
      opacity: 0.8;
    }

    &:active {
      transform: scale(0.95);
    }
  }

  .el-text {
    margin-left: 5px;
    font-size: 13px;
    font-weight: 600;
    line-height: 1.2;
    // text-shadow: 0 1px 2px rgba(0,0,0,0.8);
    cursor: pointer;
    transition: color 0.2s ease;

    &:hover {
      color: #409eff;
    }
  }
}
.head-time {
  margin-right: 1px;
}
</style>
