<template>
  <el-dropdown trigger="click" @command="onCommand">
    <div class="operation-warp">
      <u-icon>
        <svg
          viewBox="0 0 1024 1024"
          version="1.1"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            d="M586.624 234.624a74.624 74.624 0 1 1-149.184 0 74.624 74.624 0 0 1 149.12 0z m0 554.624a74.624 74.624 0 1 1-149.248 0 74.624 74.624 0 0 1 149.248 0zM512 586.624a74.624 74.624 0 1 0 0-149.248 74.624 74.624 0 0 0 0 149.248z"
            fill="currentColor"
          ></path>
        </svg>
      </u-icon>
    </div>
    <template #dropdown>
      <el-dropdown-menu>
        <!-- <el-dropdown-item command="report">举报</el-dropdown-item>
        <el-dropdown-item command="remove">删除</el-dropdown-item> -->
        <!-- <el-dropdown-item divided command="copy">复制</el-dropdown-item> -->
        <el-dropdown-item command="copy">复制</el-dropdown-item>
      </el-dropdown-menu>
    </template>
  </el-dropdown>
</template>
<script setup>
import { copy } from "@/utils/common.js";

const props = defineProps({ comment: Object });

const emit = defineEmits(["remove"]);

function rawCopy(html) {
  // 去除html标签
  const parser = new DOMParser();
  const doc = parser.parseFromString(html, "text/html");
  let rawContent = doc.body.textContent || "";
  // 去除回复评论的前缀
  if (rawContent != "" && rawContent.startsWith("回复")) {
    rawContent = rawContent.slice(2).trim();
  }
  copy(rawContent);
}
const onCommand = (command) => {
  switch (command) {
    case "remove":
      emit("remove", props.comment);
      break;
    case "report":
      ElMessage.info("举报成功!");
      break;
    case "copy":
      rawCopy(props.comment.content);
  }
};
</script>

<style lang="scss" scoped>
.el-dropdown {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  right: 0;
}
.operation-warp {
  font-size: 16px;
  color: #9499a0;
  cursor: pointer;
  position: relative;
}
.operation-warp:hover {
  color: #00aeec;
}
</style>
