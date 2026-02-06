<script>
import commentApi from "@/api/comment/commentApi.js";
import PostCard from "../posts/PostCard.vue";
import { useCurrentUserStore } from "@/stores/user";
import PageHeadBack from "@/utils/components/PageHeadBack.vue";
import SkeletonUtil from "@/utils/components/SkeletonUtil.vue";
import PageScroll from "@/utils/components/PageScroll.vue";

export default {
  components: {
    PostCard,
    PageHeadBack,
    SkeletonUtil,
    PageScroll,
  },
  setup() {
    const currentUser = useCurrentUserStore();
    return { currentUser };
  },
  data() {
    return {
      comments: [],
      currentPage: 1,
      comments_count: 0,
      loading: {
        comment: false,
      },
    };
  },
  computed: {
    isCommentManage() {
      return this.currentUser.userInfo.roleId >= 2;
    },
  },
  mounted() {
    this.getAllComments();
  },
  methods: {
    getAllComments(page = 1) {
      this.loading.comment = true;
      commentApi.getAllComments(page).then((res) => {
        if (res.code === 200) {
          this.comments = res.data;
          this.comments_count = res.total ?? 0;
        }
        this.loading.comment = false;
      });
    },
    handleCurrentChange() {
      this.getAllComments(this.currentPage);
    },
    toggleCommentStatus(item, action) {
      commentApi.enableOrDisable(item.id, action).then((res) => {
        if (res.code === 200) {
          this.comments = res.data;
          ElMessage({
            type: action === "enable" ? "success" : "warning",
            message: action === "enable" ? "已开启" : "已禁用",
          });
        }
      });
    },
    disabled(item) {
      this.toggleCommentStatus(item, "disable");
    },
    enable(item) {
      this.toggleCommentStatus(item, "enable");
    },
  },
};
</script>

<template>
  <PageHeadBack>
    <PageScroll max-height="calc(100vh - 45px - 47px)">
      <SkeletonUtil
        :loading="loading.comment"
        :row="7"
        :count="4"
        :cardStyle="{ marginBottom: '10px' }"
      >
        <PostCard
          v-for="item in comments"
          :key="item"
          :post="item"
          :cardStyle="{ marginBottom: '10px' }"
          :showEdit="false"
          :showShare="false"
          :showComment="false"
          :showPraise="false"
        >
          <el-row v-if="isCommentManage">
            <el-button @click="enable(item)" v-if="item.disabled"
              >开启</el-button
            >
            <el-button type="danger" @click="disabled(item)" v-else
              >禁用</el-button
            >
          </el-row>
        </PostCard>
      </SkeletonUtil>
      <el-pagination
        v-model:current-page="currentPage"
        :page-size="10"
        layout="total, prev, pager, next"
        :total="comments_count"
        @current-change="handleCurrentChange"
        :hide-on-single-page="true"
        :pager-count="5"
      />
    </PageScroll>
  </PageHeadBack>
</template>
<style lang="scss" scoped>
.el-pagination {
  margin-bottom: 15px;
}
</style>
