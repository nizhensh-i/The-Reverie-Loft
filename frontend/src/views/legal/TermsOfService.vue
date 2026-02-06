<script>
import PageHeadBack from "@/utils/components/PageHeadBack.vue";
import PageScroll from "@/utils/components/PageScroll.vue";

export default {
  components: {
    PageHeadBack,
    PageScroll,
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
    <PageScroll max-height="calc(100vh - 45px - 47px)">
      <div class="legal-content">
        <h1 class="page-title">用户协议</h1>
        <p class="last-updated">最后更新时间：{{ lastUpdated }}</p>

        <section class="legal-section">
          <h2>1. 协议接受</h2>
          <p>
            欢迎使用随想阁楼（以下简称"本站"）。访问或使用本站服务，即表示您同意遵守本用户协议。如果您不同意本协议的任何条款，请勿使用本站服务。
          </p>
        </section>

        <section class="legal-section">
          <h2>2. 服务内容</h2>
          <p>
            本站提供文章发布、评论互动、内容浏览等社交功能。我们保留随时修改、暂停或终止部分或全部服务的权利，恕不另行通知。
          </p>
        </section>

        <section class="legal-section">
          <h2>3. 用户账号</h2>
          <p>
            您可以通过第三方平台（如QQ）登录本站。您应对您的账号活动负责，请妥善保管您的账号信息。如发现账号异常，请立即联系我们。
          </p>
        </section>

        <section class="legal-section">
          <h2>4. 内容规范</h2>
          <p>
            您在本站发布的内容应遵守法律法规，不得包含违法、侵权、虚假、骚扰、仇恨或其他不当信息。我们有权删除违反规范的内容，并视情况采取相应措施。
          </p>
        </section>

        <section class="legal-section">
          <h2>5. 知识产权</h2>
          <p>
            您在本站发布的内容，其知识产权归您所有。您授予我们非独占、免费、全球性的许可，用于运营、改进和推广本站服务。
          </p>
        </section>

        <section class="legal-section">
          <h2>6. 免责声明</h2>
          <p>
            本站按"现状"提供，不保证服务的连续性、准确性或适用性。对于因使用或无法使用本站服务而造成的任何损失，我们不承担责任。
          </p>
        </section>

        <section class="legal-section">
          <h2>7. 协议修改</h2>
          <p>
            我们保留随时修改本协议的权利。修改后的协议将在本站公布，继续使用服务即表示接受修改后的协议。
          </p>
        </section>

        <section class="legal-section">
          <h2>8. 联系我们</h2>
          <p>如有任何问题或建议，请通过邮箱联系我们：zmc_li@foxmail.com</p>
        </section>
      </div>
    </PageScroll>
  </PageHeadBack>
</template>

<style lang="scss" scoped>
// 变量定义
$text-primary: #333;
$text-secondary: #999;
$text-muted: #666;
$text-accent: #444;

.legal-content {
  padding: 60px 40px 80px;
  margin: 0 auto;
}

.page-title {
  font-size: 32px;
  font-weight: 500;
  margin: 0 0 8px;
  color: $text-primary;
}

.last-updated {
  font-size: 13px;
  color: $text-secondary;
  margin: 0 0 40px;
}

.legal-section {
  margin-bottom: 32px;

  h2 {
    font-size: 18px;
    font-weight: 500;
    margin: 0 0 16px;
    color: $text-accent;
  }

  p {
    font-size: 15px;
    line-height: 1.8;
    color: $text-muted;
    margin: 0;
    font-weight: 350;
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
