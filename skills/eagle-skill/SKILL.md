---
name: eagle-skill
description: |
  Eagle/Elasticsearch 集群管理助手。当用户需要查看 ES 集群状态、索引信息、排查问题或管理权限时触发此 skill。

  提供功能：
  - 集群管理：查看集群列表、元数据、容量、节点信息、配置
  - 索引管理：查看/创建/更新/删除索引，开关、批量操作、别名、迁移、Shrink/Split
  - 模板管理：查看/创建/更新/删除模板，慢查询配置
  - 快照管理：创建/删除仓库，创建/恢复/删除 Snapshot
  - 插件管理：添加/删除/安装/卸载插件
  - 限流管理：创建/更新/删除限流任务，模板查询限流
  - 别名管理：查看集群别名
  - 权限管理：查看/申请/删除 ES 权限，更新 Owner
  - 文档搜索：执行 ES DSL 查询、专家搜索、SQL 搜索
  - 慢查询分析：查看慢日志、统计分析
  - 指标监控：集群健康趋势、Top 慢查询、实时指标
  - 诊断分析：查看诊断报告
  - 环境切换：支持生产/测试/海外多环境

  触发场景：
  - "查看 ES 集群状态"
  - "列出所有索引"
  - "搜索集群 xxx"
  - "查看慢查询"
  - "切换环境到测试"
  - "查看索引模板"
  - "我有 ES 集群问题"
  - "创建/删除索引"
  - "管理快照"
  - "配置限流"
allowed-tools: Bash(eagle:*)
compatibility: Require @mtfe/eagle-cli@^1.2.0 of registry http://r.npm.sankuai.com installed.

metadata:
  skillhub.creator: "yinjiale"
  skillhub.updater: "yinjiale"
  skillhub.version: "V11"
  skillhub.source: "FRIDAY Skillhub"
  skillhub.skill_id: "5955"
  skillhub.high_sensitive: "false"
---

# Eagle/Elasticsearch 集群管理指南

## 简介

Eagle 是美团内部的 Elasticsearch 索引管理平台。本 skill 提供 Eagle 集群和索引的管理能力，包括：

- **SSO 认证**: 登录、登出、状态查看
- **环境管理**: 线上/线下/海外环境切换
- **集群管理**: 查看集群列表、元数据、容量、配置、版本、操作日志、分词器等
- **节点管理**: 查看节点列表、概览、详情，支持独立命令和集群子命令两种方式
- **索引管理**: 查看/创建/更新/删除索引；开关索引、批量操作、别名管理、迁移、Shrink/Split、数据变更
- **索引模板管理**: 查看/创建/更新/删除模板；慢查询配置
- **快照管理**: 创建/删除仓库，创建/恢复/删除 Snapshot
- **插件管理**: 添加/删除/安装/卸载插件
- **限流管理**: 创建/更新/删除限流任务，模板查询限流
- **别名管理**: 查看集群别名和原始别名列表
- **Appkey 管理**: 查看 Appkey 权限、IDC 分布、关联集群组等
- **权限认证**: 查看/申请/删除 ES 权限，更新 Owner
- **文档搜索**: 支持专家模式、Profile、简单搜索和 SQL 搜索
- **慢日志管理**: 查看慢日志列表、详情、配置等
- **实时监控**: 查看索引和节点的实时统计信息
- **大盘监控**: 查看系统指标、服务器概览、历史趋势、资源分布和集群状态
- **指标监控**: 查看集群各项指标排行（慢查询、QPS、文档数、磁盘使用率等）
- **诊断分析**: 获取集群诊断报告列表

> **工具依赖**: 本 skill 使用 `eagle` CLI 工具作为执行载体。如未安装，参考下方安装说明。

---

## 环境说明

Eagle CLI 支持三套环境：
- **线上（prod）**：`https://es.sankuai.com`，默认环境
- **线下（test）**：`http://es.platsearch.test.sankuai.com`，通过 `--env test` 指定
- **海外（overseas）**：`https://es.inf.keetapp.com`，通过 `--env overseas` 指定，用于访问欧洲等海外集群

### 集群名称环境确认流程（强制执行）

**每当用户给出一个集群名称时，必须按以下步骤逐步确认集群所在环境，再执行后续操作。**

