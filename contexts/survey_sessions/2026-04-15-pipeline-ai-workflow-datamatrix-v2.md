# 调研报告 v2：Datamatrix AI 研发新范式 — 自然融入、轻量介入、价值可见

> **版本**: v2（深化版）
> **日期**: 2026-04-15
> **基于 v1 + LinkedIn AI 转型实践（Ryan Roslansky）宏观视角**
> **状态**: 可用于团队讨论

---

## 一、从宏观视角看：我们在做什么

### 1.1 LinkedIn 转型实践的核心启示

LinkedIn CEO Ryan Roslansky 在《穿越混乱的中间地带》中描述了 AI 时代组织转型的本质困境：

> **"知道要变了，但动不起来。"**

他的解法不是颁布规范，而是**把 AI 融入日常工作节奏本身**——让改变自然发生，而非强制执行。

与 Pontos 研发流程最直接相关的**五个洞察**（从源文档完整提炼）：

---

#### 洞察 1：工作图（Work Chart）替代组织架构图

LinkedIn 提出"工作图"理念：把岗位说明拆解为**一项项具体任务**，逐一判断：

```
这件事 AI 能做，还是只有我能做？
```

| 任务类型 | 典型例子 | Pipeline 中的对应 |
|---|---|---|
| **AI 独立完成** | 生成 PRD 初稿、生成 Commit Message、生成测试用例骨架 | Stage 1/5/6 的 AI 输出 |
| **人机协作完成** | AI 生成技术方案 → 人做架构评审 | Stage 2 的 Checkpoint |
| **只有人能完成** | 判断业务优先级、识别隐性约束、跨团队沟通 | Checkpoint 的人工决策点 |

**启示**：Pipeline 的人工介入节点，应精确对准"只有人能完成"的任务，其余全部自动化。

---

#### 洞察 2：Squad制 — 围绕问题组队，压缩信息流动摩擦

LinkedIn 推行"小队制（Squad）"：围绕一个具体业务问题临时组建跨职能小团队，周期结束后解散。Roslansky 解释：

> "历史上，一个产品想法必须在工程、产品和设计等独立职能部门之间流转，然后在所有这些职能部门内的独立层级之间流转，才能到达实际成员手中。这种复杂性和时间消耗让我们无法处于成功的正确位置。"

**这正是 Pipeline AI Workflow 的核心价值所在**：传统研发流程中，一个需求需要经过 PM 写 PRD → 研发对齐 → 各自理解各自写 → QA 提 Bug → 来回拉锯。每个环节都是信息被翻译、过滤、延迟的摩擦点。

Pipeline 本质上是把"跨职能小队"内化为一个人 + AI 的协作模式：
- 需求分析（原本需要 PM）→ AI 生成 PRD，研发确认
- 设计（原本需要架构师）→ AI 生成技术方案，研发做架构决策
- 开发（研发）→ Sub-agent 并行实现
- 测试（原本需要 QA）→ AI 生成测试用例，自动化运行

**信息不再在多个人之间流转，摩擦消失，决策权在离问题最近的人手中。**

**启示**：Pipeline 的价值不只是"AI 帮写代码"，而是**消除了需求从想法到提测过程中的所有跨人协作摩擦**。这是向团队介绍 Pipeline 时最有说服力的论点。

---

#### 洞察 3：Full Stack Builder — AI 时代的研发单元

LinkedIn 推行"Full Stack Builder"模式：**一个工程师借助 AI 独立完成原本需要多人协作的完整流程**——产品定义、设计、开发、测试。

这正是 Pipeline AI Workflow 的编码阶段目标：
- AI 生成实施计划（writing-plans）
- Sub-agent 并行实现各任务（subagent-driven-development）
- 双轮 Review 保证质量

**启示**：Pontos 的 Pipeline 不是"AI 帮研发写代码"，而是"研发成为 Full Stack Builder，AI 是协作者"。研发的核心价值转移到：**架构判断、业务理解、质量把关**。

---

#### 洞察 4：六周冲刺 — 计划是假设，不是路线图

LinkedIn 放弃年度规划，以**六周为迭代单位**验证假设。核心逻辑：

> 在 AI 工具以周为单位迭代的背景下，年初的优先事项到年中往往已经失效。

