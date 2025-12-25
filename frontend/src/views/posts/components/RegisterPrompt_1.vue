<template>
  <div class="register-prompt">
    <div class="prompt-content">
      <div class="prompt-icon">
        <el-icon><i-ep-Star /></el-icon>
      </div>
      <div class="prompt-text">
        <h3>登录后，你也可以留下点什么。</h3>
        <p>发布文章、点赞评论、关注作者、接收消息</p>
      </div>
      <div class="prompt-actions">
        <el-button
          type="primary"
          size="small"
          @click="$router.push('/register')"
          >立即注册</el-button
        >
        <el-button size="small" @click="$router.push('/login')">登录</el-button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "RegisterPrompt",
};
</script>

<style lang="scss" scoped>
.register-prompt {
  margin: 20px 0;
  border-radius: 12px;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4edf9 100%);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  overflow: hidden;
  transition: transform 0.3s ease, box-shadow 0.3s ease;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(0, 0, 0, 0.08);
  }
}

.prompt-content {
  display: flex;
  align-items: center;
  padding: 16px 20px;

  @media (max-width: 768px) {
    flex-direction: column;
    text-align: center;
    padding: 20px;
  }
}

.prompt-icon {
  margin-right: 16px;

  .el-icon {
    font-size: 32px;
    color: #409eff;
    background: rgba(64, 158, 255, 0.1);
    padding: 10px;
    border-radius: 50%;
  }

  @media (max-width: 768px) {
    margin-right: 0;
    margin-bottom: 12px;
  }
}

.prompt-text {
  flex: 1;

  h3 {
    font-size: 16px;
    font-weight: 600;
    margin: 0 0 4px 0;
    color: #303133;
  }

  p {
    font-size: 14px;
    color: #606266;
    margin: 0;
  }

  @media (max-width: 768px) {
    margin-bottom: 16px;
  }
}

.prompt-actions {
  display: flex;
  gap: 8px;

  @media (max-width: 768px) {
    width: 100%;
    justify-content: center;
  }
}
</style>