> ⚠️ **关键约束**：
> - **禁止用 `eagle cluster list` 判断集群是否存在**，因为它有分页，结果不完整
> - **切换环境必须重新登录**：`eagle sso login`（线上）或 `eagle sso login --env test`（线下）或 `eagle sso login --env overseas`（海外）
> - `--env` 参数**不能**跨越当前登录环境查询，必须先登录对应环境再查询

#### 第一步：在当前登录环境查询

先用 `eagle sso status` 确认当前环境，然后执行：

```bash
eagle cluster describe <cluster-name> 2>&1
```

- **成功**：集群在当前环境，直接继续
- **失败（集群不存在）**：进入第二步，切换环境查询
- **失败（sso auth failed）**：需要先登录，执行 `eagle sso login` 或 `eagle sso login --env test`

#### 第二步：切换到另一个环境查询

若当前是线上环境，先切换到线下：
```bash
eagle sso login --env test
eagle cluster describe <cluster-name> 2>&1
```

若线下也不存在，尝试海外环境：
```bash
eagle sso login --env overseas
eagle cluster describe <cluster-name> 2>&1
```

#### 第三步：根据结果决定行为

| 线上存在 | 线下存在 | 海外存在 | 行为 |
|----------|----------|----------|------|
| ✅ | ❌ | ❌ | 保持/切换到线上环境，直接继续 |
| ❌ | ✅ | ❌ | 保持/切换到线下环境，直接继续 |
| ❌ | ❌ | ✅ | 保持/切换到海外环境，直接继续 |
| ✅ | ✅ | ❌ | **必须用 AskUserQuestion 询问用户**，等待明确选择后再登录对应环境继续 |
| ✅ | ❌ | ✅ | **必须用 AskUserQuestion 询问用户**，等待明确选择后再登录对应环境继续 |
| ❌ | ✅ | ✅ | **必须用 AskUserQuestion 询问用户**，等待明确选择后再登录对应环境继续 |
| ✅ | ✅ | ✅ | **必须用 AskUserQuestion 询问用户**，等待明确选择后再登录对应环境继续 |
| ❌ | ❌ | ❌ | 告知用户集群不存在，可建议用 `eagle cluster list -n <keyword>` 搜索相近名称 |

#### 多个环境都存在时，询问示例

> 集群 `<name>` 在多个环境都存在，请问您要查询哪个环境？
> - 线上环境（prod）
> - 线下环境（test）
> - 海外环境（overseas）

**在用户明确选择之前，不得执行任何后续命令。**

### 变更操作确认

涉及创建、修改、删除等变更操作时，执行前需单独确认：

> 此操作将对**[线上/线下/海外]环境**执行变更，确认继续吗？

---

## 安装前提

### 1. 安装 @mtfe/eagle-cli

```bash
# 全局安装（推荐）
npm install -g @mtfe/eagle-cli --registry=http://r.npm.sankuai.com

# 项目内安装
npm install @mtfe/eagle-cli --save-dev --registry=http://r.npm.sankuai.com
```

### 2. 验证安装

```bash
# 检查命令是否可用
which eagle

# 查看版本
eagle --version

# 查看帮助
eagle --help
```

### 3. 环境要求

- **Node.js**: >= 14.0.0
- **npm**: >= 6.0.0
- **网络**: 需要访问美团内网（SSO 认证和 API 调用）

### 4. 常见问题

**Q: 运行 `eagle` 提示 `command not found`**

原因：使用了本地安装（`npm install`）而不是全局安装（`npm install -g`）

解决方案：
```bash
# 方案 1：改用全局安装（推荐）
npm install -g @mtfe/eagle-cli --registry=http://r.npm.sankuai.com

# 方案 2：使用 npx 运行
npx eagle --version

# 方案 3：使用完整路径
./node_modules/.bin/eagle --version
```

**Q: 需要 sudo 权限吗？**

- 使用 nvm 管理 Node.js：❌ **不需要** sudo
- 系统安装的 Node.js：✅ 可能需要 sudo

---

## 快速开始

### 1. 登录
```bash
eagle sso login              # 默认登录线上环境
eagle sso login --env test   # 登录线下环境
eagle sso login --env overseas # 登录海外环境
eagle sso login --mis yinjiale # 支持mis参数
```

### 2. 查看集群列表
```bash
eagle cluster list
```

### 3. 查看集群详情
```bash
eagle cluster describe <cluster-name>
```

### 4. 查看索引列表
```bash
eagle index list <cluster-name>
```

---

## 功能模块

### SSO 认证管理

