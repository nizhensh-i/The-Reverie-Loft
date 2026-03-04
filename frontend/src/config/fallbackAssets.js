import bgIndex from "@/asset/bg_index.jpg";
import userBgMobile from "@/asset/user_bg/mobile_image.webp";
import userBgPc from "@/asset/user_bg/pc_image.png";

const PLACEHOLDER_VALUES = new Set(["", "QINIU_DOMAIN", "undefined", "null"]);

export function getQiniuDomain() {
  return (import.meta.env.VITE_QINIU_DOMAIN || "").trim();
}

export function hasQiniuDomain() {
  const domain = getQiniuDomain();
  return domain.length > 0 && !PLACEHOLDER_VALUES.has(domain);
}

export function qiniuUrl(path, fallbackUrl) {
  if (!hasQiniuDomain()) return fallbackUrl;
  const normalized = path.startsWith("/") ? path.slice(1) : path;
  return `${getQiniuDomain()}/${normalized}`;
}

export const LOCAL_BG_INDEX = bgIndex;
export const LOCAL_USER_BG_MOBILE = userBgMobile;
export const LOCAL_USER_BG_PC = userBgPc;
