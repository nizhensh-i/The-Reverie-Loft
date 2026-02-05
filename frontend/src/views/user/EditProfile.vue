<script>
import {
  compressImages,
  uploadFiles,
  beforePicUpload,
} from "@/utils/common.js";
import PageHeadBack from "@/utils/components/PageHeadBack.vue";
import PageScroll from "@/utils/components/PageScroll.vue";
import { useCurrentUserStore } from "@/stores/user";
import { useOtherUserStore } from "@/stores/otherUser";
import { cloneDeep } from "@pureadmin/utils";
import { areaList } from "@vant/area-data";
import uploadApi from "@/api/upload/uploadApi.js";
import emitter from "@/utils/emitter.js";
import imageApi from "@/api/user/imageApi.js";
import editApi from "@/api/user/editApi.js";
import userApi from "@/api/user/userApi.js";

export default {
  components: {
    PageHeadBack,
    PageScroll,
  },
  data() {
    return {
      loading: {
        tag: false,
      },
      tagList: [],
      selectedTags: [],

      imgList: [],
      sexShow: false,
      cityShow: false,
      tagShow: false,

      imageKey: [],
      imageUrls: [],
      // 原始文件
      originalFiles: [],
      // 压缩后的文件
      compressedImages: [],
      localUserInfo: {
        sex: "",
        tags: [],
      },
    };
  },
  setup() {
    const currentUser = useCurrentUserStore();
    const other = useOtherUserStore();
    return { areaList, currentUser, other };
  },
  computed: {
    tagAdd() {
      return this.selectedTags.filter(
        (tag) => !this.localUserInfo.tags.includes(tag)
      );
    },
    tagRemove() {
      return this.localUserInfo.tags.filter(
        (tag) => !this.selectedTags.includes(tag)
      );
    },
    tagChange() {
      return this.tagAdd.length > 0 || this.tagRemove.length > 0;
    },
    tag() {
      return this.selectedTags.join(" ");
    },
  },
  mounted() {
    this.localUserInfo = cloneDeep(this.currentUser.userInfo);
    this.selectedTags = [...this.currentUser.userInfo.tags];
    this.imgList.push(this.currentUser.userInfo.image);
  },
  methods: {
    getTagList() {
      this.loading.tag = true;
      userApi
        .get_tag_list()
        .then((res) => {
          // 适配新的统一接口返回格式
          if (res.code === 200) {
            // 新格式
            this.tagList = res.data;
          } else {
            ElMessage.error("获取标签列表失败");
          }
          this.loading.tag = false;
        })
        .catch((error) => {
          this.loading.tag = false;
          ElMessage.error("获取标签列表失败");
          console.error(error);
        });
    },
    async setCity() {
      const loading = ElLoading.service({
        lock: true,
        text: "正在保存",
        background: "rgba(0, 0, 0, 0.7)",
      });
      await editApi.editUser(this.currentUser.userInfo.id, {
        location: this.localUserInfo.location,
      });
      this.currentUser.userInfo = {
        ...this.currentUser.userInfo,
        location: this.localUserInfo.location,
      };
      this.other.userInfo = {
        ...this.other.userInfo,
        location: this.localUserInfo.location,
      };
      this.cityShow = false;
      loading.close();
    },
    async selectSex(value) {
      const loading = ElLoading.service({
        lock: true,
        text: "正在保存",
        background: "rgba(0, 0, 0, 0.7)",
      });
      await editApi.editUser(this.currentUser.userInfo.id, { sex: value });
      this.localUserInfo.sex = value;
      this.currentUser.userInfo = { ...this.currentUser.userInfo, sex: value };
      this.other.userInfo = { ...this.other.userInfo, sex: value };
      this.sexShow = false;
      loading.close();
    },
    saveTags() {
      const loading = ElLoading.service({
        lock: true,
        text: "正在保存",
        background: "rgba(0, 0, 0, 0.7)",
      });
      editApi
        .editUserTag(this.currentUser.userInfo.id, {
          tagAdd: this.tagAdd,
          tagRemove: this.tagRemove,
        })
        .then((res) => {
          // 适配新的统一接口返回格式
          if (res.code === 200) {
            // 新格式
            this.localUserInfo.tags = [...this.selectedTags];
            this.currentUser.userInfo = {
              ...this.currentUser.userInfo,
              tags: [...this.selectedTags],
            };
            this.other.userInfo = {
              ...this.other.userInfo,
              tags: [...this.selectedTags],
            };
            this.tagShow = false;
            ElMessage.success("标签修改成功");
          } else {
            ElMessage.error(res.message || "标签修改失败");
          }
          loading.close();
        })
        .catch((error) => {
          loading.close();
          ElMessage.error("标签修改失败");
          console.error(error);
        });
    },
    openTag() {
      this.tagShow = !this.tagShow;
      this.getTagList();
    },
    async handleFileChange(file, fileList) {
      // 如果文件列表为空，直接返回
      if (!beforePicUpload([file])) {
        return;
      }
      const loading = ElLoading.service({
        lock: true,
        text: "正在上传",
        background: "rgba(0, 0, 0, 0.7)",
      });
      this.originalFiles = [...fileList];
      // 压缩图像
      this.compressedImages = await compressImages(
        this.originalFiles,
        this.compressedImages
      );

      // 获取上传凭证
      const uploadToken = await this.getUploadToken();
      // 上传图片
      const { imageKey, imageUrls } = await uploadFiles(
        this.compressedImages,
        this.currentUser.uploadAvatarsBaseUrl,
        uploadToken
      );
      this.imageKey = imageKey;
      this.imageUrls = imageUrls;
      // url保存至后端
      await this.submitAvatars();
      loading.close();
    },
    async submitAvatars() {
      const domin = import.meta.env.VITE_QINIU_DOMAIN;
      const imageUrl = `http://${domin}/${this.imageKey[0]}`;
      await imageApi
        .saveImageUrl(this.currentUser.userInfo.id, { image: this.imageKey[0] })
        .then((res) => {
          // 适配新的统一接口返回格式
          if (res.code === 200) {
            // 新格式
            const imageUrl = res.data.image || imageUrl;
            this.localUserInfo.image = imageUrl;
            this.currentUser.userInfo = {
              ...this.currentUser.userInfo,
              image: imageUrl,
            };
            this.other.userInfo = { ...this.other.userInfo, image: imageUrl };
            this.originalFiles = [];
            this.compressedImages = [];
            this.imgList = [];
            this.imgList.push(imageUrl);
            emitter.emit("image", imageUrl);
            ElMessage.success("图像上传成功");
          } else {
            ElMessage.error(res.message || "图像上传失败");
          }
        })
        .catch((error) => {
          ElMessage.error("图像上传失败");
          console.error(error);
        });
    },
    // 改为异步获取上传凭证
    async getUploadToken() {
      try {
        const response = await uploadApi.get_upload_token();
        // 适配新的统一接口返回格式
        if (response.code === 200) {
          // 新格式
          return response.data.upload_token;
        } else if (response.data && response.data.upload_token) {
          // 兼容旧格式
          return response.data.upload_token;
        } else {
          ElMessage.error("获取上传凭证失败");
          return null;
        }
      } catch (error) {
        ElMessage.error("获取上传凭证失败");
        console.error(error);
        return null;
      }
    },
  },
};
</script>

