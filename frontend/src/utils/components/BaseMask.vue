<template>
  <div class="Mask" :class="mode"></div>
</template>
<script>
export default {
  name: "BaseMask",
  props: {
    mode: {
      type: String,
      default: "dark",
    },
  },
};
</script>

<style lang="scss">
:root {
  --mask-dark: #000000bb;
  --mask-light: transparent;
  --mask-white: transparent;
  --mask-lightgray: rgba(0, 0, 0, 0.25);
}

.Mask {
  position: fixed;
  inset: 0;
  z-index: 3;
  background: var(--mask-dark);

  &.dark {
    background: var(--mask-dark);
  }

  &.light {
    background: var(--mask-light);
  }

  &.lightgray {
    background: var(--mask-lightgray);
  }

  &.white {
    background: var(--mask-white);
  }
}
</style>
