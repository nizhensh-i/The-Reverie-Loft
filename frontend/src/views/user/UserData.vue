<template>
  <div
    class="vapp-fullscreen-background"
    :class="{ 'content-loaded': contentLoaded }"
  >
    <el-page-header
      :style="{ color: backColor }"
      @back="$router.back()"
      title="返回"
    />

    <el-switch
      v-model="isUserPage"
      :loading="loading.switch"
      size="large"
      style="--el-switch-on-color: #424242; --el-switch-off-color: #424242"
      inline-prompt
      active-text="主页"
      inactive-text="文章"
      @change="handleSwitchChange"
      :before-change="beforeSwitch"
    />
    <div class="area-container">
      <div class="avatar" style="margin-top: 1rem">
        <music-player
          :avatar="user?.image || ''"
          :musics="user?.music || {}"
          :key="user?.image || 'placeholder'"
        ></music-player>
      </div>

      <div v-show="isUserPage">
        <!-- tags -->
        <el-card class="tags-container" v-show="user?.tags?.length > 0">
          <div class="card-title"></div>
          <div class="tags">
            <el-tag
              class="golang"
              v-for="item in user?.tags || []"
              :key="item"
              size="small"
              round
              @click="playTagAnimation"
            >
              {{ item }}
            </el-tag>
          </div>
        </el-card>
        <div class="user-info-container">
          <el-row :gutter="10">
            <el-col :span="12">
              <el-card class="user-info" shadow="never">
                <div class="card-title">
                  <span>个人信息</span>
                  <el-button
                    round
                    size="small"
                    style="margin-left: 5px"
                    v-if="isCurrentUser"
                    @click="editProfile"
                    >编辑资料</el-button
                  >
                  <el-button
                    type="danger"
                    round
                    size="small"
                    v-if="currentUser.isAdmin"
                    @click="editProfileAdmin"
                    >编辑资料 [管理员]</el-button
                  >
                </div>

                <el-row v-if="user?.nickname">
                  <el-col :xs="6" :lg="4" :xl="4">昵称</el-col>
                  <el-col :xs="8" :lg="12" :xl="10">{{
                    user?.nickname || ""
                  }}</el-col>
                </el-row>
                <el-row>
                  <el-col :xs="6" :lg="4" :xl="4">账号</el-col>
                  <el-col :xs="16" :lg="12" :xl="12">{{
                    user?.username || ""
                  }}</el-col>
                </el-row>
                <el-row v-if="user?.location">
                  <el-col :xs="6" :lg="4" :xl="4">地区</el-col>
                  <el-col :xs="16" :lg="12" :xl="10">{{ location }}</el-col>
                </el-row>
                <el-row v-if="user?.sex">
                  <el-col :xs="6" :lg="4" :xl="4">性别</el-col>
                  <el-col :xs="16" :lg="12" :xl="10">{{
                    user?.sex || ""
                  }}</el-col>
                </el-row>
                <el-row>
                  <el-col :xs="8" :lg="4" :xl="4">上线时间</el-col>
                  <el-col :xs="16" :lg="10" :xl="10">{{ from_now }}</el-col>
                </el-row>
              </el-card>
            </el-col>
            <el-col :span="12">
              <el-card class="fans" shadow="never">
                <el-row>
                  <el-col :span="6">
                    <el-statistic
                      title="粉丝"
                      :value="user?.followers_count || 0"
                      @click="followerDetail"
                    />
                  </el-col>
                  <el-col :span="6">
                    <el-statistic
                      title="关注"
                      :value="user?.followed_count || 0"
                      @click="followedDetail"
                    />
                  </el-col>
                </el-row>
              </el-card>
              <el-card class="user-wisdom" shadow="never">
                <div class="card-title">
                  <span>个性签名</span>
                </div>
                <!-- 打字机 -->
                <typewriter
                  class="typewriter"
                  :content="user?.about_me || ''"
                  :key="user?.about_me || ''"
                ></typewriter>
              </el-card>
            </el-col>
          </el-row>
        </div>
        <ButtonAnimate
          content="喜欢的电影"
          :isActive="activeInterest === 'movie'"
          @click="setActive('movie')"
        />
        <ButtonAnimate
          content="喜爱的书籍"
          :isActive="activeInterest === 'book'"
          @click="setActive('book')"
        />
        <interest
          :showInterest="activeInterest"
          :interest="user?.interest || { books: [], movies: [] }"
          :key="JSON.stringify(user?.interest || {})"
        />
        <el-card
          class="socialLinks"
          v-if="user?.social_account && !socialCount"
        >
          <socialLinks :links="user.social_account" />
        </el-card>
        <div class="bottom"></div>
      </div>
      <!-- 文章区  -->
      <div v-show="!isUserPage" class="posts-container">
        <SkeletonUtil
          :loading="loading.userData"
          :row="5"
          :count="1"
          :showAvatar="false"
        >
          <PostPreview
            v-for="item in posts"
            :key="item.id"
            :post="item"
            :containerStyle="{ marginBottom: '10px' }"
            @click="$router.push(`/postDetail/${item.id}`)"
            v-slide-in
          >
            <template #image>
              <PostImage :postImages="item.post_images" @click.stop="" />
            </template>
          </PostPreview>
          <el-pagination
            v-model:current-page="currentPage"
            :page-size="10"
            layout="total, prev, pager, next"
            :total="posts_count"
            @current-change="handleCurrentChange"
            :hide-on-single-page="true"
            :pager-count="5"
          />
          <el-empty
            :image-size="200"
            description="生活总归带点荒谬"
            v-if="posts.length === 0"
          />
        </SkeletonUtil>
      </div>
      <div class="block" v-if="!isCurrentUser"></div>
      <div class="footer" v-if="!isCurrentUser">
        <el-button color="#d1edc4" round class="chat" @click="openChat">
          <template #icon>
            <el-icon><i-ep-ChatRound /></el-icon>
          </template>
          私信
        </el-button>
        <div>
          <el-button
            color="#faecd8"
            round
            class="follow"
            v-if="isFollowOtherUser"
            @click="unFollowUser"
          >
            <template #icon>
              <el-icon>
                <i-ep-Switch v-if="isFollowEachOther" />
                <i-ep-Check v-else-if="isFollowOtherUser" />
              </el-icon>
            </template>
            取消关注
          </el-button>
          <el-button
            color="#faecd8"
            round
            class="follow"
            v-else
            :loading="loading.follow"
            @click="followUser"
          >
            <template #icon>
              <el-icon><i-ep-Plus /></el-icon>
            </template>
            关注
          </el-button>
        </div>
      </div>
    </div>
  </div>
  <van-dialog
    v-model:show="dialogShow"
    title="取消对该用户的关注"
    width="230"
    show-cancel-button
    :beforeClose="beforeClose"
  />
