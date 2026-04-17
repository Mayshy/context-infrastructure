# 熔断器（CircuitBreaker）

**所在模块**: poros-service  
**核心类**: `CircuitBreakerFilter`, `CircuitBreakerBiz`, `CircuitBreakerConfig`  
**依赖**: Rhino（美团内部限流/熔断框架）  
**创建日期**: 2026-04-07

---

## 功能说明

在代理服务层提供熔断能力。当某个维度的 ES 请求失败率超过阈值时，触发熔断，后续请求直接返回 fallback 响应，不再转发给 ES，保护集群和业务方。

---

## 架构设计

`CircuitBreakerFilter` 同时实现两个接口：
- `Filter<ESRequest>` — 在请求链中执行熔断检查
- `CircuitBreakerBiz` — 提供注册/注销/状态更新 API

`CircuitBreakerClearFilter`（响应链）— 根据 ES 响应结果更新熔断器状态（成功/失败计数）。

---

## CircuitBreakerConfig

```java
CircuitBreakerConfig config = new CircuitBreakerConfig()
    .setShouldTrigger(esRequest -> esRequest.getIndex().equals("my-index"))  // 触发条件
    .setFallback(() -> new FallbackResponse(false, "circuit breaker open"))  // fallback
    .setErrorCountThreshold(10)      // 错误数量阈值
    .setErrorPercentageThreshold(50) // 错误率阈值（%）
    .setRequestCountThreshold(20)    // 触发熔断的最小请求数
    .setRollingStatsTimeSeconds(10)  // 统计时间窗口（秒，最大 90）
    .setRecoveryTimeWindowSeconds(30); // 熔断后恢复等待时间（秒）
```

---

## 注册熔断器

通过 `CircuitBreakerBiz` 接口注册：

```java
@Inject
CircuitBreakerBiz circuitBreakerBiz;

circuitBreakerBiz.register("my-circuit-breaker", config);
```

---

## 熔断状态机（Rhino 实现）

```
Closed（正常）
    ↓ 错误率/错误数超过阈值 且 总请求数超过阈值
Open（熔断中）
    ↓ 等待 recoveryTimeWindow
Half-Open（尝试恢复）
    ↓ 一次请求成功
Closed（恢复正常）
```

恢复策略（`withRecoverStrategy(1)`）：立即恢复（Half-Open 一次成功即关闭熔断器）。

---

## FallbackResponse

```java
FallbackResponse(doNext=false, message="...")
    → 不继续请求，返回 FilterResponse.failed(message)

FallbackResponse(doNext=true, message="...")
    → 继续请求（即使熔断器 open，仍然转发给 ES）
```

---

## 注意事项

1. 熔断器按 key 维度管理，key 不能重复注册（重复注册抛 PorosException）
2. `shouldTrigger` 是 `Function<ESRequest, Boolean>`，可以按 index、appKey、操作类型等任意维度触发
3. 统计时间窗口最大 90 秒，建议不超过 60 秒
4. 熔断器状态变化时有日志记录（opened/closed）
