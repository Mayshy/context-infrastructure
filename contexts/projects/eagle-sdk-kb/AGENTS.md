# Eagle SDK KB — AI 使用指南

> 这是 Eagle SDK 工作区（Poros 及相关客户端）的知识库，供 AI assistant 在处理相关任务时参考。  
> **本 KB 是代码分析和学城文档的 AI 可读摘要，不是权威来源。**

---

## 快速定位

| 需求 | 查看文件 |
|------|---------|
| 理解整体架构和请求流程 | `00_overview/architecture.md` |
| 了解各模块职责和核心类 | `00_overview/module_map.md` |
| 了解技术栈和关键配置 | `00_overview/tech_stack.md` |
| poros-service 代理服务设计 | `01_modules/poros-service/design.md` |
| poros-high-level-client SDK 设计 | `01_modules/poros-high-level-client/design.md` |
| poros-client 低层构造器 | `01_modules/poros-client/design.md` |
| poros-common 共享基础层 | `01_modules/poros-common/design.md` |
| 高风险查询拦截特性 | `03_features/high_risk_query_throttle.md` |
| 熔断器特性 | `03_features/circuit_breaker.md` |
| DSL 过滤特性 | `03_features/dsl_filter.md` |
| 学城文档摘要（含原文链接） | `02_km_summaries/INDEX.md` |
| **验收标准 / Definition of Done** | `definition_of_done.md` |

---

## 代码位置

```
/Users/shenhuayu/Desktop/Project/poros/
├── poros-common/          # 共享基础层（发布）
├── poros-client/          # 低层客户端构造（发布）
├── poros-high-level-client/  # 对外主要 SDK（发布，多版本）
├── poros-service/         # 代理服务（不发布，部署态）
├── poros-elasticsearch-plugin/  # ES 插件（不发布）
└── poros-java-api-client/ # 生成的 API 客户端
```

### eagle_meta 聚合工作区

```
/Users/shenhuayu/Desktop/Project/eagle_meta/
├── poros/                    # symlink → poros/
├── es5-client/               # symlink → es5-client/
├── TestEagleClient/          # symlink → TestEagleClient/
├── logcenter-esclient/       # symlink → logcenter-esclient/（日志中心 ES 客户端）
├── logcenter-elasticsearch/  # symlink → log/elasticsearch（日志 SDK logcenter-esclient 对应的 ES 底层包源码）
└── kb/                       # symlink → eagle-sdk-kb/
```

> `logcenter-elasticsearch` 是 `logcenter-esclient` 所依赖的 ES 底层包的源码，对应 `/Users/shenhuayu/Desktop/Project/log/elasticsearch`。

---

## 学城文档访问

```bash
oa-skills citadel getMarkdown --contentId {id} --mis shenhuayu
oa-skills citadel getChildContent --contentId {id} --mis shenhuayu
```

**学城根目录**: https://km.sankuai.com/collabpage/1127183403（contentId: 1127183403）

---

## 使用原则

1. **先查本 KB**，再查学城原文，最后查代码
2. 本 KB 的摘要可能滞后于代码，关键实现以代码为准
3. 发现本 KB 内容过时时，用 `[TODO: 需更新]` 标注

---

## KB 当前完成度（2026-04-20 更新）

| 模块 | 状态 |
|------|------|
| 00_overview（架构/模块图/技术栈） | ✅ 完整 |
| 01_modules/poros-service/design.md | ✅ 完整 |
| 01_modules/poros-high-level-client/design.md | ✅ 完整 |
| 01_modules/poros-client/design.md | ✅ 完整 |
| 01_modules/poros-common/design.md | ✅ 完整 |
| 01_modules/poros-elasticsearch-plugin/design.md | ✅ 完整 |
| 03_features/high_risk_query_throttle.md | ✅ 完整 |
| 03_features/circuit_breaker.md | ✅ 完整 |
| 03_features/dsl_filter.md | ✅ 完整 |
| 02_km_summaries（学城文档摘要） | ✅ 7/7 已完成 |
| 04_cross_cutting/deployment_ops.md | ✅ 完整（部署与运维规范） |
| 05_runbooks/troubleshooting.md | ✅ 完整（故障排查手册） |
| 05_runbooks/version_upgrade.md | ✅ 完整（版本升级手册） |

---

