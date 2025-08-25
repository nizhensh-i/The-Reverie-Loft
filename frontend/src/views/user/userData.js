import typewriter from '@/utils/components/Typewriter.vue'
import interest from '@/views/user/components/Interest.vue'
import socialLinks from '@/utils/components/SocialLinks.vue'
import ButtonAnimate from '@/utils/components/ButtonAnimate.vue'
import cityUtil from '@/utils/cityUtil.js'
import { areaList } from '@vant/area-data'
import { useCurrentUserStore } from '@/stores/user'
import { useOtherUserStore } from '@/stores/otherUser'
import SkeletonUtil from '@/utils/components/SkeletonUtil.vue'
import PostImage from '@/views/posts/components/PostImage.vue'
import PostPreview from '@/views/posts/components/PostPreview.vue'
import userApi from '@/api/user/userApi.js'
import date from '@/utils/date.js'
import dayjs from 'dayjs'
import { showConfirmDialog } from 'vant'
import { loginReminder, compressImages, waitImage } from '@/utils/common.js'
import { ElLoading } from 'element-plus'

export default {
  components: {
    typewriter,
    interest,
    socialLinks,
    ButtonAnimate,
    SkeletonUtil,
    PostImage,
    PostPreview
  },
  data() {
    return {
      isUserPage: true,
      activeInterest: 'movie',
      but: false,
      user: {
        username: '张三',
        name: '赫赫',
        location: '上海',
        email: 'zmc@qq.com',
        about_me: '',
        member_since: '2024-9-20 12:14:00',
        last_seen: '2024-9-20 12:14:00',
        admin: false,
        followers_count: 0,
        followed_count: 0,
        is_followed_by_current_user: false,
        is_following_current_user: false,
        image: '/src/asset/image1.png',
        interest: {
          books: [],
          movies: []
        },
        social_account: {},
        tags: []
      },
      userName: '',
      posts: [{}],
      currentPage: 1,
      posts_count: 0,
      loading: {
        userData: false,
        follow: false,
        skeleton: true,
        switch: false
      },
      uploadToken: '',
      imageUrls: [],
      uploading: false,
      imageKey: [],

      drawer: false,
      imgList: [],
      skeletonThrottle: {
        leading: 300,
        trailing: 300,
        initVal: false
      },
      activeName: 'first',
      // 原始文件
      originalFiles: [],
      // 压缩后的文件
      compressedImages: []
    }
  },
  setup() {
    const currentUser = useCurrentUserStore()
    const otherUser = useOtherUserStore()
    return { currentUser, otherUser, areaList }
  },
  computed: {
    location() {
      if (this.user.location && !isNaN(this.user.location)) {
        return cityUtil.getCodeToName(this.user.location, this.areaList)
      }
      return ''
    },
    member_since() {
      return dayjs(this.user.member_since).format('YYYY-MM-DD')
    },
    from_now() {
      // 防止上线时间与当前时间过于接近而显示"几秒后"
      const time = dayjs(this.user.last_seen).subtract(5, 'second').format('YYYY-MM-DD HH:mm:ss')
      return date.dateShow(time)
    },
    isCurrentUser() {
      return this.user.username == this.currentUser.userInfo.username
    },
    isFollowCurrentUser() {
      return (
        this.currentUser.userInfo.username &&
        !this.isCurrentUser &&
        this.user.is_following_current_user
      )
    },
    isFollowEachOther() {
      return (
        this.currentUser.userInfo.username &&
        !this.isCurrentUser &&
        this.user.is_following_current_user &&
        this.user.is_followed_by_current_user
      )
    },
    isFollowOtherUser() {
      return (
        this.currentUser.userInfo.username &&
        !this.isCurrentUser &&
        this.user.is_followed_by_current_user
      )
    },
    bgImage() {
      return this.isCurrentUser ? this.currentUser.backGroundUrl : this.otherUser.backGroundUrl
    },
    backColor() {
      return this.isUserPage ? '#ffffff' : '#000000'
    },
    socialCount() {
      return Object.values(this.user.social_account).every(
        (value) => value === '' || value === null || value === undefined
      )
    },
    srcList() {
      return [this.user.image]
    }
  },
  // 当从A资料跳转B资料时，更新资料页面
  created() {
    // 首次加载时获取用户数据
    this.getUser()
    // 监听路由参数变化
    this.$watch(
      () => this.$route.params.userName,
      (newUserName, oldUserName) => {
        if (this.$route.name === 'user' && newUserName !== oldUserName) {
          this.isUserPage = true
          this.getUser()
        }
      }
    )
  },
  activated() {
    // 只刷新背景和属性，不请求接口
    const routeUserName = this.$route.params.userName
    const isViewingSelf = this.currentUser.isLogin && 
      routeUserName === this.currentUser.userInfo.username

    if (isViewingSelf) {
      this.user = { ...this.currentUser.userInfo }
      this.imgList = [this.user.image] // 修复兴趣图片不显示
      this.isUserPage = true
      this.setMainProperty()
      this.loading.skeleton = false
    } else {
      this.setMainProperty()
    }
  },
  mounted() {},
  methods: {
    setMainProperty() {
      if (!this.isUserPage) {
        return
      }
      
      // 确保背景图片URL是最新的
      let bgImageUrl = this.bgImage
      
      // 如果是当前用户，确保使用最新的背景图片
      if (this.isCurrentUser && this.currentUser.backGroundUrl) {
        bgImageUrl = this.currentUser.backGroundUrl
      } else if (!this.isCurrentUser && this.otherUser.backGroundUrl) {
        bgImageUrl = this.otherUser.backGroundUrl
      }
      
      const root = document.documentElement
      root.style.setProperty('--leleo-background-image-url', `url('${bgImageUrl}')`)
    },
    // 每次点击tag触发动画
    playTagAnimation(e) {
      const el = e.currentTarget
      el.classList.remove('animate')
      // 强制重绘
      void el.offsetWidth
      el.classList.add('animate')
    },
    setActive(type) {
      this.activeInterest = type
    },
    handleSwitchChange() {
      const root = document.documentElement
      if (this.isUserPage) {
        root.style.setProperty('--leleo-background-image-url', `url('${this.bgImage}')`)
      } else {
        root.style.setProperty('--leleo-background-image-url', `none`)
        root.style.setProperty('background-color', '#fff')
      }
    },
    async beforeSwitch() {
      // 从文章列表切换到用户资料页时，不会发请求
      if(!this.isUserPage){
        return true
      }
      this.loading.switch = true
      await this.getPosts(this.$route.params.userName, 1)
      this.loading.switch = false
      return true
    },
    getUser() {
      let userName = this.$route.params.userName
      const loading = ElLoading.service({
        lock: true,
        text: '加载中...',
        background: 'rgba(0, 0, 0, 0.7)'
      })
      this.loading.userData = true
      
      // 检查是否是查看当前登录用户的资料
      const isViewingSelf = this.currentUser.isLogin && 
        userName === this.currentUser.userInfo.username
      
      // 如果是查看自己的资料且已有数据，优先使用当前用户的数据
      if (isViewingSelf && Object.keys(this.currentUser.userInfo).length > 0) {
        this.user = { ...this.currentUser.userInfo }
        this.imgList = [this.user.image]
        this.loading.userData = false
        this.loading.skeleton = false
        this.setMainProperty()
        loading.close()
        return
      }
      
      if (!userName) {
        userName = this.otherUser.userInfo.username
      }
      if (!userName) {
        this.$message.error('要显示资料的用户名为空！')
        loading.close()
        return
      }
      
      userApi.getUserByUsername(userName).then((res) => {
        this.loading.userData = false
        
        // 适配新的统一接口返回格式
        let userData;
        if (res.code === 200) {
          // 新格式
          userData = res.data;
        }  else {
          throw new Error('获取用户数据失败');
        }
        
        this.user = userData;
        
        // 更新对应的存储
        if (isViewingSelf) {
          this.currentUser.setUserInfo(userData)
          // 确保背景图片URL也被更新
          if (userData.bg_image) {
            this.currentUser.bg_image = userData.bg_image
          }
        } else {
          this.otherUser.userInfo = userData
          // 确保背景图片URL也被更新
          if (userData.bg_image) {
            this.otherUser.bg_image = userData.bg_image
          }
        }
        
        // 清空并重新添加图片列表
        this.imgList = []
        this.imgList.push(this.user.image)
        
        // 让私信和关注按钮与用户数据同时出现
        setTimeout(() => {
          this.loading.skeleton = false
          this.setMainProperty()
          // 背景图片加载时显示loading
          waitImage([this.bgImage]).then((res) => {
            loading.close()
          })
        }, this.skeletonThrottle.trailing)
      }).catch(err => {
        this.loading.userData = false
        this.loading.skeleton = false
        loading.close()
        this.$message.error('获取用户数据失败')
        console.error(err)
      })
    },
    async getPosts(userName, page) {
      await userApi.getPosts(userName, page).then((res) => {
        // 适配新的统一接口返回格式
        if (res.code === 200) {
          // 新格式
          this.posts = res.data.posts || res.data
          this.posts_count = res.total || 0
        } else if (res.data) {
          // 兼容旧格式
          this.posts = res.data.posts
          this.posts_count = res.data.total
        }
      }).catch(error => {
        console.error('获取用户文章失败', error)
        this.$message.error('获取用户文章失败，请稍后重试')
      })
    },
    editProfile() {
      this.$router.push(`/editProfile`)
    },
    editProfileAdmin() {
      this.$router.push(`/editProfileAdmin/${this.user.id}`)
    },
    followUser() {
      if (!this.currentUser.isLogin) {
        loginReminder('快去登录再私信吧')
        return
      }
      this.loading.follow = true
      userApi.follow(this.user.username).then((res) => {
        // 适配新的统一接口返回格式
        if (res.code === 200) {
          // 新格式
          this.loading.follow = false
          this.user = res.data
          this.currentUser.addItemFollowed({
            id: this.user.id,
            name: this.user.name ? this.user.name : this.user.username,
            uName: this.user.username,
            avatar: this.user.image
          })
          this.$message.success('关注成功')
        } else {
          this.loading.follow = false
          this.$message.error(res.message || res.data?.msg || '关注失败')
        }
      })
    },
    unFollowUser() {
      showConfirmDialog({
        title: '取消对该用户的关注',
        width: 230,
        beforeClose: this.beforeClose
      })
    },

    beforeClose(action) {
      if (action !== 'confirm') {
        return Promise.resolve(true)
      } else {
        return userApi.unFollow(this.user.username).then((res) => {
          // 适配新的统一接口返回格式
          if (res.code === 200) {
            // 新格式
            this.user = res.data
            this.currentUser.delItemFollowed(this.user.username)
            this.$message.success('已取消关注')
          } else {
            this.$message.error(res.message || res.data?.msg || '取消关注失败')
          }
          return res
        })
      }
    },
    followerDetail() {
      const f = 'follower'
      this.$router.push(`/follow/${f}/${this.user.username}`)
    },
    followedDetail() {
      const f = 'followed'
      this.$router.push(`/follow/${f}/${this.user.username}`)
    },
    handleCurrentChange() {
      this.getPosts(this.$route.params.userName, this.currentPage)
    },
    showDrawer() {
      this.drawer = !this.drawer
    },
    openChat() {
      if (!this.currentUser.isLogin) {
        loginReminder('快去登录再私信吧')
        return
      }
      this.$router.push('/chat')
    }
  }
}
