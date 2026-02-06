<template>
  <PageHeadBack>
    <PageScroll max-height="calc(100vh - 45px - 47px)">
      <div>
        <el-tag
          v-for="tag in dynamicTags"
          :key="tag.name"
          :type="tag.type"
          round
          closable
          :disable-transitions="false"
          @close="handleClose(tag)"
        >
          {{ tag.name }}
        </el-tag>
        <el-input
          v-if="inputVisible"
          ref="InputRef"
          v-model="inputValue"
          class="w-20"
          size="small"
          @keyup.enter="handleInputConfirm"
          @blur="handleInputConfirm"
        />
        <el-button
          v-else
          class="button-new-tag"
          size="small"
          @click="showInput"
        >
          + 新增 Tag
        </el-button>
      </div>

      <div class="del" v-if="tagRemove.length">
        待删除的标签：
        <el-tag
          v-for="tag in tagRemove"
          :key="tag"
          type="danger"
          round
          closable
          @close="cancelDel(tag)"
        >
          {{ tag }}
        </el-tag>
      </div>

      <div class="but">
        <el-text>注：可用空格分隔，一次输入多个标签</el-text>
        <el-button type="primary" round :disabled="!tagChange" @click="reset"
          >重置</el-button
        >
        <el-button type="primary" round :disabled="!tagChange" @click="save"
          >保存</el-button
        >
      </div>

      <van-dialog
        v-model:show="dialogShow"
        :title="dialogData.title"
        :message="dialogData.message"
        width="230"
        show-cancel-button
        :beforeClose="beforeClose"
      />
    </PageScroll>
  </PageHeadBack>
</template>

<script setup>
import { nextTick, ref, computed } from "vue";
import editApi from "@/api/user/editApi.js";
import userApi from "@/api/user/userApi.js";
import PageHeadBack from "@/utils/components/PageHeadBack.vue";
import PageScroll from "@/utils/components/PageScroll.vue";

// 原始tag数组
const originTag = ref([]);
// 动态修改的tag数组
const dynamicTags = ref([]);
const inputVisible = ref(false);
const inputValue = ref("");
const InputRef = ref("");
const exitsColor = "primary";
const newColor = "success";

const dialogShow = ref(false);
const dialogData = ref({
  title: "",
  message: "",
});

const handleClose = (tag) => {
  dynamicTags.value.splice(dynamicTags.value.indexOf(tag), 1);
};
const cancelDel = (tag) => {
  dynamicTags.value.push({
    name: tag,
    type: exitsColor,
  });
};

const showInput = () => {
  inputVisible.value = true;
  nextTick(() => {
    InputRef.value.input.focus();
  });
};

const tagAdd = computed(() => {
  return dynamicTags.value
    .filter((tag) => !originTag.value.some((o) => o.name === tag.name))
    .map((item) => item.name);
});

const tagRemove = computed(() => {
  return originTag.value
    .filter((tag) => !dynamicTags.value.some((d) => d.name === tag.name))
    .map((item) => item.name);
});

const tagChange = computed(() => tagAdd.value.length || tagRemove.value.length);

const handleInputConfirm = () => {
  if (!inputValue.value) {
    inputVisible.value = false;
    inputValue.value = "";
    return;
  }
  const t = [...new Set(inputValue.value.split(" "))].filter(
    (item) => item != ""
  );
  for (const item of t) {
    const exits = dynamicTags.value.some((tag) => tag.name === item);
    if (exits) {
      ElMessage.warning(`标签${item}已存在`);
      return;
    }
  }

  t.forEach((item) => {
    dynamicTags.value.push({
      name: item,
      type: newColor,
    });
  });

  inputVisible.value = false;
  inputValue.value = "";
};
function getTagList() {
  userApi.get_tag_list().then((res) => {
    if (res.code === 200) {
      res.data.map((item) => {
        const temp = {
          name: item,
          type: exitsColor,
        };
        originTag.value.push(temp);
        dynamicTags.value.push(temp);
      });
    }
  });
}
getTagList();

const reset = () => {
  dynamicTags.value = [...originTag.value];
  inputVisible.value = false;
  inputValue.value = "";
};
const save = () => {
  if (!tagChange.value) {
    ElMessage.warning("请修改后再提交");
    return;
  }
  dialogData.value = {
    title: tagRemove.value.length
      ? `确认要移除 [${tagRemove.value}]?`
      : `新增标签 [${tagAdd.value}]`,
    message: tagRemove.value.length ? "已设置该标签的用户将受到影响" : "",
  };
  dialogShow.value = true;
};
const beforeClose = (action) => {
  if (action !== "confirm") {
    return Promise.resolve(true);
  } else {
    return editApi
      .updateTag({ tagAdd: tagAdd.value, tagRemove: tagRemove.value })
      .then((res) => {
        if (res.code === 200) {
          const addLength = tagAdd.value.length;
          if (addLength) {
            changeColor(addLength);
          }
          updateOriginTag(tagAdd.value, tagRemove.value);
          ElMessage.success("保存成功");
        } else {
          ElMessage.error("保存失败");
        }
        return res;
      });
  }
};

function changeColor(addNum) {
  let startIndex = dynamicTags.value.length - addNum - 1;
  for (let i = startIndex; i < dynamicTags.value.length; i++) {
    dynamicTags.value[i].type = exitsColor;
  }
}

function updateOriginTag(tagAdd, tagRemove) {
  if (tagAdd.length) {
    tagAdd.forEach((tag) => {
      const temp = {
        name: tag,
        type: exitsColor,
      };
      originTag.value.push(temp);
    });
  }

  if (tagRemove.length) {
    tagRemove.forEach((tag) => {
      const index = originTag.value.findIndex((item) => item.name === tag);
      if (index !== -1) {
        originTag.value.splice(index, 1);
      }
    });
  }
}
</script>

<style lang="scss" scoped>
.el-tag {
  margin: 10px;
}

.del {
  margin: 20px;
}

.but {
  position: fixed;
  bottom: 20px;
  width: 100%;

  .el-button {
    margin-top: 10px;
    width: 45%;
  }
}
</style>
