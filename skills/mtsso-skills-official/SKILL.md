---
name: mtsso-skills-official
description: 企平应用平台官方 SSO 技能，定义了跨 Skill 的身份鉴权统一协作契约（占位符语义、令牌获取、缓存、安全和错误处理）。如果依赖方 Skill 的自定义逻辑与本技能冲突，必须以本技能为准。除此以外，还提供了几个基础工具：获取应用身份票据（ClientCredentials）、票据交换（TokenExchange）、票据解析（IntrospectToken）、获取本地MOA用户身份（MoaLocalExchange）。当需要获取 SSO token、应用身份票据、用户身份票据、token 换票、introspect、MOA 鉴权时使用。

metadata:
  skillhub.creator: "suweijie02"
  skillhub.updater: "suweijie02"
  skillhub.version: "V10"
  skillhub.source: "FRIDAY Skillhub"
  skillhub.skill_id: "6556"
  skillhub.high_sensitive: "false"
---

# MTSSO 统一认证鉴权协作技能

本技能提供统一的认证鉴权协作上下文，用于帮助三方 Skill 在执行命令时自动完成 access_token 的识别、申请、注入、复用与安全控制，从而显著降低接入成本。

本技能包含 4 个标准 CLI 工具：既是技能内部依赖，也可以直接作为排障和调试工具使用。

## 工具索引

| 工具标识符 | CLI 命令 | 核心能力 |
|---|---|---|
| `mtsso:ClientCredentials` | `npx mtsso-client-credentials` | 获取应用身份 access_token |
| `mtsso:TokenExchange` | `npx mtsso-token-exchange` | 将已有 subject_token 换发为目标 audience 的 access_token |
| `mtsso:IntrospectToken` | `npx mtsso-introspect-token` | 解析 token 有效性与主体、受众、empId、过期时间等字段 |
| `mtsso:MoaLocalExchange` | `npx mtsso-moa-local-exchange` | 基于本机 MOA 登录态，一步换发目标 audience 的用户身份 access_token |

## 阅读顺序与优先级

- 第 1 章是跨 Skill 协作契约，优先级最高。
- 任何三方 Skill 通过 `skill-dependencies` 依赖本技能时，必须遵循第 1 章。
- 第 2 至第 5 章是工具路由、执行和排障细则；若与第 1 章冲突，以第 1 章为准。

## 术语（精简版）

- `subject`：token 的主体，对应 `sub` 字段。可表示应用身份，也可表示用户身份。
- `audience`：token 的受众，对应 `aud` 字段，取值为一个或多个 `client_id`。
- `用户身份票据`：历史上也称 `ssoid`，本质是 `mt_subject_type=ACCOUNT` 的 access_token。
- `empId`：账号标识，对应 token 的 `mt_empId` 字段。该字段是历史命名，实际表示账号标识，不等同于员工工号。
- `代理链`：对应 `act` 字段，用于表示多级代理关系。

## 1. 平台级协作规范（最高优先级）

### 1.1 适用范围

- 适用于所有在 `skill-dependencies.mtsso-skills-official` 下声明依赖的 Skill。
- 本章定义统一的占位符语义、取票流程、缓存、安全和错误处理规则。
- 依赖方 Skill 的自定义逻辑与本章冲突时，必须以本章为准。

### 1.2 占位符触发规则

- 发现 `${app_access_token}`：触发应用身份票据获取流程。本流程获取到的实际票据是${AGENT_SSO_CLIENT_ID}的应用身份access_token
- 发现 `${user_access_token}`：触发用户身份票据获取流程。本流程获取到实际票据是沙箱本地用户身份的access_token
- 两者都未出现：跳过，不发起任何 SSO 调用。
- 若依赖方 Skill 先生成命令模板，模型应在“实际执行前”再获取票据并替换占位符（延迟触发）。

### 1.3 audience 获取规则

- audience 来源：`skill-dependencies.mtsso-skills-official.audience`。
- 执行命令时使用空格拼接，例如：`"client_a client_b"`。
- audience 必须声明且不能为空。
- audience 最多 5 个 `client_id`，超过 5 个必须报错终止。