| 命令 | 说明 |
|------|------|
| `eagle sso login` | SSO 登录（默认 prod 环境） |
| `eagle sso login --env <env>` | 指定环境登录（prod/test/overseas） |
| `eagle sso logout` | 退出登录 |
| `eagle sso status` | 查看登录状态 |

**环境切换说明**：
- 环境只能通过 `eagle sso login --env <env>` 切换
- 不提供 `--env` 时默认使用 prod 环境
- `eagle env set` 命令已禁用

### 环境管理

| 命令 | 说明 |
|------|------|
| `eagle env show` | 查看当前登录环境（只读） |

### 集群管理

| 命令 | 别名 | 说明 |
|------|------|------|
| `eagle cluster list` | `eagle cl ls` | 列出集群 |
| `eagle cluster describe <name>` | `eagle cl desc` | 查看集群实时元数据 |
| `eagle cluster static <name>` | `eagle cl st` | 查看集群静态元数据 |
| `eagle cluster capacity <name>` | `eagle cl cap` | 查看集群容量概况 |
| `eagle cluster owner <name>` | `eagle cl o` | 查看集群 Owner |
| `eagle cluster user <name>` | `eagle cl u` | 查看集群 User |
| `eagle cluster configs <name>` | `eagle cl cfg` | 查看集群配置 |
| `eagle cluster dynamic-config <name>` | `eagle cl dc` | 查看集群动态配置 |
| `eagle cluster es-version <name>` | `eagle cl ver` | 查看集群 ES 版本 |
| `eagle cluster appkeys <name>` | `eagle cl app` | 查看集群相关 Appkeys |
| `eagle cluster name-list` | `eagle cl nl` | 列出所有集群名称 |
| `eagle cluster op-log <name>` | `eagle cl ol` | 查看集群操作日志 |
| `eagle cluster analyzers <name>` | `eagle cl az` | 查看分词器列表 |
| `eagle cluster falcon-url <name>` | `eagle cl falcon` | 获取 Falcon 监控 URL |
| `eagle cluster appkey-list` | `eagle cl akl` | 查看集群 Appkey 列表 |
| `eagle cluster list-advanced` | `eagle cl la` | 高级集群列表查询 |
| `eagle cluster operation-log` | `eagle cl oplog` | 查看集群操作日志（高级） |

**列表命令选项**:
- `-n, --name <name>` - 按集群名称过滤
- `-p, --page <page>` - 页码（默认 1）
- `-s, --size <size>` - 每页数量（默认 20）
- `--env <env>` - 指定环境（prod/test/overseas）

**高级列表选项**:
- `--type <type>` - 集群类型过滤
- `--search <keyword>` - 搜索关键词
- `--order <order>` - 排序方向
- `--sort <field>` - 排序字段
- `--show-all` - 显示所有集群

### 节点管理（独立命令）

| 命令 | 别名 | 说明 |
|------|------|------|
| `eagle node list <cluster>` | `eagle n ls` | 获取集群节点列表 |
| `eagle node overview <cluster>` | `eagle n ov` | 获取集群节点概览 |
| `eagle node detail <cluster> <ip>` | `eagle n d` | 获取节点详情 |
| `eagle node search <cluster>` | `eagle n s` | 搜索集群节点 |

**节点列表选项**:
- `--no-real-time` - 不使用实时数据
- `--search <keyword>` - 搜索关键词
- `-t, --type <type>` - 节点类型
- `--page-number <page>` - 页码
- `--page-size <size>` - 每页数量

### 集群节点子命令

| 命令 | 别名 | 说明 |
|------|------|------|
| `eagle cluster node list <name>` | `eagle cl n ls` | 查看节点列表 |
| `eagle cluster node overview <name>` | `eagle cl n ov` | 查看节点概览 |
| `eagle cluster node detail <name> <ip>` | `eagle cl n d` | 查看节点详情 |

### 索引管理

#### 查询命令

