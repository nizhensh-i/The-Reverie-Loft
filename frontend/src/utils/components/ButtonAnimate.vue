<script>
export default {
  props: {
    // 按钮文字
    content: {
      type: String,
      default: "点击",
    },
    isActive: {
      type: Boolean,
      default: false,
    },
    fontColor: {
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
  <div
    class="btn java"
    :class="{ active: isActive, fontColor: fontColor }"
    @click="$emit('click')"
  >
    {{ content }}
  </div>
</template>
<style lang="scss" scoped>
.btn {
  display: inline-block;
  vertical-align: top;
  margin: 25px 0 0 20px;
  text-align: center;
  cursor: pointer;
  border-radius: 20px;
  backdrop-filter: blur(7px);

  &.java {
    width: 80px;
    height: 30px;
    font-size: 12px;
    line-height: 30px;
    color: #fff;
    border: 1px solid rgb(216.8, 235.6, 255);
    opacity: 1;
    transition: all 0.3s;

    &:active {
      opacity: 0.7;
    }
  }

  &.active {
    border-color: rgb(4, 122, 239);
  }

  &.fontColor {
    color: #000;
  }
}
</style>
