# poros-common — 共享基础层设计

**代码位置**: `/Users/shenhuayu/Desktop/Project/poros/poros-common/`  
**创建日期**: 2026-04-07

---

## 职责

poros-common 是 Poros 的**共享基础层**，被所有其他模块依赖。包含两类代码：

1. `com.sankuai.meituan.poros.common.*` — Poros 自身的共享代码
2. `org.elasticsearch.client.*` — Fork 的 ES 客户端代码

---

## EagleApiProxy — Eagle API 的核心封装

Eagle API 是 Poros 的"控制面"，提供集群管理、鉴权、配置下发等功能。

```java
EagleApiProxy eagleApiProxy = new EagleApiProxy(clusterName, basicAuth, isClusterGroup);
```

### 核心 API

| 方法 | 用途 |
|------|------|
| `isPorosArchitecture()` | 判断集群是否使用 Poros 架构 |
| `getNodes()` | 获取 ES 节点列表 |
| `getPorosNodes()` | 获取 Poros 代理节点列表 |
| `getToken()` | 获取 Poros 认证 token（用于 RestClient 的 Authorization header） |
| `getAppkeys(auth)` | 获取集群的 appKey 白名单 |
| `getDslConfigs()` | 获取 DSL 过滤规则配置 |
| `getSlowQueryConfiguration()` | 获取慢查询配置 |
| `getMafkaTopicUrl()` | 获取 Mafka topic URL |
| `getMafkaAppkey()` | 获取 Mafka appKey |
| `notifyUser(notificationRequest)` | 发送大象告警通知 |
| `report(reportRequest)` | 上报客户端配置 |

### getApiAppkey() — 多租户支持

```java
// 根据 LOCAL_TENANT 返回不同的 Eagle API appKey
"sankuai" / "isoldeploy" → "com.{tenant}.esplatform.api"
其他 tenant              → "com.{tenant}.eagle.esplatform.api"
默认（无 tenant）         → "com.sankuai.esplatform.api"
```

---

## RequestParseUtils — ES 请求路由解析

将 HTTP method + URL path 解析为 `RequestParseResult`（含 `operationType` 和 `index`）。

### 解析机制

使用 `PorosPathTrie`（前缀树）匹配 ES REST API 路径模式：
- `GET /{index}/_search` → `OperationType.SEARCH`
- `POST /{index}/_search` → `OperationType.SEARCH`
- `POST /{index}/_search/scroll` → `OperationType.SCROLL_SEARCH`
- `GET /_cat/*` → `OperationType.CAT`
- 等等

各 HTTP method 有独立的 Parser 实现（`GetEndPointParser`, `PostEndPointParser`, etc.）。

---

## OperationType 枚举

常用值：
- `SEARCH` — `_search` 查询
- `SCROLL_SEARCH` — `_scroll` 查询
- `INDEX` — 写入文档
- `DELETE` — 删除文档
- `BULK` — 批量操作
- `CAT` — `_cat` 管理接口

---

## AuthorizationUtils

```java
// 生成 Basic Auth header value
String headerValue = AuthorizationUtils.basicAuthHeaderValue(appKey, accessKey);
// 返回 "Basic base64(appKey:accessKey)"

// 从 header value 解析 appKey 和 accessKey
Pair<String, String> pair = AuthorizationUtils.decodeToAppkeyAccessKeyPair(authorization);
```

---

## ResponseConstructor

使用反射调用 `Response` 的 package-private 构造器，用于在 Filter 层构造错误响应：

```java
// 构造一个 400 Bad Request 的 ES Response 对象
Response response = ResponseConstructor.newInstance(requestLine, httpHost, httpResponse);
```

**注意**：这是 Poros 绕过 ES 封装的关键手段之一，ES 版本升级时需要验证此处是否仍然有效。

---

## ThreadPoolUtils

```java
// 定时任务线程池，用于各 Filter 的定期配置同步
ScheduledExecutorService REPORT_API = ...;
```

---

## Fork 的 ES 客户端（org.elasticsearch.client）

### 自适应负载均衡（route/loadbalance/）

| 类 | 职责 |
|----|------|
| `LoadBalancer` 接口 | 负载均衡策略接口 |
| `AdaptiveLoadBalancer` | 自适应负载均衡实现，基于 inflight 请求数 |
| `AdaptiveInflightStat` | 统计各节点的 inflight 请求数 |
| `AdaptiveWeight` | 节点权重计算 |
| `EmptyLoadBalancer` | 空实现（不做负载均衡） |
| `LoadbalancerPicker` | 负载均衡选择器 |

### 节点嗅探（sniff/）

- `Sniffer` — 定期嗅探节点列表，节点失败时触发重嗅探
- `ElasticsearchNodesSniffer` — 通过 `_nodes` API 发现 ES 节点
- `SniffOnFailureListener` — 节点失败时触发 Sniffer
- `SniffOnCloseListener` — 客户端关闭时停止 Sniffer

### 后台任务（task/）

- `ConfigApiReportTask` — 定期上报客户端配置到 Eagle API
- `ConfigEventReportTask` — 上报配置变更事件到 Cat
- `BackgroundTasksOnCloseListener` — 客户端关闭时停止所有后台任务

### 分布式追踪（trace/）

- `TraceUtil` — 获取 TraceId（用于错误信息中附加 traceId）
- `InnerTracer` — 内部追踪实现

### 其他关键 fork 类

- `RestClient` — 核心 fork，增加了 `setClusterName()`, `setTimeout()`, `isES8Cluster()`, `setCloseListener()` 等方法
- `ClientHedgingPolicy` — 对冲请求策略（Backup Request 实现基础）
- `RegionPriorityNodeSelector` — 优先选择同 region 节点
- `PreferCoordinatingOnlyNodeSelector` — 优先选择 Coordinating-only 节点
- `DeadHostState` — 记录节点失活状态（用于故障转移）
