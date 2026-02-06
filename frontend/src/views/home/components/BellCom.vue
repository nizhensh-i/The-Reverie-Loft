<script>
import notificationApi from "@/api/notification/notificationApi.js";
import { useCurrentUserStore } from "@/stores/user";
import { useOtherUserStore } from "@/stores/otherUser";
import NotificationDetail from "./NotificationDetail.vue";
import emitter from "@/utils/emitter.js";

export default {
  components: {
    NotificationDetail,
  },
  data() {
    return {
      activeName: "first",
      notifications: [],
      classification: {
        comment: [],
        praise: [],
        at: [],
        chat: [],
        newPost: [],
      },
    };
  },
  setup() {
    const currentUser = useCurrentUserStore();
    const otherUser = useOtherUserStore();
    return { currentUser, otherUser };
  },
  watch: {
    notifications: {
      handler(newVal) {
        this.classify(newVal);
      },
      immediate: true,
      deep: true,
    },
  },
  computed: {
    showDot() {
      return this.notifications.some(
        (item) => item.type !== "新文章" && !item.isRead
      );
    },
    atUnreadNum() {
      return this.calculateUnreadCount("at");
    },
    commentUnreadNum() {
      return this.calculateUnreadCount("comment");
    },
    praiseUnreadNum() {
      return this.calculateUnreadCount("praise");
    },
    chatUnreadNum() {
      return this.calculateUnreadCount("chat");
    },
  },
  mounted() {
    this.initSocket();
  },
  beforeUnmount() {
    this.currentUser.socket?.off("new_notification");
    if (this.currentUser.socket) {
      this.currentUser.disconnectSocket();
    }
  },
  methods: {
    async initLoad() {
      // 加载本地数据
      const localData = this.currentUser.notice.Notification_data;
      const notifications = await notificationApi
        .getCurrentUserNotification()
        .then((res) => res.data);
      // 合并去重
      const allData = [...notifications, ...localData].filter(
        (item, index, self) => index === self.findIndex((t) => t.id === item.id)
      );
      this.notifications = allData;
      this.currentUser.saveNotifications(allData);
    },

    handleNoticeClear() {
      this.notifications = [];
      this.currentUser.clearNotifications();
    },

    handleMakeAll() {
      const ids = this.notifications.map((item) => {
        item.isRead = true;
        return item.id;
      });
      notificationApi.markRead({ ids });
    },
    handleNoticeRead(item) {
      if (!item.isRead) {
        item.isRead = true;
        notificationApi.markRead({ ids: [item.id] });
      }
    },
    toPost(item) {
      this.handleNoticeRead(item);
      if (!item.postId) {
        this.$router.push("/content-not-found");
        return;
      }
      this.$router.push(`/postDetail/${item.postId}`);
    },
    toChat(item) {
      this.handleNoticeRead(item);
      this.otherUser.userInfo.id = item.triggerId;
      this.otherUser.userInfo.nickname = item.triggerNickName;
      this.otherUser.userInfo.username = item.triggerUsername;
      this.$router.push("/chat");
    },
    initSocket() {
      if (!this.currentUser.isLogin) {
        return;
      }
      this.currentUser.connectSocket();
      this.initLoad();
      this.currentUser.socket.on("new_notification", this.receiveMessage);
    },
    receiveMessage(data) {
      const d = data;
      // 更新前端实时状态
      this.notifications = [d, ...this.notifications];
      const existData = this.currentUser.loadNotifications();
      // 新数据与本地数据合并后去重
      const mergedData = [d, ...existData].filter(
        (item, index, self) => index === self.findIndex((t) => t.id === item.id)
      );
      this.currentUser.saveNotifications(mergedData);
      if (mergedData.length > this.currentUser.notice.MAX_ITEM) {
        this.currentUser.saveNotifications(mergedData.slice(0, 50));
      }
      console.log("收到实时通知:", data);
    },
    mergeNotifications(localData, serverUnRead) {
      // 创建映射防止重复
      const map = new Map();
      // 本地数据优先（保证实时性）
      localData.forEach((n) => map.set(n.id, n));
      // 合并远程数据
      serverUnRead.forEach((n) => {
        if (!map.has(n.id) || !map.get(n.id).isRead) {
          map.set(n.id, { ...n, isRead: false });
        }
      });
      // 转换为数组并排序
      return Array.from(map.values()).sort(
        (a, b) => new Date(b.time) - new Date(a.time)
      );
    },
    classify() {
      this.classification.comment = this.notifications.filter(
        (item) => item.type === "评论" || item.type === "回复"
      );
      this.classification.praise = this.notifications.filter(
        (item) => item.type === "点赞"
      );
      this.classification.at = this.notifications.filter(
        (item) => item.type === "@"
      );
      this.classification.chat = this.notifications.filter(
        (item) => item.type === "私信"
      );
      this.classification.newPost = this.notifications.filter(
        (item) => item.type === "新文章"
      );
      const postNotice =
        this.classification.newPost.length > 0 &&
        this.classification.newPost.some((item) => !item.isRead);
      if (postNotice) {
        emitter.emit("followPost", this.classification.newPost);
      }
    },
    handleClick(tab) {
      this.activeName = tab.name;
    },
    calculateUnreadCount(type) {
      return this.classification[type].reduce((count, item) => {
        return count + (item.isRead ? 0 : 1);
      }, 0);
    },
  },
};
</script>

