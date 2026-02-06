<!-- 
    搜索按钮
    点击按钮后，向父组件发生点击事件，由父组件来完成点击后的具体执行
    **父组件
    <ButtonClick content="搜索" type="warning" :loading="loading.queryButton" @do-search="doSearch"></ButtonClick>
 -->
<script>
export default {
  props: {
    // 按钮文字
    content: {
      type: String,
      default: "点击",
    },
    // 按钮样式
    type: {
      type: String,
      default: "",
    },
    // 自定义颜色
    color: {
      type: String,
      default: "",
    },
    // 加载效果
    loading: {
      type: Boolean,
      default: false,
    },
    // 按钮大小
    size: {
      type: String,
      default: "default",
    },
    // 是否需要图标
    havaIcon: {
      type: Boolean,
      default: true,
    },
    disabled: {
      type: Boolean,
      default: false,
    },
    round: {
      type: Boolean,
      default: false,
    },
    width: {
      type: String,
      default: "auto",
    },
    // 是否圆角按钮
  },
  emits: ["doSearch"],
};
</script>

<template>
  <el-button
    :type="type"
    :color="color"
    :loading="loading"
    :size="size"
    :disabled="disabled"
    :round="round"
    :style="{ width: width }"
    @click="$emit('doSearch')"
  >
    <!-- 自定义图标插槽出口 -->
    {{ content }} <slot />
  </el-button>
</template>
<style lang="scss" scoped>
.el-button {
  letter-spacing: 0.08em;

  :deep(.el-icon) {
    margin-right: 6px;
    font-size: 1.2em;
  }
}
</style>