**启示**：Pipeline 的 Checkpoint 设计应是**假设验证点**，而非审批流程。每个 Checkpoint 的问题不是"方案写得够不够详细"，而是"这个假设是否经过了足够的验证，可以进入下一阶段"。

---

#### 洞察 5：叙事管理 — 转型需要载体，不只是倡导

这是源文档中最容易被忽视、但对团队落地最关键的洞察。Roslansky 说：

> "AI 不只是一个技术项目。它是一场文化转型。而文化，是从你如何花费时间、如何奖励他人、如何设定期望开始的。"

LinkedIn 的做法是：每两周举行一次 Company Connect，主角是**一线工程师**展示用 AI 做出的真实成果，而非高管宣讲。

> "这种文化动力，不能是在高管团队内部孤岛中发生的事情。"

**关键判断**：员工对 AI 转型的理解，每天都在被外部信息更新。如果团队负责人不主动持续输入清晰意图，"Pipeline 是在替代我"的威胁性叙事会自然填充这个空间。**"让流程自己说话"是不够的，需要主动的叙事管理机制。**

**启示**：Pontos 团队采用 Pipeline 的过程，需要配套的**可见性机制**：
- 第一个用 Pipeline 完成的需求，要在团队内分享（不是炫技，是建立参照）
- Checkpoint 的确认过程，要让研发感受到"我的判断被重视"，而非"走流程"
- 交付报告（Stage 9）中的耗时统计，要公开分享，让数据说话

---

### 1.2 重新定义 Pontos Pipeline 的目标

基于以上洞察，v2 的设计原则：

```
原则 1：自然触发 — 员工用一句话描述需求，Pipeline 自动收集缺失信息
原则 2：最小人工介入 — 只在"只有人能完成"的节点要求人工确认
原则 3：价值可见 — 每个阶段产出都是有用的工件，不是流程副产品
原则 4：Full Stack Builder 赋能 — AI 处理重复性工作，人聚焦判断与架构
原则 5：假设驱动 — Checkpoint 是验证假设，不是审批流程
```

---

## 二、Pontos AI Workflow v2：完整设计

### 2.1 触发方式（自然使用）

**最简触发（一句话）：**
```
开始做需求：<需求描述>
```

**Pipeline 自动收集缺失参数**（不够时主动询问，有则跳过）：
- 学城父文档 ID（用于写入产出文档）
- 服务说明书链接（首次配置后自动记忆）

**丰富触发（推荐，减少追问）：**
```
开始做需求：<需求描述>
学城父文档 ID：<id>
关联服务说明书：<km 链接>
MEP 工作项：<可选，已有工作项时提供>
```

**断点续跑（任意时刻）：**
```
从阶段4继续
重新执行阶段2（DDL 方案需要修改）
跳过阶段3直接编码（已有 MEP 工作项 WI-xxxxx）
```

**服务说明书记忆机制**：Pipeline 在首次使用时，将服务说明书的学城 contentId 写入本地 `~/.pipeline-ai-workflow/pontos-config.json`（或 Pipeline 的 manifest 文件）。后续每次触发时，Pipeline 在 Stage 0 自动读取该配置，无需用户重复提供。如果配置文件不存在，Stage 0 会主动询问并保存。

---

### 2.2 人工介入节点设计（最小化原则）

基于"工作图"思维，重新设计哪些节点需要人工确认：

| 节点 | 是否需要人工 | 原因 | 人工做什么 |
|---|---|---|---|
| Stage 1 PRD 生成 | ✅ **轻量确认**（可选） | 业务判断不可替代 | 确认需求理解是否准确，可一键通过 |
| Stage 1 复杂度评估 | ❌ 自动 | AI 评分足够准确 | — |
| Stage 2 技术方案 | ✅ **必须确认** | 架构决策是"只有人能完成"的 | 评审架构设计，确认模块影响范围 |
| Stage 2 DDL 方案 | ✅ **必须确认**（有 DDL 时） | 数据库变更高风险 | 评审 DDL 语句和迁移方案 |
| Stage 3 分支创建 | ❌ 自动 | 机械操作 | — |
| Stage 4 编码实现 | ❌ 自动（Sub-agent） | Full Stack Builder 模式 | — |
| Stage 4 覆盖率不达标 | ✅ **阻断** | 质量门控 | 决定是补测试还是豁免 |
| Stage 5 PR Review | ✅ **异步通知** | 人工 Review 不可替代 | 收到通知后按自己节奏 Review |
| Stage 6 测试用例 | ❌ 自动 | AI 生成，QA 补充 | — |
| Stage 7-9 | ❌ 自动 | 机械操作 | — |