### 1.4 票据获取流程

#### 应用身份票据（`${app_access_token}`）

```bash
npx mtsso-client-credentials --audience "<audience_list>"
```

- 凭据由平台通过系统预置文件或环境变量注入（`AGENT_SSO_CLIENT_ID`、`AGENT_SSO_CLIENT_SECRET`），无需强制显式传参。
- 成功后提取 `.access_token`，替换命令中的 `${app_access_token}`。

#### 用户身份票据（`${user_access_token}`）

```bash
npx mtsso-moa-local-exchange --audience "<audience_list>"
```

- 依赖本机 MOA 登录态和本地 WebSocket Secure 连接。
- 失败时必须给出明确提示：
  `用户身份票据获取失败：本机 MOA 未登录或不可用，请确认 MOA 已启动并完成登录后重试`
- 成功后提取 `.access_token`，替换命令中的 `${user_access_token}`。

### 1.5 会话级缓存（建议）

缓存仅允许在“票据类型 + 完全相同 audience 集合（排序后等价）”时复用。

- 缓存键格式：`<ticket_type>:<audience_hash>`
- `ticket_type`：`app_ticket` 或 `user_ticket`
- `audience_hash`：对排序后的 audience 列表计算 MD5 或 SHA256

复用规则：

- 执行前按 audience 集合计算缓存键。
- 缓存建议设置的有效期不超过 2 小时，一般通过本技能获得的票据 3 小时就会过期。

### 1.6 错误处理（必须）

| 错误场景 | 处理行为 |
|---|---|
| `npx mtsso-client-credentials` 返回非 0 | 报错终止，并输出 `stderr` 摘要 |
| `npx mtsso-moa-local-exchange` 本地 WebSocket Secure 连接失败 | 报错终止，并提示 MOA 未登录或不可用 |
| audience 未声明或为空 | 报错终止，提示开发者检查 Skill 配置 |
| audience 超过 5 个 | 报错终止，提示最多支持 5 个 `client_id` |
| 提取 `.access_token` 为空 | 报错终止，提示检查凭据与环境是否匹配 |

### 1.7 安全约束（必须）

- token 仅可用于替换当前命令中的占位符，不得输出到日志、回复或其他用户可见位置。
- 缓存 token 仅在当前会话有效，会话结束后必须清除。
- 严禁泄露 `client_secret`、`access_token`、`subject_token`。

### 1.8 最小注入执行顺序

1. 先生成业务命令（允许保留占位符）。
2. 用户确认执行后，再按占位符触发取票。
3. 提取 `.access_token` 并替换全部占位符。
4. 执行替换后的命令；后续同会话、同缓存键请求可复用缓存。

## 2. 工具路由与参数契约

### 2.0 安装与自动修复策略（重要）

- 建议模型先直接执行目标命令，例如：`npx mtsso-moa-local-exchange --audience "mtsso"`。
- 若不确定参数或用法，先执行 `npx <command> --help` 查看当前版本说明（注意是 `--help`，不是 `--hlep`）。
- 会话首次执行任一 `mtsso-*` 命令前，先检查镜像最新版本：`npm view @mtfe/mtsso-auth-official version --registry=http://r.npm.sankuai.com --prefer-online`。
- 若本地未安装或版本低于最新版本，自动执行安装命令：`npm install @mtfe/mtsso-auth-official@latest --registry=http://r.npm.sankuai.com`（本包仓库镜像）。
- 若命令执行报不存在（如 `command not found`、`not found`、`could not determine executable to run`），自动执行同一安装命令后重试原命令。
- 若版本检查失败，不阻断主流程：继续执行原命令；仅在命令不存在时触发自动安装。
- 安装成功后立即重试原命令；若仍失败，再按第 4 章排障。
- 除非用户显式禁止，不要先询问是否安装。

### 2.1 意图路由（先选命令）

