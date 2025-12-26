<template>
  <div class="comment-section">
    <div class="comment-header">
      <h3 class="comment-title">评论区</h3>
      <div class="comment-count">共 {{ query.total }} 条评论</div>
    </div>

    <u-comment-scroll :disable="disable" @more="more" class="comment-scroll">
      <u-comment
        ref="commentRef"
        :config="config"
        @submit="submit"
        @like="like"
        @mention-search="mentionSearch"
        @reply-page="replyPage"
        @show-info="showInfo"
        class="UComment"
      >
        <u-comment-nav
          v-model="latest"
          @sorted="sorted"
          class="comment-nav"
        ></u-comment-nav>
        <template #avatar="scope">
          <el-avatar
            alt="用户图像"
            :src="scope.user.avatar"
            class="comment-avatar"
          />
        </template>
        <template #operate="scope">
          <Operate :comment="scope" @remove="remove" />
        </template>
        <template #card="scope">
          <UserInfo :scope="scope" :loading="loading" :config="config" />
        </template>
      </u-comment>
    </u-comment-scroll>

    <div v-if="query.total === 0" class="empty-comments">
      <van-icon name="comment-o" class="empty-icon" />
      <p>暂无评论，快来发表第一条评论吧！</p>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, watch } from "vue";
import emoji from "@/config/emoji.js";
import Operate from "./components/CommentOperate.vue";
import UserInfo from "./components/UserInfo.vue";
import commentApi from "@/api/comment/commentApi.js";
import praiseApi from "@/api/praise/praiseApi.js";
import userApi from "@/api/user/userApi.js";
import imageCfg from "@/config/image.js";
import { useCurrentUserStore } from "@/stores/user";
import { loginReminder } from "@/utils/common.js";
import message from "@/utils/message";

const currentUser = useCurrentUserStore();
const props = defineProps({ postId: Number });
const config = reactive({
  user: {}, // 当前用户信息
  emoji: emoji, // 表情包数据
  comments: [], // 评论数据
  relativeTime: true, // 开启人性化时间
  show: {
    likes: true,
    level: false,
    address: false,
  },
  page: true, // 开启分页
  mention: {
    // 开启提交功能
    data: currentUser.userInfo.followed,
    alias: {
      username: "name",
    },
    showAvatar: true,
  },
});

config.user = {
  id: currentUser.userInfo.id,
  username: currentUser.priorityName,
  // level: 6,
  avatar: currentUser.userInfo.image
    ? currentUser.userInfo.image
    : imageCfg.logOut,
  // 评论id数组 建议:存储方式用户id和文章id和评论id组成关系,根据用户id和文章id来获取对应点赞评论id,然后加入到数组中返回
  // 存储已点赞的评论id
  likeIds: [],
};

// 用户信息是否加载
const loading = ref(false);
// 模拟请求获取用户详细信息
const showInfo = (uid, finish) => {
  loading.value = true;
  let userInfo;
  // 模拟获取后端根据uid查询用户信息

  userApi
    .getUser(uid)
    .then((res) => {
      // 适配新的统一接口返回格式
      if (res.code === 200) {
        const u = res.data;
        userInfo = {
          username: u.name ? u.name : u.username,
          level: 6,
          avatar: u.image,
          like: u.praised_count,
          attention: u.followed_count,
          follower: u.followers_count,

          id: u.id,
          isFollowed:
            currentUser.userInfo.followed.findIndex(
              (item) => item.uName == u.username
            ) != -1,
          uName: u.username,
          nickname: u.nickname,
        };
        loading.value = false;
        finish(userInfo);
      } else {
        ElMessage.error(res.message || "获取用户信息失败");
      }
    })
    .catch((error) => {
      loading.value = false;
      ElMessage.error("获取用户信息失败");
      console.error(error);
    });
};

// 提交触发搜索: 模拟请求接口返回搜索用户数据
const mentionSearch = (val) => {
  config.mention.data = currentUser.userInfo.followed.filter((v) =>
    v.name.includes(val)
  );
};
// 评论提交事件
const submit = ({ content, parentId, reply, finish, mentionList }) => {
  if (!currentUser.isLogin) {
    loginReminder("快去登录再发布评论吧");
    return;
  }

  const directParentId = reply === undefined ? null : reply.id;
  commentApi
    .submitComment(props.postId, {
      body: content,
      directParentId: directParentId,
      at: mentionList,
    })
    .then((res) => {
      // 适配新的统一接口返回格式
      if (res.code === 200) {
        finish(res.data);
        ElMessage.info("评论成功!");
      } else {
        ElMessage.error(res.message || "评论失败");
      }
    })
    .catch((error) => {
      if (error.response && error.response.status === 429) {
        ElMessage.info("操作太快了，慢点点~");
      } else {
        ElMessage.error("评论失败，请稍后重试");
      }
    });
};

// 点赞按钮事件
const like = (id, finish) => {
  if (!currentUser.isLogin) {
    loginReminder("快去登录再点赞吧");
    return;
  }

  // 确保 likeIds 是数组
  if (!config.user.likeIds || !Array.isArray(config.user.likeIds)) {
    config.user.likeIds = [];
  }

  if (config.user.likeIds.findIndex((item) => item == id) == -1) {
    // 点赞
    praiseApi
      .submitPraiseComment(id)
      .then((res) => {
        // 适配新的统一接口返回格式
        if (res.code === 200) {
          currentUser.addItemLikeIds(id);
          finish();
        } else {
          ElMessage.error(res.message || "点赞失败");
        }
      })
      .catch((error) => {
        console.error(error);
      });
  } else {
    // 取消点赞
  }
};

