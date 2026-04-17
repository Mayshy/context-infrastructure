# 高风险查询拦截（throttleHighRiskQuery）

**所在模块**: poros-high-level-client  
**核心类**: `SearchThrottleService`, `RiskType`, `QueryRiskChecker` 及各实现  
**创建日期**: 2026-04-07

---

## 功能说明

在查询发送到 ES 之前，检查查询语句是否包含高风险模式（如超大 terms、深度嵌套 agg 等），防止业务方写出"炸集群"的查询。

---

## 风险类型及阈值

阈值通过 Lion 动态配置（key: `ForceThrottleRiskCheckConfigV2`，appKey: Eagle API appKey）：

| RiskType | 检查维度 | 典型危害 |
|---------|---------|---------|
| `FROM_SIZE_RISK` | from + size > 阈值 | 深翻页，内存和 CPU 压力大 |
| `TERMS_COUNT_RISK` | terms 查询的 values 数量 | 大量 terms 导致 Query 解析和执行开销大 |
| `SHOULD_COUNT_RISK` | bool should 子查询数量 | 过多 should 导致评分计算开销大 |
| `REGEXP_MAX_STATES_COUNT` | 正则 NFA 状态数 | 复杂正则导致 NFA 状态爆炸 |
| `REGEXP_WORD_SIZE_RISK` | 正则表达式字符串长度 | 长正则解析开销大 |
| `WILDCARD_WORD_SIZE_RISK` | 通配符查询词长度 | 长通配符全量扫描 |
| `WILDCARD_WORD_PATTERN_RISK` | 通配符全是 `*` | 全量匹配，等同于 match_all |
| `MATCH_PHRASE_WORD_SIZE_RISK` | match_phrase 查询词长度 | 长短语匹配开销大 |
| `AGG_TERMS_DEPTH_RISK` | terms agg 嵌套深度 | 深层嵌套 agg 内存爆炸 |
| `AGG_TERMS_SIZE_RISK` | terms agg size | 大 size 导致 shard 级别内存压力 |
| `AGG_TERMS_SHARD_SIZE_RISK` | terms agg shardSize | 同上，更细粒度 |

---

## 检查流程

```java
// SearchThrottleService.throttle()
1. 检查 from/size 风险
2. 递归检查 query 风险（通过 QueryRiskChecker 策略模式）
3. 递归检查 aggregation 风险（深度优先遍历 TermsAggregationBuilder）
```

---

## 软拦截 vs 硬拦截

```
onlyCatThrottleEvent=true（默认）
    → 只打 Cat 点：Cat.logEvent("ES.QueryRisk.{riskType}", cluster, ...)
    → 请求继续发送

onlyCatThrottleEvent=false
    → 返回 ThrottleResult(isThrottled=true, reason=...)
    → 请求被拒绝，抛出异常
```

**推荐接入流程**：先开软拦截观察 Cat 监控，确认没有误拦截后再切换为硬拦截。

---

## Lion 动态开关

三个开关都支持通过 Lion 动态调整，无需重启：

```
{clientAppKey}.throttle.high.risk.query.{clusterName}  → throttleHighRiskQuery
{clientAppKey}.query.template.rate.limit.{clusterName} → queryTemplateRateLimit  
{clientAppKey}.only.cat.throttle.event.{clusterName}   → onlyCatThrottleEvent
```

**优先级**：Lion > 本地构造器配置
