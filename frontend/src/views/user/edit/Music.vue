<script setup>
import { ref, reactive, computed, onMounted, onUnmounted } from "vue";
import PageHeadBack from "@/utils/components/PageHeadBack.vue";
import { useCurrentUserStore } from "@/stores/user";
import { cloneDeep } from "@pureadmin/utils";
import editApi from "@/api/user/editApi.js";
import { clearObj } from "@/utils/common.js";
import "APlayer/dist/APlayer.min.css";
import APlayer from "APlayer";

const user = useCurrentUserStore();

const userData = reactive({
  localUserInfo: {
    id: "",
    music: {
      name: "",
      artist: "",
      url: "",
      pic: "",
      lrc: "",
    },
  },
});

userData.localUserInfo = cloneDeep(user.userInfo);

// 响应式数据
const musicInfoLoading = ref(false);
const setMusicLoading = ref(false);

const musicInfo = ref([]);
const searchKeyword = ref("");
const currentPage = ref(1);
const pageSize = ref(10);
// 实际用于搜索的关键词（点击搜索按钮后才生效）
const activeSearchKeyword = ref("");

// 音频播放相关
const tableHeight = ref("500");
const h1 = ref(null);
const h2 = ref(null);
const h3 = ref(null);
const aplayerInstance = ref(null);
const currentPlayingMusic = ref(null);
const isPlaying = ref(false);
const isMobile = ref(window.innerWidth <= 768);

// 抽屉显示控制
const showSelectedDrawer = ref(false);

// 计算属性：过滤后的音乐数据
const filteredMusicInfo = computed(() => {
  if (!activeSearchKeyword.value || !activeSearchKeyword.value.trim()) {
    return musicInfo.value;
  }

  const keyword = activeSearchKeyword.value.toLowerCase().trim();
  return musicInfo.value.filter(
    (item) =>
      (item?.name && item.name.toLowerCase().includes(keyword)) ||
      (item?.artist && item.artist.toLowerCase().includes(keyword))
  );
});

// 计算属性：分页后的数据
const paginatedMusicInfo = computed(() => {
  const startIndex = (currentPage.value - 1) * pageSize.value;
  const endIndex = startIndex + pageSize.value;
  return filteredMusicInfo.value.slice(startIndex, endIndex);
});

onMounted(() => {
  fetchMusicInfo();
  calTableHeight();
  initAPlayer();

  // 监听窗口大小变化
  window.addEventListener("resize", handleResize);
});

// 组件卸载时移除监听器并销毁播放器
onUnmounted(() => {
  window.removeEventListener("resize", handleResize);

  // 销毁 APlayer 实例
  if (aplayerInstance.value) {
    aplayerInstance.value.pause();
    aplayerInstance.value.destroy();
    aplayerInstance.value = null;
    isPlaying.value = false;
    currentPlayingMusic.value = null;
  }
});

// 处理窗口大小变化
const handleResize = () => {
  isMobile.value = window.innerWidth <= 768;
};

// 获取音乐信息
const fetchMusicInfo = async () => {
  musicInfoLoading.value = true;
  try {
    const response = await fetch(
      // `https://api.i-meto.com/meting/api?server=${props.musicConfig.server}&type=${props.musicConfig.type}&id=${props.musicConfig.id}`
      `https://api.qijieya.cn/meting/?server=${
        import.meta.env.VITE_MusicServer
      }&type=${import.meta.env.VITE_MusicType}&id=${
        import.meta.env.VITE_MusicPlaylistId
      }`
    );
    if (!response.ok) {
      throw new Error(`网络请求失败: ${response.status}`);
    }
    const data = await response.json();
    console.log("音乐信息获取成功:", data);
    musicInfo.value = data;
    // 重置搜索和分页状态
    searchKeyword.value = "";
    currentPage.value = 1;
  } catch (error) {
    console.error("请求音乐信息失败:", error);
    // 设置默认音乐信息以防请求失败
    musicInfo.value = [
      {
        name: "音乐加载失败",
        artist: "请检查网络连接",
        url: "",
        pic: "",
      },
    ];
  } finally {
    musicInfoLoading.value = false;
  }
};

