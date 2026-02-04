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
  data() {
    return {};
  },
  computed: {},
  mounted() {},
  methods: {
    goBack() {
      this.$router.back();
    },
  },
};
</script>
<style scoped>
.el-page-header {
  margin-bottom: 10px;
  margin-top: 10px;
}
</style>
