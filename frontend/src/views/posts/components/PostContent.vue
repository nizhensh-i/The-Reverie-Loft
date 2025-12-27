<script>
import { mavonEditor } from "mavon-editor";
import "mavon-editor/dist/css/index.css";
export default {
  props: {
    postContent: {
      type: String,
      default: "",
    },
    preview: {
      type: Boolean,
      default: false,
    },
    fontSize: {
      type: Number,
      default: 16,
    },
    postType:{
      type: String,
      default: "",
    }
  },
  components: {
    mavonEditor,
  },
  data() {
    return {
      pContent: "",
      truncationTryCount: 0, // 新增
      // 图片预览相关状态
      imageViewerVisible: false,
      imageViewerUrls: [],
      imageViewerIndex: 0,
    };
  },
  watch: {
    postContent: {
      handler(newVal) {
        this.pContent = newVal;
        this.truncationTryCount = 0; // 重置
        this.$nextTick(() => {
          this.updateTruncation();
          this.processCodeBlocks();
        });
      },
      immediate: true,
    },
    fontSize: {
      handler(newVal) {
        this.updateFontSize(newVal);
      },
    },
  },
  mounted() {
    this.$nextTick(() => {
      this.updateTruncation();
      this.processCodeBlocks();
      // 从本地存储加载字体大小设置
      const savedFontSize = localStorage.getItem("article-font-size");
      if (savedFontSize) {
        this.fontSize = parseInt(savedFontSize);
        this.updateFontSize(this.fontSize);
      }
    });
  },
  computed: {},
  methods: {
    updateFontSize(size) {
      const contentDom = this.$refs.md?.$el?.querySelector(".v-show-content");
      if (contentDom) {
        contentDom.style.fontSize = `${size}px`;

        // 根据字体大小调整其他元素
        const h1Elements = contentDom.querySelectorAll("h1");
        const h2Elements = contentDom.querySelectorAll("h2");

        h1Elements.forEach((el) => {
          el.style.fontSize = `${(size * 1.8) / 16}em`;
        });

        h2Elements.forEach((el) => {
          el.style.fontSize = `${(size * 1.5) / 16}em`;
        });
      }
    },

    updateTruncation() {
      if (!this.preview) return;

      this.$nextTick(() => {
        const contentDom = this.$refs.md?.$el?.querySelector(".v-show-content");
        if (!contentDom) return;

        // 监听图片加载
        const imgs = contentDom.querySelectorAll("img");
        let loadedCount = 0;
        const totalImgs = imgs.length;

        const checkAllLoaded = () => {
          loadedCount++;
          if (loadedCount === totalImgs && this.truncationTryCount < 10) {
            this.truncationTryCount++;
            setTimeout(() => {
              this.updateTruncation();
            }, 50);
          }
        };

        if (totalImgs > 0) {
          imgs.forEach((img) => {
            if (!img._truncationLoaded) {
              img._truncationLoaded = true;
              img.addEventListener("load", checkAllLoaded);
              img.addEventListener("error", checkAllLoaded);
            }
          });
        }

        // 先移除旧的遮罩
        const oldMask = contentDom.querySelector(".truncation-mask");
        if (oldMask) oldMask.remove();

        // 判断是否超出最大高度
        const maxHeight = 300;
        if (contentDom.scrollHeight > maxHeight) {
          contentDom.style.maxHeight = maxHeight + "px";
          contentDom.style.overflow = "hidden";
          contentDom.style.position = "relative";

          // 添加遮罩和省略号
          const mask = document.createElement("div");
          mask.className = "truncation-mask";
          mask.style.position = "absolute";
          mask.style.left = 0;
          mask.style.right = 0;
          mask.style.bottom = 0;
          mask.style.height = "40px";
          mask.style.background =
            "linear-gradient(rgba(255,255,255,0), #fff 80%)";
          // mask.style.display = 'flex'
          // mask.style.alignItems = 'flex-end'
          // mask.style.justifyContent = 'flex-end'
          // mask.style.pointerEvents = 'none'
          // mask.innerHTML =
          //   '<div style="color:#888;font-size:18px;padding:20px 10px 10px 10px;">...</div>'
          contentDom.appendChild(mask);
        } else {
          contentDom.style.maxHeight = "none";
          contentDom.style.overflow = "auto";
          contentDom.style.position = "static";
        }

        // 延迟再触发一次，兜底
        if (this.truncationTryCount < 10) {
          this.truncationTryCount++;
          setTimeout(() => {
            const dom = this.$refs.md?.$el?.querySelector(".v-show-content");
            if (dom && dom.scrollHeight > maxHeight) {
              this.updateTruncation();
            }
          }, 300);
        }
      });
    },

    // 定义SVG图标变量
    getSvgIcons() {
      return {
        copy: `
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="copy-icon">
            <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
            <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
          </svg>
        `,
        success: `
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="copy-icon">
            <polyline points="20 6 9 17 4 12"></polyline>
          </svg>
        `,
        error: `
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="copy-icon">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        `,
      };
    },

    // 创建复制按钮HTML
    createCopyButtonHtml(icon, text) {
      const svgIcons = this.getSvgIcons();
      return `${svgIcons[icon]}<span>${text}</span>`;
    },

    // 处理代码块，添加复制按钮
    processCodeBlocks() {
      this.$nextTick(() => {
        const contentDom = this.$refs.md?.$el?.querySelector(".v-show-content");
        if (!contentDom) return;

        // 移除已存在的代码块包装器
        const existingWrappers = contentDom.querySelectorAll(
          ".code-block-wrapper"
        );
        existingWrappers.forEach((wrapper) => {
          const pre = wrapper.querySelector("pre");
          if (pre) {
            wrapper.parentNode?.insertBefore(pre, wrapper);
            wrapper.remove();
          }
        });

        // 处理所有代码块
        const preElements = contentDom.querySelectorAll("pre");
        preElements.forEach((pre) => {
          // 检查是否已经处理过
          if (pre.parentNode?.classList?.contains("code-block-wrapper")) {
            return;
          }

          // 创建包装器
          const wrapper = document.createElement("div");
          wrapper.className = "code-block-wrapper";

          // 创建复制按钮
          const copyBtn = document.createElement("button");
          copyBtn.className = "copy-btn";
          copyBtn.type = "button";
          copyBtn.innerHTML = this.createCopyButtonHtml("copy", "复制");

          // 获取代码内容
          const codeElement = pre.querySelector("code");
          const codeText = codeElement ? codeElement.innerText : pre.innerText;

          // 检查Clipboard API是否可用
          const isClipboardApiAvailable = !!(
            navigator.clipboard && navigator.clipboard.writeText
          );

          // 添加复制功能
          const handleCopyClick = async () => {
            // 如果已经是已复制状态，则阻止点击事件
            if (copyBtn.classList.contains("copied")) {
              return;
            }

            if (isClipboardApiAvailable) {
              // 使用现代Clipboard API
              try {
                console.log("使用Clipboard API复制文本");
                await navigator.clipboard.writeText(codeText);
                this.handleCopySuccess(copyBtn);
              } catch (err) {
                console.error("Clipboard API失败，尝试降级方案：", err);
                this.fallbackCopyText(codeText, copyBtn);
              }
            } else {
              // 直接使用降级方案
              console.log("使用降级方案复制文本");
              this.fallbackCopyText(codeText, copyBtn);
            }
          };

          copyBtn.addEventListener("click", handleCopyClick);

          // 包装结构
          wrapper.appendChild(copyBtn);

          // 将 pre 元素移动到包装器中
          pre.parentNode?.insertBefore(wrapper, pre);
          wrapper.appendChild(pre);
        });

        // 处理图片点击事件
        this.processImages();
      });
    },

    // 处理图片点击事件，使用 Element Plus 的图片查看器
    processImages() {
      const contentDom = this.$refs.md?.$el?.querySelector(".v-show-content");
      if (!contentDom) return;

      const imgs = contentDom.querySelectorAll("img");

      // 收集所有图片URL
      const imageUrls = [];
      imgs.forEach((img) => {
        const src = img.src || img.getAttribute("data-src");
        if (src) {
          imageUrls.push(src);
        }
      });

      this.imageViewerUrls = imageUrls;

      // 为每个图片添加点击事件
      imgs.forEach((img, index) => {
        // 移除之前的点击事件监听器
        img._imageClickHandler &&
          img.removeEventListener("click", img._imageClickHandler);

        // 添加新的点击事件
        const handler = (e) => {
          e.preventDefault();
          e.stopPropagation();

          // 禁用 mavon-editor 默认的图片预览
          const parentLink = img.closest("a");
          if (parentLink && parentLink.getAttribute("href") === img.src) {
            parentLink.style.pointerEvents = "none";
          }

          // 显示 Element Plus 图片查看器
          this.openImageViewer(index);
        };

        img._imageClickHandler = handler;
        img.addEventListener("click", handler);

        // 添加鼠标样式提示
        img.style.cursor = "pointer";
        img.title = "点击查看大图";
      });
    },

    // 打开图片查看器
    openImageViewer(index) {
      if (this.imageViewerUrls.length === 0) return;

      this.imageViewerIndex = index;
      this.imageViewerVisible = true;
    },

    // 关闭图片查看器
    closeImageViewer() {
      this.imageViewerVisible = false;
    },

    // 处理复制成功
    handleCopySuccess(copyBtn) {
      copyBtn.innerHTML = this.createCopyButtonHtml("success", "已复制");
      copyBtn.classList.add("copied");

      setTimeout(() => {
        copyBtn.innerHTML = this.createCopyButtonHtml("copy", "复制");
        copyBtn.classList.remove("copied");
      }, 3000);
    },

    // 处理复制失败
    handleCopyError(copyBtn) {
      copyBtn.innerHTML = this.createCopyButtonHtml("error", "复制失败");
      copyBtn.classList.add("copied");

      setTimeout(() => {
        copyBtn.innerHTML = this.createCopyButtonHtml("copy", "复制");
        copyBtn.classList.remove("copied");
      }, 3000);
    },

    // 降级复制方案
    fallbackCopyText(codeText, copyBtn) {
      const textArea = document.createElement("textarea");
      textArea.value = codeText;
      textArea.style.position = "fixed";
      textArea.style.opacity = "0";
      document.body.appendChild(textArea);
      textArea.select();

      try {
        const successful = document.execCommand("copy");
        if (successful) {
          this.handleCopySuccess(copyBtn);
        } else {
          this.handleCopyError(copyBtn);
        }
      } catch (err) {
        console.error("降级复制方案失败：", err);
        this.handleCopyError(copyBtn);
      } finally {
        document.body.removeChild(textArea);
      }
    },
  },
};
</script>

