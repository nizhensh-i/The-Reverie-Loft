<template>
  <el-page-header @back="goBack" :title="title">
    <template #extra>
      <slot name="action"></slot>
    </template>
  </el-page-header>
  <slot></slot>
</template>

<script>
export default {
  props: {
    title: {
      type: String,
      default: "返回",
    },
  },
  methods: {
    goBack() {
      this.$router.back();
    },
  },
};
</script>
<style lang="scss" scoped>
.el-page-header {
  margin: 10px 10px 10px 20px;
}
</style>
