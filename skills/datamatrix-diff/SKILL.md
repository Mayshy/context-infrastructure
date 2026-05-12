---
name: datamatrix-diff
description: DataMatrix ES 索引数据 diff 校验工具。用于老云搜迁移到 DataMatrix 时，对比新老 ES 应用的索引数据是否一致。支持：发起校验任务、查看校验进度、查看/取消运行中任务、从 ES 持久化存储查询差异主键、对差异 doc 进行 JSON 字段级 diff 并直接输出、将校验结果保存到 KB check_log.md。触发词：发起校验、diff 任务、查校验结果、查差异 doc、迁移校验、数据一致性检查、application diff、positiveDiffCount、negativeDiffCount。
---

# DataMatrix ES Diff 工具

## 基本信息

| 环境 | 地址 |
|------|------|
| 线上 | `http://10.125.153.4:8080` |
| 线下 | `http://10.102.170.53:8080` |

默认使用**线上**地址，除非用户明确说"线下"。

---

## 1. 发起校验任务

```
POST {host}/webapi/diff/application/start
Content-Type: application/json
```

```json
{
  "oldClusterGroupName": "ES_CG_xxx",
  "oldClusterName": "xxx_default",
  "oldApplicationName": "es_xxx_appname",
  "newClusterGroupName": "ES_CG_xxx",
  "newClusterName": "xxx_default",
  "newApplicationName": "xxx_appname",
  "skipFields": ["field1"],
  "fieldNeedReplaceRN": [],
  "fieldNeedOrder": [],
  "samplingRate": 100,
  "qps": 10
}
```

**关键参数说明：**
- `oldApplicationName`：老云搜应用名，通常以 `es_` 开头
- `newApplicationName`：DataMatrix 新应用名，不带 `es_` 前缀
- `samplingRate`：建议先用 `10` 快速验证，再用 `100` 全量
- `skipFields`：JSON 空格差异字段必须跳过（见常见问题）

**成功返回**：提取 `data.taskId` 用于后续查询，`data.schemaDiffResult` 立即反映 Schema 差异。

---

## 2. 查看校验进度

```
POST {host}/webapi/diff/application/result
Content-Type: application/json

{"taskId": "<taskId>"}
```

**状态流转**：`running` → `positiveSuccess` / `negativeSuccess` → `success` / `failed` / `cancel`

**判断标准：**
- ✅ 通过：`status=success` 且 `positiveDiffCount=0` 且 `negativeDiffCount=0`
- ⚠️ 少量差异：分析 `schemaDiffResult`，判断是否可接受
- ❌ 大量差异：需排查建模配置

**输出格式（AI 应格式化展示）：**
```
状态: success ✅
正向差异: 0 / 23725 (0.00%)
反向差异: 0 / 23725 (0.00%)
Schema 差异: schemas相同
```

---

## 3. 查看运行中任务

```
GET {host}/webapi/diff/application/runningtasks
```

列出所有正在执行的 diff 任务，包含 taskId、应用名、当前进度。

---

## 4. 取消任务

```
POST {host}/webapi/diff/application/cancel
Content-Type: application/json

{"taskId": "<taskId>"}
```

---

## 5. 查询差异主键（diffIds）

差异 doc 的主键存储在 ES 索引 `application-diff-detail` 中。

**通过 eagle-skill 查询（线上集群：`eagle_eaglenode-es-larus_default`）：**

```json
POST application-diff-detail/_search
{
  "query": {
    "bool": {
      "must": [{"term": {"taskId": "<taskId>"}}]
    }
  },
  "from": 0,
  "size": 10
}
```

返回的 `_source.diffIds` 是差异文档的主键列表（每批最多 100 个）。

---

## 6. JSON Diff（字段级对比）

拿到 diffIds 后，从新老应用各取对应 doc，直接输出字段差异。

**步骤：**
1. 用 eagle-skill 从老应用 `GET /<oldApplicationName>/_doc/<id>` 取 `_source`
2. 用 eagle-skill 从新应用 `GET /<newApplicationName>/_doc/<id>` 取 `_source`
3. AI 直接对比两个 JSON，输出差异字段：

```
字段差异报告（id: 132333）
━━━━━━━━━━━━━━━━━━━━━━━━━━
字段              老值                    新值
─────────────────────────────────────────────
ownerid           "user_123"             null
isworkflow        1                      "1"    ← 类型不同
graytextvector    [0.1, 0.2, ...]        缺失
```

> **注意**：查 doc 时需要指定正确的集群（`oldClusterName` / `newClusterName`）。

---

## 7. 保存校验记录

校验完成后，将结果追加到 KB 文件：
`/Users/shenhuayu/.config/opencode/contexts/projects/datamatrix-kb/06_migration/check_log.md`

如果文件不存在，先创建（见 references/diff_workflow.md 中的记录格式）。

---

## 参考

- **标准迁移校验流程 + 记录格式**：见 `references/diff_workflow.md`
- **常见差异原因及处理**：见 `references/diff_workflow.md`
- **ES 持久化存储**：
  - 线上：https://es.sankuai.com/cluster/~eagle_eaglenode-es-larus_default/overview
  - 任务结果索引：`application-diff-result`
  - 差异主键索引：`application-diff-detail`
