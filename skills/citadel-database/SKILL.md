---
name: citadel-database
description: "学城多维表格官方Skill。支持多维表格文档创建删除、数据表创建删除恢复重命名排序，数据增删改查。触发：表格、多维表格、批量操作表格数据、数据同步、数据收集、表格操作。"
metadata:
  openclaw:
    priority: 0
    conflict_strategy: override
    emoji: "📊"
    requires:
      bins: ["node", "npx"]
      deps: ["tsx", "@it/oa-skills"]
---

# 📊 学城多维表格 XTable 

学城多维表格操作工具，通过 CLI 快速创建、查询和管理多维表格数据。认证自动处理，支持批量操作。

## 核心特性

- ✅ **HTTP REST API**：直接使用 HTTP 接口，高效稳定
- ✅ **简洁的二维数组格式**：使用 `[["值1", "值2"]]` 格式操作数据，自动类型转换
- ✅ **完整的 CRUD**：支持创建、查询、更新、删除操作
- ✅ **Token 自动缓存**：认证信息自动保存，后续调用无需重复认证
- ✅ **支持筛选和排序**：灵活的数据查询能力

## 前置检查

### Node.js 版本检查

执行 xtable skill 时会自动检查 Node.js 版本是否符合要求（>= 18.0.0）。如果版本过低，系统会：

1. **自动检测并安装 nvm**（如未安装）
2. **通过 nvm 自动安装并切换到 Node.js 18 或更高版本**
3. **重新执行命令**，使用新的 Node.js 版本

**无需手动干预，版本升级完全自动化。** ✨

### CLI 版本检查

每次执行命令前，先检查 `@it/oa-skills` 是否为最新版本：

```bash
npm list -g @it/oa-skills --depth=0 2>/dev/null | grep oa-skills
```

如果未安装或版本不是最新，执行更新：

```bash
npm install -g @it/oa-skills --registry=http://r.npm.sankuai.com
```

**此步骤必须在每次 skill 激活时执行一次，否则新命令可能不存在导致运行失败。**

## 意图路由

| 用户意图                    | 命令                                    |
| -------------------------- | --------------------------------------- |
| 创建一个新的多维表格文档     | `createDatabase --contentTitle <标题> --tableTitle <表格>` |
| 在现有文档中创建新数据表     | `createTable --contentId <id> --tableTitle <表格>`      |
| 复制数据表到指定文档         | `copyTable --sourceTableId <源ID> --targetParentId <目标父文档ID>` |
| 查看文档下有哪些表格         | `listTables --contentId <id>`                          |
| 查询表格的列结构（columnId） | `getTableMeta --tableId <id>`                          |
| 查询表格中的数据             | `queryTableData --tableId <id> [--columnIds <列ID>] [--filter <条件>] [--sort <排序>]` |
| 向表格中添加新数据           | `addData --tableId <id> --columnIds <列ID> --data '[...]'` |
| 更新表格中的数据             | `updateData --tableId <id> --rowIds <行ID> --data '[...]'` |
| 删除表格中的数据             | `deleteData --tableId <id> --rowIds <行ID>`           |
| 重命名数据表                 | `renameTable --tableId <id> --title <新标题>`         |
| 数据表排序                   | `sortTable --tableId <id> --to <位置索引>`            |
| **查询用户信息（账号转换）** | `getUserInfo --misList '["mis1", "mis2"]'`             |

### 📝 文档级别操作（使用 citadel 命令）

对于以下**文档级别**的操作，请使用 `oa-skills citadel` 命令而非 `citadel-database`：

| 操作类型         | 命令                                                                 | 说明                           |
| --------------- | -------------------------------------------------------------------- | ------------------------------ |
| 删除文档         | `oa-skills citadel deleteDocument --contentId <id>`                  | 删除多维表格文档                |
| 恢复文档         | `oa-skills citadel restoreDocument --contentId <id>`                 | 从回收站恢复文档                |
| 移动文档         | `oa-skills citadel moveDocument --contentId <id> --targetParentId <目标ID>` | 移动文档到其他位置      |
| 获取划词评论     | `oa-skills citadel getFullTextComments --contentId <id>`             | 获取文档的划词评论              |

