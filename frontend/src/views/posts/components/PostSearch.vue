<script>
export default {
  props: {
    contentRef: {
      type: Object,
      default: null,
    },
  },
  data() {
    return {
      searchText: "",
      searchResults: [], // 存储所有匹配的DOM元素引用
      currentIndex: -1,
      totalMatches: 0,
      isSearching: false,
      debounceTimer: null,
      isVisible: false,
    };
  },
  watch: {
    searchText(newVal) {
      // 实时搜索：当用户输入时，使用防抖处理搜索请求
      clearTimeout(this.debounceTimer);
      this.debounceTimer = setTimeout(() => {
        if (newVal.trim().length > 0) {
          this.search();
        } else {
          this.clearHighlights();
          this.searchResults = [];
          this.totalMatches = 0;
          this.currentIndex = -1;
        }
      }, 300); // 300ms 防抖延迟
    },
  },
  mounted() {
    // 组件挂载后添加动画效果
    setTimeout(() => {
      this.isVisible = true;
    }, 50);

    // 自动聚焦搜索框
    this.$nextTick(() => {
      this.$refs.searchInput?.focus();
    });
  },
  methods: {
    search() {
      this.isSearching = true;
      this.clearHighlights();

      if (!this.searchText.trim() || !this.contentRef) {
        this.searchResults = [];
        this.totalMatches = 0;
        this.currentIndex = -1;
        this.isSearching = false;
        return;
      }

      const contentDom = this.contentRef.$el?.querySelector(".v-show-content");
      if (!contentDom) {
        this.isSearching = false;
        return;
      }

      try {
        // 使用更简单可靠的方法查找和高亮所有匹配项
        this.simpleHighlightMatches(contentDom);

        // 更新匹配数量
        this.totalMatches = this.searchResults.length;

        if (this.totalMatches > 0) {
          this.currentIndex = 0;
          this.updateCurrentHighlight();
          this.scrollToCurrentMatch();
        }
      } catch (error) {
        console.error("搜索出错:", error);
      }

      this.isSearching = false;
    },

    simpleHighlightMatches(container) {
      // 清空之前的搜索结果
      this.searchResults = [];

      const searchTerm = this.searchText.trim();
      if (!searchTerm) return;

      // 获取所有文本内容
      const allText = container.innerText || container.textContent;
      if (!allText) return;

      // 创建一个临时的HTML元素来存储内容
      const tempDiv = document.createElement("div");
      tempDiv.innerHTML = container.innerHTML;

      // 使用简单的字符串替换来高亮文本
      const escapedSearchTerm = this.escapeRegExp(searchTerm);
      const regex = new RegExp(`(${escapedSearchTerm})`, "gi");

      // 递归处理所有文本节点
      this.processTextNodes(tempDiv, regex);

      // 更新原始容器的内容
      container.innerHTML = tempDiv.innerHTML;

      // 收集所有高亮元素
      const highlights = container.querySelectorAll(".search-highlight");
      this.searchResults = Array.from(highlights);
    },

    processTextNodes(node, regex) {
      // 如果是文本节点
      if (node.nodeType === 3) {
        const text = node.nodeValue;
        if (text.trim() === "") return;

        // 检查是否有匹配
        if (regex.test(text)) {
          // 重置正则表达式的lastIndex
          regex.lastIndex = 0;

          // 创建一个包含高亮的HTML片段
          const highlightedText = text.replace(
            regex,
            '<span class="search-highlight">$1</span>'
          );

          // 创建一个临时元素来保存高亮的HTML
          const tempSpan = document.createElement("span");
          tempSpan.innerHTML = highlightedText;

          // 替换原始节点
          const parent = node.parentNode;
          parent.replaceChild(tempSpan, node);
        }
      }
      // 如果是元素节点且不是已经高亮的元素
      else if (
        node.nodeType === 1 &&
        !node.classList?.contains("search-highlight") &&
        node.childNodes &&
        !/(script|style)/i.test(node.tagName)
      ) {
        // 创建一个副本，因为我们可能会修改childNodes集合
        const childNodes = Array.from(node.childNodes);
        childNodes.forEach((child) => {
          this.processTextNodes(child, regex);
        });
      }
    },

    clearHighlights() {
      const contentDom = this.contentRef.$el?.querySelector(".v-show-content");
      if (!contentDom) return;

      try {
        // 获取所有高亮元素
        const highlights = contentDom.querySelectorAll(".search-highlight");

        // 移除所有高亮
        highlights.forEach((el) => {
          // 获取高亮元素的文本内容
          const textContent = el.textContent;

          // 创建一个文本节点来替换高亮元素
          const textNode = document.createTextNode(textContent);

          // 替换高亮元素
          if (el.parentNode) {
            el.parentNode.replaceChild(textNode, el);
            // 尝试合并相邻的文本节点
            try {
              el.parentNode.normalize();
            } catch (e) {
              console.error("合并文本节点出错:", e);
            }
          }
        });
      } catch (error) {
        console.error("清除高亮出错:", error);

        // 如果出错，尝试恢复原始内容
        try {
          if (this.originalContent && contentDom) {
            contentDom.innerHTML = this.originalContent;
          }
        } catch (e) {
          console.error("恢复原始内容出错:", e);
        }
      }

      // 清空搜索结果
      this.searchResults = [];
    },

    updateCurrentHighlight() {
      // 移除所有当前高亮类
      this.searchResults.forEach((el) => {
        el.classList.remove("current-highlight");
        el.classList.remove("flash-highlight");
      });

      // 为当前匹配项添加特殊类
      if (
        this.currentIndex >= 0 &&
        this.currentIndex < this.searchResults.length
      ) {
        const currentEl = this.searchResults[this.currentIndex];
        currentEl.classList.add("current-highlight");
        currentEl.classList.add("flash-highlight");

        // 1秒后移除闪烁效果
        setTimeout(() => {
          if (currentEl.classList) {
            currentEl.classList.remove("flash-highlight");
          }
        }, 1000);
      }
    },

    escapeRegExp(string) {
      return string.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    },

    nextMatch() {
      if (this.totalMatches === 0) return;

      this.currentIndex = (this.currentIndex + 1) % this.totalMatches;
      this.updateCurrentHighlight();
      this.scrollToCurrentMatch();
    },

    prevMatch() {
      if (this.totalMatches === 0) return;

      this.currentIndex =
        (this.currentIndex - 1 + this.totalMatches) % this.totalMatches;
      this.updateCurrentHighlight();
      this.scrollToCurrentMatch();
    },

    scrollToCurrentMatch() {
      if (this.currentIndex === -1 || this.searchResults.length === 0) return;

      const currentEl = this.searchResults[this.currentIndex];
      if (currentEl) {
        // 直接使用 scrollIntoView 方法
        currentEl.scrollIntoView({
          behavior: "smooth",
          block: "center",
        });
      }
    },

    closeSearch() {
      // 先触发动画效果
      this.isVisible = false;

      // 等待动画完成后再关闭
      setTimeout(() => {
        this.searchText = "";
        this.clearHighlights();
        this.searchResults = [];
        this.totalMatches = 0;
        this.currentIndex = -1;
        this.$emit("close");
      }, 300);
    },
  },
};
</script>

