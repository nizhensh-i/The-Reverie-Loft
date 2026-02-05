<template>
  <div class="container">
    <PageScroll max-height="calc(100vh - 45px - 40px - 60px)">
      <!-- 功能标签页 -->
      <el-tabs
        v-model="activeTab"
        class="tabs-container"
        @tab-change="handleTabChange"
      >
        <!-- 上传图像标签页 -->
        <el-tab-pane label="上传图像" name="upload">
          <ImageUpload
            :title="uploadTitle"
            :uploadPath="uploadPath"
            @upload-success="handleUploadSuccess"
          />
        </el-tab-pane>

        <!-- 管理图像标签页 -->
        <el-tab-pane label="管理图像" name="manage">
          <!-- 图像列表 -->
          <div class="image-grid">
            <div v-if="images.length === 0 && !loading" class="empty-state">
              <el-icon class="empty-icon"><i-ep-Picture /></el-icon>
              <div class="empty-text">暂无{{ uploadTitle }}</div>
              <div class="empty-tip">请先上传{{ uploadTitle }}</div>
            </div>

            <div class="images-wrapper" v-show="images.length > 0">
              <el-row :gutter="currentGutter">
                <el-col
                  :xs="imageCol.xs"
                  :sm="imageCol.sm"
                  :md="imageCol.md"
                  :lg="imageCol.lg"
                  :xl="imageCol.xl"
                  v-for="(image, index) in images"
                  :key="image"
                >
                  <el-skeleton :loading="loadingImages.has(image)" animated>
                    <template #template>
                      <div class="skeleton-item">
                        <el-skeleton-item
                          variant="image"
                          style="height: 200px; border-radius: 12px 12px 0 0"
                        />
                        <div style="padding: 12px">
                          <el-skeleton-item
                            variant="text"
                            style="width: 80%; margin: 0 auto"
                          />
                        </div>
                      </div>
                    </template>
                    <template #default>
                      <div
                        class="image-item"
                        :class="{
                          selected: selectedImages.includes(image),
                          'fade-in': imageFadeIn.has(image),
                        }"
                        @click="toggleImageSelection(image)"
                      >
                        <!-- 选择状态指示器 -->
                        <div
                          class="selection-indicator"
                          :class="{ checked: selectedImages.includes(image) }"
                        >
                          <el-icon><i-ep-Check /></el-icon>
                        </div>

                        <!-- 图像容器 -->
                        <div class="image-container">
                          <el-image
                            :src="image"
                            fit="cover"
                            loading="lazy"
                            class="image-preview"
                            @load="onImageLoad(image, index)"
                            @error="onImageError(image)"
                          >
                            <template #error>
                              <div class="image-error">
                                <el-icon><i-ep-Picture /></el-icon>
                                <span>加载失败</span>
                              </div>
                            </template>
                          </el-image>
                        </div>

                        <!-- 图像信息 -->
                        <div class="image-info">
                          <div class="image-name">
                            {{ getImageName(image) }}
                          </div>
                          <div class="image-actions">
                            <el-button
                              size="small"
                              type="primary"
                              link
                              @click.stop="previewImage(image)"
                            >
                              <el-icon><i-ep-View /></el-icon>
                              预览
                            </el-button>
                            <el-button
                              size="small"
                              type="danger"
                              link
                              @click.stop="deleteSingleImage(image)"
                            >
                              <el-icon><i-ep-Delete /></el-icon>
                              删除
                            </el-button>
                          </div>
                        </div>
                      </div>
                    </template>
                  </el-skeleton>
                </el-col>
              </el-row>
            </div>
          </div>

          <!-- 分页 -->
          <div class="pagination-container" v-if="images.length > 0">
            <el-pagination
              v-model:current-page="query.currentPage"
              v-model:page-size="query.size"
              :page-sizes="[12, 24, 48]"
              :total="query.total"
              size="small"
              layout="total, sizes, prev, pager, next"
              @size-change="handleSizeChange"
              @current-change="handleCurrentChange"
            />
          </div>

          <!-- 操作按钮 -->
          <div class="action-bar" v-if="images.length > 0">
            <el-button
              type="danger"
              :disabled="selectedImages.length === 0"
              @click="handleDeleteSelected"
              :loading="deleting"
            >
              <el-icon><i-ep-Delete /></el-icon>
              删除选中 ({{ selectedImages.length }})
            </el-button>
            <el-button @click="handleRefresh">
              <el-icon><i-ep-Refresh /></el-icon>
              刷新列表
            </el-button>
          </div>
        </el-tab-pane>
      </el-tabs>
    </PageScroll>
  </div>
