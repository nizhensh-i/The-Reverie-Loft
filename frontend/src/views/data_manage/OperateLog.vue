<script>
import ButtonClick from "@/utils/components/ButtonClick.vue";
import PageScroll from "@/utils/components/PageScroll.vue";
import logApi from "@/api/log/logApi.js";
import ButtonReload from "@/utils/components/ButtonReload.vue";
import PageHeadBack from "@/utils/components/PageHeadBack.vue";
import notificationApi from "@/api/notification/notificationApi.js";

export default {
  components: {
    ButtonClick,
    ButtonReload,
    PageHeadBack,
    PageScroll,
  },
  data() {
    return {
      input3: "",
      filter: false,
      table: {
        tableData: [],
        multipleSelection: [],
        currentPage: 1,
        log_count: 0,
        tableHeight: "600",
      },
      loading: {
        search: false,
        table: false,
        isRotating: false,
      },
      currentRow: {
        index: 0,
        row: {},
      },
      activeName: "log",
      online: {
        user: [],
        total: 0,
      },
      dialogShow: false,
      dialogData: {
        title: "",
        beforeClose: null,
      },
    };
  },
  mounted() {
    this.calTableHeight();
    this.getLogs(this.table.currentPage);
  },
  methods: {
    // 功能：表格高度根据内容自适应
    calTableHeight() {
      const h1 = this.$refs.h1.$el.offsetHeight;
      const h2 = this.$refs.h2.$el.offsetHeight;
      // 其中一个40是盒子的总外边距
      // 6vh 是el-header高度
      // 24px是PageHeadBack高度
      this.table.tableHeight = `calc(100vh - ${h1}px - ${h2}px - 120px - 24px - 16px - 2px - var(--el-main-padding) * 2 - 6vh - 5px`;
    },
    doSearch() {
      this.loading.search = true;
      setTimeout(() => {
        this.loading.search = false;
      }, 1500);
    },
    reCalTableHeight() {
      if (this.filter) {
        this.calTableHeight();
      }
    },
    getLogs(page) {
      this.loading.table = true;
      logApi.getLogs(page).then((res) => {
        if (res.code == 200) {
          this.loading.table = false;
          if (this.loading.isRotating) {
            // 保证loading动画至少转0.5s
            setTimeout(() => {
              this.loading.isRotating = false;
            }, 500);
          }
          this.table.log_count = res.total;
          this.table.tableData = res.data;
        }
      });
    },
    deleteLog(action) {
      if (action !== "confirm") {
        return Promise.resolve(true);
      } else {
        return logApi
          .deleteLog({ ids: [this.currentRow.row.id] })
          .then((res) => {
            if (res.code == 200) {
              ElMessage.success("删除成功");
              // 移除表格的第index行
              this.table.tableData.splice(this.currentRow.index, 1);
              this.table.log_count--;
            } else {
              ElMessage.error("删除失败");
            }
            return res;
          });
      }
    },
    batchDelete(action) {
      if (action !== "confirm") {
        return Promise.resolve(true);
      } else {
        const ids = [];
        this.table.multipleSelection.forEach((item) => {
          ids.push(item.id);
        });
        return logApi.deleteLog({ ids: ids }).then((res) => {
          if (res.code == 200) {
            ElMessage.success("删除成功");
            // 根据所选的行号ids从table.tableDate移除数据
            this.table.tableData = this.table.tableData.filter((item) => {
              return !this.table.multipleSelection.includes(item);
            });
            this.table.log_count -= this.table.multipleSelection.length;
            this.table.multipleSelection = [];
          } else {
            ElMessage.error("删除失败");
          }
          return res;
        });
      }
    },
    sDel(index, row) {
      this.currentRow.index = index;
      this.currentRow.row = row;
      this.dialogData.title = "删除该条记录？";
      this.dialogData.beforeClose = this.deleteLog;
      this.dialogShow = true;
    },
    bDel() {
      this.dialogData.title = `批量删除${this.table.multipleSelection.length}条记录？`;
      this.dialogData.beforeClose = this.batchDelete;
      this.dialogShow = true;
    },
    handleCurrentChange() {
      this.getLogs(this.table.currentPage);
    },
    indexMethod(index) {
      return index + 1 + (this.table.currentPage - 1) * 15;
    },
    /** 多选列 */
    handleSelectionChange(val) {
      this.table.multipleSelection = val;
    },
    /** 清除已选中的表格行：*/
    clearSelected() {
      this.$refs.table.clearSelection();
    },
    tableHeadStyleName() {
      return "table-header";
    },
    reload() {
      this.loading.isRotating = true;
      this.getLogs(this.table.currentPage);
    },
    getOnline() {
      notificationApi.getOnline().then((res) => {
        if (res.code == 200) {
          this.online.user = res.data;
          this.online.total = res.total;
        }
      });
    },
    changeTab(tabName) {
      if (tabName === "log") {
        this.getLogs(this.table.currentPage);
      } else if (tabName === "online") {
        this.getOnline();
      }
    },
  },
};
</script>

