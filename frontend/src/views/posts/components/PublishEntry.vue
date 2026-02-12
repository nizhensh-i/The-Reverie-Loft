<template>
  <div class="publish-entry">
    <!-- 浮动发布按钮 -->
    <div class="publish-fab" @click="showPublishPanel = true">
      <el-button type="primary" circle size="large">
        <el-icon><i-ep-Edit /></el-icon>
      </el-button>
    </div>

    <!-- 发布面板 -->
    <el-drawer
      v-model="showPublishPanel"
      title="发布内容"
      direction="ttb"
      size="auto"
      :show-close="true"
      :with-header="true"
      custom-class="publish-drawer"
    >
      <div class="publish-options">
        <div class="publish-header">
          <h3>选择发布类型</h3>
        </div>

        <div class="publish-types">
          <div
            class="publish-type-item"
            :class="{ active: activeType === 'text' }"
            @click="selectPublishType('text')"
          >
            <el-icon class="publish-icon"><i-ep-ChatDotRound /></el-icon>
            <span>说说</span>
            <div class="type-desc">发布简短的文字内容</div>
          </div>

          <div
            class="publish-type-item"
            :class="{ active: activeType === 'image' }"
            @click="selectPublishType('image')"
          >
            <el-icon class="publish-icon"><i-ep-Picture /></el-icon>
            <span>图文</span>
            <div class="type-desc">发布图片和文字内容</div>
          </div>

          <div
            class="publish-type-item"
            :class="{ active: activeType === 'markdown' }"
            @click="selectPublishType('markdown')"
          >
            <el-icon class="publish-icon"><i-ep-Document /></el-icon>
            <span>Markdown</span>
            <div class="type-desc">使用Markdown编辑器发布富文本内容</div>
          </div>
        </div>

        <div class="publish-content">
          <!-- 说说发布 -->
          <div v-if="activeType === 'text'" class="text-publish">
            <el-input
              v-model="textContent"
              type="textarea"
              :autosize="{ minRows: 4, maxRows: 8 }"
              placeholder="书写片段，温润流年..."
              maxlength="310"
              show-word-limit
              :class="{ 'fade-in': showTextAnimation }"
            />
            <!-- 辅助创作 -->
            <CreativeAssist @contentGenerated="handleContentGenerated" />
            <!-- <div class="emoji-container">
              <Emoji emoName="Heo_100" :offset="[-5,8]" @selectEmoji="insertEmoji" />
            </div> -->
          </div>

          <!-- 图文发布 -->
          <div v-if="activeType === 'image'" class="image-publish">
            <el-input
              v-model="imageContent"
              class="image-text"
              type="textarea"
              :autosize="{ minRows: 3, maxRows: 6 }"
              placeholder="书写片段，温润流年..."
              maxlength="150"
              show-word-limit
            />
            <el-upload
              ref="uploadRef"
              v-model:file-list="imageFiles"
              list-type="picture-card"
              :auto-upload="false"
              :before-upload="() => false"
              accept="image/jpeg,image/png,image/jpg,image/webp"
              :on-preview="handlePictureCardPreview"
              :on-exceed="() => $message.info('最多只能上传9张图片')"
              :limit="9"
              multiple
            >
              <el-icon><i-ep-Plus /></el-icon>
            </el-upload>
            <el-dialog v-model="previewVisible">
              <img w-full :src="previewUrl" alt="Preview Image" />
            </el-dialog>
            <div class="note">
              <el-text size="small">(图文 每日发布次数限定2次)</el-text>
            </div>
          </div>

          <!-- Markdown发布 -->
          <div v-if="activeType === 'markdown'" class="markdown-publish">
            <MarkdownEditor
              ref="md"
              @contentChange="(n) => (markdownContent = n)"
            />
          </div>
        </div>

        <div class="publish-actions">
          <el-button @click="showPublishPanel = false">取消</el-button>
          <el-button
            type="primary"
            :loading="publishing"
            :disabled="!canPublish"
            @click="publishContent"
          >
            发布
          </el-button>
        </div>
      </div>
    </el-drawer>
  </div>
</template>

<script>
import Emoji from "@/utils/components/Emoji.vue";
import MarkdownEditor from "@/utils/components/MarkdownEditor.vue";
import CreativeAssist from "./CreativeAssist.vue";
import postApi from "@/api/posts/postApi.js";
import uploadApi from "@/api/upload/uploadApi.js";
import { useCurrentUserStore } from "@/stores/user";
import {
  compressImages,
  uploadFiles,
  beforePicUpload,
} from "@/utils/common.js";

