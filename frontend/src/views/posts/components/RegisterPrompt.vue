<template>
  <div class="register-prompt" @click="handleExplore">
    <div class="prompt-content">
      <div class="prompt-header">
        <div class="community-stats">
          <div class="stat-item">
            <el-icon><i-ep-User /></el-icon>
            <span class="stat-text"
              >已有 {{ currentUsers.toLocaleString() }} 位探索者</span
            >
          </div>
          <!-- <div class="stat-item">
            <el-icon><i-ep-ChatDotRound /></el-icon>
            <span class="stat-text">本周新增 {{ weeklyPosts }} 条随想</span>
          </div> -->
        </div>
        <div class="preview-content">
          <div class="preview-card">
            <h4>解锁完整阁楼地图</h4>
            <p>看看其他人分享了什么</p>
          </div>
        </div>
      </div>

      <div class="prompt-cta">
        <div class="cta-text">
          <h3>这片阁楼不止这些故事</h3>
          <p>登录后继续探索，或许能找到共鸣</p>
        </div>
        <div class="cta-actions">
          <el-button
            type="primary"
            size="default"
            round
            @click.stop="$router.push('/login')"
          >
            开始探索
          </el-button>
        </div>
      </div>
    </div>

    <div class="floating-elements">
      <div class="floating-item" style="top: 20%; left: 10%">
        <el-icon><i-ep-Collection /></el-icon>
      </div>
      <div class="floating-item" style="top: 60%; right: 15%">
        <el-icon><i-ep-Star /></el-icon>
      </div>
    </div>
  </div>
</template>

<script>
const STATS_CONFIG = {
  BASE_USERS: 127, // 初始用户基数
  USERS_PER_HOUR: 1, // 每小时新增用户数（可根据实际情况调整）
  BASE_WEEKLY_POSTS: 36, // 基础周新增随想数
  WEEKLY_VARIATION: 15, // 每周波动范围
  CACHE_KEY: "loft_stats_cache", // localStorage key
  UPDATE_INTERVAL: 5 * 60 * 1000, // 5分钟更新一次
};

export default {
  name: "RegisterPrompt",
  data() {
    return {
      currentUsers: 127,
      weeklyPosts: 36,
    };
  },
  created() {
    this.initStats();
    // 每5分钟更新一次数据
    this.updateTimer = setInterval(() => {
      this.updateStats();
    }, STATS_CONFIG.UPDATE_INTERVAL);
  },
  beforeDestroy() {
    // 清理定时器
    if (this.updateTimer) {
      clearInterval(this.updateTimer);
    }
  },
  methods: {
    // 初始化统计数据
    initStats() {
      const cache = this.getCache();
      const now = new Date();
      const today = now.toDateString();

      // 检查是否是新的一天
      if (cache.lastCalcDate !== today) {
        // 重新计算今日数据
        const startOfDay = new Date(now).setHours(0, 0, 0, 0);
        const hoursPassed = Math.min((now - startOfDay) / (1000 * 60 * 60), 24);
        const todayGrowth = Math.floor(
          hoursPassed * STATS_CONFIG.USERS_PER_HOUR
        );

        cache.lastCalcDate = today;
        cache.todayUsers = STATS_CONFIG.BASE_USERS + todayGrowth;
        cache.weeklyPosts = this.calculateWeeklyPosts();
        this.setCache(cache);
      }

      this.currentUsers = cache.todayUsers;
      this.weeklyPosts = cache.weeklyPosts;
    },

    // 更新统计数据
    updateStats() {
      const now = new Date();
      const today = now.toDateString();
      const cache = this.getCache();

      // 如果是新的一天，重新计算
      if (cache.lastCalcDate !== today) {
        // 每周一重置基数（模拟每周统计重置）
        const dayOfWeek = now.getDay(); // 0=周日
        if (dayOfWeek === 1) {
          // 周一
          // 根据上周表现微调本周基数
          const variation = Math.floor((Math.random() - 0.5) * 20);
          STATS_CONFIG.BASE_USERS = STATS_CONFIG.BASE_USERS + variation;
        }

        this.initStats();
      } else {
        // 同一天内，更新用户数和随想数
        const startOfDay = new Date(now).setHours(0, 0, 0, 0);
        const hoursPassed = Math.min((now - startOfDay) / (1000 * 60 * 60), 24);
        const todayGrowth = Math.floor(
          hoursPassed * STATS_CONFIG.USERS_PER_HOUR
        );

        this.currentUsers = STATS_CONFIG.BASE_USERS + todayGrowth;
        this.weeklyPosts = this.calculateWeeklyPosts();

        // 更新缓存
        cache.todayUsers = this.currentUsers;
        cache.weeklyPosts = this.weeklyPosts;
        this.setCache(cache);
      }
    },

    // 计算本周新增随想数
    calculateWeeklyPosts() {
      const now = new Date();
      const dayOfWeek = now.getDay(); // 0=周日
      const weekProgress = Math.max(dayOfWeek, 1) / 7; // 至少按周一计算

      // 基础值 + 本周进度 + 随机波动
      // 周一：86 * 0.7 + 波动
      // 周日：86 * 1.0 + 波动
      const baseAmount =
        STATS_CONFIG.BASE_WEEKLY_POSTS * (0.7 + weekProgress * 0.3);
      const randomFactor =
        (Math.random() - 0.5) * STATS_CONFIG.WEEKLY_VARIATION;

      return Math.max(1, Math.floor(baseAmount + randomFactor));
    },

    // 获取缓存
    getCache() {
      try {
        const cached = localStorage.getItem(STATS_CONFIG.CACHE_KEY);
        if (cached) {
          return JSON.parse(cached);
        }
      } catch (e) {
        console.warn("读取统计数据缓存失败:", e);
      }

      // 初始化缓存
      return {
        baseUsers: STATS_CONFIG.BASE_USERS,
        todayUsers: STATS_CONFIG.BASE_USERS,
        weeklyPosts: STATS_CONFIG.BASE_WEEKLY_POSTS,
        lastCalcDate: new Date().toDateString(),
      };
    },

    // 设置缓存
    setCache(data) {
      try {
        localStorage.setItem(STATS_CONFIG.CACHE_KEY, JSON.stringify(data));
      } catch (e) {
        console.warn("保存统计数据缓存失败:", e);
      }
    },

    // 点击探索
    handleExplore() {
      ElMessage({
        message: "登录后继续探索更多精彩内容",
        type: "info",
        duration: 2000,
      });
    },

    // 格式化数字（可选：大于1000时显示为K）
    formatNumber(num) {
      if (num >= 1000) {
        return (num / 1000).toFixed(1) + "K";
      }
      return num.toString();
    },
  },
};
</script>

