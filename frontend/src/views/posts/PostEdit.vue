<script>
import postApi from "@/api/posts/postApi.js";
import ButtonClick from "@/utils/components/ButtonClick.vue";
import PageHeadBack from "@/utils/components/PageHeadBack.vue";
import MarkdownEditor from "@/utils/components/MarkdownEditor.vue";
import PageScroll from "@/utils/components/PageScroll.vue";

export default {
  components: {
    ButtonClick,
    PageHeadBack,
    MarkdownEditor,
    PageScroll,
  },
  data() {
    return {
      post: {},
      postId: -1,
      richContent: {
        content: "",
        images: [],
      },
      originalPost: "",
      isChange: false,
      loading: false,
      activeRichEditor: false,
    };
  },
  beforeRouteEnter(to, from, next) {
    next((vm) => {
      vm.postId = to.params.id;
      vm.getPostById(vm.postId);
    });
  },
  watch: {
    "post.content"(newVal) {
      this.isChange = newVal !== this.originalPost;
    },
    "richContent.content"(newVal) {
      this.isChange = newVal !== this.originalPost;
    },
  },
  methods: {
    getPostById(postId) {
      postApi.getPost(postId).then((res) => {
        if (res.code == 200) {
          this.originalPost = res.data.content;
          this.post = res.data;
          if (this.post.post_type === "markdown") {
            this.activeRichEditor = true;
          }
        }
      });
    },
    normalModify() {
      this.loading = true;
      postApi
        .editPost(this.post.id, { content: this.post.content })
        .then((res) => {
          if (res.code == 200) {
            this.loading = false;
            ElMessage.success("修改成功");
            this.$router.push(`/postDetail/${this.postId}`);
          } else {
            this.loading = false;
            ElMessage.success("修改失败");
          }
        });
    },
    async richEditorModify() {
      this.loading = true;
      const images = await this.$refs.md.uploadPhotos();
      this.richContent.images = images;
      postApi.editPost(this.post.id, this.richContent).then((res) => {
        if (res.code == 200) {
          this.loading = false;
          ElMessage.success("修改成功");
          this.post.content = this.richContent.content;
          this.$router.push(`/postDetail/${this.postId}`);
        } else {
          this.loading = false;
          ElMessage.success("修改失败");
        }
      });
    },
    modify() {
      if (this.activeRichEditor) {
        this.richEditorModify();
      } else {
        this.normalModify();
      }
    },
  },
};
</script>

<template>
  <PageHeadBack>
    <PageScroll max-height="calc(100vh - 45px - 47px)">
      <h1>编辑</h1>
      <h4>你在想什么？</h4>
      <MarkdownEditor
        ref="md"
        v-if="activeRichEditor"
        :bodyInit="post.content"
        @contentChange="(n) => (richContent = n)"
      />
      <el-input
        v-else
        v-model="post.content"
        :autosize="{ minRows: 2, maxRows: 4 }"
        type="textarea"
        placeholder="发你所想"
      />
      <ButtonClick
        content="修改"
        :loading="loading"
        :disabled="!isChange"
        @do-search="modify"
      />
    </PageScroll>
  </PageHeadBack>
</template>
<style lang="scss" scoped>
.el-button {
  margin-top: 10px;
}

.el-switch {
  float: right;
  margin-top: 10px;
}
</style>
