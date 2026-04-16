# WORKSPACE.md - 目录路由速查

目标：让 AI 每轮 session 都能快速知道"去哪里找/放什么"。**找任何文件前先查这里。**

## 路由规则

### 项目与代码
- 写代码 / 跑脚本 / 一次性项目：`adhoc_jobs/<project>/`
- 工具脚本（邮件、语义搜索、分享报告等）：`tools/`
- 定时任务：`periodic_jobs/`

### 知识与记录
- 通用调研报告：`contexts/survey_sessions/`
- 思考 / 复盘 / 方法论：`contexts/thought_review/`
- 每日日志：`contexts/daily_records/`

### 系统与规则
- **Workflows**（工作流程型）：`rules/workflows/`
  - 定位：复杂任务流程、方法论、认知沉淀
  - 调用方式：直接 Read 文件内容，边理解边执行
  - 格式：`workflow_*.md`、`bestpractice_*.md`
- **Skills**（工具型）：`~/.config/opencode/skills/`
  - 定位：工具操作手册，CLI / API 调用
  - 调用方式：`skill({ name: "xxx" })`
  - 格式：`SKILL.md`（含 YAML frontmatter）
- 核心公理（Axioms）：`rules/axioms/`
- 记忆系统：`contexts/memory/` + `periodic_jobs/ai_heartbeat/`

## 命名规则
- 目录和文件名：小写 + 下划线 (snake_case)
- 临时一次性项目：`tmp_<name>/`

## Python 环境
- 根目录 `.venv/` 为工作区级环境，用 `uv pip install` 管理依赖
- 需要隔离时在 `adhoc_jobs/<project>/.venv/` 建独立环境
- **Cron 脚本注意**：cron 任务使用系统 Python（`/usr/bin/env python3`），不继承 `.venv`。若脚本依赖 `.venv` 中的包（如 `dotenv`），shebang 必须改为 `.venv/bin/python`，或在 cron 调用前 `source .venv/bin/activate`。否则会静默失败（`ModuleNotFoundError`）。

## 快速查询

<!-- 随着你的项目增长，在这里添加活跃项目的快捷路由 -->
<!-- 格式：- `project-name` → `adhoc_jobs/project_name/` (说明) -->

## 活跃项目路由

### Poros（美团 ES 代理/网关服务）
- **KB(知识库) 本地路径**：`~/.config/opencode/contexts/projects/poros-kb/`（Markdown+Git 为 AI 工作层，该知识库和本地代码仓库比学城更具时效性）
- **代码根目录**：`~/Desktop/Project/poros/`
- **子模块**：poros-common、poros-client、poros-high-level-client、poros-service、poros-elasticsearch-plugin、poros-java-api-client
- **技术栈**：Java 8 + Guice + Netty + ES Client fork（无 Spring）
- **学城文档根**：https://km.sankuai.com/collabpage/1127183403（contentId: 1127183403）


### DataMatrix（美团云搜数据平台）
- **KB(知识库) 本地路径**：`~/.config/opencode/contexts/projects/datamatrix-kb/`（Markdown+Git 为 AI 工作层，该知识库和本地代码仓库比学城更具时效性）
- **代码根目录**：`~/Desktop/Project/` 下各子服务目录（已授权直接访问）
- **子服务**：pontos（数据集成）、athena（数据建模）、hermes（数据计算）、kugget（数据质量）、worksheet（工单）
- **技术栈**：Java/Spring Boot + Blade + Flink/Spark + ES8 + HBase + Pigeon
- **学城文档根**：https://km.sankuai.com/collabpage/2708001137（contentId: 2708001137）
- **调研报告**：`contexts/survey_sessions/datamatrix_kb_selection_20260405.md`
