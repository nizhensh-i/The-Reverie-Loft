<template>
  <button class="emoji-button1">按钮</button>
</template>
<script>
export default {
  props: {
    showEmoji: {
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
<style lang="scss" scoped>
.emoji-button1 {
  position: relative;
  display: inline-block;
  font-size: 1rem;
  background-color: transparent;
  border: none;
  border-radius: 50%;
  cursor: pointer;
  transition: transform 0.5s;

  &:hover {
    transform: scale(1.2);
  }
}
</style>