## KB 维护规则

| 触发事件 | 动作 |
|----------|------|
| 读完一篇学城设计文档 | AI 生成摘要 → 存入 `02_km_summaries/{name}.md` |
| 踩到坑 / 解决难题 | 追加到对应模块 `gotchas.md` |
| 做了架构决策 | 创建 ADR → `04_cross_cutting/decisions/YYYYMMDD_title.md` |
| 发现代码与 KB 不符 | 更新 KB，标注 `[TODO: 需更新]` |
| 每月一次 | 回顾 KB，删除过时内容 |

---

## 维护历史

### 2026-04-20（Session 3）— KB 补全

**完成内容**：
- `02_km_summaries/arts_client.md`：Arts 客户端完整摘要（v1/v2 对比、依赖配置、升级参数变更）
- `02_km_summaries/snapshot_client.md`：实验性 Poros 客户端摘要（Snapshot 版本说明）
- `02_km_summaries/log_client.md`：日志客户端摘要（学城原文为空，记录已知信息）
- `02_km_summaries/performance_test.md`：客户端性能测试摘要（学城原文为空）
- `02_km_summaries/client_features.md`：客户端特性说明摘要（学城原文为空，从代码整理）
- `04_cross_cutting/deployment_ops.md`：部署与运维规范（模块发布情况、定时任务、Lion 配置、版本选择指南）
- `05_runbooks/troubleshooting.md`：故障排查手册（鉴权失败/限流/高风险查询/熔断器/包冲突/Jackson 内存泄漏）
- `05_runbooks/version_upgrade.md`：版本升级手册（poros-high-level-client/arts-client v1→v2/Snapshot 规范）

**关键认知（本次新增）**：
- Arts 客户端 v2 最新版本为 6.0.2（学城记录为 6.0.2，之前 KB 记录为 6.0.1，已更正）
- 3 篇学城文档（性能测试 2542107392、特性说明 1560978827、日志客户端 2727344046）均为空页
- 实验性 Poros 客户端文档（1201253124）内容较少，仅记录了 ES5 版本的 Snapshot 示例

---

### 2026-04-07（Session 2）— 知识飞轮第一轮

**完成内容**：
- `02_km_summaries/poros_java_api_client.md`：Poros Java API Client（ES8）学城文档摘要（contentId: 2293336777）
- `02_km_summaries/es7_compat_es8.md`：ES7 客户端兼容 ES8 学城文档摘要（contentId: 2131195847）
- `01_modules/poros-elasticsearch-plugin/design.md`：ES 插件设计文档（从代码分析）

**关键发现**：
- `poros-java-api-client` 只支持 ES8，与 RHLC 共存时包路径冲突需用全路径区分
- Jackson 2.17.0 有内存泄漏 bug，必须用 2.17.2
- `poros-elasticsearch-plugin` 只有 2 个 Java 文件：Plugin 入口 + AuthenticationService
- Eagle API 故障时插件采用宽松模式（放行），可用性优先
- MWS header 缓存 key 只取 appKey 前缀（冒号前），避免签名变化导致缓存失效
- 授权撤销最多 10 分钟延迟（`AuthorizationRechecker` 周期）

---

### 2026-04-07（Session 1）— 初始化

**完成内容**：
- 目录结构初始化
- `00_overview/`：architecture.md、module_map.md、tech_stack.md
- `01_modules/`：poros-service、poros-high-level-client、poros-client、poros-common 的 design.md
- `03_features/`：high_risk_query_throttle.md、circuit_breaker.md、dsl_filter.md
- `02_km_summaries/INDEX.md`：学城文档目录索引
- git init + AGENTS.md

**关键发现**：
- poros-high-level-client 有三个版本（5.6.3 / 6.8.10 / 7.10.0），通过环境变量切换
- `org.elasticsearch.client` 包下是 fork 的 ES 客户端，目的是访问 package-private API
- `CircuitBreakerFilter` 同时实现 `Filter<ESRequest>` 和 `CircuitBreakerBiz` 两个接口
- `ResponseConstructor` 和 `RestClientPorosImpl` 都使用反射访问 package-private 构造器，ES 版本升级时需要注意
- Arts 客户端（v1）底层依赖 poros-high-level-client；v2 依赖 poros-java-api-client，更轻量但不支持限流特性
