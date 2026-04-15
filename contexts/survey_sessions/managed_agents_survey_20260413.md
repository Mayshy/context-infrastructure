# Scaling Managed Agents：深度认知提炼

**来源**: https://www.anthropic.com/engineering/managed-agents  
**日期**: 2026-04-13  
**作者**: Lance Martin, Gabe Cemaj, Michael Cohen (Anthropic)

---

## 核心命题

这篇文章解决的不是"如何让 agent 更聪明"，而是一个系统设计问题：**如何构建一个在模型能力持续演化的前提下依然稳定的基础设施**。

Harness 是对"模型做不到什么"的编码。模型越来越强，这些编码就越来越快地过时。Managed Agents 的核心设计目标，是让系统对这种过时有抵抗力。

这个问题在 AI 基础设施领域有特殊的紧迫性。传统软件的依赖关系相对稳定，而 LLM-based 系统的核心组件（模型本身）在持续改变能力边界，意味着你今天写的 workaround 明天可能变成障碍。

---

## 关键洞察一：Harness 是技术债的温床

文章举了一个具体例子：Claude Sonnet 4.5 有"context anxiety"，会在接近上下文限制时提前结束任务。工程师在 harness 里加了 context reset 来应对。但当同样的 harness 跑在 Claude Opus 4.5 上时，这个行为已经消失了，reset 变成了无意义的开销。

这个例子揭示了一个普遍模式：**针对模型弱点的补丁，会随着模型迭代变成负担**。更难处理的是，你很难知道哪些 harness 逻辑是真正必要的，哪些已经成了死重。

