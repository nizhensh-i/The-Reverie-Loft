<script>
import PageHeadBack from "@/utils/components/PageHeadBack.vue";

export default {
  components: {
    PageHeadBack,
  },
  data() {
    return {
      lastUpdated: "2026-02-03",
    };
  },
};
</script>

<template>
  <PageHeadBack>
    <div class="legal-content">
      <h1 class="page-title">隐私政策</h1>
      <p class="last-updated">最后更新时间：{{ lastUpdated }}</p>

      <section class="legal-section">
        <h2>1. 信息收集</h2>
        <p>当您使用本站服务时，我们可能会收集以下信息：</p>
        <ul>
          <li>通过第三方登录（QQ）获取的公开信息（如用户名、头像）</li>
          <li>您主动发布的内容（文章、评论等）</li>
          <li>设备信息、浏览器类型、访问日志等技术信息</li>
        </ul>
      </section>

      <section class="legal-section">
        <h2>2. 信息使用</h2>
        <p>我们收集的信息仅用于以下目的：</p>
        <ul>
          <li>提供和维护本站服务</li>
          <li>个性化您的使用体验</li>
          <li>改进服务质量和功能</li>
          <li>与您沟通服务相关事宜</li>
        </ul>
      </section>

      <section class="legal-section">
        <h2>3. 信息共享</h2>
        <p>我们承诺：</p>
        <ul>
          <li>不会将您的个人信息出售给第三方</li>
          <li>仅在法律要求或保护我们合法权益时，才可能披露必要信息</li>
          <li>第三方登录仅获取必要的基本信息</li>
        </ul>
      </section>

      <section class="legal-section">
        <h2>4. 信息保护</h2>
        <p>
          我们采取合理的技术和管理措施保护您的信息安全。但请注意，任何网络传输或存储系统都无法保证100%安全。
        </p>
      </section>

      <section class="legal-section">
        <h2>5. 您的权利</h2>
        <p>您有权：</p>
        <ul>
          <li>查看、修改或删除您的个人信息</li>
          <li>导出您的内容数据</li>
          <li>注销您的账号</li>
          <li>联系我们提出隐私相关的疑问或请求</li>
        </ul>
      </section>

      <section class="legal-section">
        <h2>6. 政策更新</h2>
        <p>
          我们保留更新本隐私政策的权利。更新后的政策将在本站公布，继续使用服务即表示接受更新后的政策。
        </p>
      </section>

      <section class="legal-section">
        <h2>7. 联系我们</h2>
        <p>如有任何隐私相关的问题，请通过邮箱联系我们：zmc_li@foxmail.com</p>
      </section>
    </div>
  </PageHeadBack>
</template>

<style lang="scss" scoped>
.legal-content {
  padding: 60px 40px 80px;
  margin: 0 auto;
}

.page-title {
  font-size: 32px;
  font-weight: 500;
  margin: 0 0 8px 0;
  color: #333;
}

.last-updated {
  font-size: 13px;
  color: #999;
  margin: 0 0 40px 0;
}

.legal-section {
  margin-bottom: 32px;

  h2 {
    font-size: 18px;
    font-weight: 500;
    margin: 0 0 16px 0;
    color: #444;
  }

  p {
    font-size: 15px;
    line-height: 1.8;
    color: #666;
    margin: 0 0 12px 0;
    font-weight: 350;
  }

  ul {
    margin: 12px 0;
    padding-left: 24px;

    li {
      font-size: 15px;
      line-height: 1.8;
      color: #666;
      margin-bottom: 8px;
      font-weight: 350;
    }
  }
}

@media (max-width: 768px) {
  .legal-content {
    padding: 40px 20px 60px;
  }

  .page-title {
    font-size: 24px;
  }
}
</style>