**原因**：`citadel-database` 专注于数据表和数据操作，文档级别的管理（删除/恢复/移动/评论）由 `citadel` 命令负责。

## CLI 速查

所有命令格式：`oa-skills citadel-database <command> [options]`

**📖 完整参数文档**：查看 `{baseDir}/references/cli-reference.md` 获取所有命令的详细参数说明、示例和工作流。

通用选项：
- `--mis <mis>` 指定用户（可选，默认从 `~/.config/clawdgw.json` 读取）
- `--raw` 输出 JSON 到 stdout
- `--clear-cache` 清除认证缓存
- `--force-ciba` 强制使用 CIBA 认证策略

| 命令                    | 必填参数                          | 可选参数                                  |
| ---------------------- | ------------------------------- | ---------------------------------------- |
| `createDatabase`       | `--contentTitle` `--tableTitle` | `--parentId` `--columnMeta` `--templateId` |
| `createTable`          | `--contentId` `--tableTitle`   | `--columnMeta` `--columnMetaFile` `--sourceTableId` |
| `copyTable`            | `--sourceTableId` `--targetParentId` | `--columnIds` `--rowIds` `--stepVersion` |
| `listTables`           | `--contentId`                  |                                          |
| `getTableMeta`         | `--tableId`                    |                                          |
| `queryTableData`       | `--tableId`                    | `--columnIds` `--filter` `--sort` `--pageSize` `--pageToken` |
| `addData`              | `--tableId` `--columnIds` `--data` | `--file` (从文件读取 data)           |
| `updateData`           | `--tableId` `--rowIds` `--columnIds` `--data` | `--file` `--rowIdsFile` |
| `deleteData`           | `--tableId` `--rowIds`         | `--rowIdsFile` (从文件读取 rowIds)   |
| `renameTable`          | `--tableId` `--title`          |                                          |
| `sortTable`            | `--tableId` `--to`             |                                          |
| `getUserInfo`          | `--misList`                    |                                          |
columnIds 格式：逗号分隔的列 ID（如 `"1,2,3"`），或 JSON 数组（如 `"[1,2,3]"`）

## 快速开始

### 常用命令示例

```bash
# 1. 创建多维表格文档
oa-skills citadel-database createDatabase \
  --contentTitle "项目管理" \
  --tableTitle "任务列表"

# 2. 查询表格元数据（获取列ID）
oa-skills citadel-database getTableMeta --tableId "456789"

# 3. 查询数据
oa-skills citadel-database queryTableData \
  --tableId "456789" \
  --columnIds "1,2,3"

# 4. 添加数据
oa-skills citadel-database addData \
  --tableId "456789" \
  --columnIds "1,2,3" \
  --data '[["任务A", 100, "进行中"]]'

# 5. 更新数据
oa-skills citadel-database updateData \
  --tableId "456789" \
  --rowIds "123" \
  --columnIds "3" \
  --data '[["已完成"]]'
```

**💡 提示**：
- `--mis` 参数可选，默认从配置文件读取
- **自动分页**：`addData` 和 `updateData` 在超过 500 行时自动分批处理
- **大数据量支持**：使用 `--file` 参数从 JSON 文件读取数据，避免命令行参数过长
- 更多示例和完整参数见 `{baseDir}/references/cli-reference.md`

## 复制数据表

`copyTable` 命令用于将数据表（结构和数据）复制到指定文档。

### 快速示例

