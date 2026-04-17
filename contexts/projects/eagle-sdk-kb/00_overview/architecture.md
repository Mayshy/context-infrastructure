# Poros 整体架构

**学城文档**: https://km.sankuai.com/collabpage/1127183403  
**创建日期**: 2026-04-07  

---

## 一句话定义

Poros 是美团 ES 团队维护的 **ES 代理/网关服务**，同时也是一个**客户端 SDK**。它在业务方与 ES 集群之间提供鉴权、限流、熔断、DSL 过滤等能力。

---

## 核心架构：两种部署模式

### 模式 A：代理服务模式（Poros Service）

```
业务方（HTTP）
    ↓
Poros Service（Netty HTTP Server, port 8080）
    ↓ 请求过滤链（InitFilter → PermissionFilter → RateLimitFilter → QueryDSLFilter → CircuitBreakerFilter）
    ↓ 转发
ES 集群
    ↓ 响应过滤链（CatReportFilter → SlowQueryFilter → CircuitBreakerClearFilter）
    ↓
业务方
```

**适用场景**：业务方通过 HTTP 协议访问代理，无需在业务方部署 SDK。

### 模式 B：直连客户端模式（callESDirectly=true）

```
业务方
    ↓ PorosHighLevelClientBuilder.callESDirectly(true)
PorosRestHighLevelClient（内嵌 SearchThrottleService）
    ↓ 高风险查询检查 + 查询模板限流
ES 集群（直连，无代理层）
```

**适用场景**：业务方直接嵌入 SDK，跳过代理服务层，性能更高。

---

## 模块依赖关系

```
poros-high-level-client
    └── poros-client（PorosRestClientBuilder）
            └── poros-common（EagleApiProxy, RestClient fork, DTOs）
                    └── org.elasticsearch.client.*（forked ES client）

poros-service
    └── poros-common（EagleApiProxy, PorosService, DTOs）
    └── Guice（DI 框架，无 Spring）
    └── Netty（HTTP Server）

poros-elasticsearch-plugin
    └── poros-common（认证/鉴权逻辑）
```

---

## 请求完整生命周期（代理模式）

```
1. 客户端 HTTP 请求 → Netty HttpServerHandler.channelRead0()
2. 解析请求：method, endpoint, params, body, Authorization header
3. 构建 ESRequest（含 appKey, accessKey, operationType, index）
4. 调用 ESProxyBiz.handleRequest(esRequest)
5.   → RequestFilterChain.doFilter(esRequest)
6.     → InitFilter（初始化上下文）
7.     → PermissionFilter（验证 appKey/accessKey，10min 缓存，Eagle API 同步）
8.     → RateLimitFilter（Rhino OneLimiter，按 appKey 限流）
9.     → QueryDSLFilter（DSL 规则检查：terms数量/should数量/from+size/top_hits）
10.    → CircuitBreakerFilter（Rhino 熔断器，按 key 触发）
11. 若过滤通过 → RestClient.performRequest() / performRequestAsync()
12. ES 响应 → ResponseFilterChain.doFilter(esResponseWrapper)
13.   → CatReportFilter（Cat 打点：耗时、状态码）
14.   → SlowQueryFilter（慢查询日志）
15.   → CircuitBreakerClearFilter（熔断器状态更新：setSuccess/setFailed）
16. 返回响应 → Netty writeESResponse()
```

---

## 关键外部依赖

| 系统 | 用途 |
|------|------|
| **Eagle API** (`eagleweb.sankuai.com/api`) | 集群节点发现、appKey 鉴权列表、DSL 过滤配置、慢查询配置、Mafka 配置 |
| **Lion** (美团配置中心) | 动态配置：高风险拦截开关、查询模板限流开关、软拦截开关 |
| **Rhino** (美团限流/熔断框架) | OneLimiter（限流）、CircuitBreaker（熔断） |
| **Cat** (美团监控) | 打点：ES 请求耗时、高风险查询事件、模板限流事件 |
| **Pigeon/Mafka** (美团 RPC/消息) | RPC 模式下的 Poros 代理访问 |
| **KMS** (密钥管理) | accessKey 安全存储和获取（替代明文配置） |
| **MTrace** (美团分布式追踪) | Cell/Swimlane 路由信息获取 |

---

## 两个根包共存的设计意图

```
com.sankuai.meituan.poros.*   — Poros 自身的业务代码
org.elasticsearch.client.*    — Fork 的 ES 客户端代码
```

**原因**：ES 官方 `RestClient` 的部分关键方法是 `package-private` 的，只有在 `org.elasticsearch.client` 包下才能访问。Poros 通过 fork + 扩展的方式在不修改 ES 源码的前提下实现了自定义行为（如自适应负载均衡、Sniffer 扩展、Mafka 写入等）。
