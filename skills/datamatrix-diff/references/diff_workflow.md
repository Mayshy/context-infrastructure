# 迁移校验标准流程

## 标准步骤

```
1. 确认新应用索引已构建完成（hermes 全量构建 status = success）
2. 获取新老应用的 clusterGroupName、clusterName、applicationName
3. 提交 diff 任务（samplingRate=10 快速验证，通过后再 samplingRate=100 全量）
4. 轮询 result 接口，等待 status = "success"（大索引可能需要几分钟到几十分钟）
5. 检查 positiveDiffCount 和 negativeDiffCount
6. 如有 schemaDiffResult，逐字段确认是否可接受
7. 如有差异 doc，查询 diffIds → 取 doc → 输出 JSON diff
8. 保存校验结果到 check_log.md
```

---

## 常见差异原因及处理

| 差异现象 | 可能原因 | 处理方式 |
|---------|---------|---------|
| `schemaDiffResult` 有值 | 字段映射配置不一致 | 检查 hermes 索引 Schema 配置 |
| total 数量差异 | 过滤条件不同 / 全量同步未完成 | 检查 pontos 镜像过滤配置 |
| 少量 doc 差异 | 实时同步延迟 / 时序问题 | 等待 Flink catch-up 后重试 |
| 大量 doc 差异 | 建模 join 逻辑有误 | 检查 athena 建模画布配置 |
| 特定字段值差异 | FieldFormatter 函数不兼容 | 检查 FieldDefinitions 转换逻辑 |
| JSON 空格差异 | MySQL JSON 类型同步丢失空格 | 在 `skipFields` 中跳过该字段 |
| 字段类型差异（如 int vs string） | Schema 映射类型不匹配 | 检查 hermes 字段类型配置 |

---

## 校验记录格式（check_log.md）

每次校验完成后追加一条记录：

```markdown
## 2026-04-27 | app: xxx_appname

- **老应用**: es_xxx_appname (集群: xxx_default)
- **新应用**: xxx_appname (集群: xxx_default)
- **taskId**: 3620ac03-5670-4efb-ab58-b3fdb8151516
- **采样率**: 100%
- **结果**: ✅ 通过 / ❌ 有差异
- **正向差异**: 0 / 23725
- **反向差异**: 0 / 23725
- **Schema 差异**: schemas相同 / 存在差异字段: field1, field2
- **处理**: 无 / 跳过 field1（JSON空格问题）/ 待排查
- **备注**: —
```

---

## check_log.md 文件头（首次创建时使用）

```markdown
# DataMatrix 迁移校验记录

> 记录每次 ES diff 校验的结果，供迁移进度追踪参考。
> 学城迁移进度追踪：https://km.sankuai.com/collabpage/2756112613

---
```
