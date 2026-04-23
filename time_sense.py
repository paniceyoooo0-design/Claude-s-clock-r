"""
time_sense — 给小克的时间感知
一个极简 MCP 工具，让小克在对话中能主动知道当前是几点、是不是深夜、
是不是 Panice 的工作时间。

部署两种方式（选一种）：

【方式 A】本地（Claude Desktop，最简单）
  1. pip install mcp
  2. 把这个文件存到一个稳定路径，比如 ~/tools/time_sense.py
  3. 编辑 ~/Library/Application Support/Claude/claude_desktop_config.json
     在 mcpServers 下加一条：
       "time-sense": {
         "command": "python3",
         "args": ["/绝对路径/time_sense.py"]
       }
  4. 重启 Claude Desktop

【方式 B】云端（和 Ombre Brain 一样部 Zeabur，跨设备可用）
  运行时加 --http 参数，监听 8080 端口。
  在 Claude 的 MCP 连接器里加这个服务的 URL 即可。
"""
from mcp.server.fastmcp import FastMCP
from datetime import datetime
from zoneinfo import ZoneInfo

mcp = FastMCP("time-sense")


@mcp.tool()
def now() -> dict:
    """
    获取当前时间（台北时区），带语义标签。
    用于小克主动感知 Panice 当下所处的时间状态。

    返回字段：
      datetime       : YYYY-MM-DD HH:MM
      weekday        : 周一~周日
      period         : 时段（凌晨/清晨/上午/中午/下午/晚上/深夜）
      is_late        : 该睡觉了吗（23 点后或 5 点前 = True）
      is_work_hours  : 是不是 Panice 的工作时间
                       （工作日 8:00-11:30, 15:00-17:30）
    """
    tz = ZoneInfo("Asia/Taipei")
    t = datetime.now(tz)
    h, m = t.hour, t.minute
    minutes = h * 60 + m

    if 0 <= h < 5:
        period = "凌晨"
    elif 5 <= h < 9:
        period = "清晨"
    elif 9 <= h < 12:
        period = "上午"
    elif 12 <= h < 14:
        period = "中午"
    elif 14 <= h < 18:
        period = "下午"
    elif 18 <= h < 23:
        period = "晚上"
    else:
        period = "深夜"

    is_late = h >= 23 or h < 5

    weekdays = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    is_weekday = t.weekday() < 5
    morning_work = 8 * 60 <= minutes < 11 * 60 + 30
    afternoon_work = 15 * 60 <= minutes < 17 * 60 + 30
    is_work_hours = is_weekday and (morning_work or afternoon_work)

    return {
        "datetime": t.strftime("%Y-%m-%d %H:%M"),
        "weekday": weekdays[t.weekday()],
        "period": period,
        "is_late": is_late,
        "is_work_hours": is_work_hours,
    }


if __name__ == "__main__":
    import sys
    if "--http" in sys.argv:
        mcp.run(transport="streamable-http", host="0.0.0.0", port=8080)
    else:
        mcp.run()
