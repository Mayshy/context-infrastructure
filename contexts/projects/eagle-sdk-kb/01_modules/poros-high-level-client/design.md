# poros-high-level-client — 对外 SDK 设计

**代码位置**: `/Users/shenhuayu/Desktop/Project/poros/poros-high-level-client/`  
**学城文档**: https://km.sankuai.com/collabpage/1127183403  
**创建日期**: 2026-04-07

---

## 职责

poros-high-level-client 是 Poros 的**主要对外发布产物**。业务方引入此 SDK 后，可以用类似官方 ES Java High Level REST Client 的 API 访问 ES，同时获得 Poros 提供的高风险查询拦截、查询模板限流、集群路由等能力。

---

## 多版本支持

```
src/main/
├── 5.6.3/   — ES 5.x 集群使用
├── 6.8.10/  — ES 6.x 集群使用
└── 7.10.0/  — ES 7.x 集群使用（当前主力，功能最完整）
```

构建时通过 `POROS_ES_VERSION` 环境变量选择版本（默认 7.10.0）。

---

## 快速上手

```java
PorosRestHighLevelClient client = PorosHighLevelClientBuilder.builder()
    .clusterName("my-cluster")
    .appKey("com.example.myapp")
    .accessKey("my-access-key")
    .callESDirectly(true)          // true=直连ES, false=走Poros代理
    .timeoutMillis(10000)
    .throttleHighRiskQuery(true)   // 开启高风险查询拦截
    .queryTemplateRateLimit(true)  // 开启查询模板限流
    .onlyCatThrottleEvent(true)    // 软拦截（只打点不真正拦截）
    .build();
```

---

## PorosHighLevelClientBuilder 配置项全览

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `clusterName` | 必填 | ES 集群名 |
| `appKey` | 必填 | 业务方 appKey |
| `accessKey` | 必填（或 KMS） | 认证密钥 |
| `timeoutMillis` | 10000 | 全局超时（ms），0 = 不超时 |
| `callESDirectly` | `false` | `true`=直连ES, `false`=走Poros代理 |
| `throttleHighRiskQuery` | `true` | 是否开启高风险查询拦截 |
| `queryTemplateRateLimit` | `true` | 是否开启查询模板限流 |
| `onlyCatThrottleEvent` | `true` | 软拦截：只打 Cat 点，不真正拒绝 |
| `httpMaxConnectionPerRoute` | 10 | 每个 ES 节点的最大连接数 |
| `httpMaxConnectionTotal` | 30 | 总最大连接数 |
| `httpIOThreadCount` | CPU 核数 | NIO IO 线程数（建议用 `Runtime.getRuntime().availableProcessors()`） |
| `selectInterval` | 1000ms | NIO selector 轮询间隔，调小可提高超时敏感度但增加 CPU |
| `tcpKeepAlive` | `false` | TCP KeepAlive |
| `callPorosAsync` | `true` | 是否异步调用 Poros 代理 |
| `porosProtocol` | `PIGEON` | 代理模式的传输协议（HTTP / PIGEON） |
| `isClusterGroup` | `false` | 是否集群组模式（已废弃，用 flowGroupName 替代） |
| `clusterGroupName` | — | 集群组名（与 clusterName 互斥） |
| `flowGroupName` | — | 路由组名，设置后使用 MultiClientDispatcher |
| `cell` | — | Cell 隔离值（多机房路由） |
| `isES8Cluster` | `false` | 是否 ES8 集群（兼容性参数） |

---

## SearchThrottleService — 核心安全机制

### 高风险查询检查（throttleHighRiskQuery）

检查顺序：from/size → query → aggregation

**RiskType 枚举（所有风险类型）**：

