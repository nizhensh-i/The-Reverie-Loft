<script>
import noAccess from "@/asset/status/403.svg?component";
export default {
  components: {
    noAccess,
  },
};
</script>
<template>
  <div class="container">
    <p>抱歉，您无权访问该页面</p>
    <noAccess />
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
