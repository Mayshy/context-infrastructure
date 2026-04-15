# Superpowers 与 oh-my-openagent 共存调研报告

**调研日期**: 2026-04-09  
**调研问题**: superpowers 和 oh-my-openagent 能否共存？是否推荐同时使用？  
**现状**: 用户目前只使用 oh-my-openagent

---

## 核心结论（TL;DR）

**"superpowers" 不是独立 plugin，它就是 oh-my-openagent 的一部分。**

你已经在用它了。无需任何操作。

---

## 关键发现：superpowers 的真实身份

社区里"superpowers"这个词有两种语境，容易混淆：

| 语境 | 含义 |
|------|------|
| **狭义（常见用法）** | oh-my-openagent 内置的 `superpowers:*` 前缀 skills（TDD、brainstorming、debugging 等），通过 `/superpowers:skill-name` 命令调用 |
| **广义** | 整个 oh-my-openagent plugin 的"超能力"集合 |

oh-my-openagent 的 AGENTS.md 原文描述：
> "OpenCode plugin (npm: `oh-my-opencode`) extending Claude Code with multi-agent orchestration, 52 lifecycle hooks, 26 tools, skill/command/MCP systems..."

**superpowers:* 这批 skills 是 oh-my-openagent 的 builtin skills，不是外部 plugin。**

---

## oh-my-openagent 提供的 superpowers:* Skills 清单

| Skill | 用途 | 何时用 |
|-------|------|--------|
| `superpowers:brainstorming` | 将模糊需求转化为设计文档和技术规格.需求→设计文档，未获批准不得动代码 | 开始新功能前 |
| `superpowers:writing-plans` | 写详细执行计划（2-5 分钟粒度）.设计→执行计划，每步含完整代码和命令 | 设计完成后、写代码前 |
| `superpowers:test-driven-development` | 强制红-绿-重构 TDD 工作流.每 task 派新 subagent + 两阶段 review（推荐） | 任何新功能/bug 修复 |
| `superpowers:subagent-driven-development` | 在当前 session 用 subagent 执行计划. | 有计划后执行 |
| `superpowers:executing-plans` | 在独立 session/batch 模式执行计划.当前 session 串行执行（无 subagent 时用） | 多步骤任务 |
| `superpowers:finishing-a-development-branch` | 验证 → 选择合并方式 → 清理. | 功能完成后 |
| `superpowers:using-git-worktrees` | 隔离功能开发到独立 git worktree | 需要隔离的功能分支 |
| `superpowers:systematic-debugging` | 先找根因再修 bug 的调查框架 | 遇到 bug 时 |
| `superpowers:dispatching-parallel-agents` | 并行派发多个 agent 处理独立问题 | 2+ 个互不相关的任务 |
| `superpowers:requesting-code-review` | 调用 code-reviewer subagent | 完成实现后 |
| `superpowers:receiving-code-review` | 技术性验证 reviewer 反馈 | 收到 review 反馈后 |
| `superpowers:verification-before-completion` | 完成前强制运行验证命令 | 声称完成前 |
| `superpowers:writing-skills` | 创建/编辑新 skills 的指南 | 写 skill 时 |
| `superpowers:using-superpowers` | 建立 skills 使用规则 | 对话开始时 |



---

## "另一个 superpowers"：obra/superpowers

社区里还存在一个**独立的** superpowers plugin：  
`superpowers@git+https://github.com/obra/superpowers.git`

这才是真正意义上"和 oh-my-openagent 共存"的场景。

### 能否共存？

**技术上：可以。**

OpenCode plugin 系统明确支持多 plugin 共存（源码验证）：
- `plugin` 字段是数组，所有 hooks 顺序执行
- 不同名 plugin 全部加载，无冲突中断机制
- 去重只针对**同名**包（按包名 key）

```json
{
  "plugin": [
    "oh-my-opencode@latest",
    "superpowers@git+https://github.com/obra/superpowers.git"
  ]
}
```

