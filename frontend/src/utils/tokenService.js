import axios from "axios";

const TOKEN_KEY = "blog";
const REFRESH_URL = "/auth/refresh";

let refreshPromise = null;

export function getToken(type = "access_token") {
  try {
    const blogData = JSON.parse(localStorage.getItem(TOKEN_KEY) || "{}");
    return blogData[type] || "";
  } catch {
    return "";
  }
}

function setToken(type, value) {
  try {
    const blogData = JSON.parse(localStorage.getItem(TOKEN_KEY) || "{}");
    blogData[type] = value;
    localStorage.setItem(TOKEN_KEY, JSON.stringify(blogData));
  } catch {
    // ignore storage errors
  }
}

function decodeBase64Url(input) {
  const base64 = input.replace(/-/g, "+").replace(/_/g, "/");
  const padded = base64.padEnd(
    base64.length + ((4 - (base64.length % 4)) % 4),
    "="
  );
  return atob(padded);
}

export function isTokenExpired(token, leewaySeconds = 0) {
  if (!token) return true;
  const parts = token.split(".");
  if (parts.length < 2) return true;
  try {
    const payload = JSON.parse(decodeBase64Url(parts[1]));
    const exp = Number(payload?.exp || 0);
    if (!exp) return false;
    const now = Math.floor(Date.now() / 1000);
    return exp <= now + leewaySeconds;
  } catch {
    return true;
  }
}

export function isJwtLike(token) {
  return typeof token === "string" && token.split(".").length === 3;
}

export function isRefreshTokenExpired(leewaySeconds = 0) {
  const refreshToken = getToken("refresh_token");
  if (!refreshToken) return true;
  if (!isJwtLike(refreshToken)) return false;
  return isTokenExpired(refreshToken, leewaySeconds);
}

export function refreshAccessToken() {
  const refreshToken = getToken("refresh_token");
  if (!refreshToken) {
    return Promise.reject(new Error("缺少refresh_token"));
  }

  if (refreshPromise) return refreshPromise;

  refreshPromise = axios
    .post(REFRESH_URL, null, {
      headers: { Authorization: refreshToken },
      baseURL: import.meta.env.VITE_APP_BASE_API ?? "/",
      timeout: 10000,
    })
    .then((res) => {
      if (res.data.code !== 200) {
        throw new Error(res.data.message || "刷新token失败");
      }
      const accessToken = res.data.data?.access_token;
      if (!accessToken) {
        throw new Error("刷新token失败：缺少access_token");
      }
      setToken("access_token", accessToken);
      return accessToken;
    })
    .finally(() => {
      refreshPromise = null;
    });

  return refreshPromise;
}
