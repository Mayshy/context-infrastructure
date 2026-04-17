# poros-service — 代理服务设计

**代码位置**: `/Users/shenhuayu/Desktop/Project/poros/poros-service/`  
**创建日期**: 2026-04-07

---

## 职责

poros-service 是 Poros 的**服务端部署形态**。它是一个 Netty HTTP Server，监听 8080 端口，接收业务方的 ES 请求，经过 Filter 链处理后转发给 ES 集群。

**不对外发布**（只有 poros-common/client/high-level-client 发布到 Maven）。

---

## 启动流程

```
PorosServiceBootStrap.main()
    → Guice.createInjector(new PorosModule())
    → PorosModule.configure() 绑定所有 Filter、Biz、Service
    → PorosModule.provideRestClient() 构建 RestClient（含 Sniffer）
    → PorosServiceImpl.start() 启动 Netty Server
    → ReportStatusTask / ReportVersionTask 启动定时上报任务
```

---

## Guice 模块绑定（PorosModule）

```java
// 核心业务
ESProxyBiz → ESProxyBizImpl
PorosService → PorosServiceImpl
MafkaProxyBiz → MafkaAdminImpl
CircuitBreakerBiz → CircuitBreakerFilter（一个类实现两个接口）

// 请求 Filter（Named 绑定）
"Init"         → InitFilter
"Permission"   → PermissionFilter
"RateLimit"    → RateLimitFilter
"QueryDSL"     → QueryDSLFilter
"CircuitBreaker" → CircuitBreakerFilter

// 响应 Filter（Named 绑定）
"CatReport"    → CatReportFilter
"SlowQuery"    → SlowQueryFilter
"CircuitBreakerClear" → CircuitBreakerClearFilter

// Filter 链（Named 绑定）
"Request"  → RequestFilterChain（注入上面 5 个请求 Filter）
"Response" → ResponseFilterChain（注入上面 3 个响应 Filter）

// Netty Handler
"HttpServerHandler" → HttpServerHandler
```

---

## 核心类详解

### HttpServerHandler（Netty 入口）

- `extends SimpleChannelInboundHandler<FullHttpRequest>`
- `@Sharable`（单例，线程安全）
- 解析请求：method, endpoint, query params, body, Authorization header
- 调用 `RequestParseUtils.parse()` 识别 operationType 和 index
- 调用 `esProxyBiz.handleRequest(esRequest)`
- 写回响应：`NettyApacheHttpConverter.toNettyResponse(esResponse)`

### ESProxyBizImpl（核心代理逻辑）

```java
handleRequest(ESRequest esRequest):
    1. requestFilterChain.doFilter(esRequest)  // 若失败 → 返回 400 错误响应
    2. restClient.performRequest()/performRequestAsync()  // 转发 ES
    3. handleSuccess() → responseFilterChain.doFilter(new ESResponseWrapper(response, esRequest))
    4. handleException() → responseFilterChain.doFilter(new ESResponseWrapper(e, esRequest))
```

**异步模式**（`call.es.async=true`，默认）：使用 `PorosResponseListener` + `CountDownLatch` 实现同步等待异步结果。

### PermissionFilter（鉴权）

- 从 `Authorization` header 解析 appKey 和 accessKey（Basic Auth）
- 本地缓存 `volatile ConcurrentMap<appKey, accessKey>`
- 每 10 分钟从 Eagle API 同步全量 appKey 列表
- 若缓存为空则实时从 Eagle API 查询一次

### RateLimitFilter（限流）

- 使用 Rhino `OneLimiter`
- 限流 key = `RhinoUtils.computeEntrance(appKey)`
- 限流规则在 Rhino 平台配置，无需重启生效

### QueryDSLFilter（DSL 规则过滤）

- 只对 SEARCH 和 SCROLL_SEARCH 操作生效
- 检查维度：
  - `TERMS`：terms 查询的值数量
  - `SHOULD`：bool should 子查询数量
  - `TOTAL_SIZE`：from + size 总大小
  - `TOP_HITS`：agg top_hits 大小
- 超出阈值时根据策略：
  - `DECLINE`：拒绝请求（返回 400）
  - `DAXIANG`：大象通知业务方（频率限制：2 分钟内最多通知一次）
- 配置来源：Eagle API，每 10 分钟同步
- **失败不阻断**：parse 异常时直接 PASSED

### CircuitBreakerFilter（熔断器）

- 实现 `CircuitBreakerBiz` 接口（提供 register/remove/setSuccess/setFailed）
- 同时实现 `Filter<ESRequest>`（在请求链中执行）
- 使用 Rhino `CircuitBreaker`
- 每个熔断器有独立的 key 和 `CircuitBreakerConfig`（含触发条件 `Function<ESRequest, Boolean>`）
- 熔断后执行 fallback（`Supplier<FallbackResponse>`），可配置是否继续请求

### CatReportFilter（监控打点）

- 记录 ES 请求耗时（`esEnd - esStart`）、总耗时（`esEnd - porosStart`）
- Cat Transaction：操作类型 + index
- 状态码打点

### SlowQueryFilter（慢查询）

- 从 Eagle API 获取慢查询阈值配置（每 10 分钟同步）
- 超过阈值时记录慢查询日志

---

## 关键 Bean

### ESRequest
```java
String method, endpoint;
Map<String, String> params;
HttpEntity httpEntity;
Header[] headers;
String appKey, accessKey;
String operationType, index;
String remoteIp;
long porosStart, esStart, esEnd;
PorosResponseListener porosResponseListener;
Map<String, CircuitBreakerContext> circuitBreakerContexts;
```

### FilterResponse
```java
FilterResponse.PASSED          // 静态常量，表示通过
FilterResponse.failed(reason)  // 静态工厂，表示拒绝
boolean isPassed();
String getReason();
```

---

## 定时任务

| 任务 | 周期 | 职责 |
|------|------|------|
| `ReportStatusTask` | 定期 | 上报 Poros 服务状态到 Eagle API |
| `ReportVersionTask` | 定期 | 上报 Poros 版本信息到 Eagle API |
| `PermissionFilter.start()` | 10min | 同步 appKey 白名单 |
| `QueryDSLFilter.start()` | 10min | 同步 DSL 过滤规则 |
| `SlowQueryFilter.start()` | 10min | 同步慢查询配置 |
