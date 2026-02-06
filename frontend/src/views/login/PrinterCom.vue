<!-- <printer printerInfo="你好啊 哈哈哈哈">
    <template v-slot:paper="{ content }">
      <h3>{{ content }}<span class="cursor">|</span></h3>
    </template>
  </printer> -->

<template>
  <div>
    <slot name="paper" :content="content"></slot>
  </div>
</template>
<script>
export default {
  props: {
    printerInfo: {
      type: String,
      default: "",
    },
    duration: {
      type: Number,
      default: 100,
    },
    delay: {
      type: Number,
      default: 3000,
    },
    working: {
      type: Boolean,
      default: true,
    },
    once: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      content: "",
      cursor: 0,
      timer: null,
      timeout: null,
      print: true,
    };
  },
  created() {
    if (this.working) {
      this.start(this.work);
    } else {
      this.content = this.printerInfo;
    }
  },
  watch: {
    working() {
      this.toBegin();
    },
    printerInfo() {
      this.toBegin();
    },
    cursor(cursor) {
      this.content = this.printerInfo.slice(0, cursor);
    },
  },
  beforeUnmount() {
    this.clearTimers();
  },
  methods: {
    start(work) {
      this.timeout = setTimeout(() => {
        this.timer = setInterval(() => {
          work();
          if (
            this.cursor === 0 ||
            (this.cursor === this.printerInfo.length && !this.once)
          ) {
            clearInterval(this.timer);
            this.start(this.work);
          } else if (this.cursor === this.printerInfo.length && this.once) {
            clearInterval(this.timer);
          }
        }, this.duration);
      }, this.delay);
    },
    work() {
      let cursor = this.cursor;
      cursor += this.print ? 1 : -1;
      if (this.print) {
        if (cursor === this.printerInfo.length + 1) {
          cursor -= 2;
          this.print = !this.print;
        }
      } else {
        if (cursor === -1) {
          cursor += 2;
          this.print = !this.print;
        }
      }
      this.cursor = cursor;
    },
    toBegin() {
      this.cursor = 0;
      this.clearTimers();
      if (this.working) {
        this.start(this.work);
      } else {
        this.content = this.printerInfo;
      }
    },
    clearTimers() {
      if (this.timeout !== null) {
        clearTimeout(this.timeout);
        this.timeout = null;
      }
      if (this.timer !== null) {
        clearInterval(this.timer);
        this.timer = null;
      }
    },
  },
};
</script>
