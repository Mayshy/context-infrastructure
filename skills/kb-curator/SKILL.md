---
name: kb-curator
description: >
  项目知识库（KB）维护操作手册。当用户要求"更新知识库"、"整理 KB"、"KB 健康度检查"、
  "补充踩坑记录"、"给新服务建档"、"评估 KB 质量"时使用。
  也适用于：AI 在 session 结束时主动维护 KB、从 session 对话中提炼 gotchas。
triggers:
  - 更新知识库
  - 整理 KB
  - KB 健康度检查
  - 补充踩坑记录
  - 给新服务建档
  - 评估 KB 质量
  - 这个踩坑记一下
  - 更新一下 KB
---

# KB Curator — 知识库维护操作手册

## 一、KB 位置与结构

### DataMatrix KB
```
~/.config/opencode/contexts/projects/datamatrix-kb/
├── 00_overview/          # 架构总览、服务图、技术栈
├── 01_services/{svc}/    # 各子服务：design.md + gotchas.md
├── 02_km_summaries/      # 学城文档摘要（含原文链接）
├── 03_requirements/      # 产品需求 + ADR 决策记录
├── 04_cross_cutting/     # 跨服务规范（血缘/Eagle/部署）
├── 05_runbooks/          # 操作手册（ES 索引、Spark 调试）
├── 06_migration/         # 老云搜迁移专项
└── AGENTS.md             # KB 使用指南 + 维护历史
```

### Eagle SDK KB
```
~/.config/opencode/contexts/projects/eagle-sdk-kb/
```

---

## 二、触发规则（何时主动维护）

### 必须立即写入 KB 的场景

| 场景 | 写入位置 | 格式 |
|------|---------|------|
| 踩到坑（现象+原因+解决方案） | `01_services/{svc}/gotchas.md` | `## [YYYY-MM-DD] 标题` |
| 做了架构决策（有取舍权衡） | `03_requirements/decisions/YYYYMMDD_title.md` | ADR 格式 |
| 读完一篇学城设计文档 | `02_km_summaries/{topic}.md` | 摘要格式 |
| 发现代码与 KB 描述不符 | 对应 design.md | 用 `[UPDATED]` 标注 |
| 新服务加入工作区 | 新建 `01_services/{svc}/` | 见第三节 |

### Session 结束时的主动检查

每次涉及代码改动的 session 结束前，检查：
1. 是否有踩坑未记录？（报错、意外行为、配置陷阱）
2. 是否有架构决策未记录？（选择了方案A而非方案B，原因是什么）
3. 是否有 KB 内容被本次工作证明过时？

---

## 三、新服务建档流程

当一个新服务加入工作区（如 naiads、joiner），按以下顺序建档：

### Step 1：快速探索代码结构
```bash
ls /Users/shenhuayu/Desktop/Project/{service}/
cat /Users/shenhuayu/Desktop/Project/{service}/README.md
cat /Users/shenhuayu/Desktop/Project/{service}/pom.xml | grep -E "<groupId>|<artifactId>|<version>" | head -10
```

### Step 2：创建 design.md（最小可用版）

文件路径：`01_services/{svc}/design.md`

必须包含的字段：
- **定位**：这个服务是什么，解决什么问题
- **与其他服务的关系**：上下游是谁
- **模块结构**：顶层目录说明
- **入口类**：启动入口在哪
- **技术栈**：框架、中间件
- **代码路径**：`/Users/shenhuayu/Desktop/Project/{svc}/`
- **重要说明**：任何需要特别注意的背景（如"这是老系统，不是新 DataMatrix"）

### Step 3：创建空 gotchas.md

```markdown
# {svc} — 踩坑记录

> 记录实际开发中遇到的问题和解决方案。

---

（待积累）
```

### Step 4：更新 AGENTS.md 子服务表

在 `AGENTS.md` 的子服务表中追加新服务行，包含：目录名、职责说明、学城 contentId（如有）。

### Step 5：更新 WORKSPACE.md 或 service_map.md

