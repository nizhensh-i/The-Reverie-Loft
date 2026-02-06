<script>
import noServer from "@/asset/status/500.svg?component";
export default {
  components: {
    noServer,
  },
};
</script>
<template>
  <div class="container">
    <p>抱歉，服务器出错了，请稍后再尝试</p>
    <noServer />
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