```bash
# 复制整个表格
oa-skills citadel-database copyTable \
  --sourceTableId "456789" \
  --targetParentId "123456"

# 选择性复制列和行
oa-skills citadel-database copyTable \
  --sourceTableId "456789" \
  --targetParentId "123456" \
  --columnIds "[1,2,3]" \
  --rowIds "[100,101,102]"
```

**详细参数和用法**：参见 `{baseDir}/references/cli-reference.md` 的 copyTable 章节。

## 大数据量操作（--file 参数）

当需要添加、更新或删除大量数据时，使用 `--file` 参数从 JSON 文件读取数据，避免命令行参数过长。

**支持的命令**：`addData`、`updateData`、`deleteData`、`createTable`

**快速示例**：
```bash
# 准备数据文件
echo '[["员工001", 25, true]]' > data.json

# 使用文件参数
oa-skills citadel-database addData \
  --tableId "456789" \
  --columnIds "1,2,3" \
  --file data.json
```

**📖 详细说明**：参见 `{baseDir}/references/cli-reference.md` 获取完整的文件参数说明、格式要求和更多示例。

## 账号转换（MIS ↔ empId ↔ uid）

`getUserInfo` 命令用于批量查询用户信息，支持 MIS 到 uid/empId/姓名等字段的转换。

### 快速示例

```bash
# 查询用户信息
oa-skills citadel-database getUserInfo \
  --misList '["zhangsan", "lisi"]'

# 与人员列配合使用
# 步骤 1: 查询 empId
oa-skills citadel-database getUserInfo --misList '["zhangsan"]'
# 输出: empId: 2015738

# 步骤 2: 使用 empId 添加人员列数据
oa-skills citadel-database addData \
  --tableId "456789" \
  --columnIds "4" \
  --data '[[2015738]]'
```

**详细参数、返回字段说明和更多示例**：参见 `{baseDir}/references/cli-reference.md` 的 getUserInfo 章节。

## 约束

- `--mis` 参数可选，未指定时会从 `~/.config/clawdgw.json` 的 `defaultUserId` 字段读取
- 缺少关键参数时只追问必要字段（--contentId / --tableId / --columnIds），不给笼统报错
- 列 ID 格式灵活：支持逗号分隔字符串 `"1,2,3"` 或 JSON 数组 `[1,2,3]`
- 数据大小限制：单次操作最多 500 行，如果超过需要分页处理
- 批量删除前建议先查询数据确认要删除的行 ID
- **列类型选择强制要求**：创建表格时，必须根据数据实际用途选择对应的列类型，而不是简单地全部使用文本列。如果某列类型不支持，按照降级策略使用文本列（type: 1）作为备选方案

## 暂不支持

以下能力当前 **不可用**，不要伪造执行结果：

- 列的删除和修改
- 表格结构变更（添加/删除/修改列）

用户要求时明确说明"当前暂不支持"。替代方案：可通过 Web UI 手动操作或联系管理员。


## 认证

### 默认方式：SSO 统一认证
自动选择最佳认证策略（浏览器授权或 CIBA），Token 自动缓存。

**常见问题**：
- 认证失败 → `oa-skills citadel-database --clear-cache` 后重试

**详细说明**：参见 `{baseDir}/references/cli-reference.md` 的 Token 认证章节。

## 验证

执行完成后确认：

1. 命令退出码为 0
2. 创建类：返回了新文档/表格 ID 和链接
3. 查询类：返回了数据/列表
4. 数据操作类：返回操作结果摘要（新增/更新/删除的行数）
5. 给用户简明结论（ID、数量、链接），而非原始数据

## 多维表格链接格式

多维表格的完整链接格式为：

```
https://km.sankuai.com/xtable/{contentId}?table={tableId}&view={viewId}
```

示例：
```
https://km.sankuai.com/xtable/2750138424?table=2750248577&view=1000
```

参数说明：
- `contentId`: 多维表格文档 ID（必需）
- `tableId`: 表格 ID（可选，不指定则显示第一个表格）
- `viewId`: 视图 ID（可选，不指定则显示默认视图）

