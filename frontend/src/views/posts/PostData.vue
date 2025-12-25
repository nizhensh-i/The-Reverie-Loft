<script>
import PostPreview from "@/views/posts/components/PostPreview.vue";
import PostImage from "@/views/posts/components/PostImage.vue";
import notificationApi from "@/api/notification/notificationApi.js";
import postApi from "@/api/posts/postApi.js";
import { useCurrentUserStore } from "@/stores/user";
import SkeletonUtil from "@/utils/components/SkeletonUtil.vue";
import ICP from "@/utils/components/ICP.vue";
import PublishEntry from "@/views/posts/components/PublishEntry.vue";
import RegisterPrompt from "@/views/posts/components/RegisterPrompt.vue";
import AtmosphereCard from "@/views/posts/components/AtmosphereCard.vue";
import emitter from "@/utils/emitter.js";

export default {
  components: {
    PostPreview,
    PostImage,
    PublishEntry,
    SkeletonUtil,
    ICP,
    RegisterPrompt,
    AtmosphereCard,
  },
  data() {
    return {
      activeName: "all",
      posts: [],
      posts_count: -1,
      currentPage: 1,
      loading: {
        publishPost: false,
        card: false,
      },
      showEmoji: false,
      // 延迟渲染会导致与空页面闪烁
      throttle: {
        leading: 0,
        trailing: 0,
        initVal: false,
      },
      showDot: false,
      followPost: [],
    };
  },
  setup() {
    const currentUser = useCurrentUserStore();
    return { currentUser };
  },
  mounted() {
    this.getPosts(this.currentPage, this.activeName);
    // 关注的用户发布了新文章
    emitter.on("followPost", (newPost) => {
      this.showDot = true;
      this.followPost = [...newPost];
      console.log("newPost", this.followPost);
    });
    // 监听文章删除事件，刷新页面
    emitter.on("postDeleted", () => {
      this.getPosts(this.currentPage, this.activeName);
    });
  },
  methods: {
    changeTab(tabName) {
      this.getPosts(this.currentPage, tabName);
    },
    handleCurrentChange() {
      this.getPosts(this.currentPage, this.activeName);
    },
    getPosts(page, tabName) {
      this.loading.card = true;
      if (tabName === "showFollowed" && this.showDot) {
        const ids = [];
        this.followPost.forEach((item) => {
          ids.push(item.id);
        });
        // 全部标记为已读
        notificationApi.markRead({ ids: ids }).then(() => {
          this.showDot = false;
        });
      }
      postApi.getPosts(page, tabName).then((res) => {
        this.loading.card = false;
        // 适配新的统一接口返回格式
        if (res.code === 200) {
          // 新格式
          this.posts = res.data;
          this.posts_count = res.total || 0;
        }
      });
    },
    getPostsResult(post) {
      this.posts.unshift(...post);
      this.posts_count++;

      // 首页设置了缓存，手动更新为第一页
      this.currentPage = 1;
      this.loading.publishPost = false;
    },
  },
  beforeUnmount() {
    // 清理事件监听
    emitter.off("followPost");
    emitter.off("postDeleted");
  },
};
</script>

<template>
  <div class="posts-container">
    <RegisterPrompt
      v-if="!currentUser.isLogin"
      :key="'register-prompt'"
      v-slide-in
    />

    <!-- 使用新的发布入口组件 -->
    <PublishEntry
      @loading-begin="(flag) => (loading.publishPost = flag)"
      @newPost="getPostsResult"
      v-if="currentUser.isLogin"
    />
    <el-tabs
      v-model="activeName"
      type="card"
      class="demo-tabs"
      @tab-change="changeTab"
    >
      <el-tab-pane label="广场" name="all">
        <el-empty
          :image-size="200"
          v-if="activeName == 'all' && posts_count == 0 && !loading.card"
        />
        <SkeletonUtil
          :loading="loading.card"
          :row="5"
          :throttle="throttle"
          :useNew="true"
        >
          <!-- <div class="posts-list">
            <transition-group name="slide-in">
              <PostPreview
                v-for="item in posts"
                :key="item.id"
                :post="item"
                :containerStyle="{ marginBottom: '20px' }"
                @click="$router.push(`/postDetail/${item.id}`)"
                v-slide-in
              >
                <template #image>
                  <PostImage :postImages="item.post_images" @click.stop="" />
                </template>
              </PostPreview>
            </transition-group>
          </div> -->

          <AtmosphereCard v-for="item in posts" :key="item.id" />
        </SkeletonUtil>
      </el-tab-pane>
      <el-tab-pane name="showFollowed" v-if="currentUser.isLogin">
        <template #label>
          <van-badge :dot="showDot" :offset="[1, 10]"> 关注 </van-badge>
        </template>
        <el-empty
          :image-size="200"
          v-if="
            activeName == 'showFollowed' && posts_count == 0 && !loading.card
          "
        />
        <SkeletonUtil
          :loading="loading.card"
          :row="5"
          :throttle="throttle"
          :useNew="true"
        >
          <div class="posts-list">
            <transition-group name="slide-in">
              <PostPreview
                v-for="item in posts"
                :key="item.id"
                :post="item"
                :containerStyle="{ marginBottom: '20px' }"
                @click="$router.push(`/postDetail/${item.id}`)"
                v-slide-in
              >
                <template #image>
                  <PostImage :postImages="item.post_images" @click.stop="" />
                </template>
              </PostPreview>
            </transition-group>
          </div>
        </SkeletonUtil>
      </el-tab-pane>
    </el-tabs>
    <el-pagination
      v-model:current-page="currentPage"
      :page-size="10"
      layout="total, prev, pager, next"
      :total="posts_count"
      @current-change="handleCurrentChange"
      :hide-on-single-page="true"
      :pager-count="5"
    />
    <ICP />
  </div>
</template>
<style lang="scss" scoped>
@use "./components/PostCard.scss" as *;

.posts-container {
  padding: 10px;
}

.gradient-text {
  margin: 0px 0px 10px 0px;
  position: relative;
  display: inline-block;

  &::after {
    content: "";
    position: absolute;
    bottom: -5px;
    left: 0;
    width: 100%;
    height: 2px;
    background: linear-gradient(90deg, #09c8ce, #eb2f96);
    border-radius: 2px;
  }
}
// .el-pagination {
//   /* float: right; */
//   display: flex;
//   justify-content: flex-end;
//   margin-bottom: 10px;
// }
.demo-tabs {
  margin-top: 20px;
  /* 当内容较少时，让icp出现在最下方，而不是中间 */
  min-height: 47vh;

  :deep(.el-tabs__header) {
    margin-bottom: 20px;
    border-bottom: none;
  }

  :deep(.el-tabs__nav) {
    border: none;
    background: transparent;
  }

  :deep(.el-tabs__item) {
    height: 40px;
    line-height: 40px;
    padding: 0 20px;
    font-size: 15px;
    color: #606266;
    border: none;
    border-radius: 20px;
    transition: all 0.3s ease;
    margin-right: 10px;
    background-color: #f5f7fa;

    &.is-active {
      color: #fff;
      background: linear-gradient(90deg, #09c8ce, #3a7bd5);
      box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
    }

    &:hover:not(.is-active) {
      color: #409eff;
      background-color: #ecf5ff;
    }
  }

  :deep(.el-tabs__nav-wrap::after) {
    display: none;
  }
}
</style>
