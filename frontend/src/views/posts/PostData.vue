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
import PageScroll from "@/utils/components/PageScroll.vue";
import emitter from "@/utils/emitter.js";

export default {
  components: {
    PostPreview,
    PostImage,
    PublishEntry,
    SkeletonUtil,
    ICP,
    RegisterPrompt,
    PageScroll,
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
        more: false,
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
  computed: {
    noMore() {
      if (this.posts_count < 0) return false;
      return this.posts.length >= this.posts_count;
    },
    infiniteDisabled() {
      return this.loading.card || this.loading.more || this.noMore;
    },
  },
  setup() {
    const currentUser = useCurrentUserStore();
    return { currentUser };
  },
  mounted() {
    this.resetPosts(this.activeName);
    // 关注的用户发布了新文章
    emitter.on("followPost", (newPost) => {
      this.showDot = true;
      this.followPost = [...newPost];
      console.log("newPost", this.followPost);
    });
    // 监听文章删除事件，刷新页面
    emitter.on("postDeleted", () => {
      this.resetPosts(this.activeName);
    });
  },
  methods: {
    changeTab(tabName) {
      this.resetPosts(tabName);
    },
    resetPosts(tabName) {
      this.currentPage = 1;
      this.posts = [];
      this.posts_count = -1;
      this.loading.more = false;
      this.fetchPosts(1, tabName, { append: false });
    },
    async fetchPosts(page, tabName, { append = false } = {}) {
      const loadingKey = append ? "more" : "card";
      this.loading[loadingKey] = true;
      if (tabName === "showFollowed" && this.showDot && page === 1) {
        const ids = this.followPost.map((item) => item.id);
        notificationApi.markRead({ ids }).then(() => {
          this.showDot = false;
        });
      }
      try {
        const res = await postApi.getPosts(page, tabName);
        if (res.code === 200) {
          const list = Array.isArray(res.data) ? res.data : [];
          this.posts = append ? [...this.posts, ...list] : list;
          if (typeof res.total === "number") {
            this.posts_count = res.total;
          } else if (!append) {
            this.posts_count = list.length;
          } else {
            this.posts_count = Math.max(this.posts_count, this.posts.length);
          }
          return true;
        }
      } finally {
        this.loading[loadingKey] = false;
      }
      return false;
    },
    async loadMore() {
      if (this.infiniteDisabled) return;
      const nextPage = this.currentPage + 1;
      const ok = await this.fetchPosts(nextPage, this.activeName, {
        append: true,
      });
      if (ok) {
        this.currentPage = nextPage;
      }
    },
    getPostsResult(post) {
      const newPosts = Array.isArray(post) ? post : [post];
      this.posts.unshift(...newPosts);
      if (this.posts_count >= 0) {
        this.posts_count += newPosts.length;
      }

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
  <PageScroll max-height="calc(100vh - 45px - 5px)">
    <div
      class="posts-container"
      v-infinite-scroll="loadMore"
      :infinite-scroll-delay="200"
      :infinite-scroll-distance="160"
      :infinite-scroll-disabled="infiniteDisabled"
      :infinite-scroll-immediate="true"
    >
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
            <transition-group name="slide-in" tag="div" class="posts-list">
              <PostPreview
                v-for="item in posts"
                :key="item.id"
                :post="item"
                @click="$router.push(`/postDetail/${item.id}`)"
                v-slide-in
              >
                <template #image>
                  <PostImage :postImages="item.post_images" @click.stop="" />
                </template>
              </PostPreview>
            </transition-group>
          </SkeletonUtil>
          <div class="posts-infinite-footer">
            <div v-if="loading.more" class="posts-loading">加载中...</div>
            <div v-else-if="noMore && posts.length" class="posts-end">
              已经到底了～
            </div>
          </div>
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
            <transition-group name="slide-in" tag="div" class="posts-list">
              <PostPreview
                v-for="item in posts"
                :key="item.id"
                :post="item"
                @click="$router.push(`/postDetail/${item.id}`)"
                v-slide-in
              >
                <template #image>
                  <PostImage :postImages="item.post_images" @click.stop="" />
                </template>
              </PostPreview>
            </transition-group>
          </SkeletonUtil>
          <div class="posts-infinite-footer">
            <div v-if="loading.more" class="posts-loading">加载中...</div>
            <div v-else-if="noMore && posts.length" class="posts-end">
              已经到底了～
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
      <ICP />
    </div>
  </PageScroll>
</template>
<style lang="scss" scoped>
@use "./components/PostCard.scss" as *;

.gradient-text {
  position: relative;
  display: inline-block;
  margin-bottom: 10px;

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
    margin-right: 10px;
    font-size: 15px;
    color: #606266;
    background-color: #f5f7fa;
    border: none;
    border-radius: 20px;
    transition: all 0.3s ease;

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

.posts-infinite-footer {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 36px;
  padding: 0 0 24px;
  color: #909399;
  font-size: 13px;
  letter-spacing: 0.2px;

  .posts-loading {
    display: inline-flex;
    align-items: center;
    gap: 8px;

    &::before {
      content: "";
      width: 14px;
      height: 14px;
      border-radius: 50%;
      border: 2px solid rgba(9, 200, 206, 0.25);
      border-top-color: #09c8ce;
      animation: posts-spin 0.9s linear infinite;
    }
  }

  .posts-end {
    padding: 6px 14px;
    border-radius: 999px;
    background: #f5f7fa;
    color: #909399;
  }
}

@keyframes posts-spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
