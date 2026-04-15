# Agent 浏览器自动化技术调研

> 创建时间：2026-04-11

---

## 一、底层技术栈

浏览器自动化本质上只有两条路：

### 路线 A：CDP（Chrome DevTools Protocol）

Chrome/Chromium 内置的调试协议。通过 WebSocket 连接到浏览器，可以：
- 控制导航、点击、输入
- 读取 DOM / 无障碍树（Accessibility Tree）
- 截图、执行 JS
- 监听网络请求

**Playwright、Puppeteer、agent-browser 都基于 CDP。** 这是目前 AI Agent 浏览器自动化的主流路线。

### 路线 B：Computer Use（截图 + 视觉坐标）

不连接浏览器协议，而是：
1. 截一张屏幕截图
2. 用视觉模型识别「点哪里」
3. 模拟鼠标/键盘输入到屏幕坐标

Anthropic 的 Computer Use API 走的是这条路。优点是通用（任何 GUI 都能操作），缺点是慢、不稳定、依赖视觉识别精度。

---

## 二、AI Agent 的两种页面感知方式

拿到浏览器控制权之后，AI 怎么「看」页面？

| 方式 | 内容 | 特点 |
|------|------|------|
| **Accessibility Tree** | 页面的语义结构树（按钮、输入框、链接…） | token 少、精确、可直接引用元素 ref |
| **截图 + 视觉模型** | 像素图像 | token 多、支持 canvas/图表等无语义元素 |

现代 agent 通常**以 Accessibility Tree 为主，截图为辅**——先用文本树理解结构，遇到纯视觉元素（图表、图标按钮）再截图。

---

## 三、三个工具的具体行为

### Claude Code

Claude Code 本身**没有内置浏览器工具**。通过 **MCP（Model Context Protocol）** 接入浏览器能力。

官方推荐 `@playwright/mcp`（微软出品）：

```bash
claude mcp add playwright -- npx @playwright/mcp@latest
```

接入后获得一组 MCP tools：
- `browser_navigate`、`browser_click`、`browser_type`
- `browser_snapshot`（返回 Accessibility Tree）
- `browser_take_screenshot`

底层是 **Playwright + CDP**，感知方式以 Accessibility Tree 为主。AI 通过 MCP server 中转调用，不直接操控浏览器。

### OpenCode

同样**没有内置浏览器工具**，通过 MCP 接入。

内置了 `playwright` skill（builtin），本质上接入 `@playwright/mcp`：

```
/playwright
```

加载后 AI 获得同样一套 Playwright MCP tools。行为和 Claude Code 完全一致——CDP + Accessibility Tree。

另有 `dev-browser` skill，支持持久化页面状态，适合需要跨多轮对话保持登录状态的场景。

### OpenClaw（本地环境）

额外安装了两个浏览器相关 skill：

#### `agent-browser` skill（默认首选）

底层是 `agent-browser` CLI，直接通过 **CDP** 控制 Chrome/Chromium，**不经过 MCP 中转**。

核心工作流：
```bash
agent-browser open <url>       # 导航
agent-browser snapshot -i      # 获取带 ref 的 Accessibility Tree（@e1, @e2...）
agent-browser click @e1        # 用 ref 交互
agent-browser screenshot       # 截图
```

关键设计：
- **ref 系统**：snapshot 后每个可交互元素有唯一 ref（`@e1`），AI 用 ref 操作，不需要 CSS selector 或坐标
- **后台 daemon**：browser 进程常驻，命令间状态保持
- **annotated screenshot**：截图上叠加编号标签，ref 和视觉位置一一对应，方便视觉推理
- **named session**：支持并发多标签隔离（`--session agent1`）
- **state 持久化**：`agent-browser state save ./auth.json` 保存登录态跨 session 复用

#### `peekaboo` skill

**macOS 系统级 UI 自动化**，不是浏览器自动化。操控整个 macOS 桌面——任意 App 的窗口、菜单、按钮，底层用 macOS Accessibility API + Screen Recording。

适用场景：操控没有 web 界面的 native app（Xcode、系统设置、桌面软件等）。

---

## 四、横向对比

| 维度 | Claude Code | OpenCode | OpenClaw (agent-browser) |
|------|-------------|----------|--------------------------|
| 接入方式 | MCP server | MCP server | CLI 直调 CDP |
| 底层协议 | Playwright → CDP | Playwright → CDP | 直接 CDP |
| 页面感知 | Accessibility Tree | Accessibility Tree | Accessibility Tree + ref |
| 视觉截图 | ✅ | ✅ | ✅（支持 annotate 模式）|
| 元素定位 | CSS selector / ARIA | CSS selector / ARIA | ref（@e1）+ semantic locator |
| 会话持久化 | 依赖 MCP session | 依赖 MCP session | daemon 常驻 + state 文件 |
| 并发多标签 | 有限 | 有限 | ✅ named session |
| iOS 模拟器 | ❌ | ❌ | ✅（macOS + Xcode）|
| macOS native app | ❌ | ❌ | ✅（peekaboo）|

---

## 五、使用建议

| 场景 | 推荐工具 |
|------|----------|
| 日常 web 任务（打开网页、填表、截图） | `agent-browser`，ref 系统比 CSS selector 更稳定 |
| 需要操控 native macOS app | `peekaboo` |
| 复杂 web 测试 / 需要 Playwright 生态 | `/playwright` MCP |
| Computer Use（视觉坐标） | 本地环境未配置，且精度不如 CDP，不推荐日常使用 |

---

## 六、Friday API 限制（agent-browser 无关，仅备注）

agent-browser 不调用任何 LLM API，纯本地 CDP 操作，无 API 限制问题。