### 曾经的 bug（已修复）

Issue #2745（2026-03-22，已关闭）记录了同时安装两者时的 skill 解析冲突：

> "When oh-my-opencode is enabled alongside superpowers, Superpowers skills can become prompt-visible but not actually callable through the skill tool in the current session."
> — stoner-byte, GitHub Issue #2745

**修复 PR（已合并）**：
- [#3013](https://github.com/code-yeongyu/oh-my-openagent/pull/3013) fix(skill): resolve namespaced skills by short name（2026-04-02）
- [#2936](https://github.com/code-yeongyu/oh-my-openagent/pull/2936) fix: preserve nested async skill names in discovery（2026-03-30）

修复后，通过 `superpowers:skill-name` 命名空间格式可稳定调用。

---

## OpenCode Plugin 系统机制（关键原理）

来源：opencode 源码 commit `46f243f`

### 多 Plugin 共存行为

```typescript
// plugin/index.ts — hooks 顺序执行，全部运行
for (const hook of s.hooks) {
  const fn = hook[name] as any
  if (!fn) continue
  yield* Effect.promise(async () => fn(input, output))
}
```

- ✅ 所有 plugin 的同名 hook 都会依次执行
- ✅ 无冲突机制，无优先级中断
- ✅ 唯一"优先级"：plugin tool 名称与 built-in tool 同名时，plugin 胜出

### AGENTS.md 与 Plugin 完全解耦

AGENTS.md 是独立的 Instruction 系统，不属于 Plugin 系统：
- 项目级：从当前目录向上找第一个 `AGENTS.md` / `CLAUDE.md`
- 全局级：`~/.config/opencode/AGENTS.md`
- 多个文件各自加上 `Instructions from: <path>` 前缀后**拼接**传入 LLM

---

## 建议

### 你的现状：只用 oh-my-openagent

**不需要做任何事。** `superpowers:*` skills 已经内置在 oh-my-openagent 里了。

如果你想用 `superpowers:brainstorming`，直接让 AI 调用即可：
```
使用 superpowers:brainstorming skill 帮我设计这个功能
```

### 关于 obra/superpowers（第三方独立 plugin）

**不推荐额外安装。** 理由：
1. **功能高度重叠**：obra/superpowers 提供的 skills（TDD、brainstorming、debugging）与 oh-my-openagent 内置的 `superpowers:*` skills 几乎完全一致
2. **增加维护负担**：两套相似 skills 并存，AI 可能调用错误或产生混淆
3. **历史 bug 风险**：虽已修复，但两者共存仍属边缘场景，社区 Issue #3190（2026-04-07）仍无官方回复
4. **oh-my-openagent 的 superpowers 更深度集成**：与 Sisyphus orchestration、Prometheus planner、Hashline 等系统协同设计

**唯一值得考虑的场景**：obra/superpowers 有你需要但 oh-my-openagent 没有的特定 skill。先检查 oh-my-openagent 的 builtin skills 清单，再决定是否需要额外安装。

---

## 信息来源

| 来源 | URL |
|------|-----|
| oh-my-openagent 主仓库 | https://github.com/code-yeongyu/oh-my-openagent |
| Issue #2745（skill 冲突，已修复）| https://github.com/code-yeongyu/oh-my-openagent/issues/2745 |
| Issue #3190（兼容性问询，开放中）| https://github.com/code-yeongyu/oh-my-openagent/issues/3190 |
| PR #3013（skill 解析修复）| https://github.com/code-yeongyu/oh-my-openagent/pull/3013 |
| opencode 官方 plugin 文档 | https://opencode.ai/docs/plugins/ |
| opencode plugin 源码 | https://github.com/anomalyco/opencode/blob/46f243f/packages/opencode/src/plugin/index.ts |
| Skills 目录参考 | https://github.com/bruhismyname/opencode-ultimate-starter/blob/main/docs/SKILLS_CATALOG.md |
