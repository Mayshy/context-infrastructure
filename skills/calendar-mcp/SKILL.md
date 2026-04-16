---
name: calendar-mcp
description: 美团日历（日程管理）MCP 工具集（SSE Session）。支持创建/查询/编辑/取消日程、搜索日程、查询忙闲，并自动将 mis 转换为 empId（通过 lookup MCP 服务）。当用户想“安排会议/新建日程/改期/取消/查忙闲/查这段时间有哪些会”时激活。通过 oa-skills calendar-mcp CLI 执行。
metadata:
  openclaw:
    priority: 0
    conflict_strategy: override
    emoji: "📅"
    requires:
      bins: ["node", "npx"]
      deps: ["tsx", "@it/oa-skills@latest"]
---

# 📅 Calendar MCP（日程管理）操作指南（CLI 版）

本 skill 以 MCP Hub（SSE Session）方式调用日历服务，目标是：低误操作风险、可直接执行、结果可验证。

MCP Server：
- 日历服务（Schedule）：`http://mcphub-server.sankuai.com/mcphub-b/8781956a2daf4d`
- 身份映射（mis → empId）：`http://mcphub-server.sankuai.com/mcphub-api/5ef912172ad244`

换票 audience（clientId）：
- 日历（Schedule）：`9f890de0db`
- 身份映射（xm-xai）：`xm-xai`

## 当前可用能力

- 创建日程：`create_primary_schedule`
- 查询详情：`query_primary_schedule`
- 选择性编辑：`update_primary_schedule_by_selective`
- 取消日程：`delete_primary_schedule`
- 搜索日程：`search_calendar`
- 查询忙闲：`list_busy_period`
- mis → empId 映射：`get_uid_and_empid_by_mis`（lookup MCP）

## 前置检查：确保 CLI 最新

每次执行命令前，先检查 `@it/oa-skills` 是否为最新版本：

```bash
npm list -g @it/oa-skills --depth=0 2>/dev/null | grep oa-skills
```

如果未安装或版本不是最新，执行更新：

```bash
npm install -g @it/oa-skills@latest --registry=http://r.npm.sankuai.com
```

**此步骤必须在每次 skill 激活时执行一次，否则新命令可能不存在导致运行失败。**

## 核心约束

- 所有调用必须通过 `oa-skills calendar-mcp ...` 执行；不要在回复里拼接长段 SSE / curl。
- 底层 MCP Tool 的参与人相关字段实际要求 `empId`，但 `calendar-mcp` CLI 对外支持传 `mis` 或纯数字 `empId`：
  - `createSchedule --attendees`
  - `searchSchedule --attendees`
  - `listBusyPeriod --users`
  - `updateSchedule --addAttendees / --removeAttendees`
  上述参数传入 `mis` 时，CLI 会先自动转换为 `empId` 再调用 MCP。
- 对外输入时间统一按毫秒时间戳（ms）；`list_busy_period` 会在内部转换为工具需要的 `YYYY-MM-DD HH:mm:ss`。
- `search_calendar` 的 `attendUser` 必填且为 empId long 数组；CLI 负责生成 `tid`（UUID），用户无需提供。
- 用户没提供 `scheduleId` 但要改/取消/看详情：应先用 `searchSchedule` 搜索候选，再内部继续调用（不要向用户索要 `scheduleId`）。
- 默认回复只给用户关心结果（中文摘要），不贴原始 RPC；仅在排障或用户明确要求时用 `--raw`。
- 循环日程 / 会议室日程：当前不支持，直接说明暂不支持，不要继续追问循环规则/会议室细节。
- `updateSchedule` 不支持 `--attendees`。编辑参与人时只能使用：
  - `--addAttendees "mis1,mis2"`
  - `--removeAttendees "mis3,mis4"`
- 当前只支持 `mis -> empId` 转换，不支持“姓名 -> mis”自动转换；如果用户只提供人员姓名，除非能从当前上下文唯一确定对应 `mis`，否则必须要求用户补充 `mis`。
- 若一句话中包含多个动作，例如“先查忙闲再建会”“先搜这周的会再取消其中一条”，要拆成串行步骤执行；每一步只调用一个 CLI 方法。
- 查询其他人的日程时，不要表述成“对方全部日程”；应理解为“你当前有权限看到的、与输入条件匹配的日程/交集日程”。
- 删除或更新日程后，优先用 `querySchedule --raw` 或再次按 `scheduleId` 验证；`searchSchedule` 的检索结果可能有短暂延迟，不要用刚删除后的一次搜索结果直接判定删除失败。

