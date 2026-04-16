# 调研报告 v1：AI at Work — Pipeline AI Workflow 适配 Datamatrix 研发流程

> **版本**: v1（初稿）
> **日期**: 2026-04-15
> **作者**: AI 辅助调研
> **状态**: 草稿，待 v2 深化

---

## 一、调研背景

### 1.1 目标

探索并适配美团内部 **Pipeline AI Workflow**（研发全生命周期工作流自动化框架）到 **Datamatrix（Pontos）** 项目，定义 Pontos 团队的 AI 研发新范式。

### 1.2 信息来源

| 来源 | 说明 |
|---|---|
| [Pipeline AI Workflow 官方文档](https://km.sankuai.com/collabpage/2751469808) | 框架原理、阶段设计、安装使用指南 |
| Pontos 代码库（`/Users/shenhuayu/Desktop/Project/pontos`） | 项目结构、模块职责、开发模式 |
| `AGENTS.md` | Pontos 编码规范、测试约定、模块依赖 |
| codebase explore 分析 | 51个测试类、23个 controller、35个 service、4个 crane、12个 handler |

---

## 二、Pipeline AI Workflow 核心解析

### 2.1 框架定位

Pipeline AI Workflow 是一个**研发全生命周期工作流自动化框架**，运行在美团 AI Agent 平台（CatClaw/CatDesk/CatPaw）上。

**核心理念**：把研发交付流程的每个阶段变成可执行的自动化节点，通过声明式 DAG 串联成端到端流水线。从需求分析开始，到最后交付报告，十个阶段自动衔接，每个阶段完成后自动写入学城文档。

### 2.2 四层架构

```
┌─────────────────────────────────────────────────────────────┐
│                  Pipeline AI Workflow                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │  Skills   │  │  Agents  │  │  Hooks   │  │   Lib    │    │
│  │ (24 个)   │  │ (13 个)  │  │ (6 个)   │  │ (基础层)  │    │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘    │
│       ↕              ↕             ↕              ↕          │
│  ┌─────────────────────────────────────────────────────┐    │
│  │        Workflow DAG (声明式阶段图)                     │    │
│  │  Stage 0→1→2→3→4→[5∥6]→7→8→9                       │    │
│  └─────────────────────────────────────────────────────┘    │
│       ↕                                                      │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Platform Adapter (CatPaw/Claude/Codex/CatDesk/CatClaw)  │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

### 2.3 十个阶段

```
Stage 0  初始化           → 状态初始化、依赖检查
Stage 1  需求分析          → PRD + 复杂度评估 + 评审意见 [Checkpoint]
Stage 2  技术方案          → 服务识别 + 架构设计 + 方案评审 [Checkpoint]
Stage 3  MEP 分支管理      → feature 分支创建 + 工作项关联
Stage 4  编码实现          → 实施计划 + 单测覆盖报告（增量覆盖率 ≥ 60% 门控）
Stage 5  提交 & PR         → Commit + PR + Code Review（与 Stage 6 并行）
Stage 6  生成测试用例      → 正常/边界/异常场景（与 Stage 5 并行）
Stage 7  提测              → 提测单
Stage 8  自动化测试        → 自动化测试报告
Stage 9  交付报告          → 汇总产出 + 大象群通知
```

### 2.4 与传统 CI/CD Pipeline 的核心区别

| 维度 | 传统 Pipeline（CI/CD） | Pipeline AI Workflow |
|---|---|---|
| 覆盖范围 | 代码提交后（构建→部署） | 需求到提测全链路（10个阶段） |
| 触发方式 | 代码 push 自动触发 | 一句话："开始做需求，需求是 XXX" |
| 需求分析 | ❌ 不涉及 | ✅ AI 生成 PRD，自动识别歧义 |
| 服务识别 | ❌ 手工决定改哪个仓库 | ✅ 三轮评分自动判定 Owner/Contributor |
| 编码实现 | ❌ 全靠研发自己写 | ✅ TDD + Sub-agent 并行实现，双轮 Review |
| 覆盖率管控 | ⚠️ 仅 CI 阶段检查 | ✅ 五层防线，从任务级到 PR 级 |
| 测试用例 | ❌ QA 经验覆盖 | ✅ AI 基于 PRD 生成全场景 |
| 文档沉淀 | ⚠️ 需手动写 | ✅ 每阶段自动写学城 |
| 断点续跑 | ✅ 支持（CI 失败重试） | ✅ 支持（从阶段 N 继续） |
| 智能化程度 | 低（规则触发，结果确定） | 高（理解上下文，动态调整策略） |

---

## 三、Pontos 项目特征分析

### 3.1 项目概览

```
appkey:       com.sankuai.eagle.dataserver
部署模块:      pontos-server（Spring Boot fat jar，HTTP 8080 / Thrift 8411）
CI/CD:        Meituan XFrame 平台（plusboot.yaml）
配置中心:      Lion（com.dianping.lion.client.Lion）
数据库:        Zebra MySQL Proxy
消息队列:      Mafka
外部依赖:      Hermes / DTS / DMX / Octo / Worksheet / RTSla / Cantor / Iris（24个 Retrofit client）
```

### 3.2 七模块职责映射

| 模块 | 职责 | 需求触发条件 |
|---|---|---|
| `pontos-server` | REST + Thrift 主服务 | 几乎所有需求 |
| `pontos-dao` | MyBatis/tk-mapper 实体 + Mapper | 新增/修改 DB 表 |
| `pontos-common` | 工具类、通用模型 | 跨模块共享逻辑 |
| `pontos-dal` | Spark/HBase/DMX 数据访问 | 大数据存储读写 |
| `pontos-sdk` | Thrift IDL + 生成 SDK | 对外暴露新 RPC 接口 |
| `pontos-full-sync-job` | Spark 全量同步 Job | 全量同步逻辑变更 |
| `pontos-realtime-sync-job` | Flink 实时同步 Job | 实时同步逻辑变更 |

### 3.3 核心业务域

| 业务域 | 核心 Controller | 核心 Service |
|---|---|---|
| 数据源注册/管理 | `RegistrationController`, `DataSourceDetailController` | `IDataSourceService`, `IRegistrationService` |
| 数据镜像流 | `MirrorFlowController`, `MirrorConfigController` | `IMirrorFlowService`, `IMirrorConfigService` |
| 数据查询/血缘 | `DataQueryController`, `DataLineageController` | `IDataQueryService` |
| WorkSheet/Tag | `WorkSheetActionController`, `TagWorkSheetActionController` | `IWorkSheetService` |

### 3.4 标准 8 层开发路径

```
Entity (pontos-dao) → Mapper (pontos-dao) → Model/DTO (pontos-common)
→ IService (pontos-server) → ServiceImpl (pontos-server)
→ Client (pontos-server, 如需外部系统) → Controller (pontos-server)
→ Test (src/test/)
```

### 3.5 现有 AI 工作流基础

项目已有 `docs/superpowers/` 目录，包含：
- `specs/`：Feature 设计文档（问题、架构、接口定义）
- `plans/`：Step-by-step 实施计划（TDD 驱动，checkbox 任务）

参考案例：`docs/superpowers/plans/2026-04-10-flink-sla-offline-crane.md`

---

## 四、Pontos 定制化 Pipeline（v1）

### 4.1 整体流程 DAG

```
输入：需求描述 + 学城父文档 ID（+ 可选 MEP 工作项链接）

Stage 0  初始化
         ├─ 状态初始化、manifest 验证
         └─ 检查 pontos 服务说明书是否已配置

Stage 1  需求分析                                              [Checkpoint]
         ├─ PRD 生成
         ├─ Pontos 专属澄清问卷（5问）
         ├─ 复杂度评估（含 Crane/Flink/Spark 影响）
         └─ 输出：01-需求分析文档 → 写入学城

Stage 2  技术方案                                              [Checkpoint]
         ├─ 模块识别（7模块映射规则）
         ├─ 接口设计（REST + 可选 Thrift IDL）
         ├─ DDL 变更评估（触发 Zebra 迁移子流程）
         ├─ 外部 client 识别
         ├─ Lion 配置开关设计
         └─ 输出：02-技术方案 → 写入学城 + docs/superpowers/specs/

Stage 3  MEP 分支管理
         └─ 按受影响模块创建分支

Stage 4  编码实现
         ├─ 分层 TDD 顺序（8层标准路径）
         ├─ Pontos 规范门控（ApiResult/Swagger/Lombok）
         ├─ 覆盖率分层门控
         └─ 输出：03-实施计划 → docs/superpowers/plans/ + 学城

Stage 5  提交 & PR（与 Stage 6 并行）
         ├─ Commit（Angular 规范）
         ├─ PR 创建（多模块时按模块分 PR）
         └─ Code Review

Stage 6  生成测试用例（与 Stage 5 并行）
         ├─ 通用：正常/边界/异常
         └─ 镜像流需求：MirrorFlow 状态机流转矩阵

Stage 7  提测 → 06-提测单
Stage 8  自动化测试 → 05b-自动化测试报告
Stage 9  交付报告 → 07-交付报告 + 大象群通知
```

### 4.2 Stage 1 专属澄清问卷

AI 在需求分析阶段主动追问：

```
① 是否需要对外暴露 Thrift RPC 接口？（影响 pontos-sdk）
② 是否涉及调度任务（Crane）或新增定时逻辑？（影响 crane/ 包）
③ 是否涉及 Flink 实时同步 / Spark 全量同步逻辑？（影响 job 模块）
④ 是否需要新增 DB 表或修改现有表结构？（触发 DDL 子流程）
⑤ 是否需要对接新的外部系统？（影响 client/ 包）
```

### 4.3 Stage 2 模块识别规则

```
涉及 REST 接口             → pontos-server（Owner，必选）
涉及 Thrift 接口           → pontos-sdk + pontos-server/thrift/（必选）
涉及 DB 实体/Mapper        → pontos-dao（必选）
涉及 HBase/Spark/DMX       → pontos-dal（必选）
涉及全量同步逻辑            → pontos-full-sync-job（必选）
涉及实时同步逻辑            → pontos-realtime-sync-job（必选）
涉及跨模块共享工具/模型     → pontos-common（按需）
```

### 4.4 Stage 4 覆盖率分层门控

| 代码层 | 最低覆盖率 | 原因 |
|---|---|---|
| `handler/` | ≥ 80% | 状态机处理器，高风险 |
| `service/impl/` | ≥ 70% | 核心业务逻辑 |
| `controller/` | ≥ 60% | 接口层 |
| `crane/` | ≥ 60% | 调度逻辑 |
| `client/` | ≥ 50% | 外部依赖 |
| job 模块 | ≥ 50% | Spark/Flink 测试较难 |

### 4.5 Stage 6 MirrorFlow 状态机测试矩阵

```
正常流转：
  INIT → WAIT_DATASOURCE_READY → FULL_SYNC_INIT → FULL_SYNC_RUNNING
       → REALTIME_SYNC_CATCHUP → REALTIME_SYNC_RUNNING → SUCCESS

异常场景：
  □ 数据源未就绪超时 / 全量同步失败 / 实时追赶超时
  □ 版本切换失败回滚 / 并发触发幂等保护

边界场景：
  □ 空数据源 / 超大数据量 / 断点续传 / 手动 vs 自动竞态
```

---

## 五、与原版 Pipeline 差异总结（v1）

| 阶段 | 原版 | Pontos 定制 |
|---|---|---|
| Stage 1 | 通用 PRD + 复杂度 | +5问澄清问卷（Thrift/Crane/Job/DDL/外部系统）|
| Stage 2 | 微服务三轮评分 | 7模块映射规则 + DDL 子流程 + Lion 开关设计 |
| Stage 4 | 通用 TDD | 8层分层顺序 + 规范门控 + docs/superpowers/ 同步 |
| Stage 4 | 统一 60% 覆盖率 | 分层差异化（handler 80% / service 70% / job 50%）|
| Stage 5 | 单 PR | 多模块时按模块分 PR |
| Stage 6 | 通用测试矩阵 | +MirrorFlow 状态机流转专项矩阵 |
| 全程 | 通用 Commit | ApiResult/Swagger/Lombok/Lion 规范强制检查 |

---

## 六、待深化问题（v2 方向）

1. **自然使用体验**：如何降低员工使用门槛？触发方式是否足够自然？
2. **人工介入节点**：哪些 Checkpoint 需要人工确认？哪些可以自动通过？
3. **宏观视角融合**：LinkedIn AI 转型实践（工作图、六周冲刺、Full Stack Builder）对 Pontos 流程有何启示？
4. **文化落地机制**：如何让流程成为团队习惯，而非强制规范？

---

*v2 将基于 LinkedIn AI 转型实践（Ryan Roslansky / 穿越混乱的中间地带）的宏观视角进行深化。*