| 命令 | 别名 | 说明 |
|------|------|------|
| `eagle index list <cluster>` | `eagle idx ls` | 列出索引 |
| `eagle index name-list <cluster>` | `eagle idx nl` | 列出索引名称 |
| `eagle index original-name-list <cluster>` | `eagle idx onl` | 获取原始索引名称列表 |
| `eagle index describe <c> <i>` | `eagle idx desc` | 查看索引基本信息 |
| `eagle index stats <c> <i>` | `eagle idx st` | 查看索引统计信息 |
| `eagle index segments <c> <i>` | `eagle idx seg` | 查看索引段文件信息 |
| `eagle index json <c> <i>` | `eagle idx j` | 查看索引 JSON 信息 |
| `eagle index meta <c> <i>` | `eagle idx m` | 查看索引元信息 |
| `eagle index fields <c> <i>` | `eagle idx f` | 查看索引字段 |
| `eagle index types <c> <i>` | `eagle idx t` | 查看索引类型 |
| `eagle index auth <c> <i>` | - | 查看索引权限 |
| `eagle index appkey-auth <c> <i>` | `eagle idx app` | 查看索引 Appkey 权限 |
| `eagle index log <c> <i>` | `eagle idx lg` | 查看索引操作日志 |
| `eagle index monitor <c> <i>` | `eagle idx mon` | 获取索引监控配置 |

**列表命令选项**:
- `-n, --name <name>` - 按索引名称过滤
- `-a, --alias <alias>` - 按别名过滤
- `--all` - 显示所有索引（默认只显示我的索引）
- `-p, --page <page>` - 页码
- `-s, --size <size>` - 每页数量（默认 10）

#### 写操作命令（变更）

| 命令 | 别名 | 说明 |
|------|------|------|
| `eagle index create <c> <i>` | `eagle idx c` | 创建索引 |
| `eagle index update <c> <i>` | `eagle idx upd` | 通过 JSON 更新索引配置（先读后写） |
| `eagle index update-info <c> <i>` | `eagle idx ui` | 更新索引基本信息（先读后写） |
| `eagle index open <c> <i>` | `eagle idx op` | 打开索引 |
| `eagle index close <c> <i>` | `eagle idx cl` | 关闭索引 |
| `eagle index delete <c> <i>` | `eagle idx del` | 删除索引 |
| `eagle index batch-open <c>` | `eagle idx bop` | 批量打开索引 |
| `eagle index batch-close <c>` | `eagle idx bcl` | 批量关闭索引 |
| `eagle index batch-delete <c>` | `eagle idx bdel` | 批量删除索引 |
| `eagle index add-alias <c> <i> <alias>` | `eagle idx aa` | 添加索引别名 |
| `eagle index remove-alias <c> <i> <alias>` | `eagle idx ra` | 删除索引别名 |
| `eagle index transfer-alias <c> <i>` | `eagle idx ta` | 别名迁移 |
| `eagle index force-merge <c> <i>` | `eagle idx fm` | 强制段合并 |
| `eagle index flush <c> <i>` | `eagle idx fl` | Flush 索引 |
| `eagle index flush-all <c>` | `eagle idx fla` | Flush 全部索引 |
| `eagle index migrate <c> <i>` | `eagle idx mg` | 迁移索引到目标集群 |
| `eagle index shrink <c> <i>` | `eagle idx sk` | Shrink 索引（减少分片数） |
| `eagle index split <c> <i>` | `eagle idx sp` | Split 索引（增加分片数） |
| `eagle index data-change <c> <i>` | `eagle idx dc` | 按查询条件批量更新/删除数据 |
| `eagle index set-slowlog <c> <i>` | `eagle idx sl` | 更新索引慢查询阈值配置 |
| `eagle index set-monitor <c> <i>` | `eagle idx sm` | 设置索引监控开关 |

**创建/更新索引选项**:
- `--source <json>` - 索引配置 JSON 字符串
- `--file <path>` - 索引配置 JSON 文件路径
- `--appkeys <list>` - 关联的 appkey，逗号分隔（**创建时必填**）

**批量操作选项**:
- `--names <names>` - 索引名称列表，逗号分隔（**必填**）

**别名迁移选项**:
- `--alias <alias>` - 别名（**必填**）
- `--target <index>` - 目标索引名称（**必填**）

**迁移选项**:
- `--target-cluster <cluster>` - 目标集群名称（**必填**）

**Shrink/Split 选项**:
- `--target <name>` - 目标索引名称（**必填**）
- `--shards <num>` - 目标分片数（Split 时**必填**）

**数据变更选项**:
- `--op <update|delete>` - 操作类型（**必填**）
- `--query <json>` - 查询条件 JSON（**必填**）
- `--script <json>` - 更新脚本 JSON（op=update 时使用）

**慢查询配置选项**:
- `--search-threshold <ms>` - 搜索慢查询阈值（毫秒）
- `--index-threshold <ms>` - 写入慢查询阈值（毫秒）