</template>

<script>
import PageHeadBack from "@/utils/components/PageHeadBack.vue";
import PageScroll from "@/utils/components/PageScroll.vue";
import ImageUpload from "./ImageUpload.vue";
import uploadApi from "@/api/upload/uploadApi.js";
import { ElMessage, ElMessageBox } from "element-plus";
import { h } from "vue";

export default {
  name: "ImageManager",
  components: {
    PageHeadBack,
    ImageUpload,
    PageScroll,
  },
  props: {
    uploadTitle: {
      type: String,
      required: true,
    },
    uploadPath: {
      type: String,
      required: true,
    },
    loadImagesMethod: {
      type: Function,
      required: true,
    },
  },
  data() {
    return {
      // 标签页
      activeTab: "upload",

      // 管理功能相关
      images: [],
      selectedImages: [],
      loading: false,
      deleting: false,
      query: {
        currentPage: 1,
        size: 12,
        total: 0,
      },

      // 新增状态
      loadingImages: new Set(),
      imageFadeIn: new Set(),

      // 响应式配置
      imageCol: {
        xs: 12, // 移动端：每行2个
        sm: 12, // 平板：每行2个
        md: 8, // 小PC：每行3个
        lg: 6, // 中PC：每行4个
        xl: 6, // 大PC：每行4个
      },
      currentGutter: 16, // 当前使用的gutter值
    };
  },
  mounted() {
    this.loadImages();
    this.setupResponsiveConfig();
  },
  beforeUnmount() {
    // 清理事件监听器
    if (typeof this.cleanupResponsive === "function") {
      this.cleanupResponsive();
    }
  },
  methods: {
    // 设置响应式配置
    setupResponsiveConfig() {
      const updateConfig = () => {
        const width = window.innerWidth;
        if (width < 576) {
          // 移动端
          this.imageCol = { xs: 12, sm: 12, md: 8, lg: 6, xl: 6 };
          this.currentGutter = 8;
        } else if (width < 768) {
          // 平板竖屏
          this.imageCol = { xs: 12, sm: 12, md: 8, lg: 6, xl: 6 };
          this.currentGutter = 12;
        } else if (width < 992) {
          // 平板横屏/小PC
          this.imageCol = { xs: 12, sm: 12, md: 8, lg: 6, xl: 6 };
          this.currentGutter = 16;
        } else if (width < 1200) {
          // 中PC
          this.imageCol = { xs: 12, sm: 12, md: 6, lg: 6, xl: 6 };
          this.currentGutter = 20;
        } else {
          // 大PC
          this.imageCol = { xs: 12, sm: 12, md: 6, lg: 6, xl: 4 };
          this.currentGutter = 24;
        }
      };

      updateConfig();
      window.addEventListener("resize", updateConfig);

      // 存储清理函数
      this.cleanupResponsive = () => {
        window.removeEventListener("resize", updateConfig);
      };
    },

    // 标签页切换
    handleTabChange(tabName) {
      if (tabName === "manage") {
        this.loadImages();
      }
    },

    // 上传成功回调
    handleUploadSuccess() {
      this.activeTab = "manage";
      this.loadImages();
      ElMessage.success(`${this.uploadTitle}上传成功，已切换到管理页面`);
    },

    // ========== 图像管理相关方法 ==========
    async loadImages() {
      this.loading = true;
      this.loadingImages.clear();
      this.imageFadeIn.clear();
      try {
        console.log("Loading images with params:", {
          page: this.query.currentPage,
          size: this.query.size,
          method: this.loadImagesMethod.name,
        });

        const response = await this.loadImagesMethod(
          this.query.currentPage,
          this.query.size
        );

        console.log("API response:", response);

        if (response && response.code === 200) {
          this.images = Array.isArray(response.data) ? response.data : [];
          this.query.total = response.total || 0;

          // 为每个图像设置加载状态
          this.images.forEach((image, index) => {
            this.loadingImages.add(image);
            // 错开显示动画，创造流畅的进入效果
            setTimeout(() => {
              this.onImageLoad(image, index);
            }, index * 100); // 每个图像延迟100ms
          });

          console.log("Images loaded:", this.images.length);
        } else {
          console.error("API response error:", response);
          ElMessage.error(response?.message || "加载图像列表失败");
          this.images = [];
        }
      } catch (error) {
        console.error("加载图像列表失败:", error);
        ElMessage.error("加载图像列表失败");
        this.images = [];
      } finally {
        this.loading = false;
      }
    },

    handleSizeChange(size) {
      this.query.size = size;
      this.query.currentPage = 1;
      this.loadImages();
    },

    handleCurrentChange(page) {
      this.query.currentPage = page;
      this.loadImages();
    },

    handleRefresh() {
      this.selectedImages = [];
      this.loadImages();
    },

    // 图像加载成功
    onImageLoad(imageUrl, index) {
      this.loadingImages.delete(imageUrl);
      setTimeout(() => {
        this.imageFadeIn.add(imageUrl);
      }, index * 100); // 错开动画时间
    },

    // 图像加载失败
    onImageError(imageUrl) {
      this.loadingImages.delete(imageUrl);
    },

    // 切换图像选择状态
    toggleImageSelection(imageUrl) {
      const index = this.selectedImages.indexOf(imageUrl);
      if (index > -1) {
        this.selectedImages.splice(index, 1);
      } else {
        this.selectedImages.push(imageUrl);
      }
    },

    // 预览图像
    previewImage(imageUrl) {
      ElMessageBox({
        title: "图像预览",
        message: h("div", [
          h("img", {
            src: imageUrl,
            style: "width: 100%; max-height: 70vh; object-fit: contain;",
          }),
          h(
            "div",
            {
              style: "text-align: center; margin-top: 10px; color: #666;",
            },
            this.getImageName(imageUrl)
          ),
        ]),
        showConfirmButton: false,
        closeOnClickModal: true,
        closeOnPressEscape: true,
        customClass: "image-preview-dialog",
      });
    },

    // 删除单个图像
    async deleteSingleImage(imageUrl) {
      try {
        await ElMessageBox.confirm(
          `确定要删除"${this.getImageName(imageUrl)}"吗？此操作不可撤销。`,
          "确认删除",
          {
            confirmButtonText: "确定",
            cancelButtonText: "取消",
            type: "warning",
          }
        );

        const imageKeys = [imageUrl].map((url) => this.getImageKey(url));

        const response = await uploadApi.del_image(imageKeys);
        if (response.code === 200) {
          ElMessage.success("删除成功");
          this.loadImages();
        } else {
          ElMessage.error(response.message || "删除失败");
        }
      } catch (error) {
        if (error !== "cancel") {
          console.error("删除图像失败:", error);
          ElMessage.error("删除图像失败");
        }
      }
    },

    async handleDeleteSelected() {
      if (this.selectedImages.length === 0) {
        ElMessage.warning(`请选择要删除的${this.uploadTitle}`);
        return;
      }

      try {
        await ElMessageBox.confirm(
          `确定要删除选中的 ${this.selectedImages.length} 张${this.uploadTitle}吗？此操作不可撤销。`,
          "确认删除",
          {
            confirmButtonText: "确定",
            cancelButtonText: "取消",
            type: "warning",
          }
        );

        this.deleting = true;

        const imageKeys = this.selectedImages.map((url) =>
          this.getImageKey(url)
        );

        const response = await uploadApi.del_image(imageKeys);
        if (response.code === 200) {
          ElMessage.success("删除成功");
          this.selectedImages = [];
          this.loadImages();
        } else {
          ElMessage.error(response.message || "删除失败");
        }
      } catch (error) {
        if (error !== "cancel") {
          console.error("删除图像失败:", error);
          ElMessage.error("删除图像失败");
        }
      } finally {
        this.deleting = false;
      }
    },

    // 提取图像键值的通用方法
    getImageKey(imageUrl) {
      try {
        const urlObj = new URL(imageUrl);
        let key = urlObj.pathname.substring(1);
        if (key.endsWith("-slim")) {
          key = key.slice(0, -5);
        }
        return key;
      } catch {
        return imageUrl;
      }
    },

    getImageName(imageUrl) {
      try {
        const url = new URL(imageUrl);
        return url.pathname.split("/").pop() || "未知文件";
      } catch {
        return imageUrl.split("/").pop() || "未知文件";
      }
    },
  },
};
</script>

