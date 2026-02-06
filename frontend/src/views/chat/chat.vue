<!--
  注意： 
        1.看了源码，UChat组件挂载后会自动执行一次loadMore函数。所以loadMore函数包含了第一次加载的聊天记录
        2.返回的聊天记录不可以直接赋值给config.data。
          而是把已分页的数据传给finish()回调函数（底层应该是自动帮我们拼接给config.data）
        3.config.data中的id没什么用。界面是按数组顺序排列的，靠前的数组是最近发送的消息
-->
<template>
  <div class="chat-container">
    <u-chat
      :config="config"
      style="max-height: 83vh"
      @load-more="loadMore"
      @submit="submit"
      @input="onInput"
    >
      <template #header>
        <PageHeadBack :title="otherUser.priorityName" />
      </template>
    </u-chat>

    <!-- 正在输入提示 - 参考微信QQ的设计，显示在聊天内容区域顶部 -->
    <div v-if="isTyping" class="typing-indicator">
      <el-tag type="info" size="small" effect="plain" class="typing-tag">
        {{ otherUser.priorityName }} 正在输入
        <div class="typing-dots">
          <span></span>
          <span></span>
          <span></span>
        </div>
      </el-tag>
    </div>
  </div>
</template>
<!-- 
  满屏高度： height:45vh; 
  无数据：   height:83vh
  所有尺寸： height:83vh
-->
<script setup>
import { reactive, onMounted, ref, onUnmounted } from "vue";
import chatApi from "@/api/chat/chatApi.js";
import emoji from "@/config/emoji.js";
import imageCfg from "@/config/image.js";
import PageHeadBack from "@/utils/components/PageHeadBack.vue";
import { useCurrentUserStore } from "@/stores/user";
import { useOtherUserStore } from "@/stores/otherUser";

const currentUser = useCurrentUserStore();
const otherUser = useOtherUserStore();

const isTyping = ref(false);
let typingTimer = null;
let typingTimeoutTimer = null;

const config = reactive({
  user: {
    id: currentUser.userInfo.id,
    username: currentUser.priorityName,
    avatar: currentUser.userInfo.image || imageCfg.logOut,
  },
  data: [],
  emoji: emoji,
});

const query = reactive({
  current: 0,
  size: 15,
  total: 0,
  real_time_receive: false,
});

onMounted(() => {
  currentUser.enterChat(otherUser.userInfo.id);

  currentUser.socket.on("new_message", (msg) => {
    if (currentUser.activeChat === msg.sender_id) {
      query.real_time_receive = true;
      config.data.push(msg);
    }
    query.real_time_receive = false;
  });

  currentUser.socket.on("chat:typing", (data) => {
    if (data.sender_id === otherUser.userInfo.id) {
      showTypingIndicator();
    }
  });
});

onUnmounted(() => {
  clearTypingTimers();
});

function loadMore(finish) {
  if (!query.current) {
    chatApi.getMessageHistory(otherUser.userInfo.id, 1).then((res) => {
      if (res.code === 200) {
        finish([...res.data]);
        query.total = res.total ?? 0;
        query.current = 2;
      }
    });
  } else if (query.current <= Math.ceil(query.total / query.size)) {
    chatApi
      .getMessageHistory(otherUser.userInfo.id, query.current)
      .then((res) => {
        if (res.code === 200) {
          query.current++;
          finish([...res.data]);
        }
      });
  } else {
    finish([]);
  }
}

// 输入事件处理（debounce）
function onInput() {
  if (typingTimer) return;

  // 发送typing事件
  currentUser.socket.emit("chat:typing", {
    target_id: otherUser.userInfo.id,
  });

  typingTimer = setTimeout(() => {
    typingTimer = null;
  }, 300);
}

// 显示正在输入提示
function showTypingIndicator() {
  isTyping.value = true;

  if (typingTimeoutTimer) {
    clearTimeout(typingTimeoutTimer);
  }

  typingTimeoutTimer = setTimeout(() => {
    isTyping.value = false;
    typingTimeoutTimer = null;
  }, 3000);
}

// 清理定时器
function clearTypingTimers() {
  if (typingTimer) {
    clearTimeout(typingTimer);
    typingTimer = null;
  }
  if (typingTimeoutTimer) {
    clearTimeout(typingTimeoutTimer);
    typingTimeoutTimer = null;
  }
}

function submit(val, finish) {
  const chat = {
    content: val,
    uid: currentUser.userInfo.id,
    user: {
      username: currentUser.priorityName,
      avatar: currentUser.userInfo.image || imageCfg.logOut,
    },
    createTime: new Date(),
  };

  currentUser.sendMessage(chat, finish);
  isTyping.value = false;
}
</script>

<style lang="scss" scoped>
.chat-container {
  position: relative;
}

.typing-indicator {
  position: absolute;
  top: 0px;
  left: 30vw;
  right: 50vw;
  z-index: 5;
  animation: fadeIn 0.3s ease-in-out;
}

.typing-tag {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-weight: normal;
  font-size: 12px;
  background: rgba(0, 0, 0, 0.05);
  border: 1px solid rgba(0, 0, 0, 0.1);
  color: #666;
  padding: 4px 8px;
  border-radius: 12px;

  .typing-icon {
    font-size: 12px;
    color: #999;
  }

  .typing-dots {
    display: inline-flex;
    gap: 2px;
    margin-left: 4px;

    span {
      width: 3px;
      height: 3px;
      border-radius: 50%;
      background: #999;
      animation: typingBounce 1.4s infinite ease-in-out both;

      &:nth-child(1) {
        animation-delay: -0.32s;
      }

      &:nth-child(2) {
        animation-delay: -0.16s;
      }
    }
  }
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-5px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes typingBounce {
  0%,
  80%,
  100% {
    transform: scale(0);
    opacity: 0.5;
  }

  40% {
    transform: scale(1);
    opacity: 1;
  }
}
</style>
