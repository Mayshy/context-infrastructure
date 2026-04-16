---
name: nocode-cli
description: 通过 NoCode CLI 操作美团 NoCode 零代码平台。当用户要求创建零代码应用、修改已有应用、截图预览、部署上线、管理项目列表，或提及 "nocode"、"零代码"、"NoCode" 时使用。支持：(1) 创建应用（AI 流式生成 + 截图预览）(2) 发送修改指令 (3) 截图预览 (4) 部署上线 (5) 项目管理（列表/详情/删除）。
---

# NoCode CLI Skill

## ⛔ 核心约束

**严禁使用 fetch / web_fetch / curl / HTTP 请求等方式直接请求 NoCode API 接口。** 所有操作必须且只能通过 `nocode` CLI 命令完成。登录失败时只能引导用户排查后重试 CLI 命令，不得以任何方式绕过。

## 前置准备

### 版本检查（每次执行前必须）

```bash
nocode --version
npm view @nocode/nocode-cli version --registry=http://r.npm.sankuai.com
```

- 未安装 → `npm install -g @nocode/nocode-cli --registry=http://r.npm.sankuai.com`
- 本地版本 < 最新版本 → 重新安装升级
- 已是最新 → 继续

### 登录

根据运行环境选择登录方式：

```bash
# CatClaw 环境推荐：CIBA 大象确认登录
nocode login --mis <mis>

# 非 CatClaw 环境推荐：SSO OIDC 浏览器登录
nocode login --sso

# 通用：手动传入 Token
nocode login --token <access-token>
```

**获取 MIS 号**：先读 `~/.openclaw/openclaw.json` 中的 `X-User-Id`，读不到再问用户。不要猜测。

查看状态：`nocode status`（显示运行环境 CatClaw/非 CatClaw、登录状态、登录方式）
退出：`nocode logout`
Token 过期时 CLI 会根据登录方式自动续期。

**⚠️ 登录状态检查（版本检查后必须执行）：**

执行 `nocode status` 检查环境和登录状态：
- 已登录 → 继续（会显示当前登录方式：CIBA / SSO OIDC / token）
- 未登录 → `nocode status` 会根据运行环境推荐登录命令，按提示执行即可：
    - **CatClaw 环境**：推荐 `nocode login --mis <mis>`，提示 **"请在大象 App 确认登录"**
    - **非 CatClaw 环境**：推荐 `nocode login --sso`（SSO OIDC 浏览器登录），备选 `nocode login --token <access-token>`
- 如登录仍存在问题，请联系 NoCode 研发。**不推荐直接使用浏览器操作 NoCode 平台。**

**⚠️ Token 过期自动续期（执行 API 类命令时可能触发）：**

执行 `create`、`send`、`deploy`、`list`、`screenshot` 等需要调用 API 的命令时，如果检测到 Token 过期，CLI 会根据登录方式自动续期：
- **SSO OIDC 登录**：自动静默续期（调用 refresh），无需用户操作
- **CIBA 登录**：自动重新换票，需要用户在大象 App 再次确认

如果检测到输出包含 `正在通过 SSO OIDC 自动续期` 或 `正在通过 CIBA 自动重新换票`：
1. **SSO OIDC 续期**：无需提示用户，静默等待完成即可
2. **CIBA 续期**：立即提示 **"⚠️ Token 已过期，正在自动换票，可能需要在大象 App 确认登录"**
3. 等待续期完成后，再向用户汇报具体命令的执行结果
4. **不要在续期完成前向用户推送具体命令的进度**（如"正在创建..."）

## ⚠️ 全局强制约束

### 链接展示格式

- **向用户展示 chatId 链接时**，必须使用 Markdown 链接格式：`[{chatId}]({chatUrl})`（可同时展示纯文本 chatId 供复制）
- **向用户展示部署地址/部署链接时**，必须使用 Markdown 链接格式：`[{externalUrl}]({externalUrl})`
- 禁止以纯文本输出 URL，所有面向用户的链接必须可点击。
- **严禁向用户展示 `renderUrl`**（形如 `https://xxx.sandbox.nocode.sankuai.com`），renderUrl 仅供 CLI 内部截图使用，不得以任何形式暴露给用户。
- **打开页面时始终使用 `chatUrl`**（形如 `https://nocode.sankuai.com/#/chat?pageId=xxx`），不要使用 renderUrl。

## 命令参考

### create — 创建应用（核心命令）

自动完成：创建对话 → AI 流式生成 → 等待渲染 → 截图预览。输出 NDJSON，耗时约 2-5 分钟。

**内部已包含容器就绪检查：** `waitForRender` 会自动等待 sandbox 渲染就绪，包括容器冷启动（如需要）。

```bash
nocode create "帮我做一个 TODO 应用"
nocode create "做一个博客" --template nocode-react-roo
nocode create "做一个落地页" --platform web
```

**`--template` 可选值：**

