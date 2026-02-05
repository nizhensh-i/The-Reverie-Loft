<script>
import PageHeadBack from "@/utils/components/PageHeadBack.vue";
import uploadCard from "@/views/user/components/uploadCard.vue";
import ButtonAnimate from "@/utils/components/ButtonAnimate.vue";
import interest from "@/views/user/components/Interest.vue";
import PageScroll from "@/utils/components/PageScroll.vue";

export default {
  name: "BlogPost",
  props: {},
  components: {
    PageHeadBack,
    uploadCard,
    interest,
    ButtonAnimate,
    PageScroll,
  },
  data() {
    return {
      formDataMovie: {
        coverImage: [],
        name1: "",
        name2: "",
        name3: "",
      },
      formDataBook: {
        coverImage: [],
        name1: "",
        name2: "",
        name3: "",
      },
      showLog: false,
      showPre: false,
      preData: {
        movies: [],
        books: [],
      },
      activeInterest: "movie",
    };
  },
  computed: {
    // 预览按钮可点击
    isPre() {
      return (
        this.formDataMovie.coverImage.length > 0 ||
        this.formDataBook.coverImage.length > 0
      );
    },
  },
  mounted() {},
  methods: {
    pre() {
      if (this.formDataMovie.coverImage) {
        this.preData.movies = this.formDataMovie.coverImage.map(
          (item, index) => {
            return {
              url: item.url,
              describe: this.formDataMovie["name" + (index + 1)],
            };
          }
        );
      }
      if (this.formDataBook.coverImage) {
        this.preData.books = this.formDataBook.coverImage.map((item, index) => {
          return {
            url: item.url,
            describe: this.formDataBook["name" + (index + 1)],
          };
        });
      }
      this.showPre = !this.showPre;
      console.log("11", this.preData);
    },
    setActive(type) {
      this.activeInterest = type;
    },
  },
};
</script>

<template>
  <PageHeadBack>
    <PageScroll max-height="calc(100vh - 45px - 47px)">
      <div class="page-head">
        <el-text>各分类下最多展示3张图片</el-text>
        <Transition>
          <el-button
            size="small"
            round
            type="primary"
            plain
            v-show="isPre"
            @click="pre"
            >预览</el-button
          >
        </Transition>
      </div>
      <uploadCard
        ref="movie"
        v-model:formData="formDataMovie"
        type="movie"
        class="upload-card"
      />
      <uploadCard ref="book" v-model:formData="formDataBook" type="book" />

      <el-dialog v-model="showPre" width="400">
        <ButtonAnimate
          content="喜欢的电影"
          :isActive="activeInterest === 'movie'"
          :fontColor="true"
          @click="setActive('movie')"
        />
        <ButtonAnimate
          content="在看的书籍"
          :isActive="activeInterest === 'book'"
          :fontColor="true"
          @click="setActive('book')"
        />
        <interest :interest="preData" :showInterest="activeInterest" />
      </el-dialog>
    </PageScroll>
  </PageHeadBack>
</template>

<style scoped>
.page-head {
  margin: 20px 0px 70px 10px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
:deep(.el-dialog) {
  padding: 0px;
}
.upload-card {
  margin: 0px 0px 70px 0px;
}
.el-button {
  width: 70px;
}

.v-enter-active,
.v-leave-active {
  transition: opacity 0.5s ease;
}

.v-enter-from,
.v-leave-to {
  opacity: 0;
}
</style>
