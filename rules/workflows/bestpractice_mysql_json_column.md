# BestPractice: MySQL JSON 列操作陷阱

> **使用方式**：`read` 本文件，边理解边执行。适用于涉及 MySQL JSON 列的 SQL 编写和审查。

---

## When to Use

- 编写或审查包含 `json_extract()` / `JSON_EXTRACT()` 的 SQL 时
- 遇到 `Invalid JSON text: The document is empty` 报错时
- 设计包含 JSON 列的全量同步 SQL 时

---

## 陷阱：`json_extract()` 对空字符串报错

### 问题

MySQL 的 `json_extract()` 函数：
- 对 `NULL` 值：容忍，返回 `NULL`
- 对空字符串 `''`：**抛异常** `Invalid JSON text: The document is empty`

```sql
-- ❌ 危险：extension 列可能为空字符串 ''
SELECT json_extract(extension, '$.field') FROM table WHERE ...;

-- ❌ IFNULL 无法保护：函数执行阶段就抛异常，IFNULL 来不及介入
SELECT json_extract(IFNULL(extension, '{}'), '$.field') FROM table WHERE ...;
```

### 修复

用 `NULLIF(col, '')` 将空字符串转为 `NULL`，再传入 `json_extract()`：

```sql
-- ✅ 正确：先将空字符串转为 NULL，json_extract 对 NULL 容忍
SELECT json_extract(NULLIF(extension, ''), '$.field') FROM table WHERE ...;
```

### 适用范围

- 所有依赖 JSON 列的 SQL（包括 Hermes 全量同步 SQL）
- 数据来源不可控时（用户写入、历史数据迁移等场景尤其容易出现空字符串）

---

## 诊断

报错 `Invalid JSON text: The document is empty` 时：
1. 定位报错的 SQL 语句
2. 找到 `json_extract()` 调用
3. 检查传入的列是否可能为空字符串（而非 NULL）
4. 用 `NULLIF(col, '')` 包裹后重试

---

## 来源

| 日期 | 来源条目 |
|------|---------|
| 2026-05-08 | 🔴 MySQL JSON 列 `json_extract()` 对空字符串报错（Hermes 全量同步 SQL） |