<template>
  <div class="post-search-container" :class="{ visible: isVisible }">
    <div class="search-input-wrapper">
      <el-input
        ref="searchInput"
        v-model="searchText"
        placeholder="搜索文章内容..."
        clearable
        @keyup.enter="search"
        @clear="clearHighlights"
      >
        <template #prefix>
          <el-icon><i-ep-Search /></el-icon>
        </template>
        <template #append>
          <el-button @click="search" :loading="isSearching"> 搜索 </el-button>
        </template>
      </el-input>
    </div>

    <div v-if="totalMatches > 0" class="search-results-info">
      <span>{{ currentIndex + 1 }}/{{ totalMatches }} 个结果</span>
      <div class="search-navigation">
        <el-button
          type="primary"
          circle
          size="small"
          @click="prevMatch"
          :disabled="totalMatches <= 1"
        >
          <el-icon><i-ep-ArrowUp /></el-icon>
        </el-button>
        <el-button
          type="primary"
          circle
          size="small"
          @click="nextMatch"
          :disabled="totalMatches <= 1"
        >
          <el-icon><i-ep-ArrowDown /></el-icon>
        </el-button>
      </div>
      <el-button type="danger" circle size="small" @click="closeSearch">
        <el-icon><i-ep-Close /></el-icon>
      </el-button>
    </div>

    <div v-else-if="searchText && !isSearching" class="no-results">
      未找到匹配结果
    </div>
  </div>
</template>

<style lang="scss" scoped>
.post-search-container {
  position: fixed;
  top: 70px;
  right: 20px;
  z-index: 1000;
  width: 320px;
  padding: 12px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.15);
  transform: translateX(100%);
  opacity: 0;
  transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);

  &.visible {
    transform: translateX(0);
    opacity: 1;
  }

  .search-input-wrapper {
    margin-bottom: 8px;

    :deep(.el-input__wrapper) {
      box-shadow: 0 0 0 1px #dcdfe6 inset;
      transition: all 0.2s;

      &:hover,
      &:focus-within {
        box-shadow: 0 0 0 1px var(--el-color-primary) inset;
      }
    }

    :deep(.el-input__inner) {
      height: 36px;
      font-size: 14px;
    }

    :deep(.el-input-group__append) {
      padding: 0;

      .el-button {
        height: 36px;
        margin: 0;
        border-radius: 0 4px 4px 0;
      }
    }
  }

  .search-results-info {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 4px 0;
    font-size: 14px;
    color: #606266;
    animation: fadeIn 0.3s ease;

    .search-navigation {
      display: flex;
      gap: 8px;
    }
  }

  .no-results {
    padding: 4px 0;
    color: #f56c6c;
    font-size: 14px;
    text-align: center;
    animation: fadeIn 0.3s ease;
  }
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (max-width: 768px) {
  .post-search-container {
    top: 60px;
    right: 20px;
    width: calc(100% - 40px);
  }
}
</style>

<style lang="scss">
/* 全局样式，用于高亮搜索结果 */
.search-highlight {
  background-color: rgba(255, 230, 0, 0.4);
  border-radius: 2px;
  transition: background-color 0.2s ease;
}

.current-highlight {
  background-color: rgba(255, 165, 0, 0.7);
  border-radius: 2px;
  box-shadow: 0 0 0 2px rgba(255, 165, 0, 0.3);
  animation: pulse 1.5s infinite;
}

/* 闪烁效果 */
.flash-highlight {
  animation: flash 1s ease;
}

@keyframes pulse {
  0% {
    box-shadow: 0 0 0 0 rgba(255, 165, 0, 0.7);
  }

  70% {
    box-shadow: 0 0 0 5px rgba(255, 165, 0, 0);
  }

  100% {
    box-shadow: 0 0 0 0 rgba(255, 165, 0, 0);
  }
}

@keyframes flash {
  0%,
  100% {
    background-color: rgba(255, 165, 0, 0.7);
  }

  50% {
    background-color: rgba(255, 69, 0, 0.9);
  }
}
</style>
