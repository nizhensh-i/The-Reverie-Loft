<script>
export default {
  components: {},
  methods: {
    clear() {
      localStorage.clear("blog");
      ElMessage.success("清除成功");
    },
  },
};
</script>
<template>
  <div class="container">
    <el-button round type="primary" @click="clear">清空缓存</el-button>
    <el-button round type="primary" @click="$router.push('/login')"
      >回到登录页</el-button
    >
  </div>
</template>
<style lang="scss" scoped>
.container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;

  .el-button {
    width: 50%;
    margin: 0;
  }
}
</style>
