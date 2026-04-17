# Poros 技术栈备忘

**创建日期**: 2026-04-07

---

## 核心技术选型

| 层次 | 技术 | 版本/说明 |
|------|------|---------|
| **语言** | Java | 8（`sourceCompatibility = JavaVersion.VERSION_1_8`） |
| **构建** | Gradle | 多模块，`settings.gradle` 定义子模块 |
| **DI 框架** | Google Guice | 无 Spring，`@Singleton` + `@Inject` + `@Named` |
| **HTTP Server** | Netty | poros-service 的 HTTP 入口 |
| **ES Client** | Elasticsearch Java High Level REST Client | 多版本：5.6.3 / 6.8.10 / 7.10.0 |
| **限流/熔断** | Rhino（美团内部） | `OneLimiter`（限流）+ `CircuitBreaker`（熔断） |
| **配置中心** | Lion（美团内部） | 动态配置拉取，`Lion.getBoolean(appKey, key, defaultValue)` |
| **监控** | Cat（美团内部） | `Cat.logEvent()` + `Cat.newTransaction()` |
| **RPC** | Pigeon（美团内部） | 可选传输协议，替代 HTTP 直连 |
| **消息队列** | Mafka（美团内部 Kafka） | RPC 模式下的异步写入 |
| **分布式追踪** | MTrace（美团内部） | Cell/Swimlane 路由 + TraceId |
| **密钥管理** | KMS（美团内部） | accessKey 安全存储，替代明文配置 |
| **注解工具** | Lombok | `@Data`, `@Slf4j`, `@Builder`, `@NonNull` 等 |
| **JSON** | Jackson | `ObjectMapper`，`@JsonProperty` |
| **HTTP Client** | Apache HttpClient (async NIO) | `PoolingNHttpClientConnectionManager` |

---

## 关键配置项（JVM System Properties）

poros-service 启动时读取 System Properties（`-Dcluster=xxx`）：

| Key | 说明 | 默认值 |
|-----|------|--------|
| `cluster` | ES 集群名，必填 | — |
| `clusterGroup` | 集群组名（可选，与 cluster 互斥） | — |
| `timeout` | 全局超时（ms） | 30000 |
| `call.es.async` | 是否异步调用 ES | `true` |

---

## Lion Key 常量（`Constants.LionKey`）

| Key 前缀 | 用途 |
|---------|------|
| `THROTTLE_HIGH_RISK_QUERY_PREFIX + cluster` | 是否开启高风险查询拦截 |
| `QUERY_TEMPLATE_RATELIMIT_PREFIX + cluster` | 是否开启查询模板限流 |
| `ONLY_CAT_THROTTLE_EVENT_PREFIX + cluster` | 是否仅打点（软拦截） |
| `DISABLE_SEARCH_ROUND_ROBIN` | 是否禁用 Round Robin 重试 |

---

## Eagle API 接口清单

base path: `http://eagleweb.sankuai.com/api`（线上）/ `http://eagleweb.dppt.test.sankuai.com/api`（测试）

| 接口 | 用途 |
|------|------|
| `GET /clusters/{cluster}/isPoros` | 判断是否 Poros 架构 |
| `GET /clusters/{cluster}/poros-nodes` | 获取 Poros 代理节点列表 |
| `GET /clusters/{cluster}/nodes` | 获取 ES 节点列表 |
| `GET /clusters/{cluster}/token` | 获取 Poros 认证 token |
| `GET /clusters/{cluster}/appkeys` | 获取授权 appKey 列表 |
| `GET /clusters/{cluster}/dsl-filter/configuration` | 获取 DSL 过滤规则配置 |
| `GET /clusters/{cluster}/slow-query/configuration` | 获取慢查询配置 |
| `GET /clusters/{cluster}/mafkaTopic` | 获取 Mafka topic URL |
| `POST /notification/notify` | 大象告警通知 |
| `POST /clusters/{cluster}/report` | 上报客户端配置信息 |

---

## 版本控制

```bash
# 默认编译 7.10.0
./gradlew build

# 指定版本
POROS_ES_VERSION=5.6.3 ./gradlew build
POROS_ES_VERSION=6.8.10 ./gradlew build
POROS_ES_VERSION=7.10.0 ./gradlew build
```

---

## 已知踩坑 / 注意事项

1. **`ResponseConstructor.newInstance()`** 使用反射调用 `Response` 的 package-private 构造器，因为 ES 官方不暴露这个构造器。如果 ES 版本升级导致构造器签名变化，这里会 break。

2. **`RestClientPorosImpl`** 同样通过反射调用 package-private 构造器（`constructor.setAccessible(true)`）——这是 fork 策略的代价。

3. **`PermissionFilter`** 的 appKey 缓存是 `volatile ConcurrentMap`，每次 clear + reload，在高并发下可能有短暂的权限空窗期。

4. **`QueryDSLFilter` 失败不阻断**：`catch (Exception e)` 后直接 `return FilterResponse.PASSED`，DSL 解析失败不影响主流程。

5. **`callESDirectly=false` + Pigeon 模式**：通过 Mafka 异步写入，不适合需要同步响应的场景。