export default {
  name: "PublishEntry",
  components: {
    Emoji,
    MarkdownEditor,
    CreativeAssist,
  },
  emits: ["newPost", "loadingBegin"],
  data() {
    return {
      showPublishPanel: false,
      activeType: "text",
      publishing: false,
      showTextAnimation: false,

      // 说说内容
      textContent: "",

      // 图文内容
      imageContent: "",
      imageFiles: [],
      compressedImages: [],
      previewVisible: false,
      previewUrl: "",

      // Markdown内容
      markdownContent: {
        content: "",
        images: [],
        type: "markdown",
      },
    };
  },
  setup() {
    const currentUser = useCurrentUserStore();
    return { currentUser };
  },
  computed: {
    canPublish() {
      switch (this.activeType) {
        case "text":
          return this.textContent.trim().length >= 3;
        case "image":
          return (
            this.imageContent.trim().length >= 3 && this.imageFiles.length > 0
          );
        case "markdown":
          return this.markdownContent.content.trim().length >= 3;
        default:
          return false;
      }
    },
  },
  methods: {
    selectPublishType(type) {
      this.activeType = type;
    },

    insertEmoji(name) {
      this.textContent += name;
    },

    handlePictureCardPreview(file) {
      this.previewUrl = file.url;
      this.previewVisible = true;
    },

    handleContentGenerated(content) {
      this.showTextAnimation = false;
      this.$nextTick(() => {
        this.textContent = content;
        this.showTextAnimation = true;
        setTimeout(() => {
          this.showTextAnimation = false;
        }, 400);
      });
    },

    async publishContent() {
      this.publishing = true;
      this.$emit("loadingBegin", true);

      try {
        let result;

        switch (this.activeType) {
          case "text":
            result = await this.publishText();
            break;
          case "image":
            result = await this.publishImage();
            break;
          case "markdown":
            result = await this.publishMarkdown();
            break;
        }

        if (result && result.code === 200) {
          ElMessage.success("发布成功!");
          this.resetForm();
          this.showPublishPanel = false;
          this.$emit("newPost", result.data);
        }
      } catch (error) {
        console.error("发布失败:", error);
      } finally {
        this.publishing = false;
        this.$emit("loadingBegin", false);
      }
    },

    async publishText() {
      // 替换换行符为 <br>
      const formattedContent = this.textContent.replace(/\n/g, "<br>");
      return await postApi.publish_post({
        content: formattedContent,
        images: [],
        type: "text",
      });
    },

    async publishImage() {
      if (!beforePicUpload(this.imageFiles)) {
        throw new Error("图片格式或大小不符合要求");
      }

      // 压缩图像
      this.compressedImages = await compressImages(this.imageFiles, []);

      // 获取上传凭证
      const uploadToken = await this.getUploadToken();

      // 上传图片
      const { imageKey } = await uploadFiles(
        this.compressedImages,
        this.currentUser.uploadArticlesBaseUrl,
        uploadToken
      );

      const formattedContent = this.imageContent.replace(/\n/g, "<br>");
      return await postApi.publish_post({
        content: formattedContent,
        images: imageKey,
        type: "image",
      });
    },

    async publishMarkdown() {
      const images = await this.$refs.md.uploadPhotos();
      this.markdownContent.images = images;
      this.markdownContent.type = "markdown";
      return await postApi.publish_post(this.markdownContent);
    },

    async getUploadToken() {
      const response = await uploadApi.get_upload_token();
      return response.data.upload_token;
    },

    resetForm() {
      this.textContent = "";
      this.imageContent = "";
      this.imageFiles = [];
      this.compressedImages = [];
      if (this.$refs.md) {
        this.$refs.md.clean();
      }
    },
  },
};
</script>

<style lang="scss" scoped>
.publish-entry {
  position: relative;
}

.publish-fab {
  position: fixed;
  right: 20px;
  bottom: 80px;
  z-index: 1555;

  .el-button {
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.2);
    transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);

    &:hover {
      transform: scale(1.1) rotate(15deg);
    }
  }
}

.publish-drawer {
  border-radius: 16px 16px 0 0;
  overflow: hidden;
}

.publish-options {
  padding: 0 20px 20px;

  .publish-header {
    margin-bottom: 20px;
    text-align: center;

    h3 {
      font-size: 18px;
      font-weight: 500;
      color: #303133;
    }
  }
}

.publish-types {
  display: flex;
  justify-content: space-around;
  margin-bottom: 24px;

  .publish-type-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    width: 30%;
    padding: 16px;
    cursor: pointer;
    border-radius: 12px;
    transition: all 0.3s ease;

    &:hover {
      background-color: #f5f7fa;
    }

    &.active {
      background-color: #ecf5ff;
      border: 1px solid #d9ecff;

      .publish-icon {
        color: #409eff;
      }
    }

    .publish-icon {
      margin-bottom: 8px;
      font-size: 24px;
    }

    span {
      margin-bottom: 4px;
      font-size: 16px;
      font-weight: 500;
    }

    .type-desc {
      font-size: 12px;
      color: #909399;
      text-align: center;
    }
  }
}

.publish-content {
  min-height: 200px;
  margin-bottom: 24px;

  .text-publish,
  .image-publish,
  .markdown-publish {
    animation: fadeIn 0.3s ease;
  }

  .emoji-container {
    margin-top: 8px;
  }

  .note {
    margin-top: 8px;
    color: #909399;
  }
}

.image-text {
  margin-bottom: 5px;
}

.publish-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.fade-in {
  animation: textFadeIn 0.4s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes textFadeIn {
  from {
    opacity: 0.3;
  }
  to {
    opacity: 1;
  }
}
</style>
