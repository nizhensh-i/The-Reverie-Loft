import { copyTextToClipboard } from "@pureadmin/utils";
import { v4 as uuidv4 } from "uuid";
import * as qiniu from "qiniu-js";
import router from "@/router";
import lrz from "lrz";

function copy(value) {
  // 复制卡片内容到剪贴板
  if (!value) {
    ElMessage({
      message: "内容为空",
      type: "error",
    });
    return;
  }
  const success = copyTextToClipboard(value);
  ElMessage({
    message: success ? "复制成功" : "复制失败",
    type: success ? "success" : "error",
  });
}

function loginReminder(message) {
  showConfirmDialog({
    title: "您还未登录",
    message: message,
    confirmButtonText: "去登录",
    width: 300,
  })
    .then(() => {
      router.push("/login");
    })
    .catch(() => {});
}

async function retry(func, maxRetries = 3, delay = 1000, ...args) {
  let retries = 0;
  while (retries < maxRetries) {
    try {
      const result = await func(...args);
      return result;
    } catch (error) {
      retries++;
      if (retries < maxRetries) {
        await new Promise((resolve) => setTimeout(resolve, delay));
      } else {
        // 达到最大重试次数，抛出最后一次的错误
        throw error;
      }
    }
  }
}

function randomNum(minNum, maxNum) {
  switch (arguments.length) {
    case 1:
      return parseInt(`${Math.random() * minNum + 1}`, 10);
    case 2:
      return parseInt(`${Math.random() * (maxNum - minNum + 1) + minNum}`, 10);
    default:
      return 0;
  }
}

function isNode() {
  return typeof window === "undefined";
}

/*
 * @description: 防抖函数
 */
function debounce(func, wait) {
  let timeout;
  return function (...args) {
    const context = this;
    clearTimeout(timeout);
    timeout = setTimeout(() => {
      func.apply(context, args);
    }, wait);
  };
}

/*
 * @description: 清空对象属性值
 */
function clearObj(obj) {
  Object.keys(obj).forEach((key) => {
    obj[key] = "";
  });
  return obj;
}

/*
 * @description: 处理图片压缩
 * @param {Array} originalFiles 原始文件列表
 * @param {Array} _compressedImages 已压缩的图片列表
 
 * @return {Array} compressedImages 压缩后的图片列表
 */
async function compressImages(originalFiles, _compressedImages) {
  // console.log('开始压缩图片:', originalFiles)
  // console.log('已压缩的图片:', _compressedImages)
  const compressedRatio = 80;
  const compressedImages = [..._compressedImages];
  const compressionRatio = compressedRatio / 100;

  // 找出未压缩的文件
  const uncompressedFiles = originalFiles.filter(
    (file) => !compressedImages.some((img) => img.uid === file.uid)
  );
  // console.log('未压缩的文件:', uncompressedFiles)

  for (const file of uncompressedFiles) {
    const rawFile = file.raw;
    const compressedFile = await lrz(rawFile, { quality: compressionRatio });

    console.log("压缩后的文件:", compressedFile);
    console.log(
      `压缩后大小: ${(compressedFile.file.size / 1024).toFixed(2)} KB`
    );

    // 将 base64 转换为 Blob
    const byteString = atob(compressedFile.base64.split(",")[1]);
    const mimeString = compressedFile.base64
      .split(",")[0]
      .split(":")[1]
      .split(";")[0];
    const arrayBuffer = new ArrayBuffer(byteString.length);
    const uintArray = new Uint8Array(arrayBuffer);
    for (let i = 0; i < byteString.length; i++) {
      uintArray[i] = byteString.charCodeAt(i);
    }
    const blob = new Blob([arrayBuffer], { type: mimeString });

    compressedImages.push({
      src: compressedFile.base64,
      // 保存 Blob 对象
      blob,
      name: rawFile.name,
      uid: rawFile.uid,
      // markdown图片位置
      pos: rawFile.pos,
      sizeInfo: `压缩后大小: ${(compressedFile.file.size / 1024).toFixed(
        2
      )} KB`,
    });
  }
  return compressedImages;
}

