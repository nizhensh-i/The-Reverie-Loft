const DISTANCE = 100;
const DURATION = 500;

// 一个对象作为 WeakMap 的键存在，不会阻止该对象被垃圾回收
const map = new WeakMap();

// 异步观察目标元素与其祖先元素或顶级文档视口（viewport）交叉状态的方法
// 监听根中一段给定比例的可见区域
const ob = new IntersectionObserver((entries) => {
  for (const entry of entries) {
    // 该元素和视口相交
    if (entry.isIntersecting) {
      // 播放该元素动画
      const animation = map.get(entry.target);
      if (animation) {
        animation.play();
        ob.unobserve(entry.target);
      }
    }
  }
});

// 是否在视口之下
function isBelowViewport(el) {
  // 返回值是一个 DOMRect 对象
  // 该对象使用 left、top、right、bottom、x、y、width 和 height 属性描述边框框的位置和大小
  const rect = el.getBoundingClientRect();
  return rect.top - DISTANCE > window.innerHeight;
}

export default {
  mounted(el) {
    if (!isBelowViewport) {
      return;
    }
    const animation = el.animate(
      [
        {
          transform: `translateY(${DISTANCE}px)`,
          opacity: 0,
        },
        {
          transform: `translateY(0)`,
          opacity: 1,
        },
      ],
      {
        duration: DURATION,
        easing: "ease-in-out",
        fill: "forwards",
      }
    );
    animation.pause();
    ob.observe(el);
    map.set(el, animation);
  },
  unmounted(el) {
    ob.unobserve(el);
  },
};