**关键设计**：Checkpoint 分两类：
- **阻断型**（必须人工确认才能继续）：Stage 2 技术方案、DDL 评审、覆盖率不达标
- **通知型**（发通知，不阻断主流程）：Stage 1 PRD 确认、Stage 5 PR Review

---

### 2.3 完整流程 DAG（v2）

```
输入：需求描述（必填）+ 学城父文档 ID（必填）+ 服务说明书（首次必填，后续记忆）

Stage 0  初始化
         ├─ 状态初始化、依赖检查
         ├─ 读取 pontos 服务说明书（7模块架构）
         └─ 参数不足时主动询问（最多 2 个追问）

Stage 1  需求分析
         ├─ AI 生成 PRD（requirements-analyst）
         ├─ Pontos 专属澄清问卷（5问，AI 自动判断，仅在不确定时追问）
         │   ① Thrift RPC 接口？ ② Crane 定时任务？
         │   ③ Flink/Spark Job？ ④ DB 变更？ ⑤ 新外部系统？
         ├─ 复杂度评估（L/M/H + 爆炸半径）
         ├─ 【通知型 Checkpoint】→ 大象通知 PRD 已生成，可查看确认
         └─ 输出：01-需求分析文档 → 写入学城

Stage 2  技术方案
         ├─ 模块识别（7模块映射规则，自动判定 Owner/Contributor）
         ├─ 接口设计（REST + 可选 Thrift IDL）
         ├─ DDL 变更评估（如需）
         ├─ 外部 client 识别（是否需要新增 Retrofit client）
         ├─ Lion 配置开关设计
         ├─ 【阻断型 Checkpoint】→ 等待技术方案确认（大象通知 + 学城链接）
         │   └─ 回复"确认"或"修改：<意见>"即可继续
         └─ 输出：02-技术方案 → 写入学城 + docs/superpowers/specs/

Stage 3  MEP 分支管理
         ├─ 创建 MEP 工作项（ee-ones skill）
         └─ 按受影响模块创建 feature 分支（自动，无需人工）

Stage 4  编码实现（Full Stack Builder 模式）
         ├─ 生成 TDD 实施计划（writing-plans）→ docs/superpowers/plans/
         ├─ Sub-agent 并行实现（subagent-driven-development）
         │   按 8 层标准路径：dao → service → controller → crane/handler（按需）
         ├─ 每步编译验证：mvn compile -pl <module> -am -DskipTests
         ├─ 每层单测验证：mvn test -pl pontos-server -Dtest=<LayerTest>
         ├─ Pontos 规范门控（ApiResult/Swagger/Lombok/Lion 强制检查）
         ├─ 覆盖率门控（分层标准，不达标时阻断 + 大象通知）
         └─ 输出：03-实施计划 + 04-单测覆盖报告 → 写入学城

Stage 5  提交 & PR（与 Stage 6 并行）
         ├─ 生成 Angular 规范 Commit Message（code-commit-assistant）
         ├─ 创建 PR（多模块时按模块分 PR）
         ├─ 【通知型 Checkpoint】→ 大象通知 PR 已创建，附链接，请异步 Review
         └─ AI 自动 Code Review（pr-code-reviewer，基于 PRD + 技术方案）

Stage 6  生成测试用例（与 Stage 5 并行）
         ├─ AI 生成正常/边界/异常测试用例（test-case-generator）
         ├─ 镜像流需求：自动补充 MirrorFlow 状态机流转矩阵
         └─ 输出：05-测试用例 → 写入学城

Stage 7  提测
         └─ 创建提测单（ee-ones skill），关联工作项和 PR

Stage 8  自动化测试
         └─ 触发流水线，回收测试报告（ee-pipeline skill）

Stage 9  交付报告
         ├─ 汇总所有产出链接 + 各阶段耗时
         ├─ 覆盖率统计、测试通过率
         └─ 大象群通知（含学城文档目录链接）
```