// 分页切换处理
const handlePageChange = async (page) => {
  // 添加轻微延迟以模拟请求
  await new Promise((resolve) => setTimeout(resolve, 300));
  currentPage.value = page;
};

// 搜索处理
const handleSearch = async () => {
  // 添加轻微延迟以模拟请求
  await new Promise((resolve) => setTimeout(resolve, 300));

  // 设置实际搜索关键词
  activeSearchKeyword.value = searchKeyword.value;
  // 搜索时跳转到第一页
  currentPage.value = 1;
};

// 重置搜索
const handleResetSearch = async () => {
  // 添加轻微延迟以模拟请求
  await new Promise((resolve) => setTimeout(resolve, 300));

  searchKeyword.value = "";
  // 清空实际搜索关键词
  activeSearchKeyword.value = "";
};

// 选择音乐
const handleSelectMusic = async (music) => {
  // 存储上次选择的音乐
  userData.localUserInfo.music = music;
  await saveMusic();
  user.setUserInfo(userData.localUserInfo);
};

// 取消选择音乐
const handleCancelSelect = async () => {
  // 将已选择的音乐设置为空对象
  userData.localUserInfo.music = clearObj(userData.localUserInfo.music);
  await saveMusic();
  user.setUserInfo(userData.localUserInfo);
};

// 检查是否为已选择的音乐
const isSelected = (music) => {
  if (!music || !userData.localUserInfo?.music) return false;

  return (
    userData.localUserInfo.music.name === music.name &&
    userData.localUserInfo.music.artist === music.artist
  );
};

async function saveMusic() {
  try {
    setMusicLoading.value = true;

    if (!user?.userInfo?.id) {
      throw new Error("用户信息不完整，无法保存音乐设置");
    }

    await editApi.editUser(user.userInfo.id, {
      music: userData.localUserInfo.music,
    });
  } catch (error) {
    console.error("保存音乐设置失败:", error);
    // 可以在这里添加用户提示
  } finally {
    setMusicLoading.value = false;
  }
}

// 初始化 APlayer
const initAPlayer = () => {
  // 如果已有实例，先销毁
  if (aplayerInstance.value) {
    aplayerInstance.value.destroy();
  }

  // 创建新的 APlayer 实例
  aplayerInstance.value = new APlayer({
    container: document.getElementById("aplayer"),
    fixed: false, // 不固定显示，集成在页面中
    autoplay: false,
    audio: [],
    lrcType: 3,
    mini: false,
  });

  // 监听播放器事件
  aplayerInstance.value.on("play", () => {
    isPlaying.value = true;
  });

  aplayerInstance.value.on("pause", () => {
    isPlaying.value = false;
  });

  aplayerInstance.value.on("ended", () => {
    isPlaying.value = false;
    currentPlayingMusic.value = null;
  });
};

// 播放音乐
const playMusic = (music) => {
  if (!music?.url) return;

  // 如果点击的是当前正在播放的音乐
  if (currentPlayingMusic.value?.name === music.name && aplayerInstance.value) {
    if (isPlaying.value) {
      // 如果是播放状态，则暂停
      aplayerInstance.value.pause();
      isPlaying.value = false;
    } else {
      // 如果是暂停状态，则继续播放
      aplayerInstance.value.play();
      isPlaying.value = true;
    }
    return;
  }

  // 如果不是当前播放的音乐，或者没有播放器实例
  currentPlayingMusic.value = music;
  isPlaying.value = true;

  // 如果 APlayer 实例不存在，先初始化
  if (!aplayerInstance.value) {
    initAPlayer();
  }

  // 停止当前播放
  aplayerInstance.value.pause();

  // 更新音频源
  aplayerInstance.value.list.clear();
  aplayerInstance.value.list.add([
    {
      name: music.name,
      artist: music.artist,
      url: music.url,
      cover: music.pic,
      lrc: music.lrc || "",
    },
  ]);

  // 开始播放
  aplayerInstance.value.play();
};