**监控设置选项**:
- `--enabled <true|false>` - 是否启用监控（**必填**）
- `--type <type>` - 监控类型

> 所有变更命令若服务端返回工单，会自动打印审批链接。

### 索引模板管理

#### 查询命令

| 命令 | 别名 | 说明 |
|------|------|------|
| `eagle template list <cluster>` | `eagle tpl ls` | 列出索引模板 |
| `eagle template name-list <cluster>` | `eagle tpl nl` | 列出模板名称 |
| `eagle template meta <c> <t>` | `eagle tpl m` | 查看模板元信息 |
| `eagle template json <c> <t>` | `eagle tpl j` | 查看模板 JSON |
| `eagle template related-indices <c> <t>` | `eagle tpl ri` | 查看模板关联索引 |
| `eagle template slowlog-config <c> <t>` | `eagle tpl sc` | 查看慢日志配置 |
| `eagle template log <c> <t>` | `eagle tpl l` | 查看模板操作日志 |
| `eagle template monitor <c> <t>` | `eagle tpl mon` | 查看模板监控信息 |

#### 写操作命令（变更）

| 命令 | 别名 | 说明 |
|------|------|------|
| `eagle template create <c> <t>` | `eagle tpl c` | 创建索引模板 |
| `eagle template update <c> <t>` | `eagle tpl upd` | 通过 JSON 更新模板（先读后写） |
| `eagle template delete <c> <t>` | `eagle tpl del` | 删除索引模板 |
| `eagle template set-slowlog <c> <t>` | `eagle tpl sl` | 更新模板慢查询阈值配置（先读后写） |

**创建/更新模板选项**:
- `--source <json>` - 模板配置 JSON 字符串
- `--file <path>` - 模板配置 JSON 文件路径
- `--appkeys <list>` - 关联的 appkey，逗号分隔（**创建时必填**）
- `--type <type>` - 模板类型: DEFAULT / COMPOSABLE（默认 DEFAULT）

**慢查询配置选项**:
- `--search-threshold <ms>` - 搜索慢查询阈值（毫秒）
- `--index-threshold <ms>` - 写入慢查询阈值（毫秒）
- `--type <type>` - 模板类型

### 快照管理

| 命令 | 别名 | 说明 |
|------|------|------|
| `eagle snapshot repo-create <c> <repo>` | `eagle snap rc` | 创建快照仓库 |
| `eagle snapshot repo-delete <c> <repo>` | `eagle snap rd` | 删除快照仓库 |
| `eagle snapshot create <c> <repo> <snap>` | `eagle snap c` | 创建 Snapshot |
| `eagle snapshot delete <c> <repo> <snap>` | `eagle snap del` | 删除 Snapshot |
| `eagle snapshot restore <c> <repo> <snap>` | `eagle snap rs` | 从 Snapshot 恢复数据 |

**创建仓库选项**:
- `--settings <json>` - 仓库配置 JSON

**创建 Snapshot 选项**:
- `--indices <indices>` - 索引列表，逗号分隔（不填则备份全部）
- `--ignore-unavailable` - 忽略不可用索引
- `--include-global-state` - 包含全局状态

**恢复 Snapshot 选项**:
- `--indices <indices>` - 恢复的索引列表，逗号分隔
- `--ignore-unavailable` - 忽略不可用索引
- `--include-global-state` - 包含全局状态
- `--rename-pattern <pattern>` - 重命名匹配模式（正则）
- `--rename-replacement <str>` - 重命名替换字符串

### 插件管理

| 命令 | 别名 | 说明 |
|------|------|------|
| `eagle plugin add <plugin-name>` | `eagle plg a` | 添加插件 |
| `eagle plugin delete <c> <plugin-id>` | `eagle plg del` | 删除插件 |
| `eagle plugin install <c> <plugin-id>` | `eagle plg ins` | 在集群上安装插件 |
| `eagle plugin uninstall <c> <plugin-id>` | `eagle plg uni` | 从集群卸载插件 |

**添加插件选项**:
- `--cluster <name>` - 关联集群名称
- `--url <url>` - 插件下载 URL
- `--type <type>` - 插件类型
- `--desc <description>` - 插件描述

### 限流管理

