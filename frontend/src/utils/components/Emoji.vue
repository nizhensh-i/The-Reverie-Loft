<template>
  <van-popover
    v-model:show="showPopover"
    placement="bottom-start"
    :offset="offset"
  >
    <template #default>
      <transition name="body">
        <div class="emoji-body">
          <span
            v-for="(value, key, index) in emojiListURL"
            :key="index"
            @click="$emit('selectEmoji', key)"
          >
            <img
              loading="lazy"
              class="emoji"
              :src="value"
              :title="key"
              width="30"
              height="30"
            />
          </span>
        </div>
      </transition>
    </template>
    <template #reference>
      <el-button circle class="emoji-button">
        <template #icon>
          <div style="font-size: 24px">
            <EmojiIcon v-if="emoName === 'Heo_100'" />
            <Dingtalk v-if="emoName === 'dingtalk'" />
          </div>
        </template>
      </el-button>
    </template>
  </van-popover>
</template>
<script>
import emojiCfg from "@/config/emojiCfg.js";
import EmojiIcon from "@/asset/svg/emojiIcon.svg?component";
import Dingtalk from "@/asset/svg/dingtalk.svg?component";

export default {
  components: {
    EmojiIcon,
    Dingtalk,
  },
  props: {
    emoName: {
      type: String,
      default: "Heo_100",
    },
    offset: {
      type: Array,
      default: () => [0, 8],
    },
  },
  emits: ["selectEmoji"],
  data() {
    return {
      showPopover: false,
      emojiListURL: {},
      prefix: {
        Heo_100: "Heo",
        dingtalk: "ding",
      },
    };
  },
  computed: {
    emoji() {
      return emojiCfg[this.emoName] || {};
    },
    prefixName() {
      return this.prefix[this.emoName];
    },
  },
  created() {
    if (this.emoji.name) {
      this.emojiListURL = this.getEmojiList(this.emoji.name);
    }
  },
  methods: {
    getEmojiList(emojiList) {
      const result = {};
      const prefixName = this.prefixName;
      const { baseUrl = "", suffix = "" } = this.emoji;

      for (let i = 0; i < emojiList.length; i++) {
        const emojiName = `[${prefixName}:${emojiList[i]}]`;
        const url = `${baseUrl}${emojiList[i]}${suffix}`;
        result[emojiName] = url;
      }
      return result;
    },
  },
};
</script>
<style lang="scss" scoped>
.emoji-body {
  max-width: 400px;
}

.body-enter-active,
.body-leave-active {
  transition: all 0.3s;
}

.body-enter,
.body-leave-to {
  opacity: 0;
  transform: scale(0.5);
}

.emoji-button {
  margin-top: 2px;
  padding: 0;
  border: none;
  transition: all 0.5s;

  &:hover {
    background-color: transparent;
    transform: scale(1.2);
  }
}
</style>
