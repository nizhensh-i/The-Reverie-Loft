<template>
  <van-search
    v-model="value"
    v-if="showSearch"
    placeholder="搜索昵称或账号"
    @search="onSearch"
  />
  <van-pull-refresh
    v-model="internalRefreshing"
    success-text="刷新成功"
    @refresh="onRefresh"
  >
    <van-list
      v-model:loading="internalLoading"
      v-model:error="internalError"
      :finished="internalFinished"
      finished-text="没有更多了"
      error-text="请求失败，点击重新加载"
      @load="onLoad"
    >
      <slot></slot>
    </van-list>
  </van-pull-refresh>
</template>

<script>
import followApi from "@/api/user/followApi.js";
import { useCurrentUserStore } from "@/stores/user";
export default {
  props: {
    refreshing: {
      type: Boolean,
      default: false,
    },
    loading: {
      type: Boolean,
      default: false,
    },
    error: {
      type: Boolean,
      default: false,
    },
    finished: {
      type: Boolean,
      default: false,
    },
    tabAction: {
      type: String,
      default: "fan",
    },
    showSearch: {
      type: Boolean,
      default: true,
    },
  },
  emits: [
    "load",
    "refresh",
    "update:refreshing",
    "update:loading",
    "update:error",
    "update:finished",
    "searchFollowed",
    "searchFan",
  ],
  data() {
    return {
      value: "",
    };
  },
  setup() {
    const currentUser = useCurrentUserStore();
    return { currentUser };
  },
  computed: {
    internalRefreshing: {
      get() {
        return this.refreshing;
      },
      set(value) {
        this.$emit("update:refreshing", value);
      },
    },
    internalLoading: {
      get() {
        return this.loading;
      },
      set(value) {
        this.$emit("update:loading", value);
      },
    },
    internalError: {
      get() {
        return this.error;
      },
      set(value) {
        this.$emit("update:error", value);
      },
    },
    internalFinished: {
      get() {
        return this.finished;
      },
      set(value) {
        this.$emit("update:finished", value);
      },
    },
  },
  methods: {
    onRefresh() {
      this.$emit("refresh");
    },
    onLoad() {
      this.$emit("load");
    },
    onSearch() {
      if (this.tabAction === "followed") {
        followApi
          .getFollowing(this.currentUser.userInfo.username, 1, this.value)
          .then((res) => {
            if (res.code === 200) {
              this.$emit("searchFollowed", res.data);
            }
          });
      } else {
        followApi
          .getFan(this.currentUser.userInfo.username, 1, this.value)
          .then((res) => {
            if (res.code === 200) {
              this.$emit("searchFan", res.data);
            }
          });
      }
    },
  },
};
</script>