</template>

<script src="./userData.js"></script>

<style lang="scss" scoped>
:root {
  --leleo-background-image-url: none;
}

.vapp-fullscreen-background {
  position: position;
  height: 100%;
  width: 100%;
  top: 0;
  left: 0;
  z-index: -1;

  // 背景图片层
  &::before {
    content: "";
    background-image: var(--leleo-background-image-url);
    transition: background-image 0.8s ease;
    background-size: cover;
    background-position: center;
    position: absolute;
    height: 100%;
    width: 100%;
    z-index: -1;
    filter: brightness(85%);
  }

  // 玻璃态样式
  .glass {
    backdrop-filter: blur(15px);
    border-radius: 5%;
    background-color: transparent;
    border: none;
  }

  // 内容加载状态：模糊、低对比度
  .user-info,
  .fans,
  .user-wisdom,
  .tags-container,
  .socialLinks {
    @extend .glass;
    filter: blur(0.8px);
    color: rgba(255, 255, 255, 0.4) !important;
    text-shadow: 0 0 3px rgba(255, 255, 255, 0.3);
    transition: filter 0.6s ease, color 0.6s ease, text-shadow 0.6s ease;
  }

  // 标签初始状态
  .tags-container {
    max-width: 270px;
    margin: 10px auto;

    .tags {
      display: flex;
      flex-wrap: wrap;
      justify-content: center;
    }

    .el-tag {
      filter: blur(0.8px);
      color: rgba(255, 255, 255, 0.4) !important;
      transition: filter 0.6s ease, color 0.6s ease;
      background-color: transparent;
      margin: 4px;
      padding: 0px 10px;
      border-color: rgba(0, 0, 0, 0.12);
    }
  }

  // 统计数字初始状态
  .fans :deep(.el-statistic__head),
  .fans :deep(.el-statistic__number) {
    color: rgba(255, 255, 255, 0.4) !important;
    transition: color 0.6s ease;
  }

  // 内容加载完成：清晰状态
  &.content-loaded {
    .user-info,
    .fans,
    .user-wisdom,
    .tags-container,
    .socialLinks {
      filter: blur(0);
      color: #ffffff !important;
      text-shadow: none;
    }

    .tags-container .el-tag {
      filter: blur(0);
      color: #ffffff !important;
    }

    .fans :deep(.el-statistic__head),
    .fans :deep(.el-statistic__number) {
      color: #ffffff !important;
    }
  }

  // 页面头部
  .el-page-header {
    position: fixed;
    top: 56px;
    left: 10px;
    z-index: 99;
  }

  // 切换开关
  .el-switch {
    position: fixed;
    right: 0;
    z-index: 99;
  }

  // 主内容区域
  .area-container {
    overflow-y: auto;
    overflow-x: hidden;
    height: 100vh;
    z-index: 1;

    .avatar {
      display: flex;
      flex-direction: column;
      align-items: center;
      margin-bottom: 1rem;
    }

    .user-info-container {
      width: 90%;
      margin: 0 auto;

      .user-info {
        min-height: 190px;
        font-size: 12px;
        color: #fff;
        letter-spacing: 0.05em;
        margin-bottom: 10px;

        .card-title {
          margin-bottom: 10px;
          color: #fff;
          font-size: 20px;
        }
      }

      .fans .el-statistic {
        width: 30px;
        text-align: center;
      }

      .user-wisdom {
        margin-top: 5px;
        max-height: 120px;

        .typewriter {
          margin: 12px;
        }
      }
    }

    .socialLinks {
      max-width: 270px;
      margin: 0px auto;

      :deep(.el-card__body) {
        padding: 2px;
      }
    }
  }

  // 点击tag动画
  .golang {
    transition: all 0.2s ease-in-out;
    position: relative;
    opacity: 1;
    overflow: hidden;

    &::before {
      content: "";
      background-color: rgba(255, 255, 255, 0.5);
      height: 100%;
      width: 3em;
      display: block;
      position: absolute;
      top: 0;
      left: -4.5em;
      transform: skewX(-45deg) translateX(0);
      transition: none;
    }

    &.animate::before {
      transform: skewX(-45deg) translateX(260px);
      transition: all 0.7s ease-in-out;
    }
  }

  // 底部固定操作栏
  .footer {
    position: fixed;
    bottom: 0px;
    padding: 10px;
    height: 40px;
    width: 95%;
    margin: 0px auto;
    display: flex;
    justify-content: space-between;

    div,
    .chat {
      width: 48%;
      height: 40px;
    }

    .follow {
      width: 100%;
      height: 40px;
    }
  }

  // 其他样式
  .bottom {
    height: 1500px;
    width: 100%;
  }

  .posts-container {
    margin: 0px 20px;
  }

  .block {
    margin-bottom: 33px;
  }
}

// Element Plus 深度选择器
:deep(.el-card__body) {
  padding: 8px;
}

:deep(.el-tag__content) {
  color: #ffffff;
  font-family: Roboto, sans-serif;
}

// 移动端适配
@media (max-width: 768px) {
  .vapp-fullscreen-background {
    .area-container {
      .user-info-container {
        width: 95%;
      }
    }
  }
}
</style>