这呼应了 Rich Sutton 的 [The Bitter Lesson](http://www.incompleteideas.net/IncIdeas/BitterLesson.html) 的逻辑（文章直接引用了这个链接）：手工编码的假设，长期来看总是输给规模扩展。Managed Agents 的应对策略是：与其试图写出"正确的" harness，不如设计一个能容纳任意 harness 的框架。

---

## 关键洞察二：Pets vs Cattle 的基础设施哲学

初始设计把 session、harness、sandbox 全塞进一个容器。这个容器变成了"pet"：有状态、不可替换、出问题需要人工介入。

问题不只是可靠性。更深的问题是**调试能力**：出错时唯一的观察窗口是 WebSocket 事件流，但这个流无法区分 harness bug、网络丢包、容器下线这三种完全不同的故障。要真正调试就得进容器，但容器里有用户数据，这在实践中等于没有调试能力。

解耦的解法是让每个组件变成 cattle：失败时直接替换，而不是修复。这要求每个组件都是无状态的，或者状态被外化到独立存储。

---

## 关键洞察三：接口设计的三个抽象

Anthropic 最终把 agent 系统分解为三个正交的接口：

**Session（会话日志）**：append-only 的事件流，外化于所有其他组件之外。Harness 通过 `emitEvent(id, event)` 写入，通过 `getEvents()` 读取，通过 `getSession(id)` 获取完整日志。Session 的关键属性是持久性和可重放性。任何组件崩溃，都可以通过 `wake(sessionId)` 重启并从日志恢复。

**Harness（执行循环）**：调用 Claude 并路由工具调用的逻辑。关键设计是 harness 离开了容器，它调用 sandbox 的方式和调用任何其他工具完全相同：`execute(name, input) → string`。Harness 本身无状态，可以随时替换。

**Sandbox（执行环境）**：Claude 生成的代码和文件操作发生的地方。通过 `provision({resources})` 按需初始化，通过统一的 tool call 接口暴露能力。

这三个抽象的设计原则是：**接口稳定，实现可变**。这和操作系统的 `read()` syscall 逻辑完全一致，`read()` 不关心底层是磁鼓还是 NVMe SSD。文章直接引用了 ESR 的 [The Art of Unix Programming](http://www.catb.org/esr/writings/taoup/html/ch03s01.html) 里"programs as yet unthought of"这个说法，这是 Managed Agents 的设计哲学的直接来源。

---

## 关键洞察四：Session 不是 Context Window

这是文章里最有技术深度的一个区分。

传统的长任务处理方式（compaction、summarization、selective trimming）都有一个共同缺陷：**不可逆**。你在压缩上下文时做的决策，是在不知道未来哪些 token 会被需要的情况下做出的。

Managed Agents 的做法是把 session log 作为一个活在 context window 之外的持久对象。`getEvents()` 允许 harness 按需取用任意位置的历史事件，包括"从上次停止的地方继续"、"往前回溯几个事件"、"重读某个动作之前的上下文"。

这把两个关注点分离开了：
- **Context storage**（上下文存储）：session 负责，保证持久性和可访问性
- **Context management**（上下文管理）：harness 负责，决定哪些事件进入 Claude 的 context window

分离的理由是：我们无法预测未来模型需要什么样的 context engineering。把存储和管理解耦，让 harness 可以自由演化 context 管理策略，而不影响存储层。

值得注意的是，这不是 Anthropic 独创的想法。文章引用了 [arxiv.org/pdf/2512.24601](https://arxiv.org/pdf/2512.24601) 的研究，该研究探索了把 context 作为 REPL 中可编程访问的对象存储在 context window 之外的方案。Managed Agents 是把这个已知研究方向落地到生产规模的实现。

---

## 关键洞察五：安全边界的结构性解法

安全问题的根源在于：如果 credentials 和 Claude 生成的代码在同一个环境里，prompt injection 只需要让 Claude 读自己的环境变量。

文章提出的结构性解法是：**credentials 永远不出现在 sandbox 里**。

具体实现有两种模式：
1. Git 的 access token 在 sandbox 初始化时被用来 clone 仓库，然后 token 本身不再可访问。后续的 `git push/pull` 通过已配置好的 remote 工作，Claude 从未接触到 token。
2. 自定义工具的 OAuth token 存在 vault 里，Claude 的 MCP 调用经过一个 proxy，proxy 持有 session 关联的 token，从 vault 取出 credentials 后代理调用外部服务。Harness 对 credentials 完全不感知。

这个设计的优雅之处在于：它不依赖"Claude 足够聪明不会被 prompt injection"这个假设。安全保证来自结构，而非行为。这是一个重要的设计原则：随着模型越来越聪明，攻击者利用模型能力的空间也在扩大，把安全锚定在行为假设上是危险的。

---

## 关键洞察六：解耦带来的性能收益

解耦不只是架构上的优雅，它带来了可量化的性能提升。

原来的设计里，harness 在容器里，意味着每个 session 都要先等容器启动，才能开始推理。即使这个 session 根本不需要 sandbox，也要付出这个延迟。

解耦之后，sandbox 按需通过 tool call 创建。不需要 sandbox 的 session，直接从 session log 取事件，立即开始推理。结果：p50 TTFT 下降约 60%，p95 下降超过 90%。

这个数字说明了一个更普遍的原则：**过度耦合不只是架构问题，也是性能问题**。每个不必要的依赖都是潜在的延迟来源。

---

## 关键洞察七：Many Brains, Many Hands

这一节揭示了 Managed Agents 更长远的设计意图。

**Many brains** 解决了网络拓扑问题：以前 harness 在容器里，容器假设所有资源就在旁边。客户想接入自己 VPC 的资源，只能把网络 peer 过来。解耦之后，harness 可以在任何地方运行，通过统一接口连接任意位置的资源。

**Many hands** 是更有意思的方向：一个 brain 可以同时操作多个 sandbox。接口设计 `execute(name, input) → string` 把 sandbox 的具体形态完全抽象掉了，harness 不知道也不需要知道"手"是容器、手机还是 Pokémon 模拟器。这个看似荒诞的例子是刻意为之的：它展示了这个接口对"手"的形态做了多么少的假设，这正是设计目标。

更关键的一步：**brains 可以把 hands 传递给彼此**。文章原文："because no hand is coupled to any brain, brains can pass hands to one another." 这是 multi-agent 协作的基础设施层面支撑。它意味着一个 sub-agent 可以从 orchestrator 那里继承一个已经初始化好的 sandbox，包括其中的文件状态、已安装的依赖、已执行的操作历史，而不需要重新 provision。这使得有状态的 agent 间任务移交成为可能，而不只是无状态的任务分发。

---

## 关键洞察八：Meta-Harness 的设计哲学（文章核心框架）

这是文章结论部分明确提出但容易被忽视的核心概念。

文章原文："Managed Agents is a meta-harness in the same spirit, unopinionated about the specific harness that Claude will need in the future."

**Meta-harness 的含义**：Managed Agents 不是一个 harness，而是一个能运行任意 harness 的框架。它对"哪个 harness 是正确的"没有意见，只对 harness 需要满足的接口有意见。

这个区分很重要。文章举了两个例子：Claude Code 是一个优秀的 harness，广泛用于各种任务；针对特定领域的 task-specific harness 在窄域内表现更好。Managed Agents 可以容纳这两者，也可以容纳任何未来出现的 harness。

这和操作系统的类比在这里最为精确：操作系统不是某个程序，它是让程序能运行的基础设施。Managed Agents 不是某个 agent，它是让 agent 能运行的基础设施。

对工程师的实践含义：如果你在构建 agent 系统，你面临的选择不只是"用哪个 harness"，还有"是否构建一个 meta-harness 层来隔离 harness 的变化"。对于长期运营的系统，这个隔离层的价值会随着模型迭代持续增加。

---

## 元认知：文章在说什么

把这些洞察拼在一起，文章的核心论点是：

**当系统的核心组件（模型）在持续演化时，传统的"针对当前能力编写 workaround"策略会积累技术债。正确的做法是设计稳定的接口抽象，让实现可以自由替换。进一步，可以构建一个 meta-harness 层，让整个 harness 本身也成为可替换的实现。**

这不是 Anthropic 独有的工程智慧，这是操作系统设计的基本原则在 AI 基础设施领域的重新发现。但在 AI 领域，这个原则有特殊的紧迫性：模型能力的演化速度远快于传统软件的迭代速度，harness 里的假设会以更快的速度过时。

对于自己构建 agent 系统的工程师，这篇文章的实践含义是：在设计 harness 时，要能回答"这段逻辑是在补偿模型的什么弱点？这个弱点在未来模型上还会存在吗？"如果答案不确定，就应该把这段逻辑设计成可以轻松移除或替换的。更进一步，可以考虑把 harness 本身设计成一个可替换的实现，而不是系统的核心。

---

## 关于 OpenCode/OpenClaw 的参照（概念类比，非结构等价）

以下类比是概念层面的参照，帮助理解 Managed Agents 的设计思路，而非精确的架构等价映射。

OpenCode 的会话历史和 `session_id` 机制，在概念上类似于 Managed Agents 的 session log，都提供了某种形式的状态持久化。但两者有本质区别：OpenCode 的 session 是对话状态管理，Managed Agents 的 session 是容错执行恢复。`wake(sessionId)` 是一个无状态 harness 崩溃后从外部持久日志恢复的机制，而不是对话记忆。

OpenCode 的 skill system 和 orchestration 层，在概念上对应 harness 的"路由工具调用"职责。但 skill system 本质上是 prompt/instruction 层，而 Managed Agents 的 harness 是基础设施代码。这个差距说明：OpenCode 目前没有等价于 Managed Agents session 的外部持久事件日志，也没有等价于 `provision({resources})` 的按需 sandbox 机制。

这个对比的意义不是说 OpenCode 不够好，而是指出：如果要在 OpenCode 上支持真正的 long-horizon fault-tolerant agent 任务，需要补充的基础设施层是什么。

---

*报告生成于 2026-04-13，基于文章原文全文提炼*
