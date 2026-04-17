# 学城摘要：Poros Java API 客户端（ES8）

**学城原文**: https://km.sankuai.com/collabpage/2293336777  
**摘要日期**: 2026-04-07  
**文档 contentId**: 2293336777

---

## 一句话定位

`poros-java-api-client` 是基于官方 ES Java API Client 封装的新版客户端，**只支持 ES8**，支持向量检索，强类型 API，可与 ES7 的 poros-high-level-client 共存。

---

## 核心限制

- ❌ **只能访问 ES8 集群**，不支持 ES7 / ES5
- ⚠️ 与 poros-high-level-client 共存时，两者的 Request 类名很多相同，需用全路径区分：
  - RHLC（ES7）：`org.elasticsearch.*`
  - Java API Client（ES8）：`co.elastic.clients.*`
- ⚠️ 异步客户端和同时构造同步+异步客户端**不支持集群组流量调度功能**

---

## Maven 依赖

```xml
<dependencyManagement>
  <dependencies>
    <dependency>
      <groupId>com.sankuai.meituan</groupId>
      <artifactId>poros-java-api-client</artifactId>
      <version>${version}</version>
    </dependency>
    <!-- Jackson 版本必须统一为 2.17.2（2.17.0 有内存泄漏） -->
    <dependency>
      <groupId>com.fasterxml.jackson.core</groupId>
      <artifactId>jackson-databind</artifactId>
      <version>2.17.2</version>
    </dependency>
  </dependencies>
</dependencyManagement>
```

**最新正式版本**: `1.0.2`  
**Release Note**: https://km.sankuai.com/collabpage/2726233215

---

## 构造客户端

```java
// 同步客户端（推荐）
PorosApiClient porosApiClient = PorosApiClientBuilder.builder()
    .clusterName("ES集群名")
    .appKey("你的客户端appkey")  // ⚠️ 填业务自己的 appkey，不是 ES 集群 appkey！
    .timeoutMillis(10000)
    .build();

// 异步客户端
PorosApiAsyncClient asyncClient = PorosApiClientBuilder.builder()
    .clusterName("ES集群名")
    .appKey("你的客户端appkey")
    .timeoutMillis(10000)
    .buildAsyncClient();

// 同时构造同步+异步
PorosApiClients clients = PorosApiClientBuilder.builder()
    .clusterName("ES集群名")
    .appKey("你的客户端appkey")
    .timeoutMillis(10000)
    .buildClients();
```

---

## 关键 API 特性

### 3.1 Search API
- 强类型返回，支持 `SearchResponse<T>`
- 支持 `Void.class` 忽略 source（仅要 hits metadata）
- 支持 Scroll（`searchAfter` 替代旧版 scroll）

### 3.2 Bulk API
- 用 `BulkIngester` 替代 RHLC 的 `BulkProcessor`
- 支持 `maxOperations`（批量大小）+ `flushInterval`（定时刷新）

### mrrf 功能
Eagle 平台支持 mrrf（多路召回融合），用法与官方 rrf 一致：
```java
.rank(rank -> rank.mrrf(mrrf -> mrrf.windowSize(20L).rankConstant(10L)))
```

---

## 监控

| Cat 打点 | 含义 |
|---------|------|
| `ES.{集群名}` Transaction | 端到端耗时，含索引粒度明细 |
| `ES.{集群名}.retry` Problem | 客户端重试打点（连接超时、线程获取失败等触发） |

**请求类型枚举**: index / update / delete / bulk / update.by.query / delete.by.query / get / mget / search / scroll.search / reindex / arts.search / other

---

## FAQ / 坑

### 依赖冲突
`poros-java-api-client` 和 `poros-high-level-client` 共依赖 `poros-client`，共存时需要：
- `poros-high-level-client` 版本 ≥ `0.9.23_ES7`
- 不建议额外指定 `poros-client` 版本（1.0.2 之后已不需要）

### `jakarta/json/JsonException` 或 `ClassNotFoundException: jakarta.json.spi.JsonProvider`
显式配置：
```xml
<dependency>
  <groupId>jakarta.json</groupId>
  <artifactId>jakarta.json-api</artifactId>
  <version>2.0.1</version>
</dependency>
```

### Jackson 内存泄漏
`jackson 2.17.0` 有内存泄漏，可能导致 GC 飙高甚至 OOM，**必须升级到 2.17.2**。

---

## 与其他客户端对比

| 客户端 | 适用集群 | 特点 |
|--------|---------|------|
| poros-high-level-client (ES7) | ES7 / ES5 | 支持慢查询限流、高风险拦截 |
| poros-java-api-client (ES8) | ES8 only | 强类型、支持向量检索、更轻量 |
| poros-high-level-client + isES8Cluster=true | ES8（兼容模式） | 不推荐上线，仅用于迁移测试 |