- 获取应用身份 token：使用 `npx mtsso-client-credentials`
- 将已有 `subject_token` 换发到新 audience：使用 `npx mtsso-token-exchange`
- 解析 token 是否有效及关键字段：使用 `npx mtsso-introspect-token`
- 本地 MOA 已登录，一步获取目标 audience 的用户 token：使用 `npx mtsso-moa-local-exchange`

### 2.2 默认决策规则（重要）

当用户表达“应用 A 调用应用 B / 签发给 B”，但没有明确要求 Token Exchange 时：

- 默认优先：`npx mtsso-client-credentials --audience "<APP_B_CLIENT_ID>"`
- 不要默认走“先给自己发 token，再 npx mtsso-token-exchange”两跳链路
- 仅在以下场景优先使用 `npx mtsso-token-exchange`：
  - 用户明确提出“换票”或“Token Exchange”
  - 用户已提供 `subject_token`
  - 需要跨主体或跨来源迁移 token

当用户表达“获取应用身份票据”，但没有指定对象/audience时，可以直接调用 `npx mtsso-client-credentials`，获取一张给自己的票据。

### 2.3 凭据解析与环境一致性

- 在向用户追问 `client_id`、`client_secret` 之前，必须先检查（一定不要直接追问！！！）：
  - `/root/.openclaw/sso/agent_info`
  - 环境变量 `AGENT_SSO_CLIENT_ID`、`AGENT_SSO_CLIENT_SECRET`、`MTSSO_ENV`
- 统一优先级：
  1. 命令行参数（`-e/--env`、`--client_id`、`--client_secret`）
  2. `/root/.openclaw/sso/agent_info`（注意：通常在未显式传入 `--client_id` 时参与回退）
  3. 环境变量（`MTSSO_ENV`、`AGENT_SSO_CLIENT_ID`、`AGENT_SSO_CLIENT_SECRET`）
- 若三层都未提供环境值，默认 `PROD`；不会自动填充默认凭据。
- 仅当三层都缺失且无法继续执行时，才向用户说明缺失字段。
- 当环境为 `TEST`（`MTSSO_ENV=TEST` 或 `-e TEST`）时，凭据必须同步使用 TEST 凭据，禁止 TEST 和 PROD 混用。

### 2.4 四个命令的输入输出契约

| 命令 | 必需输入 | 常用可选参数                                 | 成功输出 | 失败行为 |
|---|---|----------------------------------------|---|---|
| `npx mtsso-client-credentials` | `--client_id`、`--client_secret`（可走回退解析） | `--audience`、`-e/--env`、`-v`、`-h`、`-H` | token JSON（包含 `access_token`） | 返回非 0；很多场景仅 `stderr` 有错误，`stdout` 可能无可用 JSON |
| `npx mtsso-token-exchange` | `--client_id`、`--client_secret`、`--audience`、`--subject_token`（client 参数可回退） | `-e/--env`、`-v`、`-h`、`-H`                   | token JSON（包含 `access_token`） | 返回非 0；端点返回错误 JSON 时，`stdout` 仍可能有 JSON，同时 `stderr` 给摘要 |
| `npx mtsso-introspect-token` | `--client_id`、`--client_secret`、`--token`（client 参数可回退） | `-e/--env`、`-v`、`-h`、`-H`                   | introspection JSON | 返回非 0；端点返回错误 JSON 时，`stdout` 仍可能有 JSON，同时 `stderr` 给摘要 |
| `npx mtsso-moa-local-exchange` | `--client_id`、`--client_secret`、`--audience`（client 参数可回退） | `-e/--env`、`-v`、`-h`、`-H`                   | 最终 `npx mtsso-token-exchange` 返回的 JSON | 本地 WebSocket Secure 阶段失败多为 `stderr`；末段失败时可能透传错误 JSON + `stderr` |

补充约束：

- `--audience` 最多 5 个，多个值必须整体加引号，例如：`"appA appB"`
- `--help` 的退出码为 `2`，属于正常行为
- 默认静默模式（不加 `-v`），仅在排障时加 `-v`

### 2.5 四组通用参数速查