<template>
  <PageHeadBack>
    <PageScroll>
      <el-row ref="h1" :gutter="10">
        <el-col :xs="20" :sm="16" :md="16" :lg="16" :xl="16">
          <div @click="filter = true">
            <el-input
              v-model="input3"
              size="small"
              :disabled="true"
              :class="{ input: filter, shrink: !filter }"
            />
          </div>
        </el-col>
        <el-col :xs="4" :sm="8" :md="8" :lg="8" :xl="8">
          <ButtonClick
            content="搜索"
            type="warning"
            size="small"
            :loading="loading.search"
            @do-search="doSearch"
          />
        </el-col>
      </el-row>

      <el-row ref="h2">
        <Transition @after-enter="reCalTableHeight">
          <el-card v-show="filter" :class="{ disappear: !filter }">
            分类
            <div class="close-card">
              <el-icon @click="filter = false"><i-ep-ArrowUp /></el-icon>
            </div>
          </el-card>
        </Transition>
      </el-row>

      <el-skeleton
        :rows="12"
        animated
        :loading="loading.search"
        :throttle="{ leading: 500, trailing: 500 }"
      >
        <el-tabs
          v-model="activeName"
          type="card"
          class="demo-tabs"
          @tab-change="changeTab"
        >
          <el-tab-pane label="登录日志" name="log">
            <ButtonReload
              v-model:stop="loading.isRotating"
              @click="reload"
              class="button-reload"
            />
            <el-table
              ref="table"
              :data="table.tableData"
              style="width: 100%"
              :height="table.tableHeight"
              :header-cell-class-name="tableHeadStyleName"
              @selection-change="handleSelectionChange"
              v-loading="loading.table"
            >
              <el-table-column type="selection" width="30" />
              <el-table-column
                type="index"
                label="序号"
                align="center"
                fixed
                :index="indexMethod"
                width="52px"
              />
              <el-table-column prop="username" label="用户名" width="70px" />
              <el-table-column prop="ip" label="ip" width="120" />
              <el-table-column prop="addr" label="位置" />
              <el-table-column prop="os" label="操作系统" />
              <el-table-column prop="device" label="设备" />
              <el-table-column prop="browser" label="浏览器类型" />
              <el-table-column prop="operate" label="操作" />
              <el-table-column
                prop="operateTime"
                label="操作时间"
                width="165px"
              />
              <el-table-column label="操作">
                <template #default="scope">
                  <el-button
                    size="small"
                    type="danger"
                    @click="sDel(scope.$index, scope.row)"
                  >
                    删除
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
            <div class="check-button">
              <el-button
                type="primary"
                size="small"
                :disabled="table.multipleSelection.length == 0"
                @click="bDel"
                >批量删除</el-button
              >
              <el-button
                type="primary"
                size="small"
                :disabled="table.multipleSelection.length == 0"
                @click="clearSelected"
                >清除选中</el-button
              >
            </div>
            <el-pagination
              v-model:current-page="table.currentPage"
              :page-size="15"
              layout="total, prev, pager, next"
              :total="table.log_count"
              @current-change="handleCurrentChange"
              :pager-count="5"
            />
          </el-tab-pane>
          <el-tab-pane label="实时统计" name="online">
            <ButtonReload
              v-model:stop="loading.isRotating"
              @click="getOnline"
              class="button-reload"
            />
            <el-table :data="online.user">
              <el-table-column
                type="index"
                label="序号"
                align="center"
                :index="indexMethod"
                width="52px"
              />
              <el-table-column prop="username" label="用户名" />
              <el-table-column prop="nickName" label="昵称" />
            </el-table>
          </el-tab-pane>
        </el-tabs>
      </el-skeleton>

      <van-dialog
        v-model:show="dialogShow"
        :title="dialogData.title"
        width="230"
        show-cancel-button
        :beforeClose="dialogData.beforeClose"
      />
    </PageScroll>
  </PageHeadBack>
</template>

<style lang="scss" scoped>
// 变量定义
$primary-color: #333333;
$card-bg-color: #f0f0f0;
$button-margin: 10px;

// 输入框样式
.el-input {
  left: 60%;
  width: 40%;
  border-radius: 40px;

  &.input {
    animation: expand 1s forwards;
  }

  &.shrink {
    animation: shrink 1s forwards;
  }
}

// 表格相关样式
:deep(.table-header) {
  color: $primary-color;
}

.el-table {
  color: $primary-color;
}

// 卡片样式
.el-card {
  width: 100%;
  height: 200px;
  background-color: $card-bg-color;
  animation: slideIn 0.6s forwards;

  &.disappear {
    animation: fadeOut 1.2s forwards;
  }

  .close-card {
    font-size: 1.3rem;
    position: relative;
    top: 135px;
    left: 90%;
  }
}

// 按钮样式
.check-button {
  float: right;
  margin-top: $button-margin;
  margin-right: 20px;
}

.button-reload {
  float: right;
  margin: $button-margin 5px 5px;
}

.el-pagination {
  float: right;
}

// 动画定义
@keyframes slideIn {
  from {
    width: 0;
    height: 0;
    opacity: 0;
  }

  to {
    height: 200px;
    opacity: 1;
  }
}

@keyframes fadeOut {
  to {
    width: 0;
    height: 0;
    opacity: 0;
  }
}

@keyframes expand {
  from {
    transform: scale(1);
  }

  to {
    transform: scale(2, 1);
    left: 40%;
  }
}

@keyframes shrink {
  from {
    transform: scale(2, 1);
    left: 40%;
  }

  to {
    transform: scale(1);
    left: 60%;
  }
}
</style>
