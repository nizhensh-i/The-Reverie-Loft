<script>
import followApi from "@/api/user/followApi.js";
import PageHeadBack from "@/utils/components/PageHeadBack.vue";
import FollowsList from "@/views/user/components/FollowsList.vue";
import FollowRow from "@/views/user/components/FollowRow.vue";
import PageScroll from "@/utils/components/PageScroll.vue";
import arrayUtil from "@/utils/arrayUtil.js";
import { useCurrentUserStore } from "@/stores/user";
export default {
  components: {
    PageHeadBack,
    FollowsList,
    FollowRow,
    PageScroll,
  },
  data() {
    return {
      userName: "",
      action: "follower",
      follows: {
        fan: [],
        followed: [],
      },
      fanTab: {
        finished: false,
      },
      followedTab: {
        finished: false,
      },
      loading: false,
      error: false,
      refreshing: false,
      currentPage: 1,
    };
  },
  setup() {
    const currentUser = useCurrentUserStore();
    return { currentUser };
  },
  beforeRouteEnter(to, from, next) {
    next((vm) => {
      vm.action = to.params.action;
      vm.userName = to.params.userName;
    });
  },
  computed: {
    isCurrentUser() {
      return this.userName == this.currentUser.userInfo.username;
    },
  },
  methods: {
    getFan() {
      followApi
        .getFan(this.userName, this.currentPage)
        .then((res) => {
          // 适配新的统一接口返回格式
          if (res.code === 200) {
            // 新格式
            res.data.map((item) => {
              this.follows.fan.push(item);
            });
            this.loading = false;
            this.currentPage++;
            if (this.follows.fan.length >= (res.total || 0)) {
              this.fanTab.finished = true;
            }
          } else {
            this.loading = false;
            this.error = true;
          }
        })
        .catch(() => {
          this.loading = false;
          this.error = true;
          this.fanTab.finished = true;
        });
    },
    getFollowing() {
      followApi
        .getFollowing(this.userName, this.currentPage)
        .then((res) => {
          // 适配新的统一接口返回格式
          if (res.code === 200) {
            // 新格式
            res.data.map((item) => {
              this.follows.followed.push(item);
            });
            this.loading = false;
            this.currentPage++;
            if (this.follows.followed.length >= (res.total || 0)) {
              this.followedTab.finished = true;
            }
          } else {
            this.loading = false;
            this.error = true;
          }
        })
        .catch(() => {
          this.loading = false;
          this.error = true;
          this.followedTab.finished = true;
        });
    },
    getFollowList() {
      if (this.refreshing) {
        if (this.action == "follower") {
          this.follows.fan = [];
        } else {
          this.follows.followed = [];
        }
        this.refreshing = false;
      }
      if (this.action == "follower") {
        this.getFan();
      } else if (this.action == "followed") {
        this.getFollowing();
      }
    },
    onRefresh() {
      if (this.action == "follower") {
        this.fanTab.finished = false;
      } else if (this.action == "followed") {
        this.followedTab.finished = false;
      }
      this.loading = true;

      this.currentPage = 1;
      this.getFollowList();
    },
    onClickTab() {
      if (this.action == "follower" && this.follows.fan.length != 0) {
        return;
      } else if (
        this.action == "followed" &&
        this.follows.followed.length != 0
      ) {
        return;
      }
      this.currentPage = 1;
    },
    searchFan(x) {
      this.follows.fan = x;
      this.fanTab.finished = true;
    },
    searchFollowed(x) {
      this.follows.followed = x;
      // 防止再次切换回来导致无限加载
      this.followedTab.finished = true;
    },
    remove(x) {
      this.follows.followed = arrayUtil.removeObjectByFieldValue(
        this.follows.followed,
        "username",
        x
      );
    },
  },
};
</script>

<template>
  <PageHeadBack>
    <PageScroll max-height="calc(100vh - 45px - 47px)">
      <van-tabs
        v-model:active="action"
        @click-tab="onClickTab"
        animated
        sticky
        :offset-top="50"
        title-active-color="rgb(51.2, 126.4, 204)"
      >
        <van-tab title="粉丝" name="follower">
          <FollowsList
            v-model:refreshing="refreshing"
            v-model:loading="loading"
            v-model:error="error"
            v-model:finished="fanTab.finished"
            :showSearch="isCurrentUser"
            @refresh="onRefresh"
            @load="getFollowList"
            @searchFan="searchFan"
          >
            <FollowRow
              v-for="i in follows.fan"
              :key="i"
              :follows="i"
              :showFollowButton="isCurrentUser"
            />
          </FollowsList>
        </van-tab>
        <van-tab title="关注" name="followed">
          <FollowsList
            v-model:refreshing="refreshing"
            v-model:loading="loading"
            v-model:error="error"
            v-model:finished="followedTab.finished"
            tabAction="followed"
            :showSearch="isCurrentUser"
            @refresh="onRefresh"
            @load="getFollowList"
            @searchFollowed="searchFollowed"
          >
            <FollowRow
              v-for="i in follows.followed"
              :key="i"
              :follows="i"
              tabAction="followed"
              :showFollowButton="isCurrentUser"
              @remove="remove"
            />
          </FollowsList>
        </van-tab>
      </van-tabs>
    </PageScroll>
  </PageHeadBack>
</template>
<style scoped>
.el-link {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  height: 50px;
  padding: 10px;
}
.el-avatar {
  margin-right: 20px;
}
.el-link:active {
  background: #f5f7fa;
}
.follow-icon {
  color: white;
  background-color: #cdd0d6;
  margin-right: auto;
}
</style>
