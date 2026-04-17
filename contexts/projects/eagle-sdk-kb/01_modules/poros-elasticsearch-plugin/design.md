# poros-elasticsearch-plugin 设计文档

**代码路径**: `/Users/shenhuayu/Desktop/Project/poros/poros-elasticsearch-plugin/`  
**创建日期**: 2026-04-07  

---

## 一句话定位

`poros-elasticsearch-plugin` 是一个**部署在 ES 节点侧**的安全插件，在 ES 接收 REST 请求时进行 appKey/accessKey 鉴权，鉴权逻辑与 poros-service 的 `PermissionFilter` 对称。

---

## 模块结构

```
poros-elasticsearch-plugin/
└── src/main/java/com/sankuai/meituan/poros/plugin/
    ├── AuthorizationActionPlugin.java   # ES Plugin 入口
    └── AuthenticationService.java       # 鉴权核心逻辑
```

只有 2 个主要 Java 文件，代码量极少但设计精巧。

---

## 核心类

### AuthorizationActionPlugin（Plugin 入口）

```
extends Plugin implements ActionPlugin
```

**职责**：
1. 声明自定义 ES 配置项 `poros.eagle.api.path`（必填，启动时校验）
2. 创建 `AuthenticationService` 组件（通过 `createComponents`）
3. 注册 REST Handler 拦截器（`getRestHandlerWrapper`），将所有 REST 请求包一层鉴权

**关键配置**：
```yaml
# elasticsearch.yml
poros.eagle.api.path: "https://eagleweb.sankuai.com/api"
```

---

### AuthenticationService（鉴权核心）

```
extends AbstractLifecycleComponent
```

**职责**：对每个 REST 请求做 appKey/accessKey 鉴权，结果双向缓存。

#### 支持的 Authorization Header 格式

| 前缀 | 说明 | 缓存 key |
|------|------|---------|
| `Basic ` | 标准 HTTP Basic Auth | 完整 header 值 |
| `Poros ` | Poros 自定义格式 | 完整 header 值 |
| `MWS ` | MWS 签名格式 | `MWS {appKey}` 前缀（冒号前截断） |

**跳过鉴权的路径**：`""` 和 `"/"`（健康检查等）

#### 双缓存设计

```java
// 有效授权缓存：永不过期，手动管理
ConcurrentMap<String, AuthorizationCounter> validAuthorizations

// 无效授权缓存：1 分钟后自动过期
Cache<String, AuthorizationCounter> invalidAuthorizations  // maxWeight=300, expireAfterWrite=1min
```

**为什么分开**：
- 有效授权需要长期缓存（10 分钟后后台重新检查），避免每次请求都调 Eagle API
- 无效授权短期缓存（1 分钟），防止暴力尝试，同时快速响应权限变更

#### 鉴权流程

```
1. 检查 validAuthorizations（命中 → 放行）
2. 检查 invalidAuthorizations（命中 → 拒绝 401）
3. 加 KeyedLock（按 cacheKey 粒度，防并发重复请求）
4. 双重检查（DCL）
5. 调 Eagle API POST /authorization/clusters/{clusterName}/check
6. 200 OK → 放入 valid 缓存；否则 → 放入 invalid 缓存
```

#### AuthorizationRechecker（后台定时重检）

```java
extends AbstractAsyncTask
// 每 10 分钟执行一次
```

**逻辑**：遍历所有 `validAuthorizations`，重新调 Eagle API 验证。失效的授权从 valid 移到 invalid 缓存。这是授权撤销能够生效的机制（最多 10 分钟延迟）。

#### 容错设计

```java
// checkAuth 方法：Eagle API 调用失败时，放行请求（宽松模式）
} catch (Exception e) {
    logger.warn(...);
    return true;  // ← 鉴权中心故障时不拦截，防止 ES 不可用
}
```

**⚠️ 注意**：Eagle API 故障时所有请求都会放行，这是有意的可用性优先设计。

#### AuthorizationCounter

每个缓存条目同时记录 `authHeader` 原值和访问计数（`LongAdder`），计数用于监控（未在代码中直接使用，保留扩展）。

---

## 与 poros-service PermissionFilter 的对比

| 维度 | poros-service PermissionFilter | poros-elasticsearch-plugin |
|------|-------------------------------|---------------------------|
| 部署位置 | Poros 代理服务进程 | ES 节点进程（插件形式） |
| 适用场景 | 代理模式（业务 → Poros → ES） | 直连模式（需要 ES 侧鉴权） |
| 鉴权接口 | Eagle API `/authorization/check` | Eagle API `/authorization/clusters/{name}/check` |
| 缓存时间 | 10 分钟（Lion 配置） | valid 永不过期+10min 重检，invalid 1min |
| 失败策略 | 拒绝 | 放行（可用性优先） |

---

## 关键 Gotcha

1. **ES 版本绑定**：插件使用了 ES 内部 API（`AbstractLifecycleComponent`、`AbstractAsyncTask`、`KeyedLock` 等），ES 升级时需要重新编译和验证兼容性。

2. **MWS 缓存 key 截断**：MWS header 格式为 `MWS {appKey}:{signature}:{timestamp}`，缓存时只取冒号前的部分（`MWS {appKey}`），避免签名变化导致缓存失效。

3. **授权撤销延迟**：valid 缓存永不自动过期，撤销授权最多需要 10 分钟才能生效（等待 `AuthorizationRechecker` 下一轮）。
