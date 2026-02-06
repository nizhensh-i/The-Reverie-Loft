<script>
export default {
  props: {
    toc: {
      type: Array,
      required: true,
    },
    activeId: {
      type: String,
      default: "",
    },
  },
  data() {
    return {
      show: false,
    };
  },
  methods: {
    scrollToHeading(id) {
      this.$emit("navigate", id);
      const el = document.getElementById(id);
      if (el) {
        el.scrollIntoView({ behavior: "smooth" });
      }
    },
    toggleVisible() {
      this.show = !this.show;
    },
  },
};
</script>

<template>
  <div class="toc">
    <el-button
      v-if="toc.length > 0"
      class="font-size-button"
      circle
      type="primary"
      size="large"
      @click="toggleVisible"
    >
      <span class="font-icon">目录</span>
    </el-button>

    <el-drawer
      v-model="show"
      title="目录"
      direction="rtl"
      size="280px"
      :destroy-on-close="false"
      :modal="true"
    >
      <div class="toc-content">
        <div
          v-for="item in toc"
          :key="item.id"
          class="toc-item"
          :class="{ active: activeId === item.id }"
          :style="{
            paddingLeft: `${(item.level - 1) * 12}px`,
            fontSize: `${18 - item.level * 1}px`,
          }"
          @click="scrollToHeading(item.id)"
        >
          {{ item.text }}
        </div>
      </div>
    </el-drawer>
  </div>
</template>

<style lang="scss">
.toc {
  position: fixed;
  top: 150px;
  right: 20px;
  z-index: 999;

  .font-icon {
    font-size: 13px;
  }
}

.toc-content {
  flex: 1;
  overflow-y: auto;

  .toc-item {
    margin-bottom: 8px;
    color: #555;
    font-weight: normal;
    cursor: pointer;
    transition: all 0.2s;

    &.active {
      color: #409eff;
      font-weight: bold;
    }

    &:hover {
      color: #409eff;
      transform: translateX(4px);
    }
  }
}
</style>