---

### 2.4 学城文档目录结构

```
父文档（你提供的 km_parent_id）
└── {需求名称}（目录容器）
    ├── 01-需求分析文档        ← Stage 1 产出
    ├── 02-技术方案            ← Stage 2 产出
    ├── 03-实施计划            ← Stage 4 产出
    ├── 04-单测覆盖报告        ← Stage 4 产出
    ├── 05-测试用例            ← Stage 6 产出
    ├── 06-提测单              ← Stage 7 产出
    └── 07-交付报告            ← Stage 9 产出
```

**同时本地写入**（Pontos 项目约定）：
```
docs/superpowers/
├── specs/YYYY-MM-DD-<feature>.md   ← Stage 2 产出
└── plans/YYYY-MM-DD-<feature>.md   ← Stage 4 产出
```

---

## 三、与原版 Pipeline 的核心差异与优势

### 3.1 差异对比表

| 维度 | 原版 Pipeline AI Workflow | Pontos 定制版（v2） |
|---|---|---|
| **触发方式** | 需提供需求描述 + 学城父文档 ID + 服务说明书 | 最简一句话，参数自动收集，服务说明书首次配置后记忆 |
| **人工介入** | Checkpoint 均需确认 | 分阻断型/通知型，最小化必须人工介入的节点 |
| **需求分析** | 通用 PRD + 复杂度评估 | +Pontos 专属5问澄清（AI 自动判断，仅在不确定时追问）|
| **服务识别** | 微服务三轮评分（适用于多仓库微服务架构） | 7模块映射规则（适用于单仓库多模块 Maven 架构）|
| **DDL 流程** | 无专项处理 | DDL 变更触发专属子流程（Zebra 迁移方案 + 回滚）|
| **外部系统** | 无专项处理 | 自动识别是否需要新增 Retrofit client（24个已有 client）|
| **配置开关** | 无专项处理 | Lion 配置开关设计（灰度/降级/限流）|
| **编码顺序** | 通用 TDD | 8层分层顺序（dao→service→controller→crane/handler）|
| **覆盖率** | 统一 ≥ 60% | 分层差异化（handler≥80% / service≥70% / job≥50%）|
| **PR 策略** | 单 PR | 多模块时按模块分 PR（dao PR → server PR 依赖顺序）|
| **测试矩阵** | 通用正常/边界/异常 | +MirrorFlow 状态机流转专项矩阵 |
| **本地文档** | 仅写学城 | 同时写入 docs/superpowers/specs/ 和 plans/（项目约定）|
| **规范门控** | 通用代码规范 | ApiResult/Swagger/Lombok/Lion 强制检查（Pontos 专属）|

### 3.2 核心优势（vs 原版）

**优势 1：自然使用，无感融入**

原版需要提前准备三个参数（需求、学城 ID、服务说明书）。v2 设计为：
- 服务说明书首次配置后自动记忆，后续无需重复提供
- 学城 ID 不填时，AI 主动询问（最多 2 个追问，不超过 1 分钟）
- 员工感知到的是"说一句话，AI 开始工作"，而非"填表格"

**优势 2：精准的人工介入**

原版 Checkpoint 较多，可能造成"等待确认"的摩擦感。v2 区分：
- **阻断型**（2个）：技术方案确认 + DDL 评审 — 这是真正需要人判断的
- **通知型**（2个）：PRD 生成通知 + PR Review 通知 — 异步，不阻断主流程

研发的体感：**"我只需要在两个关键节点做决策，其余 AI 自动推进"**

**优势 3：Full Stack Builder 赋能**

基于 LinkedIn "工作图"洞察，Pontos Pipeline v2 明确了人与 AI 的分工：

| 研发做什么（不可替代） | AI 做什么（自动化） |
|---|---|
| 架构决策（Stage 2 确认） | PRD 生成、复杂度评估 |
| 业务判断（DDL 方案评审） | 模块识别、接口设计、代码实现 |
| 质量把关（覆盖率不达标时决策） | 单测生成、Commit 生成、测试用例生成 |
| PR Review（异步，按自己节奏） | Code Review（AI 先做一轮） |