const calTableHeight = async () => {
  const h1Height = h1.value?.offsetHeight || 0;
  const h2Height = h2.value?.offsetHeight || 0;
  const h3Height = h3.value?.offsetHeight || 0;
  // 播放器现在集成在卡片内部，表格高度需要适应卡片内容
  tableHeight.value = `calc(100vh - ${h1Height}px - ${h2Height}px - ${h3Height}px - 120px - 30px - var(--el-main-padding) * 2)`;
};
</script>

<template>
  <PageHeadBack>
    <!-- 统一卡片容器 -->
    <el-card class="music-container" shadow="hover">
      <!-- 卡片头部：搜索和已选择区域 -->
      <template #header>
        <div class="card-header" ref="h1">
          <div class="header-left">
            <span class="card-title">
              <el-icon><i-ep-Headset /></el-icon>
              音乐库
            </span>
            <el-tag
              v-if="
                userData.localUserInfo.music &&
                userData.localUserInfo.music.name
              "
              type="success"
              size="small"
              class="selected-tag"
              @click="showSelectedDrawer = true"
            >
              <el-icon><i-ep-Star /></el-icon>
              已选择
            </el-tag>
          </div>

          <div class="header-right">
            <el-input
              v-model="searchKeyword"
              placeholder="搜索歌曲名或作者"
              clearable
              @keyup.enter="handleSearch"
              @clear="handleResetSearch"
              style="width: 280px"
              size="small"
            >
              <template #prefix>
                <el-icon><i-ep-Search /></el-icon>
              </template>
              <template #append>
                <el-button
                  type="primary"
                  @click="handleSearch"
                  size="small"
                  :loading="musicInfoLoading"
                >
                  搜索
                </el-button>
              </template>
            </el-input>
          </div>
        </div>
      </template>

      <!-- 卡片内容：音乐列表 -->
      <!-- 桌面端：表格布局 -->
      <el-table
        v-if="!isMobile"
        :data="paginatedMusicInfo"
        v-loading="musicInfoLoading"
        :height="tableHeight"
        stripe
        border
        class="music-table desktop-table"
        ref="h2"
      >
        <el-table-column prop="pic" label="封面" width="80" align="center">
          <template #default="scope">
            <el-image
              :src="scope.row.pic"
              style="width: 40px; height: 40px; border-radius: 4px"
              fit="cover"
              :preview-src-list="scope.row.pic ? [scope.row.pic] : []"
              :preview-teleported="true"
              :hide-on-click-modal="true"
            >
              <template #error>
                <div class="image-error">
                  <el-icon><i-ep-Picture /></el-icon>
                </div>
              </template>
            </el-image>
          </template>
        </el-table-column>

        <el-table-column prop="name" label="歌曲名" min-width="100" />

        <el-table-column prop="artist" label="作者" min-width="60" />

        <el-table-column label="试听" width="55" align="center">
          <template #default="scope">
            <el-button
              circle
              size="small"
              :type="
                currentPlayingMusic?.name === scope.row.name
                  ? 'success'
                  : 'primary'
              "
              @click="playMusic(scope.row)"
              :disabled="!scope.row.url"
            >
              <el-icon>
                <i-ep-VideoPlay
                  v-if="
                    !(currentPlayingMusic?.name === scope.row.name && isPlaying)
                  "
                />
                <i-ep-VideoPause v-else />
              </el-icon>
            </el-button>
          </template>
        </el-table-column>

        <el-table-column label="选择" width="100" align="center" fixed="right">
          <template #default="scope">
            <el-button
              :type="isSelected(scope.row) ? 'danger' : 'primary'"
              size="small"
              @click="
                isSelected(scope.row)
                  ? handleCancelSelect()
                  : handleSelectMusic(scope.row)
              "
              :loading="setMusicLoading && isSelected(scope.row) === false"
              :disabled="!scope.row.url"
            >
              {{ isSelected(scope.row) ? "取消选择" : "选择" }}
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 移动端：紧凑卡片布局 -->
      <div v-else class="mobile-music-list" ref="h2">
        <div
          v-for="(music, index) in paginatedMusicInfo"
          :key="index"
          class="mobile-music-card"
          :class="{
            selected: isSelected(music),
            playing: currentPlayingMusic?.name === music.name,
          }"
        >
          <div class="card-content">
            <!-- 左侧：封面和基础信息 -->
            <div class="music-cover-info">
              <div class="music-cover">
                <el-image
                  :src="music.pic"
                  fit="cover"
                  :preview-src-list="music.pic ? [music.pic] : []"
                  :preview-teleported="true"
                >
                  <template #error>
                    <div class="cover-error">
                      <el-icon><i-ep-Picture /></el-icon>
                    </div>
                  </template>
                </el-image>
              </div>
              <div class="music-basic-info">
                <div class="music-name" :title="music.name">
                  {{ music.name }}
                </div>
                <div class="music-artist" :title="music.artist">
                  {{ music.artist }}
                </div>
              </div>
            </div>

            <!-- 右侧：操作按钮组 -->
            <div class="music-actions-group">
              <el-button
                circle
                size="small"
                :type="
                  currentPlayingMusic?.name === music.name
                    ? 'success'
                    : 'primary'
                "
                @click="playMusic(music)"
                :disabled="!music.url"
                class="play-btn"
              >
                <el-icon>
                  <i-ep-VideoPlay
                    v-if="
                      !(currentPlayingMusic?.name === music.name && isPlaying)
                    "
                  />
                  <i-ep-VideoPause v-else />
                </el-icon>
              </el-button>

              <el-button
                :type="isSelected(music) ? 'danger' : 'primary'"
                size="small"
                @click="
                  isSelected(music)
                    ? handleCancelSelect()
                    : handleSelectMusic(music)
                "
                :loading="setMusicLoading && isSelected(music) === false"
                :disabled="!music.url"
                class="select-btn"
              >
                {{ isSelected(music) ? "取消" : "选择" }}
              </el-button>
            </div>
          </div>

          <!-- 状态指示器 -->
          <div class="status-indicator">
            <span v-if="isSelected(music)" class="selected-indicator">
              <el-icon><i-ep-Star /></el-icon>已选择
            </span>
            <span
              v-if="currentPlayingMusic?.name === music.name && isPlaying"
              class="playing-indicator"
            >
              <el-icon><i-ep-Headset /></el-icon>播放中
            </span>
          </div>
        </div>

        <div
          v-if="paginatedMusicInfo.length === 0 && !musicInfoLoading"
          class="empty-state"
        >
          <el-empty description="暂无音乐数据" />
        </div>
      </div>

      <!-- 分页区域 -->
      <div class="pagination-section" ref="h3">
        <el-pagination
          v-model:current-page="currentPage"
          :page-size="pageSize"
          :total="filteredMusicInfo.length"
          layout="total, prev, pager, next"
          :pager-count="5"
          :hide-on-single-page="true"
          size="small"
          background
          @size-change="
            (size) => {
              pageSize = size;
              currentPage = 1;
            }
          "
          @current-change="handlePageChange"
        />
      </div>

      <!-- 播放器区域 - 集成在卡片底部 -->
      <div class="player-section">
        <div id="aplayer"></div>
      </div>
    </el-card>

    <!-- 已选择音乐抽屉 -->
    <el-drawer
      v-model="showSelectedDrawer"
      title="已选择的音乐"
      direction="rtl"
      size="350px"
    >
      <div
        class="selected-music-drawer"
        v-if="userData.localUserInfo.music && userData.localUserInfo.music.name"
      >
        <div class="selected-music-content">
          <el-image
            :src="userData.localUserInfo.music.pic"
            style="
              width: 120px;
              height: 120px;
              border-radius: 8px;
              margin-bottom: 16px;
            "
            fit="cover"
            :preview-src-list="
              userData.localUserInfo.music.pic
                ? [userData.localUserInfo.music.pic]
                : []
            "
            :preview-teleported="true"
            :hide-on-click-modal="true"
          >
            <template #error>
              <div class="image-error-large">
                <el-icon><i-ep-Picture /></el-icon>
                <span>无封面</span>
              </div>
            </template>
          </el-image>

          <div class="music-info-drawer">
            <h3 class="music-title">{{ userData.localUserInfo.music.name }}</h3>
            <p class="music-author">
              {{ userData.localUserInfo.music.artist }}
            </p>
          </div>

          <div class="drawer-actions">
            <el-button
              type="primary"
              @click="playMusic(userData.localUserInfo.music)"
              :disabled="!userData.localUserInfo.music.url"
            >
              <el-icon><i-ep-VideoPlay /></el-icon>
              播放
            </el-button>
            <el-button type="danger" @click="handleCancelSelect">
              <el-icon><i-ep-Delete /></el-icon>
              取消选择
            </el-button>
          </div>
        </div>
      </div>

      <div v-else class="empty-selected">
        <el-empty description="暂未选择音乐" />
      </div>
    </el-drawer>
  </PageHeadBack>
