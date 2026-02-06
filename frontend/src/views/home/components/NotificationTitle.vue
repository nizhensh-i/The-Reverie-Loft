<script>
export default {
  props: {
    nItem: {
      type: Object,
      default() {
        return {};
      },
    },
  },
  data() {
    return {};
  },
  computed: {
    suffix() {
      if (this.nItem.type === "评论") {
        return "的文章";
      } else if (this.nItem.type === "回复") {
        return "评论";
      } else if (this.nItem.type === "点赞" && !this.nItem.commentId) {
        return "的文章";
      } else if (
        this.nItem.type === "点赞" &&
        this.nItem.commentId &&
        this.nItem.postId
      ) {
        return "的评论";
      }
      return "";
    },
  },
};
</script>

<template>
  <p class="notification-title">
    {{
      `${
        nItem.triggerNickName ? nItem.triggerNickName : nItem.triggerUsername
      } ${nItem.type} 了你${suffix}`
    }}
  </p>
</template>
<style scoped>
.notification-title {
  font-weight: 600;
  font-size: 0.875rem;
  margin: 0;
  padding: 0;
  line-height: 1.4;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}
</style>
