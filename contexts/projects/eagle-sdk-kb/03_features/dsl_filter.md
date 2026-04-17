# DSL 过滤（QueryDSLFilter）

**所在模块**: poros-service  
**核心类**: `QueryDSLFilter`, `DSLQueryConverter`, `DSLFilterConfigDTO`  
**创建日期**: 2026-04-07

---

## 功能说明

在代理服务层对 ES 查询语句进行规则检查，防止业务方发送超出阈值的大查询，并支持通过大象通知业务方。

与 poros-high-level-client 中的 `SearchThrottleService` 类似，但 DSL Filter 工作在**代理服务层**（poros-service），不需要业务方升级 SDK。

---

## 检查维度

| 类型 | 说明 |
|------|------|
| `TERMS` | terms 查询的 values 数量 |
| `SHOULD` | bool should 子查询数量 |
| `TOTAL_SIZE` | from + size 总大小 |
| `TOP_HITS` | agg top_hits 的 size |

---

## 降级策略（StrategyEnum）

每个规则可以配置多个策略的组合：

| 策略 | 行为 |
|------|------|
| `DECLINE` | 拒绝请求，返回 400 错误 |
| `DAXIANG` | 发送大象告警通知业务方 |

通过 `StrategyEnum.zipStrategies()` 将策略列表压缩为 `byte`，再用位运算判断是否包含某策略。

---

## 大象通知频率限制

```java
// 避免告警轰炸
private static final int DSL_THRESH_HOLD = 100;         // 缓存的非法查询数量阈值
private static final long NOTIFY_TIME_INTERVAL = 2 分钟; // 通知最小间隔

// 触发通知条件：
// 1. filterCountCache.size() >= DSL_THRESH_HOLD（积累了足够多的非法查询）
// 2. 距上次通知超过 2 分钟
```

---

## 配置来源

- 来源：Eagle API（`/clusters/{cluster}/dsl-filter/configuration`）
- 缓存：`volatile ConcurrentMap<clusterName, DSLFilterConfigDTO>`
- 同步频率：每 10 分钟

---

## 重要行为

1. **只对查询操作生效**：`operationType == SEARCH || SCROLL_SEARCH`，其他操作（写入、删除等）直接 PASS
2. **配置为空时直接 PASS**：未配置 DSL 规则时不做任何检查
3. **失败不阻断**：DSL 解析异常时 `catch (Exception e)` 后直接 PASS，不影响主流程
