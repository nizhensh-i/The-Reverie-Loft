<script>
export default {
  props: {
    postImages: {
      type: Array,
      default() {
        return [];
      },
    },
  },
  computed: {
    gridTemplateColumns() {
      const count = this.postImages.length;
      if (count === 1) return "1fr";
      if (count === 2 || count === 4) return "1fr 1fr";
      return "1fr 1fr 1fr";
    },
    containerWidth() {
      const count = this.postImages.length;
      if (count === 1) return "220px";
      if (count === 2 || count === 4) return "320px";
      return "330px";
    },
  },
};
</script>

<template>
  <div class="container" :style="{ width: containerWidth }">
    <div class="preview" :style="{ gridTemplateColumns }">
      <el-image
        v-for="(url, index) in postImages"
        :key="url"
        :src="url"
        :preview-src-list="postImages"
        :initial-index="index"
        alt="文章图片"
        lazy
        fit="cover"
        preview-teleported
      >
        <template #error>
          <div class="image-slot">
            <el-icon><i-ep-picture /></el-icon>
          </div>
        </template>
      </el-image>
    </div>
  </div>
</template>
<style lang="scss" scoped>
.container {
  .preview {
    display: grid;
    gap: 5px;
    width: 100%;
    margin: 0 auto;

    .el-image {
      width: 100%;
      aspect-ratio: 1;

      .image-slot {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 100%;
        height: 100%;
        color: var(--el-text-color-secondary);
        font-size: 14px;
        background: var(--el-fill-color-light);

        .el-icon {
          font-size: 30px;
        }
      }
    }
  }
}
</style>
