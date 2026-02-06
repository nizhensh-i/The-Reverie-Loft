<!-- 
    重新加载数据按钮
    **父组件
    <<ButtonReload v-model:stop="isRotating" @click="reload"/>
 -->
<script>
export default {
  props: {
    stop: {
      type: Boolean,
      default: false,
    },
  },
  emits: ["update:stop"],
  data() {
    return {};
  },
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
  mounted() {},
  methods: {},
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