## 人员 ID 转换

人员列（columnType: 4）使用 `empId` 作为标识符。如需转换 MIS/UID/empId，使用 **account-switcher** skill：

```bash
# 安装
mtskills i account-switcher

# 使用人员列示例
# 1. 转换 MIS → empId（假设得到 2015738）
# 2. 添加数据
oa-skills citadel-database addData \
  --tableId "456789" \
  --columnIds "1,2" \
  --data '[["任务A",[2015738,2015739]]]'
```

## 列类型对照表

**📖 完整数据格式文档**：查看 `{baseDir}/references/data-format.md` 获取详细的数据格式说明、转换规则、筛选/排序语法和常见错误解决方案。

| columnType | 类型说明 | 数据结构 | CellData 字段 | 示例 |
|------------|----------|----------|--------------|------|
| 1 | 文本 | `IRichTextNode[]` | `textCellValue` | `[{type:"text",value:"任务A"}]` |
| 2 | 数字 | `number` | `numberCellValue` | `100` |
| 3 | 单选 | `string` | `selectCellValue` | `"进行中"` |
| 4 | 人员 | `empId[]` | `peopleCellValue` | `[2015738,2015739]` *（ID转换用skill 3572）* |
| 5 | 多选 | `string[]` | `multipleSelectCellValue` | `["标签1","标签2"]` |
| 6 | 附件 | `string[]` (fileUrl) | - | `["https://..."]` |
| 7 | 日期 | `number` (timestamp) | `dateCellValue` | `1704067200000` |
| 8 | 货币 | `number` | `numberCellValue` | `99.99` |
| 9 | 公式 | 不可编辑 | - | 只读，不支持写入 |

### 文本类型（columnType: 1）- 富文本

文本列支持富文本格式（`IRichTextNode[]`），包括纯文本、超链接和 @提及。

**快速示例**：

```bash
# 简单文本（自动转换）
--data '[["任务A"]]'

# 超链接
--data '[[
  [
    {"type":"text","value":"查看"},
    {"type":"link","value":"文档","link":"https://km.sankuai.com/page/123"}
  ]
]]'

# @提及人员（empId 必须是数字）
--data '[[
  [
    {"type":"mention","value":"张三","empId":2015739}
  ]
]]'
```

**详细格式说明**：参见 `{baseDir}/references/data-format.md` 的富文本章节。

## 列类型选择

根据数据实际用途选择对应列类型，获得更好的展示和筛选效果：

| 数据用途 | 推荐类型 |
|---------|---------|
| 文本内容 | `1` (文本) |
| 数值、金额 | `2` (数字) / `8` (货币) |
| 状态、分类 | `3` (单选) / `5` (多选) |
| 负责人、参与者 | `4` (人员) |
| 日期、时间 | `7` (日期) |
| 文件、图片 | `6` (附件) |

**💡 提示**：
- 单选/多选选项会自动创建，无需预先配置
- 详细格式和降级策略参见 `{baseDir}/references/data-format.md`

## 筛选和排序

### 快速示例

```bash
# 筛选查询（filterValue 必须是字符串数组）
--filter '{"conjunction":"and","conditions":[{"columnId":1,"operator":"==","filterValue":["完成"]}]}'

# 排序查询
--sort '[{"columnId":2,"desc":true}]'
```

**⚠️ 重要**：`filterValue` 必须是字符串数组，即使是数字也要用字符串（如 `["50"]` 而非 `[50]`）。

**详细操作符和语法**：参见 `{baseDir}/references/data-format.md` 的筛选和排序章节。

## 项目结构

```text
skills/citadel-database/
└── SKILL.md          # Skill 定义

src/citadel-database/
├── types.ts          # 类型定义
├── client.ts         # XTableClient 实现（HTTP REST API）
└── cli.ts            # CLI 入口
```

## 最佳实践