</template>

<style lang="scss" scoped>
.music-container {
  margin-bottom: 20px;

  :deep(.el-card__header) {
    padding: 16px 20px;
    border-bottom: 1px solid #f0f0f0;
  }

  .card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;

    .header-left {
      display: flex;
      align-items: center;
      gap: 12px;

      .card-title {
        font-size: 16px;
        font-weight: 600;
        color: #303133;
        display: flex;
        align-items: center;
        gap: 8px;
      }

      .selected-tag {
        cursor: pointer;
        transition: all 0.3s ease;

        &:hover {
          transform: scale(1.05);
          box-shadow: 0 2px 8px rgba(103, 194, 58, 0.2);
        }
      }
    }

    .header-right {
      display: flex;
      align-items: center;

      :deep(.el-input-group__append) {
        .el-button {
          border-top-left-radius: 0;
          border-bottom-left-radius: 0;
        }
      }
    }
  }
}

.music-table {
  margin-bottom: 0;

  .image-error {
    width: 40px;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
    background-color: #f5f7fa;
    border-radius: 4px;
    color: #c0c4cc;
  }
}

.pagination-section {
  display: flex;
  justify-content: center;
  padding: 16px 0 8px;
  margin-top: 16px;
  border-top: 1px solid #f0f0f0;
}

