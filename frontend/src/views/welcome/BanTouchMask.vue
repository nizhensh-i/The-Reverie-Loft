<script setup>
defineOptions({
  name: "BanTouchMask",
});

defineProps({
  touchable: Boolean,
});
</script>

<template>
  <div v-if="!touchable" class="ban-touch-mask"></div>
</template>

<style lang="scss" scoped>
.ban-touch-mask {
  position: absolute;
  inset: 0;
  z-index: 999;
  width: 100%;
  height: 100%;
}
</style>