| RiskType | 描述 | 检查对象 |
|---------|------|---------|
| `FROM_SIZE_RISK` | from + size 超过阈值 | SearchSourceBuilder |
| `TERMS_COUNT_RISK` | terms 查询的 values 数量过多 | TermsQueryBuilder |
| `SHOULD_COUNT_RISK` | bool should 子查询数量过多 | BoolQueryBuilder |
| `REGEXP_MAX_STATES_COUNT` | 正则 NFA 状态数过多 | RegexpQueryBuilder |
| `REGEXP_WORD_SIZE_RISK` | 正则表达式长度过长 | RegexpQueryBuilder |
| `WILDCARD_WORD_SIZE_RISK` | 通配符查询词过长 | WildcardQueryBuilder |
| `WILDCARD_WORD_PATTERN_RISK` | 通配符全是 `*` | WildcardQueryBuilder |
| `MATCH_PHRASE_WORD_SIZE_RISK` | match_phrase 查询词过长 | MatchPhraseQueryBuilder |
| `AGG_TERMS_DEPTH_RISK` | terms agg 嵌套深度过大 | TermsAggregationBuilder |
| `AGG_TERMS_SIZE_RISK` | terms agg size 过大 | TermsAggregationBuilder |
| `AGG_TERMS_SHARD_SIZE_RISK` | terms agg shardSize 过大 | TermsAggregationBuilder |

**QueryRiskChecker 策略模式**：
```java
static Map<String, QueryRiskChecker> queryRiskCheckers = new HashMap<>();
// 初始化时按 QueryBuilder 类名注册对应的 Checker
queryRiskCheckers.put(TermsQueryBuilder.class.getName(), new TermsQueryRiskChecker());
queryRiskCheckers.put(BoolQueryBuilder.class.getName(), new BoolQueryRiskChecker());
// ...
```

**风险阈值配置**（`ForceThrottleRiskQueryConfig`）：
- 来源：Lion，key = `ForceThrottleRiskCheckConfigV2`，appKey = Eagle API appKey
- JSON 配置，包含各 RiskType 的阈值

### 查询模板限流（queryTemplateRateLimit）

- 使用 `QueryTemplateExtractor.extract(requestSource)` 提取查询模板 ID
- 限流 key = `cluster_templateId_index`
- Rhino OneLimiter 执行限流判断
- 限流规则在 Rhino 平台配置

### 软拦截 vs 硬拦截

```java
if (isOnlyCatThrottleEvent()) {
    // 软拦截：只打 Cat 点，请求继续执行
    Cat.logEvent("ES.QueryRisk." + riskType.type, cluster, ...);
} else {
    // 硬拦截：返回 ThrottleResult(isThrottled=true)，请求被拒绝
    return new ThrottleResult(true, reason);
}
```

**配置优先级**：Lion 配置 > 本地构造器配置。三个开关都可以通过 Lion 动态调整，无需重启。

---

## 多客户端路由（flowGroupName 模式）

```java
// 配置 flowGroupName 后，build() 调用 buildClientGroup()
PorosHighLevelClientBuilder.builder()
    .clusterName("my-cluster")
    .flowGroupName("my-flow-group")
    .build();
// → MultiClientDispatcher.build()
// → 根据 flowGroupName 从 Eagle API 获取路由配置
// → 按 cell/swimlane/idc 路由到不同集群
```

---

## 压测客户端（PorosStressTestClient）

- 包装 `PorosInnerRestHighLevelClient`
- 压测流量双写到压测集群
- 通过 Lion 开关控制是否启用

---

## 关键踩坑

1. **`httpIOThreadCount` 建议**：要么用默认值（CPU 核数），要么显式设置为 `Runtime.getRuntime().availableProcessors()`，不要随意设小值。

2. **`selectInterval` 与超时敏感度**：如果 `timeoutMillis < 1000ms`，需要同时把 `selectInterval` 调小，否则超时不够精准。

3. **`onlyCatThrottleEvent` 默认为 true**：新接入时默认软拦截，不会真正拒绝请求。如果要开启硬拦截，需要显式 `.onlyCatThrottleEvent(false)`。

4. **Lion 配置优先于本地配置**：`isThrottleHighRiskQuery()`、`isQueryTemplateRateLimit()`、`isOnlyCatThrottleEvent()` 三个方法都会先查 Lion，查不到才用本地值。这意味着即使本地配置了 `false`，Lion 上配置了 `true` 也会生效。
