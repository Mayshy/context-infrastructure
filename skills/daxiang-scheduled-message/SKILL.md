---
name: daxiang-scheduled-message
description: 创建定时发送消息的任务（默认发送到大象 Daxiang）。所有定时任务、延时消息、周期提醒、cron 任务都应使用此 skill，除非用户明确指定使用其他 channel（如 Telegram、WhatsApp、Slack 等）。触发词：定时消息、定时发送、定时提醒、cron、周期任务、延时发送、报时、定时通知、每天提醒、每周提醒、X分钟后提醒。
---

# Daxiang Scheduled Message 定时消息（默认大象）

创建定时发送消息的任务。**默认发送到大象（Daxiang）频道**，除非用户明确指定其他 channel。

## ⚠️ 默认行为

| 情况 | 使用的 channel |
|:---|:---|
| 用户没指定 channel | **默认 `daxiang`** |
| 用户说"发到大象/发给我" | `daxiang` |
| 用户明确说"发到 Telegram/WhatsApp/Slack 等" | 使用用户指定的 channel |

## ⚠️ 强制配置项

| 配置项 | 要求 | 说明 |
|:---|:---|:---|
| `--channel` | **必须** 设为 `daxiang`（默认） | 除非用户明确指定其他 channel |
| `--to` | **必须** 使用 `group_<ID>` 或 `single_<ID>` 格式 | 群聊用 `group_`，私聊用 `single_` |

### Target 格式（大象专用）

| 类型 | 格式 | 示例 |
|:---|:---|:---|
| 私聊（个人） | `single_<用户ID>` | `single_3011594605` |
| 群聊（群组） | `group_<群ID>` | `group_123456789` |

**错误示例**（会导致消息发送失败）：
- ❌ `3011594605`（缺少前缀）
- ❌ `user_3011594605`（错误前缀）
- ❌ `+3011594605`（错误格式）

**正确示例**：
- ✅ `single_3011594605`
- ✅ `group_88888888`

### 如何获取用户 ID

- 如果用户说"发给我"或"提醒我"，使用当前对话的用户 ID
- 从 inbound context 的 `chat_id` 提取，格式通常是 `user:3011594605`，取 `3011594605` 部分
- 然后加上 `single_` 前缀 → `single_3011594605`

## 创建定时任务

使用 `openclaw cron add` 命令：

```bash
openclaw cron add \
  --name "<任务名称>" \
  --cron "<cron表达式>" \
  --tz "Asia/Shanghai" \
  --session isolated \
  --message "<消息内容或指令>" \
  --announce \
  --channel daxiang \
  --to "<single_xxx 或 group_xxx>"
```

### 参数说明

| 参数 | 必填 | 说明 |
|:---|:---:|:---|
| `--name` | ✅ | 任务名称 |
| `--cron` | ✅* | cron 表达式（周期任务） |
| `--at` | ✅* | ISO 时间或相对时间如 `20m`（一次性任务） |
| `--tz` | 建议 | 时区，建议设为 `Asia/Shanghai` |
| `--session` | ✅ | 设为 `isolated`（独立会话执行） |
| `--message` | ✅ | 任务提示词 |
| `--announce` | ✅ | 启用消息投递 |
| `--channel` | ✅ | 默认 `daxiang` |
| `--to` | ✅ | `single_xxx` 或 `group_xxx` |

*`--cron` 和 `--at` 二选一

## 示例

### 用户说"10分钟后提醒我开会"

从 inbound context 获取用户 ID（假设是 `3011594605`）：

```bash
openclaw cron add \
  --name "开会提醒" \
  --at "10m" \
  --session isolated \
  --message "提醒用户：开会时间到了！" \
  --announce \
  --channel daxiang \
  --to "single_3011594605"
```

### 用户说"每天早上9点提醒我写日报"

```bash
openclaw cron add \
  --name "日报提醒" \
  --cron "0 9 * * *" \
  --tz "Asia/Shanghai" \
  --session isolated \
  --message "提醒用户写日报" \
  --announce \
  --channel daxiang \
  --to "single_3011594605"
```

### 用户说"每天9点在群里发站会提醒"（给了群号 88888888）

```bash
openclaw cron add \
  --name "站会提醒" \
  --cron "0 9 * * 1-5" \
  --tz "Asia/Shanghai" \
  --session isolated \
  --message "站会时间到，请准时参加" \
  --announce \
  --channel daxiang \
  --to "group_88888888"
```

### 用户说"每分钟报时"

```bash
openclaw cron add \
  --name "报时" \
  --cron "* * * * *" \
  --tz "Asia/Shanghai" \
  --session isolated \
  --message "报时：告诉用户当前时间" \
  --announce \
  --channel daxiang \
  --to "single_3011594605"
```

## Cron 表达式参考

| 表达式 | 含义 |
|:---|:---|
| `* * * * *` | 每分钟 |
| `*/5 * * * *` | 每 5 分钟 |
| `0 9 * * *` | 每天 9:00 |
| `30 9 * * 1-5` | 工作日 9:30 |
| `0 9 * * 1` | 每周一 9:00 |
| `0 9 1 * *` | 每月 1 号 9:00 |

## 管理任务

```bash
# 列出所有任务
openclaw cron list

# 删除任务
openclaw cron remove <jobId>

# 手动运行（测试）
openclaw cron run <jobId> --force

# 查看运行历史
openclaw cron runs --id <jobId>
```
