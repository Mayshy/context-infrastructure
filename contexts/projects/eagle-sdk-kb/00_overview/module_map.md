# Poros 模块职责图

**创建日期**: 2026-04-07

---

## 模块一览

| 模块 | 是否发布 | 核心职责 |
|------|---------|---------|
| `poros-common` | ✅ 发布 | 共享 DTOs、常量、解析器、工具类、forked ES RestClient |
| `poros-client` | ✅ 发布 | 低层 REST client 构造器（HTTP + RPC 两种传输方式） |
| `poros-high-level-client` | ✅ 发布 | 对外主要 SDK，封装 ES High Level REST Client，含限流/熔断/多版本支持 |
| `poros-service` | ❌ 不发布 | 部署为代理服务，含 Netty HTTP Server + Filter 链 + Guice 模块 |
| `poros-elasticsearch-plugin` | ❌ 不发布 | 安装到 ES 节点的认证/鉴权插件 |
| `poros-java-api-client` | ❌ 不发布 | 生成的 API 客户端（自动生成，不手动维护） |

---

## poros-common — 共享基础层

### 核心类

| 类 | 职责 |
|----|------|
| `EagleApiProxy` | Eagle API 的 HTTP 封装，提供节点发现、appKey 鉴权、DSL 配置、慢查询配置等接口 |
| `PorosService` | 顶层服务接口（poros-service 中实现） |
| `ClusterAwareness` | 集群感知工具 |
| `GroupClients` | 集群组客户端管理 |
| `Dispatcher` | 请求分发器 |

### bean 包
- `PorosRequest` / `PorosResponse` — 顶层请求/响应 DTO
- `PorosClientConfig` — 客户端配置（上报给 Eagle API 用）
- `DSLFilterConfigDTO` — DSL 过滤规则配置
- `SlowQueryConfig` — 慢查询配置
- `ClusterGroupRouteConfig` — 集群组路由配置
- `LoadBalanceType` — 负载均衡类型枚举
- `ClientFlowConfig` — 流量控制配置

### constant 包
- `RequestStrategy` — 请求策略（DEFAULT, DISABLE_ROUND_ROBIN）
- `OperationType` — 操作类型（SEARCH, SCROLL_SEARCH, INDEX, DELETE, ...）
- `Constants.LionKey` — Lion 配置 Key 常量

### parser 包（ES 请求路由解析）
- `RequestParseUtils` — 入口，根据 HTTP method + path 解析操作类型和 index
- `EndPointParser` — 解析器接口
- `PorosPathTrie` — 路径前缀树，用于 ES REST API 路由匹配
- `GetEndPointParser` / `PostEndPointParser` / `PutEndPointParser` / `DeleteEndPointParser` / `HeadEndPointParser` — 各 HTTP method 的解析实现

### utils 包
- `AuthorizationUtils` — Basic Auth 编解码
- `ResponseConstructor` — 构造 ES Response 对象（反射访问 package-private 构造器）
- `ThreadPoolUtils` — 定时任务线程池（`REPORT_API` 用于定期同步配置）
- `IDCUtils` — IDC 机房信息获取
- `LionUtils` — Lion 配置中心工具
- `ES8CompatibleUtils` — ES8 兼容性工具
- `CatUtils` — Cat 监控打点工具

### org.elasticsearch.client fork
- `RestClient` — 核心 fork，增加了负载均衡、自适应权重、Mafka 写入等能力
- `RestClientBuilder` — 构造器扩展
- `route/loadbalance/` — 自适应负载均衡（`AdaptiveLoadBalancer`, `AdaptiveInflightStat`）
- `sniff/` — 节点嗅探（`Sniffer`, `ElasticsearchNodesSniffer`, `SniffOnFailureListener`）
- `task/` — 后台任务（`ConfigApiReportTask` 上报客户端配置，`ConfigEventReportTask` 上报配置事件）
- `trace/` — 分布式追踪（`TraceUtil`, `InnerTracer`）

---

## poros-client — 低层客户端构造层

### 核心类

| 类 | 职责 |
|----|------|
| `PorosRestClientBuilder` | 核心构造器，决定使用 HTTP 直连还是 RPC（Pigeon/Mafka）模式 |
| `RestClientPorosImpl` | RPC 模式的 RestClient 实现（通过 Mafka 异步写入） |
| `CatHttpProcessor` | HTTP 拦截器，负责 Cat 监控打点 |
| `PorosNodesSniffer` | Poros 节点嗅探（从 Eagle API 获取代理节点列表） |
| `PorosProtocol` | 枚举：HTTP / PIGEON（RPC） |

### 三种连接模式

```
callESDirectly=true   → buildHTTPClient(ES 节点) → 直连 ES
callESDirectly=false + HTTP  → buildHTTPClient(Poros 代理节点)
callESDirectly=false + PIGEON → buildRPCClient() → Mafka 异步写入
```

---

## poros-high-level-client — 对外 SDK（主要发布产物）

### 多版本结构
```
src/main/
├── 5.6.3/   — ES 5.x 版本的 HighLevelClient 实现
├── 6.8.10/  — ES 6.x 版本的 HighLevelClient 实现
└── 7.10.0/  — ES 7.x 版本的 HighLevelClient 实现（当前主力）
```
通过 `POROS_ES_VERSION` 环境变量控制编译哪个版本。

### 7.10.0 核心类

| 类 | 职责 |
|----|------|
| `PorosHighLevelClientBuilder` | 用户侧构造器入口，配置限流/熔断/集群信息 |
| `PorosRestHighLevelClient` | 对外暴露的客户端，代理所有 ES API 调用 |
| `PorosInnerRestHighLevelClient` | 内部实现，含 SearchThrottleService 调用 |
| `PorosStressTestClient` | 压测客户端（双写到压测集群） |
| `MultiClientDispatcher` | 多客户端路由分发（flowGroupName 路由组模式） |
| `SearchThrottleService` | 高风险查询检查 + 查询模板限流的核心服务 |
| `RequestConverters` | 将 ES Java API 请求对象转换为 HTTP 请求 |

---

## poros-service — 代理服务（部署态）

### 核心类

| 类 | 职责 |
|----|------|
| `PorosServiceBootStrap` | 启动入口，初始化 Guice 容器和 Netty Server |
| `PorosModule` | Guice 模块，所有绑定在此声明 |
| `HttpServerHandler` | Netty ChannelHandler，HTTP 请求入口 |
| `ESProxyBiz` / `ESProxyBizImpl` | 核心代理业务逻辑（过滤链 + ES 请求转发） |
| `EnvironmentAwareness` | 读取 JVM System Properties（cluster, timeout, call.es.async） |
| `RequestFilterChain` | 请求过滤链（5 个 filter 串联） |
| `ResponseFilterChain` | 响应过滤链（3 个 filter 串联） |

### Filter 清单

**请求过滤链（按顺序）**：
1. `InitFilter` — 初始化请求上下文
2. `PermissionFilter` — appKey/accessKey 鉴权（10min 缓存，Eagle API 同步）
3. `RateLimitFilter` — Rhino OneLimiter 按 appKey 限流
4. `QueryDSLFilter` — DSL 规则检查（terms/should/from+size/top_hits 阈值）
5. `CircuitBreakerFilter` — Rhino 熔断器（按 key 维度，触发条件可自定义）

**响应过滤链（按顺序）**：
1. `CatReportFilter` — Cat 打点（请求耗时、状态码、操作类型）
2. `SlowQueryFilter` — 慢查询日志记录
3. `CircuitBreakerClearFilter` — 更新熔断器状态（成功/失败计数）
