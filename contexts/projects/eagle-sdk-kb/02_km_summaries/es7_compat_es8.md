# 学城摘要：ES7 客户端兼容 ES8

**学城原文**: https://km.sankuai.com/collabpage/2131195847  
**摘要日期**: 2026-04-07  
**文档 contentId**: 2131195847

---

## 一句话定位

用 ES7 的 `poros-high-level-client` 加一个参数 `isES8Cluster(true)` 访问 ES8 集群。**仅用于迁移测试，不建议上线。** 正式使用请用 `poros-java-api-client`。

---

## 背景

- 官方从 ES7.16 开始废弃 `RestHighLevelClient`，推出新 Java API Client
- 业务从 RHLC 升级到 Java API Client 有成本，因此提供了兼容模式
- 兼容模式无法使用 ES8 全部特性，仅用于测试

---

## 使用方式

### Maven 依赖

```xml
<dependency>
  <groupId>com.sankuai.meituan</groupId>
  <artifactId>poros-high-level-client</artifactId>
  <version>0.9.23_ES7-SNAPSHOT</version>
</dependency>
<dependency>
  <groupId>org.elasticsearch</groupId>
  <artifactId>elasticsearch</artifactId>
  <version>7.10.2-mt4</version>
  <exclusions>
    <exclusion>
      <groupId>org.elasticsearch.client</groupId>
      <artifactId>elasticsearch-rest-client</artifactId>
    </exclusion>
  </exclusions>
</dependency>
```

### 代码改造：只需加 `isES8Cluster(true)`

```java
PorosHighLevelClient client = PorosHighLevelClientBuilder.builder()
    .clusterName("集群名")
    .appKey("客户端appkey")
    .callESDirectly(true)
    .isES8Cluster(true)  // ← 唯一改动
    .build();
```

`RestClient` 直接使用时同理：
```java
RestClient restClient = RestClient.builder(nodes)
    .setClusterName(clusterName)
    .isES8Cluster(true)  // ← 唯一改动
    .build()
```

---

## 已知不兼容列表（踩坑必看）

### 1. 组合索引模板（Composable Index Template）解析失败

**现象**：创建 1 个组合索引模板后，单独查找该模板成功，但 `getIndexTemplate`（获取所有模板）会抛异常：

```
java.io.IOException: Unable to parse response body
Caused by: XContentParseException: [data_stream_template] unknown field [hidden]
```

**根因**：ES8 的 `data_stream` 模板新增了 `hidden` 字段，ES7 的解析器不认识，直接报错。

**影响范围**：`IndicesClient.getIndexTemplate()` 调用全量模板时必现。

---

## 结论

| 场景 | 建议 |
|------|------|
| 集群从 ES7 升级到 ES8 的过渡测试 | 可用兼容模式（`isES8Cluster=true`） |
| 新业务接入 ES8 集群 | 直接用 `poros-java-api-client` |
| 生产环境长期使用 ES8 | **必须**用 `poros-java-api-client`，兼容模式不支持全部特性 |
