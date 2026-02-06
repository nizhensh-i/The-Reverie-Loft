<template>
  <div class="leleo-typewriter" style="text-align: center">
    <span class="qm">“ </span><span ref="text" class="msg"></span
    ><span class="qm"> ”</span>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from "vue";
import TypeIt from "typeit";

const props = defineProps({
  content: {
    type: String,
    default: "",
  },
});

const text = ref(null);
let typeitInstance = null;

function runTypeIt(str) {
  if (typeitInstance) {
    typeitInstance.destroy();
    typeitInstance = null;
  }

  if (!text.value) return;

  typeitInstance = new TypeIt(text.value, {
    strings: str,
    cursorChar:
      "<span class='cursorChar' style='font-size: 12px;color: var(--leleo-vcard-color);'>|<span>",
    speed: 150,
    lifeLike: true,
    cursor: true,
    breakLines: false,
    loop: false,
  });
  typeitInstance.go();
}

onMounted(() => {
  runTypeIt(props.content);
});

watch(() => props.content, runTypeIt);
</script>

<style lang="scss" scoped>
.leleo-typewriter {
  text-align: center;
}

.msg,
.qm {
  color: #ffffff;
  font-size: 25px;
  font-weight: bold;
  font-family: Arial, sans-serif;
  letter-spacing: 2px;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.3);

  @media screen and (min-width: 960px) and (max-width: 1200px) {
    font-size: 20px;
  }

  @media (max-width: 960px) {
    font-size: 16px;
  }
}

.msg {
  :deep(.cursorChar) {
    display: inline-block;
    margin-left: 2px;
  }
}

@media (max-width: 960px) {
  .leleo-typewriter {
    min-height: 76px;
  }
}
</style>
