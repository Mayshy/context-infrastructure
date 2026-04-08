# Memory Observations

这是三层记忆系统的 L1/L2 层。每日观察由 `periodic_jobs/ai_heartbeat/src/v0/observer.py` 自动写入，每周由 `reflector.py` 整理和蒸馏。

## 格式说明

每个日期条目格式如下：

```
Date: YYYY-MM-DD

🔴 High: [方法论/约束] 描述
🟡 Medium: [项目状态/决策] 描述
🟢 Low: [任务流水] 描述
```

### 优先级定义

- **🔴 High**：跨项目通用的经验教训、硬性约束、影响系统架构的重大决策。永久保留，候选晋升为 axiom 或 skill。
- **🟡 Medium**：活跃项目的关键进展、技术决策背景、未来几周仍需参考的信息。
- **🟢 Low**：日常任务流水、瞬时 debug 记录、临时上下文。定期垃圾回收。

## 如何加载记忆

不要全文加载这个文件（可能很大）。按需检索：

```bash
# 搜索特定主题
grep -n "关键词" contexts/memory/OBSERVATIONS.md

# 搜索最近 N 天
grep -A 20 "Date: $(date -v-7d +%Y-%m-%d)" contexts/memory/OBSERVATIONS.md
```

或使用语义搜索（`rules/skills/semantic_search.md`）做跨日期语义检索。

---

<!-- 以下是记录区域，由 observer.py 自动追加 -->

---

Date: 2026-04-05

🟡 Medium: [项目状态] DataMatrix KB 选型调研完成（v1.0）。结论已晋升至 WORKSPACE.md。下一步：初始化 ~/Desktop/Project/datamatrix-kb/ 目录结构 + 批量生成学城文档摘要。

---

Date: 2026-04-06

🟡 Medium: [项目状态] DataMatrix KB 大规模建设完成（3 个 Session，共 4 次 commit）。contexts/projects/datamatrix-kb/ 目录结构全部初始化，00_overview/（架构/服务图/技术栈）✅、01_services/ 全部 5 个子服务 design.md ✅、02_km_summaries/ P0+P1 共 8 篇摘要 ✅；仍待补充：P2/P3 摘要（6 篇）、03_requirements/product_backlog.md、04_cross_cutting/data_lineage.md、05_runbooks/。
🟡 Medium: [技术决策] kugget 服务职责已澄清：学城目录分类为"数据质量"有误，实为**索引服务平台**（appkey: com.sankuai.eagle.indexserver），负责索引 Schema 管理和计算任务 DAG，与 hermes 是兄弟服务。已在 contexts/projects/datamatrix-kb/AGENTS.md 中更正。
🟡 Medium: [项目状态] oh-my-openagent 深度调研完成，报告存档于 contexts/survey_sessions/oh_my_openagent_survey_20260405.md。核心结论：OMO 是基于 OpenCode 的多模型 agent 编排 harness，三层架构（Planning/Execution/Worker），按 category 路由模型而非硬编码模型名。
🟡 Medium: [项目状态] 中国大模型能力调研完成，报告存档于 contexts/survey_sessions/chinese_llm_survey_20260405.md。对比了 DeepSeek/Qwen/GLM/Kimi/MiniMax 5 家，MiniMax M2.7 因 Agent RL 特性被选为主力 sub-agent 模型。
🟡 Medium: [配置变更] oh-my-openagent.jsonc 已更新：sisyphus/hephaestus/prometheus/librarian/explore 均路由至 minimax/MiniMax-M2.7；oracle 和 ultrabrain/reasoning 类别保留 meituan/claude-sonnet-4-6；opencode.json 新增 minimax provider 配置（Anthropic 兼容接口）。
🟡 Medium: [项目状态] macOS terminal 效率工具调研完成，报告存档于 contexts/survey_sessions/macos_terminal_ai_dev_survey_20260405.md 和 contexts/survey_sessions/iterm2_terminal_ai_survey_20260405.md。高 ROI 工具：uv、Starship、fzf、bat+eza+rg+fd、Ghostty、tmux。
🔴 High: [架构约束] DataMatrix 的 ES 索引构建采用"Spark 离线构建快照 → S3 → 灰度切流"模式（而非 ES 直写），原因是直写会导致 CPU/IO 争抢和段文件膨胀。切换时副本从 S3 拉取（非从主分片复制），大幅降低主分片压力。这是该系统最核心的设计决策之一，影响所有 hermes 相关开发。

---

Date: 2026-04-08

🟡 Medium: [项目状态] Poros KB 全面初始化完成（2026-04-07，2 个 Session）。contexts/projects/poros-kb/ 目录结构建立：00_overview/（architecture、module_map、tech_stack）✅、01_modules/ 全部 5 个子模块 design.md ✅、03_features/（high_risk_query_throttle、circuit_breaker、dsl_filter）✅、02_km_summaries/ 已完成 2/7（poros_java_api_client、es7_compat_es8）⚠️；04_cross_cutting/ 和 05_runbooks/ 待写。
🟡 Medium: [技术决策] Poros 核心架构细节落地记录：poros-high-level-client 有 5.6.3/6.8.10/7.10.0 三版本通过环境变量切换；CircuitBreakerFilter 同时实现两个接口；ResponseConstructor/RestClientPorosImpl 使用反射访问 package-private 构造器（ES 升级时高风险）；Arts v1 依赖 poros-high-level-client，v2 依赖 poros-java-api-client（更轻量但不支持限流）。
🔴 High: [技术约束] Jackson 2.17.0 有内存泄漏 bug，必须使用 2.17.2。适用于 poros-java-api-client 及所有依赖它的服务。
🟡 Medium: [技术决策] poros-elasticsearch-plugin 故障降级策略：Eagle API 故障时采用宽松模式（放行请求），可用性优先于安全性；MWS header 缓存 key 只取 appKey 冒号前缀，避免签名变化导致缓存失效；授权撤销最多 10 分钟延迟（AuthorizationRechecker 周期）。
🟡 Medium: [项目状态] rules/WORKSPACE.md 新增 Poros 活跃项目路由条目，记录代码根目录、子模块列表、技术栈、学城文档根和 KB 本地路径（contexts/projects/poros-kb/）。
🟡 Medium: [新 Skill] skills/release-notes-updater/ 新建（2026-04-07 ~20:06），用于从 git commit range 提取变更并更新学城 release notes 文档（预置表格模板于 skills/release-notes-updater/references/table-template.md）。触发词：更新 release notes、把最近变更写进 release notes。
🟢 Low: [工具文档] contexts/survey_sessions/unix_file_read_cmd.md 新增：Unix 文件读取命令速查（less/more/cat/head/tail/grep/rg/find/fd/bat/vim/nano/sed/awk），整理了场景速查表和推荐工具链（bat、rg、fd、eza、fzf）。
