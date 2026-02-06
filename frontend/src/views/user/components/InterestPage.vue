<script>
export default {
  props: {
    interest: {
      type: Array,
      default() {
        return [
          {
            url: "",
            describe: "",
          },
        ];
      },
    },
  },
  data() {
    return {
      activeName: "first",
      preList: [],
    };
  },
  watch: {
    interest: {
      handler(newVal) {
        this.preList = newVal.map((item) => {
          return item.url;
        });
      },
      deep: true,
      immediate: true,
    },
  },
};
</script>

<template>
  <div class="interest-container">
    <div class="bookshelf">
      <div class="book" v-for="(movie, index) in interest" :key="index">
        <el-image
          alt="兴趣图片"
          :src="movie.url"
          fit="cover"
          :preview-src-list="preList"
          :initial-index="index"
          preview-teleported
        ></el-image>
        <el-text class="book-name" truncated>{{ movie.describe }}</el-text>
      </div>
      <div class="book" v-if="interest.length === 0">
        <el-text class="book-empty">空空如页...</el-text>
      </div>
    </div>
  </div>
</template>
<style lang="scss" scoped>
// 设置为毛玻璃样式
.glass {
  backdrop-filter: blur(7px);
  border-radius: 5%;
  color: #ffffff;
  background-color: transparent;
  border: none;
}

.interest-container {
  margin: 0 auto;
  width: 90%;
}

.bookshelf {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(110px, 1fr));
  gap: 10px;
  justify-items: center;
}

.book {
  @extend .glass;
  width: 100%;
  max-width: 117px;
  position: relative;
  display: flex;
  flex-direction: column;
  margin: 10px 0;

  .el-image {
    width: 100%;
    height: 130px;
    border-radius: 5%;
  }

  .text-base {
    width: 97%;
    margin-top: 3px 0 0 2px;
    color: #ffffff;
    line-height: 1.6;
  }

  .book-name {
    @extend .text-base;
    font-size: 0.9rem;
  }

  .book-empty {
    @extend .text-base;
    font-size: 0.8rem;
    margin-left: 5px;
  }
}

@media (min-width: 768px) {
  .interest-container {
    width: 97%;
  }

  .bookshelf {
    grid-template-columns: repeat(auto-fill, minmax(117px, 1fr));
    gap: 15px;
  }
}
</style>