function beforePicUpload(fileList) {
  for (const file of fileList) {
    const isImage = file.raw.type.startsWith("image/");
    if (!isImage) {
      ElMessage({
        message: "只能上传图片格式文件！",
        type: "error",
      });
      return false;
    }
    const limitPic =
      file.raw.type === "image/png" ||
      file.raw.type === "image/jpg" ||
      file.raw.type === "image/jpeg" ||
      file.raw.type === "image/webp";
    if (!limitPic) {
      ElMessage({
        message: "请上传格式为png/jpg/jpeg/webp的图片",
        type: "warning",
      });
      return false;
    }
  }
  return true;
}

// 文件上传至七牛云
// compressedImages：已压缩的文件
// targetPath： 七牛云存储的路径
// uploadToken： 上传的凭证
// 返回：key数组 ['', ''] or [{'url':'', 'pos':''}, {}]， 完整url数组
async function uploadFiles(compressedImages, targetPath, uploadToken) {
  const putExtra = {};
  const config = {
    // 存储区域
    region: qiniu.region.z0,
  };
  const imageKey = [];
  const imageUrls = [];
  let result;
  try {
    for (const file of compressedImages) {
      const folder = targetPath;
      const uniqueFileName = `${uuidv4()}.${file.name.split(".").pop()}`;
      const key = folder + uniqueFileName;
      const observable = qiniu.upload(
        file.blob,
        key,
        uploadToken,
        putExtra,
        config
      );
      await new Promise((resolve, reject) => {
        observable.subscribe({
          next() {},
          error(err) {
            reject(err);
          },
          complete(res) {
            file.pos === undefined
              ? imageKey.push(res.key)
              : imageKey.push({ pos: file.pos, url: res.key });
            const imageUrl = `${import.meta.env.VITE_QINIU_DOMAIN}/${res.key}`;
            imageUrls.push(imageUrl);
            resolve();
          },
        });
      });
    }
    result = { imageKey, imageUrls };
  } catch (error) {
    console.error("Upload failed:", error);
    result = { imageKey, imageUrls };
  }
  return result;
}

function waitImage(imageUrls) {
  // 返回 Promise，让调用者感知加载状态
  return new Promise((resolve) => {
    const imagePromises = imageUrls.map((url) => {
      return new Promise((resolve, reject) => {
        const imgs = new Image();
        imgs.src = url;
        imgs.onload = () => resolve();
        imgs.onerror = (err) => reject(err);
      });
    });

    // 设置超时机制：2.5秒
    const timeoutPromise = new Promise((resolve) => {
      setTimeout(() => {
        resolve("timeout");
      }, 2500);
    });

    Promise.race([Promise.all(imagePromises), timeoutPromise])
      .then(() => {
        resolve(); // 加载完成，loading 结束
      })
      .catch((err) => {
        console.error("壁纸加载失败:", err);
        resolve(); // 即使失败也结束 loading
      });
  });
}

/**
 * @description: 禁止调试功能（仅在生产环境使用）
 */
function blockDebug() {
  function block() {
    if (
      window.outerHeight - window.innerHeight > 200 ||
      window.outerWidth - window.innerWidth > 200
    ) {
      document.body.innerHTML = "检测到非法调试,请关闭后刷新重试!";
    }
    setInterval(() => {
      const constructor = function () {
        return false;
      };
      constructor.constructor("debugger").call();
    }, 50);
  }
  try {
    block();
  } catch (err) {
    console.log(err);
  }
}

export {
  copy,
  loginReminder,
  retry,
  randomNum,
  isNode,
  debounce,
  clearObj,
  compressImages,
  uploadFiles,
  beforePicUpload,
  waitImage,
  blockDebug,
};
