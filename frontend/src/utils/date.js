import dayjs from "@/config/dayjsCfg";

export default {
  isYesterday(date) {
    // 将输入的日期字符串转换为 dayjs 对象
    const inputDate = dayjs(date).startOf("day");
    // 获取当前日期的 dayjs 对象
    const today = dayjs().startOf("day");
    // 计算 inputDate 与今天日期的差值，单位为天
    const diff = today.diff(inputDate, "day");
    // 如果差值为 -1，则说明 inputDate 是昨天
    return diff === 1;
  },
  toDateStr(date) {
    return dayjs(date).tz("UTC").format("YYYY-MM-DD HH:mm:ss");
  },
  dateShow(date) {
    // 当天内返回相对时间，其他的时间自定义
    const d = dayjs(date);
    const currentYear = dayjs().year();
    const currentMonth = dayjs().month() + 1;
    // 注意，date()是日期，而day()是星期几
    const currentDay = dayjs().date();

    const year = d.year();
    const month = d.month() + 1;
    const day = d.date();
    if (year > currentYear) {
      return "null";
    }
    // 今年
    if (year === currentYear) {
      if (month === currentMonth && day === currentDay) {
        // 今天 返回相对时间
        return d.fromNow();
      } else if (month === currentMonth && day === currentDay - 1) {
        // 昨天
        return "昨天 " + d.format("HH:mm");
      } else {
        // 本月之前的日期
        return d.format("MM-DD HH:mm");
      }
    }
    // 今年之前的日期
    else if (year < currentYear) {
      return d.format("YYYY-MM-DD HH:mm");
    }
  },
};