## 认证

认证由 CLI 自动处理：Supabase CIBA → 换票 → Bearer Token（`Authorization: Bearer <token>`）。首次调用需在大象 App 确认授权，token 自动缓存。

常见自查：
- 认证失败/过期：`oa-skills calendar-mcp --clear-cache` 后重试
- mis 无法解析：需要用户提供正确 mis（不支持“姓名 → mis”自动识别）

## CLI 使用

所有命令格式：`oa-skills calendar-mcp <method> [options]`

```bash
# 查看帮助
oa-skills calendar-mcp --help

# mis -> empId
oa-skills calendar-mcp resolveEmpIdsByMis --misCsv "cuiweitong,zhangsan"

# 创建日程（CLI 接受 mis 或 empId，内部自动转换为 MCP 需要的 empId）
oa-skills calendar-mcp createSchedule --title "项目周会" --attendees "cuiweitong,zhangsan" --startMs 1772660400000 --endMs 1772664000000 --location "A3-09木星" --memo "同步进度"

# 搜索日程（CLI 接受 mis 或 empId，内部自动转换为 MCP 需要的 empId）
oa-skills calendar-mcp searchSchedule --attendees "cuiweitong,zhangsan" --startMs 1772611200000 --endMs 1772697599000 --title "周会"

# 查忙闲（CLI 接受 mis 或 empId，内部自动转换为 MCP 需要的 empId）
oa-skills calendar-mcp listBusyPeriod --users "cuiweitong,zhangsan" --minMs 1772611200000 --maxMs 1772697599000

# 查详情 / 改期 / 取消（内部优先用搜索结果的 scheduleId，不对外展示）
oa-skills calendar-mcp querySchedule --scheduleId "schedule-id"
oa-skills calendar-mcp updateSchedule --scheduleId "schedule-id" --title "改期" --startMs 1772667600000 --endMs 1772671200000
oa-skills calendar-mcp updateSchedule --scheduleId "schedule-id" --addAttendees "cuiweitong,zhangsan"
oa-skills calendar-mcp updateSchedule --scheduleId "schedule-id" --removeAttendees "lisi"
oa-skills calendar-mcp deleteSchedule --scheduleId "schedule-id"
```

注意：
- `createSchedule` 使用 `--attendees`
- `updateSchedule` 不接受 `--attendees`，只能用 `--addAttendees` / `--removeAttendees`
- 如果用户给的是 `mis`，CLI 会自动做 `mis -> empId` 转换；如果用户直接给纯数字 `empId`，也可以直接透传

## 执行策略

### 创建：按风险分流

以下场景，创建前优先执行 `listBusyPeriod`：
- 多人会议
- 用户明确要求避冲突 / 找都空的时间
- 需要向用户推荐候选时间

以下场景可跳过忙闲检查：
- 单人提醒
- 用户明确要求“直接创建，不用查忙闲”

### 搜索：用于先定位候选日程

适用场景：
- 用户只记得参与人、时间范围、标题关键词，想先列出候选日程
- 用户没有 `scheduleId`，但需要先搜索再决定查哪条详情、编辑或取消

约束：
- `searchSchedule` 是“按条件列出候选日程”，不是“按 ID 查详情”
- 当查询对象包含其他用户时，搜索结果应理解为“当前你有权限看到的匹配日程”，不要表述成对方全部日程

### 查询详情：内部依赖 `scheduleId`

适用场景：
- 用户要看某一条已知日程的详细信息

约束：
- 如果用户没有 `scheduleId`，先用 `searchSchedule` 找候选，再内部继续调用 `querySchedule`
- 不要向用户索要 `scheduleId`
- 对用户回复时默认不展示 `scheduleId`

### 忙闲查询：用于找空档，不代替日程详情

适用场景：
- 创建多人会议前检查冲突
- 用户问“这几个人什么时候都有空”
- 需要给出候选会议时间

不适用场景：
- 用户已经提供 `scheduleId`，想确认具体某个日程的内容
- 用户只是想查看某一条日程详情

## 输出规则

- 默认输出中文摘要；`--raw` 才输出原始 JSON/文本
- 默认不对外展示 `scheduleId`