研发从"写每一行代码"转变为"做关键决策 + 质量把关"。

**优势 4：Pontos 特有的质量保障**

原版 Pipeline 是通用框架，不了解 Pontos 的技术栈约束。v2 内置：
- **MirrorFlow 状态机测试矩阵**：镜像流是 Pontos 核心业务，状态遗漏代价极大
- **分层覆盖率门控**：handler 层 80%（高风险），job 层 50%（测试成本高）
- **Lion 开关强制**：所有新功能必须有降级开关，避免无法快速回滚
- **DDL 专项流程**：Zebra 大表变更需要在线 DDL 评估，避免锁表

---

## 四、实际使用场景演示

### 场景 1：典型后端功能需求（最常见）

```
# 员工输入（最简）
开始做需求：为数据源列表新增「最近同步时间」展示字段，从 MirrorFlow 最新记录聚合

# Pipeline 自动执行
✅ Stage 1: AI 判断 → REST 接口（✅），Thrift（❌），Crane（❌），DB 变更（✅，新增字段），外部系统（❌）
✅ Stage 2: 模块识别 → pontos-server + pontos-dao
           技术方案生成 → 接口定义 + DDL（ALTER TABLE 加字段）
           【阻断型 Checkpoint】→ 大象通知："技术方案已生成，请确认：<学城链接>"
           员工回复："确认" → 继续
✅ Stage 3: 创建分支 feature/WI-xxxxx/datasource-last-sync
✅ Stage 4: Sub-agent 实现（8层路径）
           覆盖率：service 71% ✅，controller 62% ✅
✅ Stage 5&6: PR 创建 + 测试用例（并行）
✅ Stage 9: 交付报告，大象群通知
```

### 场景 2：涉及 Crane 的定时任务需求

```
# 员工输入
开始做需求：新增 Flink SLA 离线检测，每 5 分钟检查未上报心跳的 Job，发大象告警

# Pipeline 自动执行
✅ Stage 1: AI 判断 → Crane（✅），DB 变更（✅），外部系统（✅，大象 IM）
✅ Stage 4: 分层实现 → Entity + Mapper → Service → Crane
           【阻断型 Checkpoint 触发】→ 覆盖率：crane 58% < 60% → 大象通知："Crane 层覆盖率不足，请决策：补测试 or 豁免？"
           员工回复："补测试" → AI 继续补充测试用例
```

### 场景 3：跨模块复杂需求

```
# 员工输入
开始做需求：新增数据源 Thrift 查询接口，支持外部服务通过 RPC 查询数据源元信息

# Pipeline 自动执行
✅ Stage 1: AI 判断 → Thrift（✅），DB 变更（❌）
✅ Stage 2: 模块识别 → pontos-server + pontos-sdk
           【阻断型 Checkpoint】→ 技术方案含 Thrift IDL 设计，需确认接口定义
✅ Stage 3: 创建两个模块的分支
✅ Stage 4: 分 PR 实现 → pontos-sdk（IDL）→ pontos-server（实现）
✅ Stage 5: 两个 PR，依赖顺序：sdk PR 先合并，server PR 后合并
```

---

## 五、安装与配置

### 5.1 一次性安装

```bash
# 克隆 Pipeline AI Workflow
git clone ssh://git@git.sankuai.com/ee-plugins/super-assistant.git

# 安装
python skills/ppl-yc-pipeline-workflow/scripts/install_super_assistant.py
```

### 5.2 一次性配置（Pontos 专属）

**步骤 1**：在学城创建 Pontos 服务说明书（参考 AGENTS.md + SERVICE.DESCRIPTION.xml）

内容包含：
- 7个模块职责说明
- 4个核心业务域描述
- 关键接口约定（ApiResult/Swagger/Lombok/Lion）
- 24个外部 client 列表

**步骤 2**：首次使用时提供服务说明书链接，Pipeline 自动记忆，后续无需重复。

### 5.3 日常使用

```
# 最简触发
开始做需求：<需求描述>

# 推荐触发（减少追问）
开始做需求：<需求描述>
学城父文档 ID：<id>
关联服务说明书：<已记忆，可省略>
```

---

