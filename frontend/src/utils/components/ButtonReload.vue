<script>
/**
 * 重新加载数据按钮
 * @example
 * <ButtonReload v-model:stop="isRotating" @click="reload" />
 */
export default {
  props: {
    stop: {
      type: Boolean,
      default: false,
    },
  },
  emits: ["update:stop"],
  computed: {
    internalStop: {
      get() {
        return this.stop;
      },
      set(value) {
        this.$emit("update:stop", value);
      },
    },
  },
};
</script>

<template>
  <el-button circle :disabled="internalStop">
    <template #icon>
      <el-icon :class="{ spin: internalStop }" size="large"
        ><i-ep-RefreshRight
      /></el-icon>
    </template>
  </el-button>
</template>
<style lang="scss" scoped>
.spin {
  animation: rotate 1s linear infinite;
}

@keyframes rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>
