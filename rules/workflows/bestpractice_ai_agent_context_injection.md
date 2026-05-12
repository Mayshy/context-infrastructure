# Best Practice: AI Agent 上下文注入与知识持久化

## 适用场景

- 启动新项目 KB，需要让 AI（包括子 Agent）正确理解验收标准
- 使用 Oracle / ulw-loop 做代码验证时
- 配置 ai_heartbeat observer/reflector 自动化任务时
- 任何需要跨 session 保留决策或约束的场景

---

## 核心原则

### 1. 子 Agent 不自动注入上下文

Oracle、ulw-loop 内的验证 Agent、以及任何通过 `task()` 启动的子 Agent，只能感知：
- 当前 session 的对话内容
- 调用时手写的 prompt

它们**不会**自动读取：
- 项目 DoD 文件（definition_of_done.md）
- 项目 AGENTS.md
- OBSERVATIONS.md 或任何记忆文件

**解决方案**：在项目 AGENTS.md 中显式写明"验证时必须读取 [绝对路径] 的 DoD 文件"，并在调用子 Agent 时将关键约束内联到 prompt 中。

### 2. 重要约束必须写入文件才能被记忆

口头约定、session 内的推理链、被放弃的方案，ai_heartbeat observer 的 file-based 扫描捕获不到。只有显式写入文件的内容才能进入记忆系统。

**操作规范**：
- 重大技术决策 → 写入项目 KB 的 decisions/ 目录（ADR 格式）
- 跨项目通用约束 → 写入 OBSERVATIONS.md（🔴 High 条目）
- 临时上下文 → 写入 OBSERVATIONS.md（🟡/🟢 条目，定期 GC）

### 3. 知识必须主动流向能力层

OBSERVATIONS.md 是中转站，不是终点。规律停留在日志层不会自动转化为 skill 或 workflow。

**流向路径**：
```
口头/session 决策
    ↓ 显式写入
OBSERVATIONS.md (L1/L2)
    ↓ Reflector 晋升
rules/ (L3 约束) 或 skills/__drafts__/ (能力层)
    ↓ 用户确认
skills/<name>/SKILL.md (正式 skill)
```

---

## 项目 AGENTS.md 验收标准模板

在每个项目 KB 的 AGENTS.md 中加入以下段落：

```markdown
## 验收标准（AI 必读）

在完成任何实现任务或调用 Oracle 验证前，必须读取以下文件：

- **DoD（完成定义）**：`[绝对路径]/definition_of_done.md`
- **核心约束**：[内联最重要的 2-3 条约束，不要只给路径]

示例核心约束：
- 所有 API 调用必须使用 HTTPS（HTTP 会 302 丢失 POST body）
- edge 方向：inputNodeId = 下游（接收方），outputNodeId = 上游（发送方）
```

---

## observer session log 扫描（待实现）

当前 ai_heartbeat observer 只做 file-based 扫描，存在盲区。改进方向：

1. 读取 `~/.local/share/opencode/opencode.db`（SQLite）
2. 查询 `part` 表中昨天工作 sessions 的 TextPart（assistant 回复）
3. 与 file-based 扫描结果并行合并，写入 OBSERVATIONS.md

SQLite 表结构参考：
- `session` 表：session_id、created_at
- `message` 表：message_id、session_id、role
- `part` 表：message_id、type（TextPart/ToolPart）、content

注意：observer/reflector automation sessions 跑完即删（cascade），只需扫描用户工作 sessions。

---

## 来源条目

- 2026-04-15 🔴 High: observer 是纯 file-based 扫描，无法捕获 session 内决策
- 2026-04-16 🔴 High: ulw-loop Oracle 验证不自动读取 definition_of_done.md
- 2026-04-16 🔴 High: AI 自我学习的核心断点：知识停留在 OBSERVATIONS.md 日志层
