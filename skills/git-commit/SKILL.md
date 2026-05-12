---
name: git-commit
description: 生成 Conventional Commits 格式的提交信息。Use when user says "commit", "commit this", "create commit", "提交", "写 commit message"，或完成代码修改后需要提交。
---

# Git Commit Message

生成清晰、可搜索的 Conventional Commits 格式提交信息。

## 格式

```
<type>(<scope>): <subject>

<body>

<footer>
```

## Type

| Type | 场景 |
|------|------|
| `feat` | 新功能 |
| `fix` | Bug 修复 |
| `refactor` | 重构（无功能变更） |
| `test` | 添加/修改测试 |
| `perf` | 性能优化 |
| `docs` | 文档 |
| `build` | Maven/Gradle/依赖变更 |
| `chore` | 维护性工作（CI、配置等） |

## Scope（常用范围）

**DataMatrix 服务：**
- `pontos` — 数据集成服务
- `hermes` — 数据计算服务
- `athena` — 数据建模服务
- `kugget` — 索引服务平台
- `worksheet` — 工单服务
- `naiads` / `joiner` — 老云搜服务

**Eagle SDK / Poros：**
- `poros` — ES 客户端核心
- `poros-client` — 低层客户端
- `eagle` — Eagle 管控层

**通用：**
- `flink` — Flink 作业相关
- `spark` — Spark 作业相关
- `blade` — Blade JDBC 相关
- `pigeon` — Pigeon RPC 相关
- `mafka` — Mafka 消息队列相关
- `lion` — Lion 配置相关
- `deps` — 依赖更新

## Subject 规则

- 祈使句：`add support` 不是 `added support`
- 不加句号
- ≤ 50 字符
- 首字母小写（type 之后）

## Body（推荐写）

- 解释 WHAT 和 WHY，不是 HOW
- 每行 ≤ 72 字符
- 引用 issue：`Fixes #123` / `Relates to #456`

## 工作流

1. `git diff --staged --stat` — 了解变更范围
2. 根据变更文件路径确定 scope
3. 确定 type（功能/修复/重构/测试）
4. 生成 message，执行 `git commit -m "..."`

## 示例

### Bug 修复
```
fix(pontos): 修复 getDefaultMirrorColumnDataType 类型修饰符清洗缺失

第一/二轮匹配直接 return sourceColumnDataType.toLowerCase() 不做清洗，
导致 "int unsigned" 的 baseType 包含修饰符，generateDefaultValueSchemaStr
的 switch 全部 miss，DEFAULT 值静默返回空串。

Fixes #xxx
```

### 性能优化
```
perf(pontos): BladeNormalExporter 改用显式 multi-row INSERT

rewriteBatchedStatements 对 Zebra BladeDataSource 不可靠，
改为 SqlUtils.generateMultiRowInsertIgnoreSql() 显式构造批量 SQL，
行为透明可控，batch size 对齐 TiDB 官方建议 ≤200 行/事务。
```

### 新功能
```
feat(pontos): 新增 BatchUpdatePackage Crane Job

自动检测 Spark/Flink 包名并推送大象通知，支持 dryRun 开关。
新增 6 个 Lion Key：默认包名、dryRun 开关、大象推送配置。
```

### 依赖更新
```
build(deps): 升级 Jackson 至 2.17.2

2.17.0 存在内存泄漏 bug，2.17.2 修复。
影响 poros-java-api-client 及所有依赖它的服务。
```

### 重构
```
refactor(hermes): 提取 DataSinker docAcc 累加逻辑

修复 repartitionRDD 未 persist 导致两次 Action 触发 docAcc 重复
累加的 bug，同时将 recordCount 上报到 processInstance。
```

## 反模式

❌ 避免：
- `fix stuff` / `update code` / `changes` / `wip`
- 混合无关变更到一个 commit
- subject 超过 50 字符

✅ 好的 commit：
- 单一逻辑变更
- subject 可以被 `git log --oneline` 搜索到
- body 解释了为什么这么改（而不只是改了什么）

## Token 优化

- 只读 `git diff --staged --stat` + 关键文件的 diff，不读整个文件
- body 控制在 2-3 行
- 多个小变更合并为一个逻辑 commit
