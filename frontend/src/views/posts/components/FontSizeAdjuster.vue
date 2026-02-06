<script>
export default {
  props: {
    defaultFontSize: {
      type: Number,
      default: 16,
    },
  },
  data() {
    return {
      visible: false,
      fontSize: this.defaultFontSize,
      tempFontSize: this.defaultFontSize,
    };
  },
  watch: {
    defaultFontSize: {
      handler(newVal) {
        this.fontSize = newVal;
        // 当默认字体大小变化时，更新临时字体大小
        if (!this.visible) {
          this.tempFontSize = newVal;
        }
      },
      immediate: true,
    },
  },
  methods: {
    toggleVisible() {
      this.visible = !this.visible;
      if (this.visible) {
        // 打开时使用当前实际的字体大小
        this.tempFontSize = this.fontSize;
      }
    },
    saveFontSize() {
      this.fontSize = this.tempFontSize;
      localStorage.setItem("article-font-size", this.fontSize.toString());
      this.$emit("save", this.fontSize);
      this.visible = false;
    },
    resetFontSize() {
      this.tempFontSize = 16;
    },
  },
};
</script>

<template>
  <div class="font-size-adjuster">
    <el-button
      class="font-size-button"
      circle
      type="primary"
      size="large"
      @click="toggleVisible"
    >
      <span class="font-icon">T</span>
    </el-button>

    <el-drawer
      v-model="visible"
      title="调整文章字体大小"
      direction="rtl"
      size="280px"
      :with-header="true"
      :destroy-on-close="false"
      :modal="true"
    >
      <div class="font-size-content">
        <div class="font-size-preview">
          <div class="preview-title">预览效果</div>
          <div class="preview-text" :style="{ fontSize: tempFontSize + 'px' }">
            这是预览文本，调整滑块可以改变字体大小，使阅读更加舒适。
          </div>
        </div>

        <div class="font-size-control">
          <div class="control-label">
            <span>字体大小: {{ tempFontSize }}px</span>
            <el-button link @click="resetFontSize">重置</el-button>
          </div>

          <el-slider
            v-model="tempFontSize"
            :min="12"
            :max="24"
            :step="1"
            show-stops
          />

          <div class="control-buttons">
            <el-button @click="visible = false">取消</el-button>
            <el-button type="primary" @click="saveFontSize">保存设置</el-button>
          </div>
        </div>
      </div>
    </el-drawer>
  </div>
</template>

<style lang="scss" scoped>
.font-size-adjuster {
  position: fixed;
  right: 20px;
  bottom: 130px;
  z-index: 999;
}

.font-size-button {
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.font-size-content {
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 0 20px;
}

.font-size-preview {
  max-height: 200px;
  padding: 16px;
  margin-bottom: 24px;
  overflow: auto;
  background-color: #f5f7fa;
  border-radius: 8px;

  .preview-title {
    margin-bottom: 12px;
    font-size: 16px;
    font-weight: 500;
    color: #606266;
  }

  .preview-text {
    line-height: 1.8;
    color: #303133;
  }
}

.font-size-control {
  margin-bottom: 20px;
}

.control-label {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;

  span {
    font-size: 14px;
    color: #606266;
  }
}

.control-buttons {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
}
</style>