| 命令 | 别名 | 说明 |
|------|------|------|
| `eagle ratelimit create <c>` | `eagle rl c` | 创建限流任务 |
| `eagle ratelimit update <c>` | `eagle rl upd` | 更新限流任务（先读后写） |
| `eagle ratelimit delete <c> <id>` | `eagle rl del` | 删除限流任务 |
| `eagle ratelimit reorder <c>` | `eagle rl ro` | 调整限流任务优先级顺序 |
| `eagle ratelimit add-query-limit <c> <appkey>` | `eagle rl aql` | 为 Appkey 添加模板查询限流 |
| `eagle ratelimit update-query-limit <c> <appkey>` | `eagle rl uql` | 修改 Appkey 的模板查询限流 |
| `eagle ratelimit delete-query-limit <c> <appkey> <template-id>` | `eagle rl dql` | 删除 Appkey 的模板查询限流 |

**创建限流任务选项**:
- `--name <name>` - 任务名称（**必填**）
- `--priority <num>` - 优先级
- `--rate-limit <num>` - 限流值（QPS）
- `--condition <json>` - 限流条件 JSON

**更新限流任务选项**:
- `--id <id>` - 任务 ID（**必填**）
- `--name <name>` - 任务名称
- `--priority <num>` - 优先级
- `--rate-limit <num>` - 限流值（QPS）
- `--condition <json>` - 限流条件 JSON

**调整顺序选项**:
- `--ids <ids>` - 任务 ID 列表，按优先级从高到低逗号分隔（**必填**）

**模板查询限流选项**:
- `--template-id <id>` - 模板 ID（**必填**）
- `--rate-limit <num>` - 限流值 QPS（**必填**）

### 别名管理

| 命令 | 别名 | 说明 |
|------|------|------|
| `eagle alias name-list <cluster>` | `eagle al nl` | 列出集群别名 |
| `eagle alias original-alias-list <cluster>` | `eagle al oal` | 列出原始别名 |

**原始别名选项**:
- `--include-all` - 包含所有别名
- `--page-number <page>` - 页码
- `--page-size <size>` - 每页数量

### Appkey 管理

| 命令 | 别名 | 说明 |
|------|------|------|
| `eagle appkey auth-list` | `eagle ak al` | 获取 Appkey 权限列表 |
| `eagle appkey belongs-to-eagle <appkey>` | `eagle ak bte` | 检查 Appkey 是否属于 Eagle |
| `eagle appkey related-cluster-group <appkey>` | `eagle ak rcg` | 获取 Appkey 关联的集群组 |
| `eagle appkey idc-distribution <appkey>` | `eagle ak idc` | 获取 Appkey IDC 分布 |
| `eagle appkey client-version` | `eagle ak cv` | 获取集群关联客户端版本记录 |

**权限列表选项**:
- `-c, --cluster-name <name>` - 集群名称过滤
- `-a, --appkey <appkey>` - Appkey 过滤
- `-o, --owner <owner>` - 所有者过滤
- `--page-number <page>` - 页码
- `--page-size <size>` - 每页数量

**客户端版本选项**:
- `-c, --cluster-name <name>` - 集群名称（**必填**）
- `--client-type-str <type>` - 客户端类型
- `-a, --appkey <appkey>` - Appkey 过滤

### 权限认证

| 命令 | 别名 | 说明 |
|------|------|------|
| `eagle auth es-list` | `eagle auth el` | 获取 ES 权限列表 |
| `eagle auth system-list <resource> <type>` | `eagle auth sl` | 获取系统权限列表 |
| `eagle auth apply` | `eagle auth ap` | 申请 ES 权限 |
| `eagle auth delete <id>` | `eagle auth del` | 删除 ES 权限 |
| `eagle auth update-owner <id> <owner>` | `eagle auth uo` | 更新 ES 权限 Owner |

**ES 权限查询选项**:
- `-c, --cluster-name <name>` - 集群名称
- `-i, --index-name <name>` - 索引名称
- `-t, --template-name <name>` - 模板名称
- `-u, --user <user>` - 用户名

**申请权限选项**:
- `--cluster <name>` - 集群名称（**必填**）
- `--index <name>` - 索引名称
- `--template <name>` - 模板名称
- `--appkey <appkey>` - Appkey
- `--privilege <type>` - 权限类型（READ/WRITE/MANAGE）
- `--reason <reason>` - 申请原因

### 文档搜索

| 命令 | 别名 | 说明 |
|------|------|------|
| `eagle search expert [query]` | `eagle s e` | 专家模式搜索 |
| `eagle search profile` | `eagle s p` | Profile 搜索 |
| `eagle search simple` | `eagle s s` | 简单搜索 |
| `eagle search sql <cluster>` | - | SQL 搜索 |

