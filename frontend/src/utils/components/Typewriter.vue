<template>
  <div class="leleo-typewriter" style="text-align: center">
    <span class="qm">“ </span><span ref="text" class="msg"></span
    ><span class="qm"> ”</span>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from "vue";
import TypeIt from "typeit";
const prop = defineProps({
  content: {
    type: String,
    default: "",
  },
});
const text = ref("");
let typeitInstance = null; // 新增变量保存实例

function runTypeIt(str) {
  if (typeitInstance) {
    typeitInstance.destroy(); // 销毁旧实例
    typeitInstance = null;
  }
  text.value.innerHTML = ""; // 清空旧内容
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
  runTypeIt(prop.content);
});

watch(
  () => prop.content,
  (val) => {
    runTypeIt(val);
  }
);
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