//请求回复分页
const replyPage = ({ parentId, current, finish }) => {
  commentApi
    .getReplyComment(parentId, current)
    .then((res) => {
      // 适配新的统一接口返回格式
      if (res.code === 200) {
        let tmp = {
          total: res.total || 0,
          // 分页提取回复
          list: res.data,
        };
        finish(tmp);
      } else {
        ElMessage.error(res.message || "获取回复失败");
      }
    })
    .catch((error) => {
      ElMessage.error("获取回复失败，请稍后重试");
      console.error(error);
    });
};

const query = reactive({
  current: 1, // 当前页数
  size: 10, // 页大小
  total: 0, // 评论总数
});
// 是否禁用滚动加载评论
const disable = ref(false);

// 请求接口请求加载更多评论
const more = () => {
  if (query.current <= Math.ceil(query.total / query.size)) {
    commentApi
      .getComment(props.postId, query.current)
      .then((res) => {
        // 适配新的统一接口返回格式
        if (res.code === 200) {
          config.comments.push(...res.data);
          query.current++;
        } else {
          ElMessage.error(res.message || "加载评论失败");
          finish(); // 即使失败也要调用finish
        }
      })
      .catch((error) => {
        ElMessage.error("加载评论失败，请稍后重试");
        console.error(error);
      });
  } else {
    disable.value = true;
  }
};

//排序
const latest = ref(true);
const sorted = (latest) => {
  if (latest) {
    // 按最新时间排序（时间从新到旧）
    config.comments.sort(
      (a, b) => new Date(b.createTime) - new Date(a.createTime)
    );
  } else {
    // 按点赞数量排序（点赞数从高到低）
    config.comments.sort((a, b) => b.likes - a.likes);
  }
};

const commentRef = ref();
// 删除评论
const remove = (comment) => {
  setTimeout(() => {
    commentRef.value?.remove(comment);
  }, 200);
};

let currentRequestId = 0;
function getComment() {
  const requestId = ++currentRequestId;
  commentApi
    .getComment(props.postId, query.current)
    .then((res) => {
      if (requestId !== currentRequestId) {
        // 忽略非最新请求的结果
        return;
      }

      // 适配新的统一接口返回格式
      if (res.code === 200) {
        config.comments = [...res.data];
        query.current++;
        query.total = res.total || 0;

        // 如果已经加载完所有评论，禁用滚动加载
        if (query.current > Math.ceil(query.total / query.size)) {
          disable.value = true;
        }
      } else {
        ElMessage.error(res.message || "获取评论失败");
      }
    })
    .catch((error) => {
      // ElMessage.error('获取评论失败，请稍后重试')
      message.error("获取评论失败，请稍后重试");
      console.error(error);
    });
}
function has_praised() {
  praiseApi
    .has_praised_comment_ids(props.postId)
    .then((res) => {
      // 适配新的统一接口返回格式
      if (res.code === 200) {
        config.user.likeIds = [...res.data];
      } else {
        ElMessage.error(res.message || "获取点赞状态失败");
      }
    })
    .catch((error) => {
      // ElMessage.error('获取点赞状态失败，请稍后重试')
      message.error("获取点赞状态失败，请稍后重试");
      console.error(error);
    });
}
watch(
  () => props.postId,
  () => {
    // 重置状态
    config.comments = [];
    // 一定要重置页码。否则导致请求的页码不正确，返回的数据为空数组
    query.current = 1;
    query.total = 0;
    disable.value = false;

    setTimeout(getComment, 200);
    if (currentUser.isLogin) {
      setTimeout(has_praised, 250);
    }
  }
);
</script>

<style lang="scss" scoped>
.comment-section {
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid #f0f0f0;
}

.comment-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding: 0 4px;
}

.comment-title {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin: 0;
  position: relative;

  &::before {
    content: "";
    position: absolute;
    left: -4px;
    top: 2px;
    bottom: 2px;
    width: 3px;
    background: linear-gradient(to bottom, #09c8ce, #eb2f96);
    border-radius: 3px;
  }
}

.comment-count {
  font-size: 14px;
  color: #999;
}

.UComment {
  padding: 0;

  :deep(.u-comment-box) {
    border-radius: 8px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);

    .u-comment-textarea {
      border-radius: 6px;
      border-color: #e8e8e8;

      &:focus {
        border-color: #1890ff;
        box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.1);
      }
    }

    .u-comment-submit {
      background-color: #1890ff;
      border-radius: 4px;

      &:hover {
        background-color: #40a9ff;
      }
    }
  }

  :deep(.u-comment-item) {
    padding: 12px;
    margin-bottom: 12px;
    border-radius: 8px;
    background-color: #fafafa;
    transition: background-color 0.2s ease;

    &:hover {
      background-color: #f5f5f5;
    }
  }
}

.comment-avatar {
  border: 2px solid #fff;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
}

.comment-nav {
  margin-bottom: 16px;

  :deep(.u-comment-nav-item) {
    padding: 6px 12px;
    border-radius: 16px;

    &.active {
      background-color: #e6f7ff;
      color: #1890ff;
    }
  }
}

.empty-comments {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 0;
  color: #999;

  .empty-icon {
    font-size: 48px;
    margin-bottom: 16px;
    color: #d9d9d9;
  }

  p {
    font-size: 14px;
    margin: 0;
  }
}

@media (max-width: 768px) {
  .comment-section {
    margin-top: 16px;
    padding-top: 12px;
  }

  .comment-title {
    font-size: 16px;
  }

  .comment-count {
    font-size: 12px;
  }

  .UComment {
    :deep(.u-comment-item) {
      padding: 10px;
      margin-bottom: 10px;
    }
  }
}
</style>
