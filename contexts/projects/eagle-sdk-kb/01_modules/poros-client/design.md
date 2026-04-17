# poros-client — 低层客户端构造层设计

**代码位置**: `/Users/shenhuayu/Desktop/Project/poros/poros-client/`  
**创建日期**: 2026-04-07

---

## 职责

poros-client 是 Poros 的**低层客户端模块**，负责根据配置构建 `RestClient` 实例。它处理三种连接模式的选择和底层 HTTP/RPC 连接池的配置。

poros-high-level-client 依赖此模块（通过 `PorosRestClientBuilder`）。

---

## 核心类：PorosRestClientBuilder

### 三种连接模式决策树

```
callESDirectly=true
    → buildHTTPClient(ES 节点直连)
    → 使用 ElasticsearchNodesSniffer 自动发现节点

callESDirectly=false
    → 检查 eagleApiProxy.isPorosArchitecture()
    → 若非 Poros 架构 → buildHTTPClient(ES 节点直连)
    → 若是 Poros 架构：
        → porosProtocol=HTTP → buildHTTPClient(Poros 代理节点)
        → porosProtocol=PIGEON → buildRPCClient(Mafka 异步写入)

isClusterGroup=true（已废弃）
    → buildRPCClient()
```

### 集群 vs 集群组

```
clusterName 不为空, clusterGroupName 为空 → 单集群模式
clusterName 为空, clusterGroupName 不为空 → 集群组模式（callESDirectly 必须 true）
两者都不为空 / 都为空 → 抛 PorosException
```

### KMS 认证

```java
if (KmsUtils.authSwitch(this.appKey)) {
    // 从 KMS 获取最新版本的 accessKey
    // 替换本地配置的 accessKey
    this.authorizeByKms = true;
}
```

---

## buildHTTPClient 关键配置

```java
RestClient.builder(nodes)
    .setClusterName(clusterName)
    .setTimeout(timeoutMillis)
    .isES8Cluster(isES8Cluster)
    .setDefaultHeaders(defaultHeaders)  // Authorization: Basic base64(appKey:accessKey)
    .setFailureListener(sniffOnFailureListener)  // 节点失败时触发 sniffer
    .setCloseListener(compositeOnCloseListener)  // 关闭时清理 sniffer + 后台任务
    .setHttpClientConfigCallback(httpClientBuilder -> {
        // 添加 CatHttpProcessor（Cat 监控打点）
        // 配置 NIO IO 线程数、selectInterval、tcpKeepAlive
        // 配置连接池：maxPerRoute + maxTotal
        // 禁用 auth caching
    })
    .setRequestConfigCallback(requestConfigBuilder -> {
        // connectTimeout = socketTimeout = connectionRequestTimeout = timeoutMillis
    })
```

### Sniffer 配置

```java
Sniffer.builder(restClient)
    .setNodesSniffer(snifferSupplier)  // 直连=ElasticsearchNodesSniffer, 代理=PorosNodesSniffer
    .setSniffIntervalMillis(DEFAULT_SNIFF_INTERVAL)
    .setSniffAfterFailureDelayMillis(DEFAULT_SNIFF_AFTER_FAILURE_DELAY)
```

---

## buildRPCClient（Mafka 异步写入）

```java
// 通过反射调用 RestClientPorosImpl 的 package-private 构造器
Constructor<RestClientPorosImpl> constructor = RestClientPorosImpl.class.getDeclaredConstructor(...);
constructor.setAccessible(true);
return constructor.newInstance(clusterName, appKey, accessKey, maxRetryTimeoutMillis, 
    callPorosAsync, isClusterGroup, mafkaTopic, mafkaAppkey);
```

**注意**：RPC 模式下请求通过 Mafka 异步写入，不适合需要同步读响应的查询场景。

---

## CatHttpProcessor（监控打点）

实现 `HttpRequestInterceptor` 和 `HttpResponseInterceptor`：
- 请求拦截：记录请求开始时间，创建 Cat Transaction
- 响应拦截：记录响应状态码，完成 Cat Transaction

---

## PorosNodesSniffer

- 实现 `NodesSniffer` 接口
- 从 `EagleApiProxy.getPorosNodes()` 获取 Poros 代理节点列表
- 用于代理模式下的节点发现（替代 `ElasticsearchNodesSniffer`）

---

## 后台任务（BackgroundTasksOnCloseListener）

构建 RestClient 时注册两个后台任务：

| 任务 | 职责 |
|------|------|
| `ConfigEventReportTask` | 上报配置事件到 Cat（timeout, authorizedByKms 等） |
| `ConfigApiReportTask` | 上报客户端配置到 Eagle API（appKey, cluster, timeout, 限流开关等） |

客户端关闭时（`close()`）自动停止这些后台任务。