## 六、宏观视角：这不只是工具，是工作方式的重构

### 6.1 LinkedIn 经验的核心判断

Ryan Roslansky 说：

> "AI 不只是一个技术项目。它是一场文化转型。而文化，是从你如何花费时间、如何奖励他人、如何设定期望开始的。"

Pontos Pipeline v2 的设计，不只是"让 AI 帮写代码"，而是在重新定义**研发的工作方式**：

- **研发的时间** → 从"写代码"转向"架构决策 + 质量把关"
- **研发的奖励** → 不是代码行数，而是需求交付质量和架构合理性
- **研发的期望** → 成为 Full Stack Builder，一个人能完成完整的需求交付

### 6.2 三类任务的重新分工

基于"工作图"框架，Pontos 研发的任务重新分配：

```
AI 独立完成（Pipeline 自动化）：
  PRD 初稿、复杂度评估、模块识别、接口设计初稿
  代码实现（Sub-agent）、Commit Message、测试用例生成
  Code Review（AI 先做一轮）、提测单创建、交付报告

人机协作完成（Checkpoint 确认）：
  技术方案评审（AI 生成，人确认架构合理性）
  DDL 方案评审（AI 生成，人确认安全性）
  覆盖率不达标时的决策（补测试 or 豁免）
  PR Review（AI 先做，人做最终判断）

只有人能完成（Pipeline 不替代）：
  业务优先级判断（哪个需求更重要）
  隐性约束识别（只有熟悉系统的人才知道的坑）
  跨团队沟通与对齐
  技术债务的权衡决策
```

### 6.3 采用路径：主动叙事管理 + 30-60-90 框架

LinkedIn 的经验明确指出：**转型需要载体，不只是倡导**。"让流程自己说话"是不够的——你需要主动的叙事管理，否则威胁性叙事会填满空间。

Roslansky 在《Open to Work》中提出了一套结构化的采用框架：

| 阶段 | 时间 | 行动 | Pontos 对应 |
|---|---|---|---|
| **评估** | 前 30 天 | 把工作拆解为具体任务，逐一判断 AI 可替代程度 | 团队负责人先用 Pipeline 跑一个真实需求，感受哪些阶段 AI 做得好、哪些需要人判断 |
| **建立** | 第 31-60 天 | 主动强化人类核心能力，识别自己的"情境知识" | 在 Checkpoint 中刻意练习架构判断，把 AI 释放的时间用于技术债务评估和系统设计 |
| **行动** | 第 61-90 天 | 从个人实验进入团队结构性调整 | 在团队内分享 Pipeline 使用经验，建立可见性机制（参考 LinkedIn Company Connect）|

**关键顺序**：负责人的个人实验先行，团队层面的推广随后。反过来往往适得其反。

**Pontos 团队的可见性机制建议**：
- 每次用 Pipeline 完成的需求，在交付报告（Stage 9）中公开耗时数据
- 第一个完整走完 Pipeline 的需求，在团队内做 5 分钟分享（不是培训，是建立参照）
- Checkpoint 的确认回复，要让研发感受到"我的架构判断被记录在案"，而非"走审批流程"

**Pipeline 本身就是最好的载体**——但它需要人来激活它的可见性。

---

## 七、待验证假设（下一步）

| 假设 | 验证方式 |
|---|---|
| 员工能在 2 分钟内完成触发 | 用一个真实需求走一遍 Stage 0-1 |
| 技术方案 Checkpoint 不超过 10 分钟 | 记录员工从收到通知到回复的时间 |
| 覆盖率门控不会成为流程瓶颈 | 统计触发覆盖率阻断的频率 |
| Full Stack Builder 模式减少跨人协作成本 | 对比 Pipeline 前后的需求交付周期 |

---

*v2 完成。从 LinkedIn AI 转型实践（Ryan Roslansky）提炼五个 Pipeline 相关洞察：工作图（人工介入节点设计）、Squad制（消除跨人协作摩擦）、Full Stack Builder（研发角色重定义）、六周冲刺（Checkpoint 作为假设验证）、叙事管理（主动采用机制）。融入 Pontos 技术栈约束（7模块/MirrorFlow状态机/Lion开关），形成可直接落地的研发流程设计。*