<style lang="scss" scoped>
.register-prompt {
  position: relative;
  margin: 24px 0;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(0, 0, 0, 0.05);
  overflow: hidden;
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);

  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 32px rgba(0, 0, 0, 0.08);
    border-color: rgba(64, 158, 255, 0.15);
  }
}

.prompt-content {
  padding: 24px;
  position: relative;
  z-index: 2;
}

.prompt-header {
  margin-bottom: 20px;
}

.community-stats {
  display: flex;
  gap: 20px;
  margin-bottom: 16px;
  flex-wrap: wrap;

  .stat-item {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 13px;
    color: #606266;
    font-weight: 500;

    .el-icon {
      font-size: 16px;
      color: #409eff;
    }
  }

  @media (max-width: 768px) {
    gap: 12px;

    .stat-item {
      font-size: 12px;
    }
  }
}

.preview-content {
  .preview-card {
    padding: 16px;
    background: rgba(245, 247, 250, 0.7);
    border-radius: 12px;
    border: 1px solid rgba(0, 0, 0, 0.03);

    h4 {
      font-size: 15px;
      font-weight: 600;
      margin: 0 0 4px 0;
      color: #303133;
    }

    p {
      font-size: 13px;
      color: #606266;
      margin: 0;
    }
  }
}

.prompt-cta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;

  @media (max-width: 768px) {
    flex-direction: column;
    text-align: center;
    gap: 20px;
  }
}

.cta-text {
  flex: 1;

  h3 {
    font-size: 18px;
    font-weight: 600;
    margin: 0 0 6px 0;
    color: #303133;
    line-height: 1.4;
  }

  p {
    font-size: 14px;
    color: #606266;
    margin: 0;
    line-height: 1.5;
  }

  @media (max-width: 768px) {
    h3 {
      font-size: 17px;
    }
  }
}

.cta-actions {
  flex-shrink: 0;

  .el-button {
    padding: 10px 24px;
    font-weight: 500;
  }

  @media (max-width: 768px) {
    width: 100%;

    .el-button {
      width: 100%;
    }
  }
}

.floating-elements {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
  opacity: 0.25;
  z-index: 1;
}

.floating-item {
  position: absolute;
  animation: float 6s ease-in-out infinite;

  &:nth-child(2) {
    animation-delay: 1s;
  }

  .el-icon {
    font-size: 20px;
    color: #409eff;
    opacity: 0.4;
  }
}

@keyframes float {
  0%,
  100% {
    transform: translateY(0px) rotate(0deg);
  }
  50% {
    transform: translateY(-10px) rotate(5deg);
  }
}
</style>
