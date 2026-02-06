<script>
import postApi from "@/api/posts/postApi.js";
import ButtonClick from "@/utils/components/ButtonClick.vue";
import Emoji from "@/utils/components/Emoji.vue";
import MarkdownEditor from "@/utils/components/MarkdownEditor.vue";
export default {
  emits: ["postsResult", "loadingBegin"],
  components: {
    ButtonClick,
    Emoji,
    MarkdownEditor,
  },
  data() {
    return {
      content: "",
      posts: [],
      loading: false,
      richContent: {
        content: "",
        images: [],
        type: "text",
      },
      activeRichEditor: false,
      showPopover: false,
      showEmoji: false,
    };
  },

  methods: {
    normalPublish() {
      this.$emit("loadingBegin", true);
      this.loading = true;
      const formattedContent = this.content.replace(/\n/g, "<br>");
      postApi
        .publish_post({ content: formattedContent, type: "text" })
        .then((res) => {
          this.loading = false;
          this.$emit("postsResult", res);
          if (res.code === 200) {
            this.content = "";
            ElMessage.success("发布成功!");
          } else {
            ElMessage.error("发布失败!");
          }
        });
    },
    async richEditorPublish() {
      this.$emit("loadingBegin", true);
      this.loading = true;
      const images = await this.$refs.md.uploadPhotos();
      this.richContent.images = images;
      this.richContent.type = "markdown";
      postApi.publish_post(this.richContent).then((res) => {
        this.loading = false;
        this.$emit("postsResult", res);
        if (res.code === 200) {
          this.$refs.md.clean();
          ElMessage.success("发布成功!");
        } else {
          ElMessage.error("发布失败!");
        }
      });
    },
    publish() {
      if (this.activeRichEditor) {
        this.richEditorPublish();
      } else {
        this.normalPublish();
      }
    },
    insertEmoji(name) {
      this.content += name;
    },
  },
};
</script>

<template>
  <div class="text-title">
    <el-text>你在想什么？</el-text>
  </div>
  <Transition mode="out-in">
    <MarkdownEditor
      ref="md"
      v-if="activeRichEditor"
      @contentChange="(n) => (richContent = n)"
    />
    <div v-else>
      <el-input
        v-model="content"
        :autosize="{ minRows: 2, maxRows: 4 }"
        type="textarea"
        @focus="() => (showEmoji = true)"
        @blur="() => (showEmoji = false)"
        placeholder="书写片段,温润流年。"
      />
      <!-- <Emoji emoName="Heo_100" :offset="[-5,8]" @selectEmoji="insertEmoji" /> -->
      <!-- <Emoji emoName="dingtalk" :offset="[-35,8]" @selectEmoji="insertEmoji" /> -->
    </div>
  </Transition>

  <ButtonClick
    class="custom-button"
    content="发布"
    size="small"
    :disabled="!content && !richContent.content"
    :loading="loading"
    @do-search="publish"
  >
    <el-icon><i-ep-Pointer /></el-icon>
  </ButtonClick>
  <div class="switch">
    <el-button size="small" @click="$router.push('/pubImage')">图文 </el-button>
    <el-switch
      v-model="activeRichEditor"
      inline-prompt
      inactive-text="普通编辑器"
      active-text="Markdown编辑器"
    />
  </div>
</template>
<style lang="scss" scoped>
.text-title {
  margin: 10px 0;
}

:deep(.el-card__body) {
  padding: 5px;
}

.el-input {
  width: 100%;
}

.custom-button {
  margin: 10px 0;
}

.switch {
  float: right;
  margin-top: 10px;

  .el-switch {
    margin-left: 10px;
  }
}

// 过渡动画
.v-enter-active {
  transition: opacity 0.3s ease;
}

.v-enter-from {
  opacity: 0;
}
</style>
