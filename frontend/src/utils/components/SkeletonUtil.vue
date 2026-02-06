<script>
export default {
  props: {
    loading: {
      type: Boolean,
      default: false,
    },
    throttle: {
      type: Object,
      default() {
        return { leading: 300, trailing: 300, initVal: true };
      },
    },
    showAvatar: {
      type: Boolean,
      default: true,
    },
    row: {
      type: Number,
      default: 4,
    },
    count: {
      type: Number,
      default: 3,
    },
    cardStyle: {
      type: Object,
      default() {
        return {};
      },
    },
    useNew: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {};
  },
  methods: {},
};
</script>

<template>
  <el-skeleton
    v-if="!useNew"
    animated
    :loading="loading"
    :count="count"
    :throttle="throttle"
  >
    <template #template>
      <el-card shadow="hover" :style="cardStyle">
        <div class="skeleton-container">
          <el-skeleton-item
            variant="circle"
            style="--el-skeleton-circle-size: 40px"
            v-if="showAvatar"
          />
          <div class="item">
            <el-skeleton-item variant="text" style="width: 40%" />
            <el-skeleton-item
              variant="text"
              v-for="item in row - 2"
              :key="item"
            />
            <el-skeleton-item variant="text" style="width: 60%" />
          </div>
        </div>
      </el-card>
    </template>
    <slot></slot>
  </el-skeleton>

  <!-- 适配新版首页文章预览界面 -->
  <el-skeleton
    animated
    :loading="loading"
    :count="count"
    :throttle="throttle"
    v-else
  >
    <template #template>
      <div class="container">
        <div class="container-head">
          <div class="container-head-left">
            <el-skeleton-item
              variant="circle"
              style="--el-skeleton-circle-size: 40px"
              v-if="showAvatar"
            />
            <el-skeleton-item variant="text" style="width: 60%" />
          </div>
          <el-skeleton-item variant="text" style="width: 15%" />
        </div>

        <div class="container-content">
          <el-skeleton-item variant="text" style="width: 40%" />
          <el-skeleton-item
            variant="text"
            v-for="item in row - 2"
            :key="item"
          />
          <el-skeleton-item variant="text" style="width: 60%" />
        </div>

        <div class="block"></div>
      </div>
    </template>
    <slot></slot>
  </el-skeleton>
</template>
<style lang="scss" scoped>
:deep(.el-card__body) {
  padding: 5px 20px;
}

.skeleton-container {
  display: flex;
  gap: 10px;
}

.item {
  display: flex;
  flex-direction: column;
  gap: 10px;
  width: 80%;
}

.container {
  display: flex;
  flex-direction: column;

  &-head {
    display: flex;
    justify-content: space-between;
    align-items: center;

    &-left {
      display: flex;
      justify-content: space-between;
      align-items: center;
      width: 30%;
    }
  }

  &-content {
    display: flex;
    flex-direction: column;
    gap: 10px;
    width: 100%;
    padding: 15px 20px;
  }
}

.block {
  width: 100%;
  height: 5px;
  margin: 5px 0;
  background-color: #f5f7fa;
}
</style>
