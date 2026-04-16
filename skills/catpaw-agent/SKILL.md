---
name: catpaw-agent
description: '使用 CatPaw CLI 通过 acpx 调用进行代码开发。CatPaw 是美团内部的 AI 编码助手，支持通过 ACP 协议与 acpx 集成。触发条件：用户提到 catpaw、catpaw-cli、使用 catpaw 进行编码、使用 acpx 调用 catpaw 等。'
metadata:
  {
    "openclaw": { "emoji": "🐱"}
  }
---

# CatPaw Agent 使用指南

CatPaw 是美团内部的 AI 编码助手，可以通过 `acpx` 调用。

## 前置要求

### 1. 安装 acpx
```bash
npm install -g acpx@latest
```

### 2. 安装 catpaw-cli

从美团 S3 下载 catpaw-cli 并配置到环境变量中：

```bash
mkdir -p ~/bin && curl -o ~/bin/catpaw-cli -L https://s3plus.sankuai.com/mcopilot-pub/cli/v0.1.9/catpaw-cli-linux-x64 && chmod +x ~/bin/catpaw-cli
```

将 `~/bin` 加入 PATH：

```bash
echo 'export PATH="$HOME/bin:$PATH"' >> ~/.bashrc && source ~/.bashrc
```

验证安装：
```bash
catpaw-cli --version
```

### 3. 配置 CatPaw 认证与客户端信息

通过环境变量 `CATPAW_CONFIG_CONTENT` 统一配置认证 cookie 和客户端信息。

#### 步骤 1：获取 cookie

> **前置条件**：脚本依赖 `IDENTIFIER`，会按以下顺序读取：
> 1. 环境变量 `$IDENTIFIER`
> 2. `/root/.openclaw/config/sandbox.json` 中的 `identifier` 字段

询问用户的个人 **misId**（不可省略，每人不同），然后执行脚本获取 cookie：

```bash
# 在 skill 目录下执行，SKILL_DIR 替换为实际路径
CATPAW_COOKIE=$(bash $SKILL_DIR/scripts/get-catpaw-cookie.sh <用户的misId>)
```

脚本执行流程：
1. 发起 CIBA 认证请求，获取 `auth_req_id`
2. 轮询等待用户在**大象 App** 上确认授权（每 5 秒一次，最多 3 分钟）
3. 用 `access_token` 换取 ssoid cookie
4. 将 cookie 以 `1d47d6ff96_ssoid=<value>` 格式输出

#### 步骤 2：设置 CATPAW_CONFIG_CONTENT

将 cookie 和客户端信息统一写入 `CATPAW_CONFIG_CONTENT` 环境变量：

```bash
export CATPAW_CONFIG_CONTENT='{"source":"CatClaw","cookie":"'"$CATPAW_COOKIE"'","misId":"<用户的misId>"}'
```

> **说明**：`CATPAW_CONFIG_CONTENT` 是一个 JSON 字符串，包含以下字段：
> - `source`：客户端来源标识
> - `cookie`：认证 cookie（即步骤 1 获取的值）
> - `misId`：用户的个人 misId

### 4. 配置 acpx

初始化 acpx 配置文件：

```bash
acpx config init
```

然后在生成的配置文件中的 `agents` 字段中添加 catpaw：

```json
{
  "defaultAgent": "catpaw",
  "defaultPermissions": "approve-all",
  "nonInteractivePermissions": "deny",
  "authPolicy": "skip",
  "ttl": 300,
  "timeout": null,
  "format": "text",
  "agents": {
    "catpaw": {
      "command": "catpaw-cli acp"
    }
  },
  "auth": {}
}
```

## 使用方式

### 基本流程

使用 CatPaw 分为两步：**创建会话** → **在会话中对话**。

#### 步骤 1：创建会话

建议先切换到目标项目目录，再创建会话，这样 CatPaw 可以感知项目上下文：

```bash
cd /你的项目目录
acpx catpaw sessions new
```

也可以为会话指定名称，方便管理多个会话：

```bash
acpx catpaw sessions new --name my-project
```

#### 步骤 2：在会话中对话

会话创建后，通过 `acpx catpaw` 或 `acpx catpaw prompt` 发送消息，会话会持续保持上下文：

```bash
# 直接对话（在当前 session 中）
acpx catpaw "创建一个新的 Vue 组件"

# 等价写法
acpx catpaw prompt "创建一个新的 Vue 组件"

# 使用命名会话对话
acpx catpaw -s my-project "添加表单验证逻辑"
```

> **提示**：`acpx catpaw exec` 是一次性执行模式，不会创建或复用会话，适合快速执行单个独立任务。多轮协作开发请使用上述会话模式。

### 会话管理

```bash
# 查看所有会话
acpx catpaw sessions list

# 查看当前会话详情
acpx catpaw sessions show

# 查看会话历史
acpx catpaw sessions history

# 关闭会话
acpx catpaw sessions close
```

### 示例

```bash
# 1. 进入项目目录并创建会话
cd ~/projects/my-app
acpx catpaw sessions new --name my-app

# 2. 多轮对话协作开发
acpx catpaw "创建一个 Vue3 登录页面，包含用户名、密码输入框和登录按钮"
acpx catpaw "给登录表单添加表单验证"
acpx catpaw "为登录组件添加单元测试"

# 3. 完成后关闭会话
acpx catpaw sessions close
```

## 常用场景

| 场景 | 命令 |
|------|------|
| 创建新项目 | `acpx catpaw "创建一个 React + TypeScript 项目"` |
| 添加组件 | `acpx catpaw "添加一个 Header 组件"` |
| 代码审查 | `acpx catpaw "审查这段代码并提出改进建议"` |
| 调试问题 | `acpx catpaw "帮我调试这个报错：..."` |
| 写测试 | `acpx catpaw "为这个模块编写测试用例"` |
| 快速单次任务 | `acpx catpaw exec "这个函数的作用是什么"` |

## 注意事项

1. **首次配置**：首次使用需获取 cookie 并配置 `CATPAW_CONFIG_CONTENT` 环境变量，其中 cookie 会过期，需在过期后重新获取并更新
2. **工作目录**：建议在目标项目目录下执行，这样 CatPaw 可以感知项目上下文
3. **交互模式**：CatPaw 会自动执行代码操作，无需手动确认

## 故障排查

### 认证失败
```
Error: ssoid 不存在
```
解决：重新获取 cookie 并更新 `CATPAW_CONFIG_CONTENT`：
```bash
CATPAW_COOKIE=$(bash $SKILL_DIR/scripts/get-catpaw-cookie.sh <用户的misId>)
export CATPAW_CONFIG_CONTENT='{"source":"CatClaw","cookie":"'"$CATPAW_COOKIE"'","misId":"<用户的misId>"}'
```