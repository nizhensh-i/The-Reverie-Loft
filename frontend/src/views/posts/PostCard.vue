<script>
import { useCurrentUserStore } from "@/stores/user";
import { useOtherUserStore } from "@/stores/otherUser";
import date from "@/utils/date.js";
import imageCfg from "@/config/image.js";
import praise from "@/api/praise/praiseApi.js";
import emojiCfg from "@/config/emojiCfg.js";
import { loginReminder } from "@/utils/common.js";
import dayjs from "@/config/dayjsCfg";

export default {
  props: {
    post: {
      type: Object,
      default() {
        return {
          id: 1,
          body: "文章",
          body_html: null,
          timestamp: "2024-9-20 12:14:00",
          author: "张三",
          nick_name: "",
          commentCount: 20,
          disabled: false,
          image: "",
          praise_num: 0,
          has_praised: false,
        };
      },
    },
    loading: {
      type: Boolean,
      default: false,
    },
    // 卡片的背景颜色
    cardBgColor: {
      type: String,
      default: "white",
    },
    cardStyle: {
      type: Object,
      default() {
        return {};
      },
    },
    showImage: {
      type: Boolean,
      default: true,
    },
    showEdit: {
      type: Boolean,
      default: true,
    },
    showShare: {
      type: Boolean,
      default: true,
    },
    showComment: {
      type: Boolean,
      default: true,
    },
    showPraise: {
      type: Boolean,
      default: true,
    },
  },
  emits: ["share"],
  data() {
    return {
      praiseNum: 0,
      hasPraised: false,
      iconSize: 15,
      eStyle: `style="width: 26px;height: 26px;vertical-align: middle; position: relative;top: -3px;margin: 0px 2px 0px 3px;"`,
    };
  },
  setup() {
    const currentUser = useCurrentUserStore();
    const otherUser = useOtherUserStore();
    return { currentUser, otherUser };
  },
  watch: {
    "post.praise_num": {
      handler(newValue) {
        this.praiseNum = newValue;
      },
      immediate: true,
    },
    "post.has_praised": {
      handler(newValue) {
        this.hasPraised = newValue;
      },
      immediate: true,
    },
  },
  computed: {
    from_now() {
      if (date.isYesterday(this.post.timestamp)) {
        let time = dayjs(this.post.timestamp).format("HH:mm");
        return `昨天 ${time}`;
      }
      return dayjs(this.post.timestamp).fromNow();
    },
    isCommentManage() {
      return this.currentUser.userInfo.roleId >= 2;
    },
    show_body() {
      return this.isCommentManage || !this.post.disabled;
    },
    image() {
      if (!this.post.image) {
        return imageCfg.random();
      }
      return this.post.image;
    },
    isUserRoute() {
      return this.$route.path.startsWith("/user");
    },
    skeletonItemWidth() {
      return this.avatar ? "80%" : " 100%";
    },
  },
  mounted() {},
  methods: {
    share() {
      this.$router.push(`/postDetail/${this.post.id}`);
    },
    edit() {
      this.$router.push(`/editPost/${this.post.id}`);
    },
    comment() {
      this.$router.push(`/postDetail/${this.post.id}`);
    },
    praise() {
      if (!this.currentUser.isLogin) {
        loginReminder("快去登录再点赞吧");
        return;
      }
      praise.submitPraise(this.post.id).then((res) => {
        if (res.code == 200) {
          this.praiseNum = res.total;
          this.hasPraised = res.data.has_praised;
        } else {
          ElMessage.error(res.data.detail);
        }
      });
    },
    parseContent(content) {
      let r1 = this.replaceHeo(content);
      let r2 = this.replaceDingtalk(r1);
      return r2;
    },

    replaceHeo(content) {
      if (!/\[Heo:(.+?)\]/.test(content)) {
        return content;
      }
      const withHeo = content.replace(
        /\[Heo:(.+?)\]/g,
        `<img src="${emojiCfg.Heo_100.baseUrl}$1${emojiCfg.Heo_100.suffix}" ${this.eStyle}/>`
      );
      return withHeo;
    },
    replaceDingtalk(content) {
      if (!/\[ding:(.+?)\]/.test(content)) {
        return content;
      }
      const withDing = content.replace(
        /\[ding:(.+?)\]/g,
        `<img src="${emojiCfg.dingtalk.baseUrl}$1${emojiCfg.dingtalk.suffix}" ${this.eStyle}/>`
      );
      return withDing;
    },
    toUser() {
      // 接口都已改为根据用户id获取用户数据
      this.otherUser.userInfo.id = this.post.user_id;
      this.$router.push(`/user/${this.post.author}`);
    },
  },
};
</script>