**专家模式选项**:
- `-c, --cluster <cluster>` - 集群名称（**必填**）
- `-i, --index <index>` - 索引名称
- `-f, --file <path>` - 从文件读取查询

**Profile 选项**:
- `-c, --cluster <cluster>` - 集群名称（**必填**）
- `-i, --index <index>` - 索引名称（**必填**）
- `-q, --query <json>` - 查询 JSON（**必填**）

**简单搜索选项**:
- `-c, --cluster <cluster>` - 集群名称（**必填**）
- `-i, --index <index>` - 索引名称（**必填**）
- `-q, --query <query>` - 查询字符串（**必填**）
- `--from <offset>` - 起始偏移
- `--size <size>` - 返回数量

**SQL 选项**:
- `-s, --sql <sql>` - SQL 语句（**必填**）
- `--fetch-size <size>` - 每次获取数量

### 慢日志管理

| 命令 | 别名 | 说明 |
|------|------|------|
| `eagle slowlog node-list <cluster>` | `eagle sl nl` | 获取慢日志节点列表 |
| `eagle slowlog list` | `eagle sl ls` | 获取慢日志列表 |
| `eagle slowlog detail` | `eagle sl d` | 获取慢日志详情 |
| `eagle slowlog config <cluster>` | `eagle sl cfg` | 获取慢日志配置 |
| `eagle slowlog by-id <id>` | `eagle sl id` | 根据 ID 获取慢日志 |
| `eagle slowlog n-day-before <cluster> [day]` | `eagle sl ndb` | 获取 N 天前的慢日志统计 |
| `eagle slowlog within-n-day <cluster> [day]` | `eagle sl wnd` | 获取 N 天内的慢日志摘要 |

**慢日志列表选项**:
- `-c, --cluster-name <name>` - 集群名称（**必填**）
- `-i, --index-name <name>` - 索引名称
- `-n, --node-ip <ip>` - 节点 IP
- `--start-time <time>` - 开始时间
- `--end-time <time>` - 结束时间
- `-t, --slow-log-type <type>` - 慢日志类型
- `-p, --page <page>` - 页码
- `-s, --page-size <size>` - 每页数量

**慢日志详情选项**:
- `-c, --cluster-name <name>` - 集群名称（**必填**）
- `-i, --index-name <name>` - 索引名称（**必填**）
- `--start-time <time>` - 开始时间（**必填**）
- `--end-time <time>` - 结束时间（**必填**）
- `--shard-id <id>` - 分片 ID（**必填**）
- `--slow-log-type <type>` - 慢日志类型（**必填**）
- `--slow-log-id <id>` - 慢日志 ID（**必填**）

### 实时监控

| 命令 | 别名 | 说明 |
|------|------|------|
| `eagle realtime indices-stats <cluster>` | `eagle rt is` | 索引实时统计 |
| `eagle realtime node-stats <cluster>` | `eagle rt ns` | 节点实时统计 |

**索引统计选项**:
- `-i, --indices <indices>` - 指定索引（逗号分隔）
- `-t, --top <n>` - 显示 Top N

**节点统计选项**:
- `-n, --nodes <nodes>` - 指定节点（逗号分隔）
- `-t, --top <n>` - 显示 Top N

### 大盘监控

| 命令 | 别名 | 说明 |
|------|------|------|
| `eagle dashboard system-metric` | `eagle db sm` | 系统指标大盘 |
| `eagle dashboard server-overview <range>` | `eagle db so` | 服务器概览 |
| `eagle dashboard history-trend <range>` | `eagle db ht` | 历史趋势 |
| `eagle dashboard res-dist <range> <type>` | `eagle db rd` | 资源分布统计 |
| `eagle dashboard cluster-status` | `eagle db cs` | 集群状态列表 |

**时间范围参数**: `1`=3天, `2`=7天, `3`=1月, `4`=6月, `5`=1年

### 指标监控

