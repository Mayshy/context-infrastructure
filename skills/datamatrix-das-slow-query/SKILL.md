---
name: datamatrix-das-slow-query
description: "DataMatrix Blade 集群慢查询分析 Skill。查询 DAS（das.mws.sankuai.com）上 platsearch_blade_datamatrixsh1、platsearch_blade_datamatrixsh2、platsearch_blade_datamatrixhl0 三个集群的 SELECT 类型慢查询，过滤掉 COUNT(*) 和低频（12小时内不足10次）SQL，按扫描行数排序输出 Top 10 高风险 SQL，并附优化建议。最后将分析结果发送到 Friday。触发词：blade慢查询、DAS慢查询、datamatrix慢查询、查一下慢查、慢SQL分析、platsearch blade slow query。"
---

# DataMatrix Blade 慢查询分析

## 监控集群（固定配置，无需用户输入）

```
platsearch_blade_datamatrixsh1   DB: mirror_sh_01
platsearch_blade_datamatrixsh2   DB: mirror_sh_02
platsearch_blade_datamatrixhl0   DB: mirror_test
```

## 执行流程

### Step 1：打开 DAS 页面（获取认证 Cookie）

用 Playwright MCP 导航到 DAS，时间范围取**最近 12 小时**：

```
https://das.mws.sankuai.com/das/slow-query/blade-clusterdetail/platsearch_blade_datamatrixsh1
  ?slowQueryTab=Blade&activeName=cluster&topCluster=platsearch_blade_datamatrixsh1
  &time=["<12小时前>","<当前时间>"]&timeRadio=""&checked=1
```

等待页面加载完成（`browser_wait_for time=3`）。

### Step 2：并行查询三个集群（JS 注入）

用 `browser_run_code_unsafe` 在页面内 fetch API，**三个集群串行**（避免并发限流）：

```javascript
async (page) => {
  const clusters = [
    'platsearch_blade_datamatrixsh1',
    'platsearch_blade_datamatrixsh2',
    'platsearch_blade_datamatrixhl0'
  ];
  const BEGIN = '<12小时前ISO时间>';   // 例：2026-05-09T02:12:37
  const END   = '<当前ISO时间>';       // 例：2026-05-09T14:12:37

  const results = {};
  for (const cluster of clusters) {
    const data = await page.evaluate(async (c, b, e) => {
      const resp = await fetch(
        `/blade/api/v2/slow-query/cluster/${c}/templates`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            order: 'maxScanRows',
            sort: 'desc',
            begin_at: b,
            end_at: e,
            show_external_sql: true,
            query_type: 'select',
            current: 1,
            page_size: 100   // 多取，过滤后取 Top 10
          })
        }
      );
      return await resp.json();
    }, cluster, BEGIN, END);

    // 过滤规则：排除 COUNT(*)、排除 < 10次、排除 maxScanRows <= 0
    results[cluster] = (data?.result?.data || [])
      .filter(d => {
        const sql = (d.sQlTemplate || '').trim().toUpperCase();
        return !sql.startsWith('SELECT COUNT')
          && d.queryCount >= 10
          && d.maxScanRows > 0;
      })
      .slice(0, 10)
      .map((d, i) => ({
        rank: i + 1,
        table: (d.tableNames?.[0] || d.tables?.[0] || '')
          .replace(/_\d{14}$/, ''),   // 去掉时间戳后缀
        dbName: d.dBName,
        sql: d.sQlTemplate || '',
        maxScanRows: d.maxScanRows,
        avgScanRows: d.avgScanRows,
        queryCount: d.queryCount,
        avgQueryTime: Math.round(d.averageQueryTime * 1000) / 1000
      }));
  }
  return JSON.stringify(results, null, 2);
}
```

### Step 3：分析并输出结果

对每条慢查询，输出以下字段，并给出优化建议：

| 字段 | 说明 |
|---|---|
| 集群 | 集群名 |
| 表名 | 去掉时间戳后缀的基础表名 |
| SQL | 完整 SQL 模板（`?` 为参数占位符） |
| 最大扫描行数 | maxScanRows |
| 平均扫描行数 | avgScanRows |
| 查询次数 | queryCount（12h 内） |
| 平均耗时(s) | avgQueryTime |
| 优化建议 | 见下方「优化建议规则」 |

#### 优化建议规则

根据 SQL 模式自动生成建议：

| SQL 模式 | 根因 | 建议 |
|---|---|---|
| `WHERE IFNULL(col, ?) = ?` | 函数包裹列名，索引失效 | 改写为 `(col = ? OR (col IS NULL AND ? IS NULL))`，并在 col 上建索引 |
| `WHERE date(col) > ?` | date() 函数包裹，索引失效 | 改为范围条件 `col > ?`，去掉函数包裹 |
| `AND 1 = 1` | ORM 冗余条件 | 排查 ORM 动态拼接逻辑，消除冗余条件 |
| `WHERE col != ?` / `col IS NOT NULL` | 反向条件走不了索引 | 改为正向条件，或建覆盖索引 |
| `OR` 多字段条件 | OR 无法走联合索引 | 拆成两条 SQL + UNION，或建多个单列索引 |
| 普通等值查询扫描行数 > 1万 | 缺索引 | 在 WHERE 条件字段上建索引或复合索引 |
| 多字段 AND 条件 | 缺复合索引 | 按等值字段顺序建复合索引，范围字段放最后 |

#### 风险等级

- **P0**：`queryCount >= 1000` 或 `avgScanRows >= 100000`
- **P1**：`queryCount >= 100` 或 `avgScanRows >= 10000`
- **P2**：其余

### Step 4：发送分析结果到 Friday

使用 `friday-catclaw-mcp` skill 将分析结果发送到 Friday（用户的 mis 为 `shenhuayu`）。

消息格式：

```
【DataMatrix Blade 慢查询分析】<当前日期> 最近12小时

集群：platsearch_blade_datamatrixsh1 / sh2 / hl0

=== Top N 高风险 SQL ===

[P0] 集群: xxx | 表: xxx
查询次数: xxx | 最大扫描行: xxx | 平均耗时: xs
SQL:
  SELECT ...
  FROM ...
  WHERE ...
优化建议: ...

（每条 SQL 一段，按风险等级 P0 → P1 → P2 排列）

---
完整分析见 DAS: https://das.mws.sankuai.com/das/slow-query?slowQueryTab=Blade&activeName=cluster
```

发送前需加载 `friday-catclaw-mcp` skill 获取具体发送方式。

## 注意事项

- DAS 需要 SSO 认证，通过 Playwright 浏览器复用已有登录态（无需手动传 token）
- 时间范围始终为「当前时间往前推 12 小时」，自动计算，无需用户输入
- `page_size: 100` 确保有足够候选 SQL 经过过滤后仍能凑满 10 条
- 如果某集群过滤后不足 10 条，如实输出，不补充 COUNT(*) 类 SQL
