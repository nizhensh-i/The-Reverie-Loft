<template>
  <PageHeadBack title="管理公共图像">
    <ImageManager
      upload-title="公共图像"
      :upload-path="uploadPath"
      :load-images-method="loadImagesMethod"
    />
  </PageHeadBack>
</template>

<script>
import PageHeadBack from "@/utils/components/PageHeadBack.vue";
import ImageManager from "./ImageManager.vue";
import imageApi from "@/api/user/imageApi.js";
import { useCurrentUserStore } from "@/stores/user";

export default {
  name: "AvatarsManager",
  components: {
    ImageManager,
    PageHeadBack,
  },
  computed: {
    uploadPath() {
      const currentUser = useCurrentUserStore();
      return currentUser.userAvatars;
    },
    loadImagesMethod() {
      return imageApi.getPublicImages;
    },
  },
};
</script>
