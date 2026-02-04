<template>
  <PageHeadBack title="管理背景图片">
    <el-tabs v-model="activeDeviceTab" class="tabs-container">
      <el-tab-pane label="移动端" name="mobile" lazy>
        <ImageManager
          title="移动端背景图片"
          upload-title="移动端背景图片"
          :upload-path="mobileUploadPath"
          :load-images-method="mobileLoadImagesMethod"
          :show-header="false"
        />
      </el-tab-pane>
      <el-tab-pane label="电脑端" name="pc" lazy>
        <ImageManager
          title="电脑端背景图片"
          upload-title="电脑端背景图片"
          :upload-path="pcUploadPath"
          :load-images-method="pcLoadImagesMethod"
          :show-header="false"
        />
      </el-tab-pane>
    </el-tabs>
  </PageHeadBack>
</template>

<script>
import ImageManager from "./ImageManager.vue";
import imageApi from "@/api/user/imageApi.js";
import { useCurrentUserStore } from "@/stores/user";
import PageHeadBack from "@/utils/components/PageHeadBack.vue";

export default {
  name: "BackgroundImageManager",
  components: {
    PageHeadBack,
    ImageManager,
  },
  data() {
    return {
      activeDeviceTab: "mobile",
    };
  },
  computed: {
    mobileUploadPath() {
      const currentUser = useCurrentUserStore();
      return currentUser.userBackgroundUrl;
    },
    pcUploadPath() {
      const currentUser = useCurrentUserStore();
      return currentUser.userPcBackgroundUrl;
    },
    mobileLoadImagesMethod() {
      // 返回一个包装函数，处理特殊的参数
      return (currentPage, size) => {
        const currentUser = useCurrentUserStore();
        return imageApi.getBackgroundImage(
          currentPage,
          size,
          currentUser.userBackgroundUrl,
          1
        );
      };
    },
    pcLoadImagesMethod() {
      return (currentPage, size) => {
        const currentUser = useCurrentUserStore();
        return imageApi.getBackgroundImage(
          currentPage,
          size,
          currentUser.userPcBackgroundUrl,
          1
        );
      };
    },
  },
};
</script>