### 1. 创建表格时选择正确的列类型

在创建表格之前，应该明确每一列的用途和数据类型，然后选择对应的列类型。这是数据质量的基础。

**✅ 推荐做法**：根据数据用途选择合适的列类型（参考前面的"列类型选择"章节）。

### 2. 先查询元数据，了解列结构

查询表格前，先通过 `getTableMeta` 获取表格的列定义和列 ID：

```bash
oa-skills citadel-database getTableMeta --tableId "456789" --mis "your_mis"
```

使用返回的 `columnId` 和 `columnType` 进行后续操作。

### 3. 使用 Token 缓存

认证信息会自动缓存，有效期内无需重复认证。如需清除：

```bash
oa-skills citadel-database --clear-cache
```

### 4. 批量操作

一次性添加或更新最多 500 行数据，提高效率：

```bash
oa-skills citadel-database addData \
  --tableId "456789" \
  --columnIds "1,2,3" \
  --data '[["值1", 100, "进行中"], ["值2", 200, "待处理"], ...]'
```

### 5. 错误处理

遇到错误时，检查错误信息中的 TraceID 用于问题排查。常见错误：

- 认证失败：清除缓存，重新发起认证
- API 错误：检查参数是否正确，TraceID 用于追踪
- 数据验证失败：检查数据与列类型是否匹配

## 常见问题

### Q: 如何获取列ID？

A: 使用 `getTableMeta` 命令查询表格元数据，返回结果中包含每列的 `colId`。

### Q: 日期格式如何处理？

A: 日期使用毫秒时间戳格式（13位数字）。可以使用 `new Date().getTime()` 或 `Date.parse("2024-01-01")` 获取。

### Q: 如何处理人员类型？

A: 人员类型需要使用员工ID（empId），是一个数字数组。例如：`[12345, 67890]`。

**人员 ID 转换**：如需在 MIS、empId、大象 UID 之间相互转换，请使用 **skill account-switcher**。

### Q: 单选/多选类型需要提前创建选项吗？

A: **不需要！** 对于单选（columnType: 3）和多选（columnType: 5）类型的列：
- 在 `addData` 或 `updateData` 时，直接使用选项文本即可
- 系统会自动创建不存在的选项
- 例如：直接写入 `"进行中"`、`"已完成"` 等选项文本，无需提前在表格中创建

**示例**：
```bash
# 直接添加数据，"进行中"、"高优先级" 等选项会自动创建
oa-skills citadel-database addData \
  --tableId "456789" \
  --columnIds "1,2,3" \
  --data '[["任务A", "进行中", "高优先级"]]'
```

### Q: 如何删除多维表格文档？

A: 多维表格文档的删除需要使用 **citadel** skill 的删除文档命令：

```bash
# 删除多维表格文档
oa-skills citadel deleteDocument --contentId "2750138424"

# 如果误删，可以从回收站恢复
oa-skills citadel restoreDocument --contentId "2750138424"
```

**注意**：删除操作会将文档移至回收站，而不是永久删除。

### Q: 认证失败怎么办？

A: 
1. 检查是否在手机上确认了登录请求
2. 清除缓存重新认证：`oa-skills citadel-database --clear-cache`
3. 确认 MIS 账号是否有效

### Q: API 调用失败如何排查？

A: 错误信息中包含 TraceID，可以用于在日志系统中追踪问题：
```
API 错误 (400): Invalid parameter (TraceID: abc123...)
```

## 故障排除

### Node.js 版本问题

命令会自动检查并升级 Node.js 版本（>= 18）。如需手动操作：

```bash
# 检查版本
node --version

# 手动升级
nvm install 18 && nvm use 18
```

### 认证问题

```bash
# 清除缓存重试
oa-skills citadel-database --clear-cache
```

## 问题反馈
点击https://applink.neixin.cn/profile?gid=70411238253加入学城多维表格官方Skill客服群大象群