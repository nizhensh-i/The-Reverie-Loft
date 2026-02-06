<script>
import contentDeleted from "@/asset/status/content-deleted.svg?component";

export default {
  name: "ContentNotFound",
  components: {
    contentDeleted,
  },
  methods: {
    goHome() {
      this.$router.push("/posts");
    },
  },
};
</script>

<template>
  <div class="container">
    <p>该内容已被作者删除或不存在</p>
    <contentDeleted />
    <el-button round type="primary" @click="goHome"> 返回首页 </el-button>
  </div>
</template>

<style lang="scss" scoped>
.container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-items: center;

  p {
    color: #71717a;
  }

  .el-button {
    width: 50%;
  }
}
</style>