<style lang="scss" scoped>
.container {
  padding: 20px;
}

.tabs-container {
  width: 100%;

  :deep(.el-tabs__header) {
    margin-bottom: 24px;
  }

  :deep(.el-tabs__nav-wrap) {
    &::after {
      display: none;
    }
  }
}

// ========== 管理页面样式 ==========
.image-grid {
  margin-bottom: 20px;
  min-height: 400px;
  background: #fafafa;
  border-radius: 12px;
  position: relative;
}

.images-wrapper {
  width: 100%;
  min-height: 300px;
  position: relative;
}

.image-item {
  position: relative;
  margin-bottom: 20px;
  border-radius: 12px;
  overflow: hidden;
  background: #fff;
  border: 1px solid #e4e7ed;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  opacity: 0;
  transform: translateY(20px);
  min-height: 240px; // 确保有最小高度
  display: flex;
  flex-direction: column;

  &.fade-in {
    opacity: 1;
    transform: translateY(0);
  }

  &:hover {
    transform: translateY(-8px);
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
    border-color: #409eff;

    .selection-indicator {
      opacity: 1;
    }

    .image-info {
      .image-actions {
        opacity: 1;
        transform: translateY(0);
      }
    }
  }

  &.selected {
    border: 2px solid #409eff;
    box-shadow: 0 0 0 4px rgba(64, 158, 255, 0.15),
      0 20px 40px rgba(0, 0, 0, 0.15);
    background: linear-gradient(135deg, #f0f9ff 0%, #e6f7ff 100%);
  }
}

// 选择状态指示器
.selection-indicator {
  position: absolute;
  top: 12px;
  right: 12px;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.95);
  border: 2px solid #dcdfe6;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10;
  opacity: 0.7;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);

  &:hover {
    transform: scale(1.1);
    border-color: #409eff;
  }

  &.checked {
    background: #409eff;
    border-color: #409eff;
    opacity: 1;
    transform: scale(1.1);

    .el-icon {
      color: white;
      font-size: 16px;
      animation: checkBounce 0.3s ease-out;
    }
  }

  .el-icon {
    color: #909399;
    font-size: 14px;
    transition: all 0.3s ease;
  }
}