<template>
  <el-card shadow="hover" :style="cardStyle">
    <el-row>
      <el-col :span="4" v-if="showImage">
        <el-avatar alt="用户图像" :src="image" @click.stop="toUser" />
      </el-col>
      <el-col :span="showImage ? 20 : 24">
        <el-row justify="space-between" class="content">
          <el-col :xs="18" :sm="18" :md="10" :lg="10" :xl="10">
            <el-link target="_blank" type="primary" @click.stop="toUser">
              {{ post.nick_name ? post.nick_name : post.author }}
            </el-link>
          </el-col>
          <el-col :xs="6" :sm="3" :md="2" :lg="3" :xl="3" :push="2">
            <el-text class="mx-1" size="small">{{ from_now }}</el-text>
          </el-col>
        </el-row>
        <el-row v-if="post.disabled">
          <p><i>此评论已被版主禁用</i></p>
        </el-row>
        <el-row
          ><div v-if="post.body_html && show_body" v-html="post.body_html"></div
        ></el-row>
        <el-row v-if="!post.body_html && show_body"
          ><div v-html="parseContent(post.summary || post.body)"></div
        ></el-row>

        <el-row :gutter="35" justify="end" class="icon-event">
          <el-col
            :xs="4"
            :sm="4"
            :md="2"
            :lg="2"
            :xl="2"
            v-if="showEdit && post.author == currentUser.userInfo.username"
          >
            <van-icon name="edit" @click.stop="edit" :size="iconSize" />
          </el-col>
          <el-col
            :xs="4"
            :sm="4"
            :md="2"
            :lg="2"
            :xl="2"
            v-else-if="showEdit && currentUser.userInfo.isAdmin == 'true'"
          >
            <van-icon
              name="edit"
              @click.stop="edit"
              :size="iconSize"
              color="red"
            />
          </el-col>

          <el-col
            :xs="4"
            :sm="4"
            :md="2"
            :lg="2"
            :xl="2"
            v-if="showShare && !isUserRoute"
          >
            <van-icon
              name="share-o"
              @click.stop="this.$emit('share', true)"
              :size="iconSize"
            />
          </el-col>

          <el-col :xs="4" :sm="6" :md="4" :lg="2" :xl="2" v-if="showComment">
            <el-space :size="3">
              <van-icon name="notes-o" @click.stop="comment" :size="iconSize" />
              <el-text class="mx-1">{{ post.comment_count }}</el-text>
            </el-space>
          </el-col>

          <el-col :xs="5" :sm="5" :md="2" :lg="2" :xl="2" v-if="showPraise">
            <el-space :size="3">
              <transition :name="hasPraised ? 'praise' : ''" mode="out-in">
                <van-icon
                  name="good-job"
                  @click.stop=""
                  :size="iconSize"
                  v-if="hasPraised"
                  key="praised"
                />
                <van-icon
                  name="good-job-o"
                  @click.stop="praise"
                  :size="iconSize"
                  v-else
                  key="unPraise"
                />
              </transition>
              <el-text class="mx-1">{{ praiseNum }}</el-text>
            </el-space>
          </el-col>
        </el-row>
      </el-col>
    </el-row>
    <slot></slot>
  </el-card>
</template>
<style scoped>
.content {
  min-height: 60px;
}

.el-button {
  padding: 0px 5px;
}
:deep(.el-card__body) {
  padding: 5px 20px;
}
.el-card {
  background-color: v-bind(cardBgColor);
}
.van-skeleton {
  padding: 0px;
}
.icon-event {
  height: 22px;
}
.praise-enter-active,
.praise-leave-active {
  transition: all 0.15s cubic-bezier(0.42, 0, 0.34, 1.55);
}
.praise-enter-from,
.praise-leave-to {
  transform: scale(0);
}
.praise-enter-to,
.praise-leave-from {
  transform: scale(1);
}
</style>