| 命令 | 别名 | 说明 |
|------|------|------|
| `eagle metrics cluster <name>` | `eagle m cl` | 集群监控指标 |
| `eagle metrics slow-query-avg` | `eagle m sqa` | 慢查询平均耗时 Top10 |
| `eagle metrics query-qps-avg` | `eagle m qqa` | 查询 QPS 平均 Top10 |
| `eagle metrics index-qps-avg` | `eagle m iqa` | 写入 QPS 平均 Top10 |
| `eagle metrics top-docs` | `eagle m td` | 文档数 Top10 |
| `eagle metrics top-indices` | `eagle m ti` | 索引数 Top10 |
| `eagle metrics top-shards` | `eagle m ts` | 分片数 Top10 |
| `eagle metrics disk-usage-percent` | `eagle m dup` | 磁盘使用率 Top10 |
| `eagle metrics io-util-avg` | `eagle m iua` | IO 使用率平均 Top10 |
| `eagle metrics heap-usage-percent` | `eagle m hup` | 堆内存使用率 Top10 |

**指标选项**:
- `--start-time <time>` - 开始时间
- `--end-time <time>` - 结束时间
- `--cluster-num <n>` - 集群数量（默认 10）
- `--daily` - 按天统计
- `--data-source <source>` - 数据源
- `--top <n>` - Top N

### 诊断分析

| 命令 | 别名 | 说明 |
|------|------|------|
| `eagle diagnostic reports <cluster>` | `eagle diag r` | 获取诊断报告列表 |

**诊断选项**:
- `-s, --size <size>` - 每页数量
- `-p, --page <page>` - 页码

---

## 写操作说明

以下命令涉及数据变更，执行前需要额外确认。所有变更命令若服务端返回工单，会**自动打印审批链接**。

### 索引变更

| 命令 | 必填选项 |
|------|----------|
| `eagle index create` | `--source` 或 `--file`, `--appkeys` |
| `eagle index update` | `--source` 或 `--file` |
| `eagle index update-info` | 至少一项：`--desc`, `--owner`, `--tags` |
| `eagle index open / close / delete` | 无额外选项 |
| `eagle index batch-open / batch-close / batch-delete` | `--names` |
| `eagle index add-alias / remove-alias` | `<alias>` 参数 |
| `eagle index transfer-alias` | `--alias`, `--target` |
| `eagle index migrate` | `--target-cluster` |
| `eagle index shrink` | `--target` |
| `eagle index split` | `--target`, `--shards` |
| `eagle index data-change` | `--op`, `--query` |
| `eagle index set-slowlog` | `--search-threshold` 或 `--index-threshold` |
| `eagle index set-monitor` | `--enabled` |

### 模板变更

| 命令 | 必填选项 |
|------|----------|
| `eagle template create` | `--source` 或 `--file`, `--appkeys` |
| `eagle template update` | `--source` 或 `--file` |
| `eagle template delete` | 无额外选项 |
| `eagle template set-slowlog` | `--search-threshold` 或 `--index-threshold` |

### 权限变更

| 命令 | 必填选项 |
|------|----------|
| `eagle auth apply` | `--cluster` |
| `eagle auth delete` | `<id>` 参数 |
| `eagle auth update-owner` | `<id>`, `<owner>` 参数 |

### 快照变更

| 命令 | 必填选项 |
|------|----------|
| `eagle snapshot repo-create` | 无额外必填（可提供 `--settings`） |
| `eagle snapshot repo-delete` | 无额外选项 |
| `eagle snapshot create` | 无额外必填（可提供 `--indices` 等） |
| `eagle snapshot delete` | 无额外选项 |
| `eagle snapshot restore` | 无额外必填（可提供 `--indices` 等） |

### 插件变更

| 命令 | 必填选项 |
|------|----------|
| `eagle plugin add` | 无额外必填（可提供 `--cluster`, `--url` 等） |
| `eagle plugin delete / install / uninstall` | `<cluster>`, `<plugin-id>` 参数 |

### 限流变更

| 命令 | 必填选项 |
|------|----------|
| `eagle ratelimit create` | `--name` |
| `eagle ratelimit update` | `--id` |
| `eagle ratelimit delete` | `<cluster>`, `<config-id>` 参数 |
| `eagle ratelimit reorder` | `--ids` |
| `eagle ratelimit add-query-limit / update-query-limit` | `--template-id`, `--rate-limit` |
| `eagle ratelimit delete-query-limit` | `<cluster>`, `<appkey>`, `<template-id>` 参数 |

---

## 使用示例

参阅 [references/examples.md](references/examples.md) 获取常见场景的操作示例：
- 查看集群状态
- 排查索引问题
- 检查权限
- 结合 jq 进行数据分析

---

## 常见问题

参阅 [references/TROUBLESHOOTING.md](references/TROUBLESHOOTING.md) 解决登录、权限、命令错误等问题。
