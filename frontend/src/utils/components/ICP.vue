<script setup>
import { ref, onMounted, onUnmounted } from "vue";

const beginYear = "2024";
const currentYear = new Date().getFullYear();
const author = {
  name: "随想阁楼",
  link: "https://github.com/nizhensh-i/loft",
  title: "随想阁楼",
};
const icp = {
  code: import.meta.env.VITE_ICP,
  link: "http://beian.miit.gov.cn/",
};

const isFixed = ref(false);

function checkFooterPosition() {
  const bodyHeight = document.body.scrollHeight;
  const windowHeight = window.innerHeight;
  isFixed.value = bodyHeight <= windowHeight;
}

onMounted(() => {
  window.addEventListener("resize", checkFooterPosition);
  window.addEventListener("load", checkFooterPosition);
  checkFooterPosition();
});

onUnmounted(() => {
  window.removeEventListener("resize", checkFooterPosition);
  window.removeEventListener("load", checkFooterPosition);
});
</script>

<template>
  <div id="copyright-icp-footer" class="footer" :class="{ fixed: isFixed }">
    <div class="footer-divider"></div>
    <div class="footer-content">
      <div class="footer-links">
        <router-link to="/about" class="footer-link">关于我们</router-link>
        <router-link to="/terms" class="footer-link">用户协议</router-link>
        <router-link to="/privacy" class="footer-link">隐私政策</router-link>
      </div>
      <ul id="copyright-icp-ul">
        <li v-if="icp.code" class="icp-item">
          <svg
            class="code-icon"
            fill="#008cff"
            xmlns="http://www.w3.org/2000/svg"
            name="icp"
            viewBox="0 0 2000 2000"
          >
            <path
              d="M897 1979q15 0 30-2 7-1 42.5-9.5t91-29.5q55.5-21 123.5-59t139-97.5q71-59.5 137.5-144t119.5-199q53-114.5 84.5-262.5t31.5-336V583q0-69-57-121-55-44-127-41-5 1-45 1-34 0-92.5-4T1254 401q-57-15-116.5-53.5T1036 276q-28-22-45-33-43-25-93.5-25T803 244q-2 1-14 11-90 78-151 109.5T548 401q-63 13-122 17t-93 4q-38 0-45-1-73-4-127 41-57 52-57 121v257q0 188 31 336.5t84 262.5q53 114 118.5 199T474 1782q71 59 138.5 97t123 59q55.5 21 90.5 30t42 9q15 2 29 2zM277 540h5q8 1 51 1 38 0 104-4t137-20q134-30 295-174 14-7 30.5-6t29.5 8q5 3 14 10t20 15l1 1q48 38 118 82.5t145 63.5q72 16 137.5 20t102.5 4q43 0 51-1h5q21 0 38 13 15 14 15 30v257q0 169-27 302t-73 236q-46 103-104 178.5T1252 1685q-62 53-121 87t-107.5 52.5q-48.5 18.5-79 26.5t-36.5 8q-11 2-21 0-7 0-45.5-10.5t-98-36q-59.5-25.5-129-73t-138.5-122Q407 1543 350 1435t-92-255q-35-147-35-340V583q0-16 15-29 17-14 39-14zm-77 207v104h1400V747H200zm184 194v476h99V941h-99zm528 311q-4 41-35 70-30 30-74 30-54 0-87-44-34-44-34-131 0-85 31-130 31-44 87-44 87 0 112 107l92-8q-14-81-69-125-54-43-136-43-104 0-164 68t-60 177q0 67 26 124 25 56 72 88 47 33 122 33 90 0 145-46t64-118l-92-8zm270 165v-189h137q78 0 128-40 51-41 51-106 0-57-47-99-46-42-143-42h-225v476h99zm0-262v-143h108q59 0 81 21 23 21 23 50 0 33-25 52-24 20-70 20h-117z"
            />
          </svg>
          <a class="code-text" :href="icp.link" target="_blank">{{
            icp.code
          }}</a>
        </li>
        <li v-if="author.name" class="copyright-item">
          {{ `Copyright © ${beginYear}-${currentYear} ` }}
          <a v-if="!author.link">{{ author.name }}</a>
          <a
            v-else-if="author.link && author.title"
            :href="author.link"
            :title="author.title"
            target="_blank"
            >{{ author.name }}</a
          >
          <a
            v-else-if="author.link && !author.title"
            :href="author.link"
            target="_blank"
            >{{ author.name }}</a
          >
        </li>
      </ul>
    </div>
  </div>
</template>

<style scoped lang="scss">
.footer {
  width: 100%;
  // padding: 20px 0 16px;
  // margin-top: 40px;
  transition: all 0.3s ease;

  &.fixed {
    background-color: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(5px);
  }

  @media (max-width: 768px) {
    // padding: 16px 0 12px;
    // margin-top: 30px;
  }
}

.footer-divider {
  height: 1px;
  margin-bottom: 16px;
  background: linear-gradient(
    to right,
    transparent,
    rgba(0, 0, 0, 0.08),
    transparent
  );
}

.footer-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.footer-links {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 24px;
  margin-bottom: 12px;

  @media (max-width: 768px) {
    gap: 16px;
    margin-bottom: 10px;
  }
}

.footer-link {
  font-size: 13px;
  font-weight: 400;
  color: #666;
  text-decoration: none;
  transition: all 0.3s ease;

  &:hover,
  &.router-link-active {
    color: #0069c2;
  }

  &.router-link-active {
    font-weight: 500;
  }

  @media (max-width: 768px) {
    font-size: 12px;
  }
}

ul {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  color: #999;

  @media (max-width: 768px) {
    font-size: 11px;
  }

  li {
    margin: 4px 0;

    a {
      color: #999;
      text-decoration: none;
      transition: all 0.3s ease;
      position: relative;

      &[href] {
        &:hover {
          color: #0069c2;

          &::after {
            width: 100%;
          }
        }

        &::after {
          content: "";
          position: absolute;
          bottom: -2px;
          left: 0;
          width: 0;
          height: 1px;
          background-color: #0069c2;
          transition: width 0.3s ease;
        }
      }
    }
  }
}

.code-icon {
  width: 1em;
  height: 1em;
  margin-right: 3px;
  vertical-align: middle;
  transition: transform 0.3s ease;
}

.icp-item:hover .code-icon {
  transform: scale(1.1);
}

.code-text {
  vertical-align: middle;
}
</style>