- `-h, --help`：显示完整参数与示例，若大模型需了解指令更多或更详细用法，请执行 `npx <command> --help`。
- `-e, --env <PROD|TEST>`：指定运行环境；不传默认 `PROD`。若使用 `TEST`，必须配套 TEST 凭据，禁止与 PROD 凭据混用。
- `-v, --verbose`：开启详细日志（通常输出到 `stderr`），用于排障定位；常规调用建议保持默认静默。
- `-H, --header "K: V"`：追加自定义请求头，可多次传入；常用于链路追踪、灰度标记或上游要求的扩展头。

## 3. 串联规则（避免 subject_token 传参错误）

### 3.1 只传 token 字段，不传整段 JSON

- `npx mtsso-token-exchange --subject_token` 需要 token 字符串。
- `npx mtsso-introspect-token --token` 需要 token 字符串。
- 不要把完整 JSON 直接传给这两个参数。

### 3.2 推荐提取模板

```bash
token_response="$(npx mtsso-client-credentials --audience "$TARGET_CLIENT_ID")" || exit 1
subject_token="$(echo "$token_response" | jq -r '.access_token // empty')"
[ -n "$subject_token" ] || { echo "错误: 请传 access_token 字段而非完整 JSON" >&2; exit 1; }
npx mtsso-token-exchange --audience "$TARGET_CLIENT_ID" --subject_token "$subject_token"
```

## 4. 排障速查

| 现象 | 常见原因 | 建议动作 |
|---|---|---|
| `invalid subject_token` 或 `can not find token format` | 把完整 JSON 传给了 `--subject_token` | 先提取 `.access_token` 再传入 |
| `--audience 最多支持 5 个 client_id` | audience 数量超限 | 拆分为多次调用，不要自动截断 |
| 返回非 JSON 或 endpoint 调用失败 | 网络异常、环境不匹配、上游异常 | 加 `-v` 重试，并核对环境与凭据一致性 |
| 已切到 TEST 但仍使用 PROD 凭据 | 高频配置错误 | 同步替换为 TEST 凭据后重试 |
| `npx mtsso-*` 命令不存在 | 本地尚未安装工具包 | 自动执行 `npm install @mtfe/mtsso-auth-official@latest --registry=http://r.npm.sankuai.com` 后重试原命令 |
| `npx mtsso-client-credentials` 失败且无可解析 stdout JSON | 错误信息主要在 `stderr` | 先检查退出码，再查看 `stderr` |
| 本地 WebSocket Secure 连接失败 | 本机 MOA 未登录或不可用 | 启动并登录 MOA 后重试 |

## 5. 最小执行规范

- 先检查退出码，再解析 `stdout` JSON。
- 建议模型在会话首次调用 `mtsso-*` 前先执行 `npm view @mtfe/mtsso-auth-official version --registry=http://r.npm.sankuai.com --prefer-online` 检查最新版本；非首次仍先直接执行命令。
- 若本地缺失或版本落后，自动运行 `npm install @mtfe/mtsso-auth-official@latest --registry=http://r.npm.sankuai.com` 后执行（或重试）原命令。
- 若参数不确定，先执行 `npx <command> --help` 获取当前版本的完整参数说明（注意拼写为 `--help`）。
- 涉及三方 Skill 的 token 占位符注入时，先执行第 1 章，再执行本章细则。
- 命令串联时，统一执行 token 字段提取与空值校验。
- 需要验证 token 是否有效（例如 `active`）时，必须调用 `npx mtsso-introspect-token`。
- 仅查看 payload 字段时可以做 Base64 解码，但不能替代 introspection 做鉴权判断。

## 6. 依赖声明最小示例

```yaml
---
name: calendar-skill
skill-dependencies:
  mtsso-skills-official:
    user_access_token_placeholder: ${user_access_token}
    audience:
      - calendar_skill_001
      - mt_calendar_service
---
```

执行要点：

1. 先生成业务命令（可保留 `${user_access_token}`）。
2. 执行前读取依赖配置中的 audience。
3. 调用 `npx mtsso-moa-local-exchange` 获取 token，提取 `.access_token`。
4. 替换占位符后执行命令；同会话同 audience 集合可按缓存规则复用。
