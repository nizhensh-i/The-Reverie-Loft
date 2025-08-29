const updateUser = [
  {
    path: '/editProfile',
    name: 'editProfile',
    component: () => import('../views/user/EditProfile.vue'),
    meta: { requireAuth: true }
  },
  {
    path: '/editCommonField',
    name: 'editCommonField',
    component: () => import('../views/user/edit/CommonField.vue')
  },
  {
    path: '/editBackGround',
    name: 'editBackGround',
    component: () => import('../views/user/edit/Background.vue')
  },
  {
    path: '/editInterest',
    name: 'editInterest',
    component: () => import('../views/user/edit/Interest.vue'),
    meta: { requireAuth: true }
  }
]
const setting = [
  {
    path: '/bindEmail',
    name: 'bindEmail',
    component: () => import('../views/user/EmailPage.vue'),
    meta: { keepAlive: true, requireAuth: true }
  },
  {
    path: '/changeEmail',
    name: 'changeEmail',
    component: () => import('../views/user/EmailChange.vue'),
    meta: { keepAlive: true, requireAuth: true }
  },
  {
    path: '/changePassword',
    name: 'changePassword',
    component: () => import('../views/user/PasswordChange.vue'),
    meta: { keepAlive: true, requireAuth: true }
  },
  {
    path: '/PasswordChangeAdmin',
    name: 'PasswordChangeAdmin',
    component: () => import('../views/user/PasswordChangeAdmin.vue'),
    meta: { roles: ['admin'] }
  },
  {
    path: '/resetPassword',
    name: 'resetPassword',
    component: () => import('../views/user/PasswordReset.vue')
  }
]

const error = [
  {
    path: '/403',
    name: 'notAuth',
    component: () => import('../views/error/NotAuth.vue')
  },
  {
    path: '/404',
    name: 'notFound',
    component: () => import('../views/error/NotFound404.vue')
  },
  {
    path: '/500',
    name: 'networkError',
    component: () => import('../views/error/NetError.vue')
  }
]
const admin = [
  {
    path: '/editProfileAdmin/:id',
    name: 'editProfileAdmin',
    component: () => import('../views/user/EditProfileAdmin.vue'),
    meta: { roles: ['admin'] }
  },
  {
    path: '/commentManagement',
    name: 'commentManagement',
    component: () => import('../views/comment/commentManagement.vue'),
    meta: { roles: ['admin'] }
  },
  {
    path: '/operateLog',
    name: 'operateLog',
    component: () => import('../views/data_manage/OperateLog.vue'),
    meta: { roles: ['admin'] }
  },
  {
    path: '/tag',
    name: 'tag',
    component: () => import('../views/user/admin/Tag.vue'),
     meta: { roles: ['admin'] }
  }
]
const routes = [
  {
    path: '/home',
    name: 'home',
    component: () => import('../views/home/AppLayout.vue'),
    children: [
      {
        path: '/posts',
        name: 'posts',
        component: () => import('../views/posts/PostData.vue'),
        meta: { keepAlive: true }
      },
      {
        path: '/user/:userName',
        name: 'user',
        component: () => import('../views/user/UserData.vue'),
      },

      // 上传公共背景库图片
      {
        path: '/uploadBg',
        name: 'uploadBg',
        component: () => import('../views/user/admin/BackgoundImage.vue'),
        meta: { requireAuth: true }
      },
      {
        path: '/postDetail/:id',
        name: 'postDetail',
        component: () => import('../views/posts/PostDetail.vue')
      },
      {
        path: '/pubImage',
        name: 'pubImage',
        component: () => import('../views/posts/publish/PublishImage.vue'),
        meta: { keepAlive: true }
      },
      {
        path: '/chat',
        name: 'chat',
        component: () => import('../views/chat/chat.vue'),
        meta: { requireAuth: true }
      },
      {
        path: '/editPost/:id',
        name: 'editPost',
        component: () => import('../views/posts/PostEdit.vue'),
        meta: { requireAuth: true }
      },
      {
        path: '/follow/:action/:userName',
        name: 'follow',
        component: () => import('../views/user/FollowList.vue')
      },

      {
        path: '/register',
        name: 'register',
        component: () => import('../views/login/RegisterPage.vue')
      },
      ...updateUser,
      ...setting,
      ...error,
      ...admin
    ]
  },
  { path: '/', redirect: '/welcome' },
  // 登陆页面
  {
    path: '/login',
    name: 'login',
    component: () =>
      import.meta.env.DEV == true
        ? import('@/views/login/LoginPageDev.vue')
        : import('@/views/login/LoginPage.vue')
  },
  // 清除本地缓存
  {
    path: '/clear',
    name: 'clear',
    component: () => import('../views/login/Clear.vue')
  },
  {
    path: '/welcome',
    name: 'welcome',
    component: () => import('../views/welcome/BlogIndex.vue')
  }
]

export default routes
