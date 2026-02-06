<template>
  <div class="container">
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
  </div>
  <ButtonClick
    class="button"
    content="上传"
    size="small"
    :disabled="ban_pub"
    @do-search="submitBlog"
  >
    <el-icon><i-ep-Pointer /></el-icon>
  </ButtonClick>
</template>

<script>
import PageHeadBack from "@/utils/components/PageHeadBack.vue";
import ButtonClick from "@/utils/components/ButtonClick.vue";
import uploadApi from "@/api/upload/uploadApi.js";

import {
  compressImages,
  uploadFiles,
  beforePicUpload,
} from "@/utils/common.js";

export default {
  name: "BlogPost",
  props: {
    title: {
      type: String,
      default: "背景",
    },
    uploadPath: {
      type: String,
      default: "",
    },
  },
  components: {
    PageHeadBack,
    ButtonClick,
  },
  emits: ["upload-success"],
  data() {
    return {
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
      // 默认压缩比率为80%
      compressedRatio: 80,
    };
  },
  computed: {
    ban_pub() {
      return this.originalFiles.length === 0;
    },
  },

  methods: {
    async getUploadToken() {
      const response = await uploadApi.get_upload_token();
      return response.data.upload_token;
    },
    debounce(func, wait) {
      let timeout;
      return function (...args) {
        const context = this;
        clearTimeout(timeout);
        timeout = setTimeout(() => {
          func.apply(context, args);
        }, wait);
      };
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

    handleFileRemove(file) {
      // 删除原始文件
      this.originalFiles = this.originalFiles.filter((f) => f.uid !== file.uid);
      // 删除压缩文件
      this.compressedImages = this.compressedImages.filter(
        (img) => img.uid !== file.uid
      );
    },
    async submitBlog() {
      if (this.originalFiles.length === 0) {
        ElMessage.error("图片不能为空");
        return;
      }
      if (!beforePicUpload(this.originalFiles)) {
        return;
      }
      const loadingInstance = this.$loading({
        lock: true,
        text: "Loading",
        background: "rgba(0, 0, 0, 0.7)",
      });
      try {
        // 获取上传凭证
        const uploadToken = await this.getUploadToken();
        // 上传图片
        await uploadFiles(this.compressedImages, this.uploadPath, uploadToken);
        this.originalFiles = [];
        this.compressedImages = [];
        loadingInstance.close();
        this.$emit("upload-success");
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
}

img {
  width: 100%;
}

.button {
  margin-top: 20px;
}
</style>
