<script>
import noExist from "@/asset/status/404.svg?component";
export default {
  components: {
    noExist,
  },
};
</script>
<template>
  <div class="container">
    <p>您访问的页面不存在</p>
    <noExist />
    <el-button round type="primary" @click="$router.push('/posts')"
      >返回首页</el-button
    >
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
