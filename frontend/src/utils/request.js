import { useCurrentUserStore } from "@/stores/user";
import errorManager from "@/utils/message";
import router from "../router/index.js";
import axios from "axios";

// ============ 常量定义 ============
const REFRESH_URL = "/auth/refresh";
const TOKEN_KEY = "blog";
const EXPIRED_MESSAGE = "身份已过期";
const FRESH_REQUIRED_MESSAGE = "该操作需要重新登录以验证身份";

const ResponseCode = {
  SUCCESS: 200,
  BAD_REQUEST: 400,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  NOT_FOUND: 404,
  TOO_MANY_REQUESTS: 429,
  SERVER_ERROR: 500,
};

const ErrorMessageMap = {
  [ResponseCode.BAD_REQUEST]: "参数错误",
  [ResponseCode.UNAUTHORIZED]: "身份未认证",
  [ResponseCode.FORBIDDEN]: "禁止访问",
  [ResponseCode.NOT_FOUND]: "资源不存在",
  [ResponseCode.TOO_MANY_REQUESTS]: "请求频率超限",
  [ResponseCode.SERVER_ERROR]: "服务器内部错误",
};

const SPECIAL_MESSAGES = {
  FRESH_REQUIRED: FRESH_REQUIRED_MESSAGE,
  TOKEN_EXPIRED: EXPIRED_MESSAGE,
};

// ============ axios实例 ============
const $http = axios.create({
  baseURL: import.meta.env.VITE_APP_BASE_API ?? "/",
  timeout: 10000,
});

// ============ token管理 ============
let isRefreshing = false;
let pendingQueue = [];

function getToken(type = "access_token") {
  try {
    const blogData = JSON.parse(localStorage.getItem(TOKEN_KEY) || "{}");
    return blogData[type] || "";
  } catch {
    return "";
  }
}

export function handleUnauthorized() {
  const store = useCurrentUserStore();
  if (store.access_token) {
    store.logOut();
    router.push("/login");
  }
}

// ============ token刷新 ============
function processQueue(error, newToken = null) {
  pendingQueue.forEach(({ resolve, reject }) => {
    error ? reject(error) : resolve(newToken);
  });
  pendingQueue = [];
}

async function refreshToken() {
  const res = await axios.post(REFRESH_URL, null, {
    headers: { Authorization: getToken("refresh_token") },
    baseURL: import.meta.env.VITE_APP_BASE_API ?? "/",
    timeout: 10000,
  });

  if (res.data.code !== 200) {
    throw new Error(res.data.message || "刷新token失败");
  }

  const accessToken = res.data.data.access_token;
  const store = useCurrentUserStore();
  store.access_token = accessToken;
  return accessToken;
}

function retryRequest(config, token) {
  config.headers.Authorization = token;
  return $http(config);
}

function handleTokenExpired(config) {
  if (config.url.includes(REFRESH_URL)) {
    errorManager.warning("您的身份已过期, 请重新登录");
    handleUnauthorized();
    return Promise.reject();
  }

  if (isRefreshing) {
    return new Promise((resolve, reject) => {
      pendingQueue.push({
        resolve: (token) => resolve(retryRequest(config, token)),
        reject,
      });
    });
  }

  isRefreshing = true;
  return refreshToken()
    .then((newToken) => {
      processQueue(null, newToken);
      return retryRequest(config, newToken);
    })
    .catch((refreshError) => {
      if (refreshError.response?.status === 401) {
        errorManager.warning("您的身份已过期, 请重新登录");
      }
      processQueue(refreshError, null);
      handleUnauthorized();
      return Promise.reject(refreshError);
    })
    .finally(() => {
      isRefreshing = false;
    });
}

// ============ 统一错误处理 ============
function navigateToErrorPage(code) {
  const routes = {
    [ResponseCode.FORBIDDEN]: "/403",
    [ResponseCode.NOT_FOUND]: "/404",
    [ResponseCode.SERVER_ERROR]: "/500",
  };
  routes[code] && router.push(routes[code]);
}

function showErrorMessage(code, message) {
  if (code === ResponseCode.TOO_MANY_REQUESTS) return;
  const msg = message || ErrorMessageMap[code];
  const method = code >= 400 && code < 500 ? "warning" : "error";
  msg && errorManager[method](msg);
}

function handleStandardResponse(response) {
  const { code, message } = response.data;

  if (code === ResponseCode.SUCCESS) return response.data;

  if (
    code === ResponseCode.UNAUTHORIZED &&
    message === SPECIAL_MESSAGES.FRESH_REQUIRED
  ) {
    errorManager.warning("为了您的账户安全，请重新登录");
    handleUnauthorized();
    return Promise.reject(new Error(SPECIAL_MESSAGES.FRESH_REQUIRED));
  }

  if (
    code === ResponseCode.UNAUTHORIZED &&
    message === SPECIAL_MESSAGES.TOKEN_EXPIRED
  ) {
    return handleTokenExpired(response.config);
  }

  if (code === ResponseCode.UNAUTHORIZED) {
    showErrorMessage(code, message);
    handleUnauthorized();
    return Promise.reject(message);
  }

  showErrorMessage(code, message);
  navigateToErrorPage(code);
  return Promise.reject(message || "请求失败");
}

function handleHttpError(error) {
  const { status, data } = error.response || {};

  if (!error.response) {
    errorManager.error(
      error.code === "ECONNABORTED" ? "请求超时" : "网络连接失败"
    );
    return Promise.reject(error);
  }

  if (data?.code !== undefined) return Promise.reject(error);

  showErrorMessage(status, data?.message);
  navigateToErrorPage(status);
  return Promise.reject(error);
}

// ============ 日志工具 ============
function logRequest(config) {
  console.log("==>请求开始", config.baseURL + config.url, config.data || "");
}

function logResponse(response) {
  console.log("==>请求结束", response);
}

function logError(error) {
  console.log("==>请求错误", error);
}

// ============ 拦截器配置 ============
function setInterceptors(...instances) {
  instances.forEach((instance) => {
    instance.interceptors.request.use(
      (config) => {
        const token = getToken(
          config.useRefreshToken ? "refresh_token" : "access_token"
        );
        if (token) config.headers.Authorization = token;
        logRequest(config);
        return config;
      },
      (error) => {
        logError(error);
        errorManager.error(error);
        return Promise.reject(error);
      }
    );

    instance.interceptors.response.use((response) => {
      logResponse(response);
      if (response.status !== 200) return Promise.reject(response);
      return response.data.code !== undefined
        ? handleStandardResponse(response)
        : response;
    }, handleHttpError);
  });
}

setInterceptors($http);

export { $http };
