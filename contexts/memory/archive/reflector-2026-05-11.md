# Reflector Summary — 2026-05-11

## 晋升内容

### 晋升到 rules/workflows/

1. **`bestpractice_ai_debugging_diagnosis.md`（追加）**
   - 新增"ES Sniffer 启动报错快速分类"章节
   - 来源：2026-04-21 🔴 ES Sniffer TimeoutException vs ClassNotFoundException 判断框架
   - 核心内容：TimeoutException = 网络层超时（非版本冲突），poros-client 移除导致节点注入丢失

2. **`bestpractice_tidb_batch_write.md`（新建）**
   - 来源：2026-04-27、2026-05-06、2026-05-08、2026-05-09 共 4 条 🔴 条目
   - 核心内容：batch size ≤200 约束、rewriteBatchedStatements 两大陷阱、multi-row INSERT/upsert 显式构造模式、写入瓶颈排查框架

3. **`bestpractice_spark_rdd_pitfalls.md`（新建）**
   - 来源：2026-05-08 🔴/🟡 条目（DataSinker docAcc 重复累加、BladeBulkloadExporter 冗余 count、HermesImporter 每行 new CSVParser）
   - 核心内容：RDD 未 persist 导致多次 Action 重复计算、Accumulator 值翻倍诊断、冗余 count() 消除

4. **`bestpractice_mysql_json_column.md`（新建）**
   - 来源：2026-05-08 🔴 MySQL JSON 列空字符串报错
   - 核心内容：json_extract() 对空字符串报错（对 NULL 容忍）、NULLIF 修复模式

5. **`INDEX.md`（更新）**
   - 新增上述 3 个 bestpractice 文件的索引条目
   - 更新 bestpractice_ai_debugging_diagnosis.md 的描述

### 未晋升到 rules/ 的 🔴 条目（项目特定，不具普适性）

- Athena CuratorCache master 感知失效（分布式 ZK 特定 bug，不通用）
- Pontos getDefaultMirrorColumnDataType 类型映射 bug（项目特定代码缺陷）
- Poros SDK 流量组配置 v2 设计（项目架构决策，非通用方法论）
- Pontos Blade 容量感知选择（项目特定部署约束）

## GC 结果

OBSERVATIONS.md 从 **224 行**减少到 **178 行**（减少 46 行）。

删除内容：
- 所有 🟢 Low 任务流水条目（已归档）
- 重复出现的 KB 待办逾期条目（保留最新一条，删除 2026-04-23/04-27/05-05/05-06/05-07 的重复版本）
- 2026-04-21 OMO 分享文档重复条目（与 04-20 重复）
- 2026-05-05 无工作 session 条目（已归档）

保留内容：
- 所有 🔴 High 技术约束（永久有效）
- 活跃项目的关键 🟡 Medium 条目
- 最新一条 KB 待办逾期（2026-05-08/05-09，问题仍存在）

## 归档结果

新建 3 个归档文件：

| 文件 | 内容 | 归档条目数 |
|------|------|-----------|
| `archive/2026-04-20.md` | 2026-04-20 至 04-22、04-26 的已完结项目状态 | 6 条 |
| `archive/2026-04-27.md` | 2026-04-27 至 04-28 的已完结 skill 创建/发布记录 | 6 条（含 🟢） |
| `archive/2026-05-04.md` | 2026-05-05 至 05-09 的已完结项目状态和任务流水 | 11 条（含 🟢） |

归档判断依据：
- 已完成的功能开发（BatchUpdatePackage Crane Job、multiReaderDataSources、blade-multi-row-insert）
- 已发布的 skill（datamatrix-diff、omo-multiagent-architecture 草稿）
- 已完成的项目阶段（Notes Karpathy Wiki 清理阶段）
- 所有过期 🟢 任务流水

## Skill 草稿

生成 1 个草稿：

- `DRAFT_20260511_tidb-blade-batch-write.md` — TiDB/Blade 批量写入操作手册（触发词：Blade 写入、rewriteBatchedStatements、batch size、INSERT IGNORE、upsert）

跳过（不满足"≥2个不同日期"条件）：
- Poros 路由策略（ES5 vs ES7）— 仅 2026-05-09 出现一次
- PowerMock + mockito-inline 兼容性 — 仅 2026-05-08 出现一次
- Athena CuratorCache — 仅 2026-04-23 出现一次

已有 skill 覆盖：
- datamatrix-diff、datamatrix-das-slow-query — 已正式发布

## 备注

- 现有草稿：`DRAFT_20260427_omo-multiagent-architecture.md`（上次 reflector 生成，尚未确认发布）
- KB 待办逾期问题（Lion cluster 字段、naiads/joiner contentId、P3 摘要）已持续 23 天，建议用户主动处理或决定是否关闭
- DataMatrix 迁移进度、Eagle SDK 可观测性项目状态保留在 OBSERVATIONS.md（活跃项目，未完结）
