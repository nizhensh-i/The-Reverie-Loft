<script>
import PageHeadBack from "@/utils/components/PageHeadBack.vue";
import homeIcon from "@/asset/svg/homeIcon.svg?component";
export default {
  components: {
    PageHeadBack,
    homeIcon,
  },
  data() {
    return {
      currentYear: new Date().getFullYear(),
      creator: {
        name: "阁楼主人",
        title: "全栈开发者",
        bio: "用代码解决问题，也顺手记录生活。",
      },
    };
  },
};
</script>

<template>
  <PageHeadBack>
    <div class="about-container">
      <div class="about-content">
        <!-- 个人介绍区域 -->
        <div class="intro-section">
          <div class="avatar">
            <homeIcon />
          </div>
          <h1 class="name">{{ creator.name }}</h1>
          <p class="title">{{ creator.title }}</p>
          <p class="bio">{{ creator.bio }}</p>
        </div>

        <!-- 项目介绍 -->
        <div class="project-section">
          <h2 class="section-title">关于本站</h2>
          <div class="section-content">
            <p class="description">
              这是一个个人作品，一个安静的角落，用来记录技术探索、生活感悟和创作思考。
            </p>
            <p class="description">
              没有商业目标，没有增长压力，只是单纯地享受创造的过程，和偶尔相遇的共鸣。
            </p>
          </div>
        </div>

        <!-- 联系我 -->
        <div class="contact-section">
          <h2 class="section-title">联系我</h2>
          <div class="contact-links">
            <el-link
              href="mailto:zmc_li@foxmail.com"
              :underline="false"
              class="contact-link"
            >
              <el-icon class="link-icon"><i-ep-Message /></el-icon>
              <span class="link-text">zmc_li@foxmail.com</span>
            </el-link>
          </div>
        </div>

        <!-- 版权信息 -->
        <div class="footer-section">
          <p class="copyright">
            &copy; {{ currentYear }}
            <a
              href="https://github.com/nizhensh-i"
              target="_blank"
              :underline="false"
            >
              随想阁楼</a
            >
          </p>
          <p class="motto">Stay hungry, stay foolish.</p>
        </div>
      </div>
    </div>
  </PageHeadBack>
</template>

<style lang="scss" scoped>
.about-container {
  background: #fff;
}

.about-content {
  max-width: 600px;
  width: 100%;
  padding: 80px 40px 60px;
  margin: 0 auto;
}

// PC端样式 (≥768px)
@media (min-width: 768px) {
  .about-container {
    padding: 0;
  }

  .about-content {
    margin: 0;
    padding: 100px 60px 80px 120px;
    max-width: none;
    width: auto;
  }
}

// 大屏PC端 (≥1200px)
@media (min-width: 1200px) {
  .about-content {
    padding-left: 180px;
    padding-right: 80px;
  }
}

// 个人介绍
.intro-section {
  text-align: center;
  margin-bottom: 48px;

  .avatar {
    margin-bottom: 18px;

    .avatar-circle {
      width: 80px;
      height: 80px;
      background: #333;
      border-radius: 50%;
      display: inline-flex;
      align-items: center;
      justify-content: center;

      .avatar-text {
        font-size: 36px;
        color: white;
        font-weight: 300;
      }
    }
  }

  .name {
    font-size: 28px;
    font-weight: 400;
    margin: 0 0 8px 0;
    color: #333;
    letter-spacing: 1px;
  }

  .title {
    font-size: 14px;
    color: #999;
    margin: 0 0 16px 0;
    font-weight: 400;
    letter-spacing: 0.5px;
  }

  .bio {
    font-size: 15px;
    color: #666;
    line-height: 1.7;
    margin: 0 auto;
    max-width: 400px;
  }
}

// 区块标题
.section-title {
  font-size: 14px;
  font-weight: 500;
  margin: 0 0 20px 0;
  color: #999;
  text-transform: uppercase;
  letter-spacing: 1px;
  padding-bottom: 8px;
  border-bottom: 1px solid #eee;
}

// 项目介绍
.project-section {
  margin-bottom: 40px;

  .section-content {
    margin-bottom: 0;

    .description {
      font-size: 16px;
      line-height: 1.8;
      color: #444;
      margin: 0 0 16px 0;
      font-weight: 350;

      &:last-child {
        margin-bottom: 0;
      }
    }
  }
}

// 联系方式
.contact-section {
  margin-bottom: 40px;

  .contact-links {
    .contact-link {
      display: block;
      padding: 12px 0;
      color: #555;
      transition: color 0.2s ease;

      &:hover {
        color: #333;
      }

      .link-icon {
        margin-right: 8px;
        font-size: 16px;
        color: #999;
        vertical-align: middle;
      }

      .link-text {
        font-size: 15px;
        vertical-align: middle;
        font-weight: 350;
      }
    }
  }
}

// 底部
.footer-section {
  padding-top: 32px;
  border-top: 1px solid #eee;
  margin-bottom: 40px;
  text-align: center;

  .copyright {
    font-size: 13px;
    color: #999;
    margin: 0 0 8px 0;
    font-weight: 350;
    a {
      color: #999;
    }
  }

  .motto {
    font-size: 15px;
    color: #666;
    font-style: italic;
    margin: 0;
    font-weight: 350;
  }
}

// ==================== 响应式样式 ====================

// 手机设备 (< 768px)
@media (max-width: 767px) {
  .about-container {
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .about-content {
    margin: 0 auto;
    padding: 0px 20px;
  }

  .intro-section {
    margin-bottom: 40px;

    .avatar .avatar-circle {
      width: 64px;
      height: 64px;

      .avatar-text {
        font-size: 28px;
      }
    }

    .name {
      font-size: 24px;
    }
  }

  .project-section {
    margin-bottom: 32px;
  }

  .contact-section {
    margin-bottom: 32px;
  }

  .footer-section {
    margin-bottom: 32px;
    padding-top: 24px;
  }
}
</style>