<template>
  <div class="notification-wrapper">
    <van-popover
      :show-arrow="false"
      close-on-click-action
      :offset="[-120, 15]"
      class="notification-popover"
    >
      <template #reference>
        <div class="notification-icon-container">
          <van-badge :dot="showDot" :offset="[-8, 5]">
            <el-button circle class="notification-button">
              <template #icon>
                <el-icon :size="20" class="bell-icon"><i-ep-Bell /></el-icon>
              </template>
            </el-button>
          </van-badge>
        </div>
      </template>
      <template #default>
        <div class="notification-container">
          <el-tabs
            v-model="activeName"
            class="notification-tabs"
            :stretch="true"
            @tab-click="handleClick"
          >
            <el-tab-pane name="first">
              <template #label>
                <van-badge
                  :content="atUnreadNum"
                  :show-zero="false"
                  :offset="[12, -5]"
                >
                  @我的
                </van-badge>
              </template>
              <NotificationDetail
                :notifications="classification.at"
                @read="handleNoticeRead"
                @viewPost="toPost"
              />
            </el-tab-pane>
            <el-tab-pane name="second">
              <template #label>
                <van-badge
                  :content="commentUnreadNum"
                  :show-zero="false"
                  :offset="[12, -5]"
                  >评论
                </van-badge>
              </template>
              <NotificationDetail
                :notifications="classification.comment"
                @read="handleNoticeRead"
                @viewPost="toPost"
              />
            </el-tab-pane>
            <el-tab-pane name="third">
              <template #label>
                <van-badge
                  :content="praiseUnreadNum"
                  :show-zero="false"
                  :offset="[12, -5]"
                  >赞</van-badge
                >
              </template>
              <NotificationDetail
                :notifications="classification.praise"
                @read="handleNoticeRead"
                @viewPost="toPost"
              />
            </el-tab-pane>
            <el-tab-pane name="fourth">
              <template #label>
                <van-badge
                  :content="chatUnreadNum"
                  :show-zero="false"
                  :offset="[12, -5]"
                >
                  私信
                </van-badge>
              </template>
              <NotificationDetail
                :notifications="classification.chat"
                @read="handleNoticeRead"
                @viewPost="toPost"
                @viewChat="toChat"
              />
            </el-tab-pane>
          </el-tabs>
        </div>
        <div class="notification-footer">
          <el-button
            class="view-all-btn"
            :disabled="!showDot"
            @click="handleMakeAll"
            type="primary"
            size="small"
            :icon="showDot ? 'Check' : ''"
          >
            标记全部已读
          </el-button>
          <el-button
            :disabled="notifications.length <= 0"
            class="clear-btn"
            @click="handleNoticeClear"
            type="danger"
            size="small"
            plain
            :icon="notifications.length > 0 ? 'Delete' : ''"
          >
            清空
          </el-button>
        </div>
      </template>
    </van-popover>
  </div>
</template>
<style scoped>
:root {
  --primary-color: #3a7bd5;
  --secondary-color: #00d2ff;
  --accent-color: #4a90e2;
  --danger-color: #f56c6c;
  --text-color: #2c3e50;
  --light-text: #6c757d;
  --border-color: #e9ecef;
  --hover-color: #f8f9fa;
  --shadow-color: rgba(0, 0, 0, 0.08);
}

.notification-wrapper {
  position: relative;
}

.notification-icon-container {
  position: relative;
  display: inline-block;
}

.notification-button {
  border-color: transparent;
  /* background: linear-gradient(145deg, #f0f4f8, #ffffff); */
  box-shadow: 0 2px 8px var(--shadow-color);
  transition: all 0.3s ease;
  height: 35px;
  width: 40px;
}

.notification-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.bell-icon {
  color: var(--primary-color);
  transition: all 0.3s ease;
}

.notification-button:hover .bell-icon {
  transform: rotate(12deg);
}

@keyframes pulse {
  0% {
    transform: scale(0.95);
    opacity: 0.7;
  }
  70% {
    transform: scale(1.1);
    opacity: 0;
  }
  100% {
    transform: scale(0.95);
    opacity: 0;
  }
}

.notification-popover :deep(.van-popover__content) {
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 6px 30px rgba(0, 0, 0, 0.12);
}

.notification-container {
  width: 340px;
  max-height: 500px;
  padding: 0;
  overflow: hidden;
}

.notification-popover :deep(.van-popover) {
  width: 340px !important;
  max-width: 340px !important;
}

.notification-tabs {
  padding: 10px;
}

.notification-tabs :deep(.el-tabs__nav) {
  width: 100%;
}

/* 修复tab上的红点显示问题 */
.notification-tabs :deep(.van-badge) {
  position: absolute;
  top: 2px;
  right: -8px;
  transform: scale(0.8);
}

.notification-tabs :deep(.van-badge__content) {
  min-width: 16px;
  height: 16px;
  padding: 0 4px;
  font-weight: 500;
  line-height: 16px;
}

.notification-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-top: 1px solid var(--border-color);
  padding: 12px 16px;
  background-color: #f9fafc;
}

.view-all-btn,
.clear-btn {
  font-size: 12px;
  border-radius: 20px;
  padding: 6px 12px;
  transition: all 0.3s ease;
}

.view-all-btn:not(:disabled):hover,
.clear-btn:not(:disabled):hover {
  transform: translateY(-1px);
}
/* 禁用状态样式 */
button[disabled] {
  opacity: 0.6;
  cursor: not-allowed;
}

.van-cell {
  width: 100%;
  transition: background-color 0.2s ease;
}

.van-cell:hover {
  background-color: var(--hover-color);
}
</style>