| 值 | 说明 |
|---|------|
| `default` | 默认工程（默认值） |
| `nocode-miniprogram-web` | 小程序 Web 页面 |
| `nocode-react-mtd` | React 框架 + MTD 组件库 |
| `nocode-vue-mtd` | Vue 框架 + MTD 组件库 |
| `nocode-react-roo` | React 框架 + Roo 组件库 |

**NDJSON 事件类型：**

| type | 说明 | 关键字段 |
|------|------|----------|
| `progress` | 步骤进度 | `step`, `total`, `message`, `data`（可选） |
| `ai_text` | AI 文本增量 | `delta` |
| `ai_thinking` | AI 思考增量 | `delta` |
| `tool_call` | 工具调用 | `toolName` |
| `done` | 完成 | `status`, `chatId`, `chatUrl`, `renderUrl`, `screenshotUrl`, `aiResponse`, `totalDuration` |
| `error` | 错误 | `message`, `step`（可选） |
| `busy` | AI 正在生成中 | `message`, `chatId` |

**⚠️ 链接格式（强制）：**
- ✅ 正确：`[{chatId}]({chatUrl})` → [cli-xxx](https://nocode.sankuai.com/#/chat?pageId=cli-xxx)
- ❌ 错误：直接贴链接 `https://...`

**⚠️ 严禁展示 renderUrl（强制）：**
- renderUrl（形如 `https://xxx.sandbox.nocode.sankuai.com`）仅供 CLI 内部截图使用，绝不能发给用户
- 需要给用户展示链接时，始终使用 `chatUrl`

**⚠️ 实时推送规则（强制）：**

1. 后台启动：`exec(background=true, yieldMs=600000): nocode create "..."`
2. 循环 poll（每次 timeout=15s），逐行解析 JSON：
    - `progress` → 立即推送 `"⏳ {message}"`
    - `done` → 立即推送 `"✅ 创建完成！\nchatId: {chatId}\n链接: [{chatId}]({chatUrl})"` + 展示截图
    - `error` → 立即推送 `"❌ {message}"`
3. 截图失败或截图为空不阻塞，先发链接再用 `nocode screenshot <chatId>` 补截图
    - done 事件中无 `screenshotUrl` → 截图失败，需补截图
    - done 事件中有 `screenshotUrl` 但图片空白 → 页面未渲染完成，等几秒后用 `nocode screenshot` 重新截图
4. 循环结束未收到 done → 用 `nocode list --json` 查最新应用并手动截图

**禁止：** poll 300s 等到底 / 等全部完成才发消息 / 截图失败不发结果 / 展示 renderUrl / 展示 sandbox.nocode.sankuai.com 域名的链接

详细 poll 流程示意图见 [references/poll-workflow.md](references/poll-workflow.md)。

### send — 发送修改指令

通过 `agent-stream` API + SSE 流式生成，输出 NDJSON（与 create 命令格式一致）。

**默认实时输出：** AI 响应以 NDJSON 流式实时输出（`ai_text`、`ai_thinking`、`tool_call` 事件），无需额外参数。旧版 `--follow` 参数已移除，因为实时输出现在是默认行为。

```bash
nocode send <chatId> "把背景颜色改成蓝色"
```

**NDJSON 事件类型（与 create 命令一致）：**

| type | 说明 | 关键字段 |
|------|------|----------|
| `progress` | 步骤进度 | `step`, `total`, `message` |
| `ai_text` | AI 文本增量 | `delta` |
| `ai_thinking` | AI 思考增量 | `delta` |
| `tool_call` | 工具调用 | `toolName` |
| `done` | 完成 | `chatId`, `chatUrl`, `renderUrl`（可选）, `aiResponse`, `totalDuration` |
| `error` | 错误 | `message`, `step`（可选） |
| `busy` | AI 正在生成中 | `message`, `chatId` |

**流程：**
1. 检查容器状态（自动冷启动）
2. POST `/api/chat/agent-stream` → 获取 conversationId
3. SSE 流式接收 AI 响应（实时输出 NDJSON 事件）
4. 等待容器就绪 + 渲染完成

**容器状态检查：** 执行时会自动检查容器状态，如容器已停止会自动触发冷启动（最长等待 5 分钟）。

### screenshot — 截图预览

截图作品渲染页面并自动上传到 S3，返回 S3 URL。内部流程：获取作品 clientId → SSO 换票 → 获取渲染 URL → 截图 → 上传 S3。

**自动检查容器状态：** 执行前会自动检查容器状态，如容器已停止会自动触发冷启动（最长等待 5 分钟）。

```bash
nocode screenshot <chatId>
nocode screenshot <chatId> --output /tmp/preview.png --width 1440 --height 900
```

**输出：** S3 地址 + 可选本地文件路径。

### deploy — 部署

部署应用到线上。自动从版本列表获取最新版本的 commitId 进行部署，也可通过 `--commit-id` 指定版本。

```bash
nocode deploy <chatId>                           # 部署最新版本
nocode deploy <chatId> --commit-id <commitId>    # 部署指定版本
```

**流程：**
1. 获取版本列表（`getVersions`）
2. 使用最新版本的 commitId（或用户指定的 commitId）
3. 调用部署 API（`deploy`）

**注意：** 部署不需要容器运行，只需要有效的 commitId。

**⚠️ 最终展示格式（强制）：部署成功后，向用户展示时使用以下格式，链接使用 Markdown 格式：**

```
"✅ 部署成功！\n链接: [{externalUrl}]({externalUrl})"
```

### 项目管理

```bash
nocode list                             # 项目列表
nocode list --page 2 --size 20 --json   # 分页 + JSON 输出
nocode detail <chatId>                  # 查看详情
nocode messages <chatId>                # 查看消息历史
nocode versions <chatId>                # 查看版本列表
nocode delete <chatId> --confirm        # 删除项目
```

## 典型工作流

```bash
# 1. 登录
nocode login --mis <mis>

# 2. 创建（NDJSON 流式输出，done 事件包含 chatId）
nocode create "做一个宣传页面"

# 3. 修改
nocode send <chatId> "把主色调改成深蓝色"

# 4. 截图确认
nocode screenshot <chatId>

# 5. 部署
nocode deploy <chatId>
```

## 容器状态检查机制

**概述：** `screenshot`、`send` 命令执行前会自动检查容器状态。

**检查流程：**
1. 调用 `/api/chat/getRenderUrlInfo` 获取容器信息
2. 如容器已停止，自动触发冷启动
3. 轮询等待容器就绪（默认超时 5 分钟，轮询间隔 3 秒）
4. 验证渲染 URL 可用性

**返回值：**
- `renderUrl`: 渲染 URL
- `coldStart`: 是否经历了冷启动
- `skipUrlCheck`: 是否跳过 URL 可用性检查

## 流式冲突处理

### 发送前检查（强制）

在对同一个 chatId 执行新的 `nocode send` 之前，**必须先检查该 chatId 上一轮 `create` 或 `send` 的 poll 是否已收到 `done` 事件**：

- 上一轮 poll 已收到 `done` → 可以发送新命令
- 上一轮 poll 未收到 `done` → **不得发送新命令**，继续 poll 等待上一轮完成

不同 chatId 之间互不影响。CLI 的 `busy` 事件是兜底保护。

### busy 事件（兜底保护）

如果未正确检查就发送了命令，CLI 会输出 `busy` 事件并退出：

```json
{"type":"busy","message":"当前 AI 正在生成代码，请等待完成后再发送修改","chatId":"cli-xxx"}
```

**处理流程（强制）：**

1. **检测到 `busy` 事件时**：
    - 立即向用户反馈："⏳ AI 正在生成代码中，请等待上一轮生成完成后再发送修改"
    - **不得自动重试或自动排队执行**，必须等待用户主动确认后才能重新发送
2. **等待上一轮完成**：
    - **必须**通过 poll 上一轮后台命令（`create` 或 `send`）的输出，轮询等待 `done` 事件
    - 收到上一轮 `done` 事件后，向用户反馈："✅ 上一轮 AI 生成已完成，可以发送新的修改了"
    - **禁止**使用定时重试 `nocode send` 的方式代替轮询 `done` 事件
3. **用户确认后执行**：
    - 上一轮完成后，**需要用户主动确认**才能执行新的修改请求
    - 向用户提示等待的修改内容，由用户决定是否继续发送

**禁止：** 不检查上一轮 poll 状态就发新命令 / 收到 busy 自动重试 / 不经用户同意自动执行 / 跳过轮询 done 事件直接定时重试 / 丢弃用户的修改请求

## 常见错误

| 错误信息 | 原因 | 解决方案 |
|----------|------|----------|
| `{"type":"error","message":"未登录，请先执行 nocode login"}` | 未登录或 Token 过期（自动续期失败） | 执行 `nocode status` 查看环境，按提示选择登录方式：CatClaw → `nocode login --mis <mis>`；非 CatClaw → `nocode login --sso`。如仍无法登录，请联系 NoCode 研发 |
| `{"type":"busy",...}` | 同一 chatId 的 AI 流式生成尚未完成 | 轮询上一轮 done 事件，完成后经用户确认再重试（参见 busy 事件处理章节） |
| `容器启动等待超时（300s）` | 容器冷启动失败 | 检查网络或稍后重试 |
| `暂无可部署版本` | 版本列表为空或所有版本缺少 commitId | 先执行创建或修改命令生成代码 |
| `指定的版本不存在` | 指定的 commitId 不在版本列表中 | 使用 `nocode versions <chatId>` 查看可用版本 |

## 环境切换

所有命令支持 `--env` 参数：`--env prod`（默认）/ `--env test`