<template>
  <PageHeadBack>
    <PageScroll>
      <el-upload
        :show-file-list="false"
        :auto-upload="false"
        accept="image/jpeg,image/png,image/jpg,image/webp"
        :on-change="handleFileChange"
        :limit="1"
      >
        <template #trigger>
          <van-cell title="图像" is-link>
            <template #value>
              <el-image
                shape="square"
                style="width: 30px; height: 30px"
                :preview-src-list="imgList"
                alt="用户图像"
                :src="localUserInfo.image"
                @click.stop=""
              />
            </template>
          </van-cell>
        </template>
      </el-upload>

      <van-cell
        title="昵称"
        is-link
        :value="localUserInfo.nickname"
        @click="$router.push({ path: '/editCommonField', query: { type: 1 } })"
      />
      <van-cell title="账号" :value="localUserInfo.username" />
      <van-cell
        title="性别"
        is-link
        :value="localUserInfo.sex"
        @click="sexShow = !sexShow"
      />
      <van-cell
        title="所在地"
        is-link
        :value="currentUser.cityName"
        @click="cityShow = !cityShow"
      />
      <van-cell title="标签" is-link :value="tag" @click="openTag" />
      <van-cell
        title="签名"
        is-link
        :value="localUserInfo.about_me"
        @click="$router.push({ path: '/editCommonField', query: { type: 2 } })"
      />
      <van-cell title="音乐" is-link @click="$router.push('/editMusic')" />

      <van-cell
        title="兴趣封面"
        class="image"
        is-link
        @click="$router.push('/editInterest')"
      />
      <van-cell
        title="背景图片"
        is-link
        @click="$router.push('/editBackGround')"
      />
      <van-cell
        title="社交账号"
        class="socical-link"
        is-link
        @click="$router.push({ path: '/editCommonField', query: { type: 3 } })"
      />
      <el-dialog v-model="sexShow" title="设置性别" width="80%" align-center>
        <van-cell title="男" clickable @click="selectSex('男')" />
        <van-cell title="女" clickable @click="selectSex('女')" />
      </el-dialog>
      <van-action-sheet v-model:show="cityShow" title="选择城市">
        <van-area
          v-model="localUserInfo.location"
          :area-list="areaList"
          @confirm="setCity"
        />
      </van-action-sheet>

      <van-action-sheet v-model:show="tagShow" title="选择标签">
        <div class="tag-container" v-loading="loading.tag">
          <el-checkbox-group v-model="selectedTags" :min="0" :max="3">
            <el-checkbox
              v-for="tag in tagList"
              :key="tag"
              :value="tag"
              size="large"
            >
              <template #default>
                <el-tag type="primary" effect="plain" round size="small">{{
                  tag
                }}</el-tag>
              </template>
            </el-checkbox>
          </el-checkbox-group>
          <el-button
            class="tag-but"
            round
            @click="saveTags"
            :disabled="!tagChange"
            >保存</el-button
          >
        </div>
      </van-action-sheet>
    </PageScroll>
  </PageHeadBack>
</template>
<style scoped>
.form-name,
.form-city,
.form-about {
  margin-bottom: 30px;
}

.avatar {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 1rem;
}
:deep(.el-upload) {
  display: flex;
}
.sava-but {
  margin-top: 20px;
}

.el-checkbox-group {
  width: 85%;
  margin: 0 auto;
}
.image {
  margin-top: 35px;
}
.socical-link {
  margin-top: 35px;
}

.tag-container {
  min-height: 10px;
}
.tag-but {
  width: 100%;
  margin: 20px auto;
}
</style>