如果新服务影响整体服务图，更新 `00_overview/service_map.md`。

---

## 四、gotchas.md 写作规范

好的 gotchas 必须包含三要素：

```markdown
## [YYYY-MM-DD] 一句话描述现象

**现象**：触发条件是什么，看到了什么报错或异常行为。

**原因**：根本原因（代码层面，不是猜测）。

**解决**：具体操作步骤或配置修改。

**注意**：（可选）相关的边界条件、降级行为、后续风险。
```

**不好的 gotchas（避免）：**
- 只写"修复了 XXX bug"（没有现象和原因）
- 只写配置修改（没有说明为什么要这样配）
- 写了解决方案但没写触发条件

---

## 五、KB 健康度评估

快速评估一个 KB 的质量：

### 检查清单

```
[ ] 每个子服务都有 design.md 且内容非占位符
[ ] 每个子服务都有 gotchas.md（哪怕只有一条）
[ ] AGENTS.md 子服务表与实际代码目录一致
[ ] 02_km_summaries/ 覆盖了所有 P0/P1 学城文档
[ ] 04_cross_cutting/ 关键规范已填充（不是占位符）
[ ] 05_runbooks/ 有至少一个可操作的手册
[ ] AGENTS.md 维护历史"下一步"中无超过 30 天的待办
```

### 质量信号

**高质量 KB 的特征：**
- gotchas.md 有 3 条以上真实踩坑（说明 KB 在被使用）
- design.md 包含"入口类"和"关键路径"（AI 可以直接定位代码）
- 维护历史记录了"关键认知"而非只有"完成内容"

**低质量 KB 的特征：**
- 大量 `[TODO: 待填充]` 占位符
- design.md 只是学城文档的复制粘贴
- gotchas.md 为空或只有一行"待积累"

---

## 六、学城文档摘要规范

读完一篇学城文档后，生成摘要存入 `02_km_summaries/{topic}.md`：

```markdown
# {主题} — 学城摘要

> 学城原文：https://km.sankuai.com/collabpage/{contentId}
> 摘要日期：YYYY-MM-DD
> 摘要质量：P0/P1/P2（重要性分级）

---

## 核心定位

（一句话说清楚这个文档讲什么）

## 关键设计

（最重要的 3-5 个设计决策，用 bullet）

## 接口/数据结构

（如有，列出关键接口签名或数据结构）

## 与其他服务的关系

（上下游依赖）

## 注意事项

（坑、限制、特殊约定）
```

---

## 七、ADR（架构决策记录）格式

文件路径：`03_requirements/decisions/YYYYMMDD_{title}.md`

```markdown
# ADR-{序号}: {决策标题}

- **日期**：YYYY-MM-DD
- **状态**：已接受 / 已废弃 / 待定
- **决策者**：shenhuayu

## 背景

为什么需要做这个决策？面临什么问题？

## 决策

选择了什么方案？

## 考虑过的替代方案

| 方案 | 优点 | 缺点 | 放弃原因 |
|------|------|------|---------|
| 方案A（已选） | ... | ... | — |
| 方案B | ... | ... | ... |

## 影响

这个决策会带来什么后果？哪些地方需要注意？
```

---

## 八、常见操作速查

### 追加一条 gotcha
```bash
# 直接 append，避免全文编辑大文件
cat >> ~/.config/opencode/contexts/projects/datamatrix-kb/01_services/pontos/gotchas.md << 'EOF'

## [2026-XX-XX] 标题

**现象**：...
**原因**：...
**解决**：...
EOF
```

### 检查哪些文件是占位符
```bash
grep -r "TODO: 待" ~/.config/opencode/contexts/projects/datamatrix-kb/ --include="*.md" -l
```

### 检查 AGENTS.md 维护历史中的逾期待办
```bash
# 手动查看最近几次 session 的"下一步"部分
grep -A 5 "下一步" ~/.config/opencode/contexts/projects/datamatrix-kb/AGENTS.md
```
