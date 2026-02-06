<template>
  <PageHeadBack>
    <div class="container">
      <el-input
        v-model="content"
        :autosize="{ minRows: 8 }"
        type="textarea"
        placeholder="书写片段，温润流年..."
        :input-style="inputStyle"
        minlength="5"
        maxlength="150"
        show-word-limit
      />
      <el-upload
        ref="uploadRef"
        v-model:file-list="originalFiles"
        list-type="picture-card"
        :auto-upload="false"
        :before-upload="() => false"
        accept="image/jpeg,image/png,image/jpg,image/webp"
        :on-change="handleFileChange"
        :on-preview="handlePictureCardPreview"
        :on-remove="handleFileRemove"
        :on-exceed="handleExceed"
        :limit="9"
        multiple
      >
        <el-icon><i-ep-Plus /></el-icon>
      </el-upload>

      <el-dialog v-model="dialogVisible">
        <img w-full :src="dialogImageUrl" alt="Preview Image" />
      </el-dialog>
      <div class="note">
        <el-text size="small">(图文 每日发布次数限定2次)</el-text>
      </div>
    </div>
    <template #action>
      <ButtonClick
        content="发布"
        size="small"
        :disabled="ban_pub"
        @do-search="submitBlog"
      >
        <el-icon><i-ep-Pointer /></el-icon>
      </ButtonClick>
    </template>
  </PageHeadBack>
</template>

<script>
import PageHeadBack from "@/utils/components/PageHeadBack.vue";
import ButtonClick from "@/utils/components/ButtonClick.vue";
import { useCurrentUserStore } from "@/stores/user";
import uploadApi from "@/api/upload/uploadApi.js";
import postApi from "@/api/posts/postApi.js";
import emitter from "@/utils/emitter.js";
import {
  compressImages,
  uploadFiles,
  beforePicUpload,
} from "@/utils/common.js";

export default {
  name: "BlogPost",
  props: {},
  components: {
    PageHeadBack,
    ButtonClick,
  },
  data() {
    return {
      content: "",
      imageUrls: [],
      uploading: false,
      imageKey: [],

      inputStyle: {
        width: "100%",
        marginBottom: "10px",
        borderColor: "#ffffff",
        boxShadow: "0 0 0 0 #ffffff",
      },
      dialogVisible: false,
      dialogImageUrl: "",
      // 原始文件
      originalFiles: [],
      // 压缩后的文件
      compressedImages: [],
    };
  },
  setup() {
    const currentUser = useCurrentUserStore();
    return { currentUser };
  },
  computed: {
    ban_pub() {
      return this.content === "" || this.originalFiles.length === 0;
    },
  },
  methods: {
    async getUploadToken() {
      const response = await uploadApi.get_upload_token();
      return response.data.upload_token;
    },
    async handleFileChange(file, fileList) {
      if (!beforePicUpload([file])) {
        return;
      }
      // 确保只添加新的文件
      const newFiles = fileList.filter(
        (f) => !this.originalFiles.some((of) => of.uid === f.uid)
      );
      this.originalFiles = [...this.originalFiles, ...newFiles];
      // console.log('文件列表:', this.originalFiles)
      // 压缩图像
      this.compressedImages = await compressImages(
        this.originalFiles,
        this.compressedImages
      );
    },
    handleFileRemove(file, fileList) {
      // 删除原始文件
      this.originalFiles = this.originalFiles.filter((f) => f.uid !== file.uid);
      // 删除压缩文件
      this.compressedImages = this.compressedImages.filter(
        (img) => img.uid !== file.uid
      );

      // console.log('文件已删除:', file.name)
      // console.log('当前原始文件列表:', this.originalFiles)
      // console.log('当前压缩文件列表:', this.compressedImages)
    },
    async submitBlog() {
      if (this.content === "") {
        ElMessage.error("内容不能为空");
        return;
      } else if (this.originalFiles.length === 0) {
        ElMessage.error("图片不能为空");
        return;
      }
      if (!beforePicUpload(this.originalFiles)) {
        return;
      }
      const loadingInstance = this.$loading({
        lock: true,
        text: "正在发布",
        background: "rgba(0, 0, 0, 0.7)",
      });
      try {
        // 获取上传凭证
        const uploadToken = await this.getUploadToken();
        // 上传图片
        const { imageKey, imageUrls } = await uploadFiles(
          this.compressedImages,
          this.currentUser.uploadArticlesBaseUrl,
          uploadToken
        );
        this.imageKey = imageKey;
        this.imageUrls = imageUrls;
        const formattedContent = this.content.replace(/\n/g, "<br>");
        postApi
          .publishRichPost({
            content: formattedContent,
            imageUrls: this.imageKey,
          })
          .then((response) => {
            if (response.code === 200) {
              ElMessage.success("发布成功");
              this.content = "";
              this.originalFiles = [];
              emitter.emit("newPost", response.data);
              this.$router.push("/posts");
            }
            loadingInstance.close();
          })
          .catch((error) => {
            loadingInstance.close();
            if (error.response.status === 429) {
              uploadApi.del_image(this.imageKey);
              ElMessage.info("今天的发布次数已达上限～");
            }
          });
      } catch (error) {
        loadingInstance.close();
      }
    },
    handlePictureCardPreview(uploadFile) {
      this.dialogImageUrl = uploadFile.url;
      this.dialogVisible = true;
    },
    handleExceed() {
      ElMessage.info("最多只能上传9张图片");
    },
  },
};
</script>

<style lang="scss" scoped>
.container {
  display: flex;
  flex-direction: column;
  align-items: flex-start;

  :deep(.el-textarea__inner) {
    resize: none;
  }

  .note {
    padding: 5px;
  }

  img {
    width: 100%;
  }
}
</style>