.player-section {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #f0f0f0;

  #aplayer {
    margin: 0;
    border-radius: 8px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);

    :deep(.aplayer-info) {
      background: #f8f9fa;
      border-bottom: 1px solid #e8e8e8;
    }

    :deep(.aplayer-controller) {
      background: #fff;
    }

    :deep(.aplayer-list) {
      border: none;
      max-height: 200px;
    }
  }
}

.selected-music-drawer {
  padding: 20px;

  .selected-music-content {
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;

    .image-error-large {
      width: 120px;
      height: 120px;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      background-color: #f5f7fa;
      border-radius: 8px;
      color: #c0c4cc;
      gap: 8px;

      .el-icon {
        font-size: 32px;
      }

      span {
        font-size: 14px;
        color: #909399;
      }
    }

    .music-info-drawer {
      margin-bottom: 24px;

      .music-title {
        margin: 0 0 8px 0;
        font-size: 18px;
        font-weight: 600;
        color: #303133;
      }

      .music-author {
        margin: 0;
        font-size: 14px;
        color: #606266;
      }
    }

    .drawer-actions {
      display: flex;
      gap: 12px;

      .el-button {
        min-width: 100px;
      }
    }
  }
}

.empty-selected {
  padding: 40px 20px;
}

// 移动端紧凑卡片布局
.mobile-music-list {
  margin-bottom: 0;

  .mobile-music-card {
    background: #fff;
    border: 1px solid #e8e8e8;
    border-radius: 12px;
    margin-bottom: 8px;
    padding: 12px;
    transition: all 0.3s ease;
    position: relative;

    &:hover {
      box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
      transform: translateY(-1px);
    }

    &.selected {
      border-color: #f56c6c;
      background: linear-gradient(135deg, #fef0f0 0%, #fff 50%);
      box-shadow: 0 2px 8px rgba(245, 108, 108, 0.15);
    }

    &.playing {
      border-color: #67c23a;
      background: linear-gradient(135deg, #f0f9eb 0%, #fff 50%);
      box-shadow: 0 2px 8px rgba(103, 194, 58, 0.15);
    }

    .card-content {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 8px;

      .music-cover-info {
        display: flex;
        align-items: center;
        gap: 12px;
        flex: 1;
        min-width: 0;

        .music-cover {
          flex-shrink: 0;

          .el-image {
            width: 44px;
            height: 44px;
            border-radius: 8px;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);

            .cover-error {
              width: 44px;
              height: 44px;
              display: flex;
              align-items: center;
              justify-content: center;
              background: linear-gradient(135deg, #f5f7fa 0%, #e4e7ed 100%);
              border-radius: 8px;
              color: #c0c4cc;

              .el-icon {
                font-size: 20px;
              }
            }
          }
        }

        .music-basic-info {
          flex: 1;
          min-width: 0;

          .music-name {
            font-size: 15px;
            font-weight: 600;
            color: #303133;
            margin-bottom: 2px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            line-height: 1.2;
          }

          .music-artist {
            font-size: 13px;
            color: #606266;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            line-height: 1.2;
          }
        }
      }

      .music-actions-group {
        display: flex;
        align-items: center;
        gap: 6px;
        flex-shrink: 0;

        .play-btn {
          width: 36px;
          height: 36px;

          .el-icon {
            font-size: 16px;
          }
        }

        .select-btn {
          height: 36px;
          padding: 0 12px;
          font-size: 13px;
          min-width: 50px;
        }
      }
    }

    .status-indicator {
      margin-top: 8px;
      display: flex;
      align-items: center;
      gap: 8px;

      .selected-indicator {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        font-size: 12px;
        color: #f56c6c;
        background: rgba(245, 108, 108, 0.1);
        padding: 2px 8px;
        border-radius: 12px;

        .el-icon {
          font-size: 12px;
        }
      }

      .playing-indicator {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        font-size: 12px;
        color: #67c23a;
        background: rgba(103, 194, 58, 0.1);
        padding: 2px 8px;
        border-radius: 12px;

        .el-icon {
          font-size: 12px;
        }
      }
    }
  }

  .empty-state {
    padding: 40px 20px;
    text-align: center;
    color: #909399;
  }
}

// 响应式适配
@media (max-width: 768px) {
  .music-container {
    .card-header {
      flex-direction: column;
      align-items: stretch;
      gap: 16px;

      .header-left {
        justify-content: center;
      }

      .header-right {
        justify-content: center;

        .el-input {
          width: 100% !important;
          max-width: 280px;
        }
      }
    }
  }

  // 桌面端表格在移动端隐藏
  .desktop-table {
    display: none;
  }
}

// 桌面端适配
@media (min-width: 769px) {
  // 移动端卡片在桌面端隐藏
  .mobile-music-list {
    display: none;
  }

  .desktop-table {
    display: table;
  }
}
</style>