<template>
  <div class="post-content-wrapper">
    <mavon-editor
      ref="md"
      v-model="pContent"
      class="detail"
      :subfield="false"
      :editable="false"
      box-shadow-style="#ffffff"
      default-open="preview"
      :toolbars-flag="false"
      :markdown-options="{
        breaks: true,
        linkify: true,
        typographer: true,
        highlight: false,
        bulletListMarker: '-',
      }"
    />
    <!-- Element Plus 图片查看器 -->
    <el-image-viewer
      v-if="imageViewerVisible"
      :url-list="imageViewerUrls"
      :initial-index="imageViewerIndex"
      @close="closeImageViewer"
      teleported
    />
  </div>
</template>

<style lang="scss" scoped>
// $serif-font: "Times New Roman", "Source Han Serif SC", "Songti SC", serif;
// $no-serif-font: "-apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif";
.post-content-wrapper {
  width: 100%;
  margin: 0;
  padding: 0;
}

.base {
  font-size: 16px;
  line-height: 1.8;
  letter-spacing: 0.02em;
  color: #333;
}

.v-note-wrapper {
  min-height: 25px;
  border: none !important;
  @extend .base;
}

// 优化 markdown 内容样式
:deep(.v-show-content) {
  padding: 0 !important;
  background-color: transparent !important;

  // 标题样式优化
  h1,
  h2,
  h3,
  h4,
  h5,
  h6 {
    margin-top: 1.5em;
    margin-bottom: 0.8em;
    font-weight: 600;
    line-height: 1.4;
    color: #222;
  }

  h1 {
    font-size: 1.8em;
    border-bottom: 1px solid #eee;
    padding-bottom: 0.3em;
  }

  h2 {
    font-size: 1.5em;
    border-bottom: 1px solid #f0f0f0;
    padding-bottom: 0.2em;
  }

  // 段落样式
  p {
    margin: 0.8em 0 1.2em;
    line-height: 1.8;
  }

  // 列表样式
  ul,
  ol {
    padding-left: 1.5em;
    margin: 0.8em 0;
  }

  // 无序列表
  ul {
    list-style-type: disc;
    padding-left: 2em;
  }

  // 有序列表
  ol {
    list-style-type: decimal;
    padding-left: 2em;
  }

  li {
    margin: 0.4em 0;
    line-height: 1.6;
  }

  // 引用样式
  blockquote {
    padding: 0.5em 1em;
    color: #666;
    border-left: 4px solid #ddd;
    margin: 1em 0;
    background-color: #f9f9f9;
    border-radius: 0 4px 4px 0;
  }

  // 代码样式
  pre {
    margin: 1em 0;
    border-radius: 6px;
    background-color: #f6f8fa !important;
    padding: 1em;
    overflow: auto;
  }

  // 代码块内的 code 元素样式
  pre code {
    font-family: Consolas, Monaco, "Andale Mono", monospace;
    background-color: transparent !important;
    padding: 0 !important;
    border-radius: 0 !important;
    font-size: 0.9em;
    color: inherit;
    display: block;
    line-height: 1.5;
  }

  // 行内代码样式
  :not(pre) > code {
    font-family: Consolas, Monaco, "Andale Mono", monospace;
    background-color: #f6f8fa;
    padding: 0.2em 0.4em;
    border-radius: 3px;
    font-size: 0.9em;
    color: #e83e8c;
  }

  // 图片样式
  img {
    max-width: 100%;
    border-radius: 6px;
    margin: 1em auto;
    display: block;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }

  // 表格样式
  table {
    border-collapse: collapse;
    width: 100%;
    margin: 1em 0;
    overflow-x: auto;
    display: block;
  }

  th,
  td {
    border: 1px solid #ddd;
    padding: 8px 12px;
  }

  th {
    background-color: #f6f8fa;
    font-weight: 600;
  }

  // 水平线
  hr {
    height: 1px;
    background-color: #eee;
    border: none;
    margin: 1.5em 0;
  }

  // 链接样式
  a {
    color: #0366d6;
    text-decoration: none;

    &:hover {
      text-decoration: underline;
    }
  }
}