// 图像容器
.image-container {
  position: relative;
  width: 100%;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;

  &:hover .image-preview {
    transform: scale(1.05);
  }
}

.image-preview {
  width: 100%;
  height: 200px;
  display: block;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border-radius: 12px 12px 0 0;
  object-fit: cover;
}

// 图像信息
.image-info {
  padding: 12px;
  background: linear-gradient(
    135deg,
    rgba(255, 255, 255, 0.98) 0%,
    rgba(248, 250, 252, 0.95) 100%
  );
  border-radius: 0 0 12px 12px;
  border-top: 1px solid rgba(240, 240, 240, 0.8);
}

.image-name {
  font-size: 13px;
  color: #303133;
  font-weight: 500;
  margin-bottom: 8px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  text-align: center;
  letter-spacing: 0.5px;
}

.image-actions {
  display: flex;
  justify-content: center;
  gap: 8px;
  opacity: 0;
  transform: translateY(10px);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);

  .el-button {
    border-radius: 8px;
    font-size: 12px;
    padding: 4px 8px;
    height: 28px;

    &.is-link {
      border: none;
      background: rgba(64, 158, 255, 0.1);

      &:hover {
        background: rgba(64, 158, 255, 0.2);
        transform: translateY(-2px);
      }

      &.el-button--danger {
        background: rgba(245, 108, 108, 0.1);

        &:hover {
          background: rgba(245, 108, 108, 0.2);
        }
      }
    }
  }
}

// 错误状态
.image-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 200px;
  background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
  color: #ef4444;
  font-size: 14px;
  border-radius: 12px 12px 0 0;

  .el-icon {
    font-size: 32px;
    margin-bottom: 8px;
  }
}

@keyframes checkBounce {
  0% {
    transform: scale(0.8);
  }
  50% {
    transform: scale(1.2);
  }
  100% {
    transform: scale(1);
  }
}

// ========== 骨架屏样式 ==========
.skeleton-item {
  position: relative;
  margin-bottom: 20px;
  border-radius: 12px;
  overflow: hidden;
  background: #fff;
  border: 1px solid #e4e7ed;
  min-height: 240px;
  display: flex;
  flex-direction: column;
}

.pagination-container {
  display: flex;
  justify-content: center;
  margin: 32px 0;
}

.action-bar {
  display: flex;
  justify-content: center;
  gap: 16px;
  margin-top: 32px;
  padding: 24px;
  background: linear-gradient(135deg, #fafbfc 0%, #f5f7fa 100%);
  border-radius: 12px;
  border: 1px solid #f0f0f0;
  .el-button {
    border-radius: 10px;
    padding: 14px 15px;
    font-weight: 600;
    font-size: 14px;
    letter-spacing: 0.5px;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    border: none;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  }
}

// ========== 空状态样式 ==========
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 300px;
  color: #909399;

  .empty-icon {
    font-size: 64px;
    margin-bottom: 16px;
    opacity: 0.5;
  }

  .empty-text {
    font-size: 16px;
    margin-bottom: 8px;
    font-weight: 500;
  }

  .empty-tip {
    font-size: 14px;
    opacity: 0.7;
  }
}
</style>