.detail {
  height: 100% !important;
}

// 代码块包装器样式
:deep(.code-block-wrapper) {
  position: relative;
  margin: 1.5em 0;
}

// 代码块复制按钮
:deep(.copy-btn) {
  position: absolute;
  top: 4px;
  right: 8px;
  z-index: 10;
  padding: 0px 8px;
  font-size: 12px;
  background: #f8f9fa;
  border: 1px solid #f6f8fa;
  border-radius: 4px;
  color: #24292e;
  cursor: pointer;
  transition: all 0.2s ease;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial,
    sans-serif;
  display: flex;
  align-items: center;
  gap: 4px;

  &.copied {
    color: #9bd7a2;
    cursor: default !important;
    pointer-events: none !important;
  }

  .copy-icon {
    flex-shrink: 0;
  }
}

// 代码块样式调整
:deep(pre) {
  position: relative;
  margin: 0 !important;
  border-radius: 6px;
  background-color: #f6f8fa !important;
  padding: 1em !important;
  overflow: auto;

  // 避免复制按钮挡住代码
  padding-top: 2.5em !important;

  .hljs {
    background: none;
  }
  // 确保语法高亮背景色统一
  code {
    background: none !important;
    // 处理语法高亮的各类元素
    .hljs-keyword,
    .hljs-selector-tag,
    .hljs-built_in,
    .hljs-name,
    .hljs-tag {
      color: #d73a49;
    }
    .hljs-string,
    .hljs-title,
    .hljs-section,
    .hljs-attribute,
    .hljs-literal,
    .hljs-template-tag,
    .hljs-template-variable,
    .hljs-type,
    .hljs-addition {
      color: #032f62;
    }

    .hljs-comment,
    .hljs-quote,
    .hljs-deletion,
    .hljs-meta {
      color: #6a737d;
    }

    .hljs-number,
    .hljs-regexp,
    .hljs-literal,
    .hljs-built_in,
    .hljs-builtin-name {
      color: #005cc5;
    }

    .hljs-class .hljs-title {
      color: #6f42c1;
    }

    .hljs-function .hljs-title {
      color: #6f42c1;
    }
  }
}

// 适配移动端
@media (max-width: 768px) {
  :deep(.v-show-content) {
    font-size: 14px;

    h1 {
      font-size: 1.6em;
    }

    h2 {
      font-size: 1.4em;
    }
  }

  :deep(.copy-btn) {
    padding: 0px 6px;
    font-size: 11px;
    top: 3px;
    right: 6px;
  }

  :deep(pre) {
    padding-top: 2em !important;
  }
}
</style>
