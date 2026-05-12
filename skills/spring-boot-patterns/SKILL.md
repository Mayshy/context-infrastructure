# Skill: spring-boot-patterns

## Description

DataMatrix 项目的 Spring Boot 编码规范审查。覆盖 Controller / Service / 异常处理 / Lion 配置 / Mafka / Pigeon / Blade JDBC 七大领域，基于 pontos/hermes/athena/kugget/worksheet 真实代码提炼。

**由 `workflow_code_review.md` 中的 Java 专项分支调用，不独立触发。**

---

## 触发条件（由 workflow 判断）

代码包含以下任意特征时启用本 skill：
- `@RestController` / `@Service` / `@Configuration` 类
- `ApiResult` 响应封装
- `Lion.get*()` / `@ConfigValue` / `@MdpConfig`
- `MafkaClient` / `@MafkaConsumer` / `@MdpMafkaMsgReceive`
- `InvokerConfig` / `ServiceFactory.getService()`
- `BladeDataSource` / `JdbcTemplate`

---

## 审查清单

### 1. 响应封装（ApiResult）

**✅ 正确：统一使用 `ApiResult<T>`**
```java
// 成功
return ApiResult.success(data);

// 失败（消息）
return ApiResult.fail("error message");

// 失败（ErrorCode）
return ApiResult.fail(ErrorCode.PARAM_VALIDATION_ERROR, errorList);

// 权限失败
return ApiResult.authFail(code, message);

// SSO 失败
return ApiResult.ssoFail(message);
```

**❌ 禁止：**
- 直接返回 `ResponseEntity`（不符合项目规范）
- 直接返回 POJO（绕过统一响应结构）
- 在 Controller 里 `throw` 异常（应 try-catch 后返回 `ApiResult.fail`）

**⚠️ 注意：hermes 的 `ApiResult` 与 pontos 略有差异**
- pontos: `{code, message, success, data}`，`RemoteCode` 枚举（0/401/402/500）
- hermes: `{code, message, data}`，code 0=正常，500=错误，无 `success` 字段
- 同一服务内保持一致，跨服务不要混用

---

### 2. Controller 规范

**✅ 标准声明：**
```java
@Api(tags = "模块名", description = "...")     // Swagger 必填
@RestController
@Slf4j
@RequestMapping(value = GlobalAttribute.URL_PREFIX + "/resource")
public class XxxController {

    @Autowired
    private IXxxService xxxService;

    @ApiOperation(value = "接口说明")
    @PostMapping(value = "/action")
    public ApiResult<ResponseType> doAction(
            HttpServletRequest request,
            @ApiParam(value = "参数说明") @RequestBody @Valid XxxRequest req) {
        String userMis = RequestParseUtil.getUserMis(request);
        try {
            ResponseType result = xxxService.doAction(req, userMis);
            return ApiResult.success(result);
        } catch (Exception e) {
            log.error("doAction failed: ", e);
            return ApiResult.fail(e.getMessage());
        }
    }
}
```

**URL 前缀规范：**
| 服务 | 公开接口 | 内部接口 |
|------|---------|---------|
| pontos | `/pontos/api/v1/` | `/pontos/internal/v1/` |
| hermes | `/hermes/api/v1/` | `/hermes/api/v1/internal/` |
| kugget | `/kugget-platform/` | — |
| worksheet | `/worksheet/api/v1/` | `/worksheet/api/flow/manage` |

**❌ 禁止：**
- Controller 中包含业务逻辑（应下沉到 Service）
- 直接暴露 Entity/DO（应使用 DTO/VO）
- 硬编码 URL 字符串（应使用 `GlobalAttribute.URL_PREFIX` 常量）
- 缺少 `@Api` / `@ApiOperation`（影响 Swagger 文档）

---

### 3. Service 层规范

**✅ 标准结构：接口 + Impl**
```java
// 接口（pontos/hermes 风格：I 前缀）
public interface IXxxService {
    ResponseType doAction(XxxRequest req, String userMis);
}

// 实现
@Service
@Slf4j
public class XxxServiceImpl implements IXxxService {

    @Autowired
    private XxxMapper xxxMapper;

    @Override
    @Transactional(rollbackFor = Exception.class)   // 写操作必须加
    public ResponseType doAction(XxxRequest req, String userMis) { ... }

    // 读操作：不加 @Transactional 或加 readOnly=true
    public List<Xxx> listXxx(QueryParam param) { ... }
}
```

**@Transactional 规范：**
```java
// 写操作（标准）
@Transactional(rollbackFor = Exception.class)

// 需要隔离级别时（如防幻读）
@Transactional(isolation = Isolation.READ_COMMITTED, rollbackFor = Exception.class)

// 跨数据源（hermes 多 DataSource 场景）
@Transactional(value = "dataverseManager", rollbackFor = Exception.class)

// ❌ 禁止：裸 @Transactional（不指定 rollbackFor，默认只回滚 RuntimeException）
```

**❌ 禁止：**
- Service 类上加 `@Transactional`（粒度太粗）
- 构造器注入（项目统一使用 `@Autowired` 字段注入）
- kugget 风格接口无 `I` 前缀混入 pontos/hermes 代码（保持各服务内一致性）

---

### 4. 异常处理规范

**✅ 全局异常处理器（每个服务必须有）：**
```java
@RestControllerAdvice
@Slf4j
public class GlobalExceptionHandler {

    // 参数校验失败（@Valid 触发）
    @ExceptionHandler(ConstraintViolationException.class)
    public ApiResult<List<String>> handleParamException(ConstraintViolationException e) {
        List<String> errors = e.getConstraintViolations().stream()
            .map(ConstraintViolation::getMessage).collect(Collectors.toList());
        return ApiResult.fail(ErrorCode.PARAM_VALIDATION_ERROR, errors);
    }

    // 权限异常
    @ExceptionHandler(PermissionException.class)
    public ApiResult<List<String>> handlePermissionException(PermissionException e) {
        return ApiResult.authFail(ErrorCode.NO_PERMISSION_ERROR.getCode(), e.getMessage());
    }

    // 兜底
    @ExceptionHandler(RuntimeException.class)
    public Object handleRuntimeException(RuntimeException e) {
        log.error("unexpected error: {}", e.getMessage(), e);
        return ApiResult.fail(e.getMessage());
    }
}
```

**✅ 自定义异常：继承 RuntimeException**
```java
public class XxxException extends RuntimeException {
    public XxxException(String msg) { super(msg); }
    public XxxException(String msg, Throwable cause) { super(msg, cause); }  // 保留异常链
}
```

**ErrorCode 枚举规范（pontos 风格）：**
```java
public enum ErrorCode {
    PARAM_VALIDATION_ERROR(ErrorType.Param, "参数不合法", 5001),
    NO_PERMISSION_ERROR(ErrorType.Auth, "权限校验不通过", 5002),
    RESOURCE_NOT_FOUND(ErrorType.Biz, "资源不存在", 5003),
    ERR_NOT_SUPPORT(ErrorType.Other, "其他异常", 9001);
    // 5001-5099: 参数错误
    // 5100-5199: 权限错误
    // 5200-5299: 业务错误
    // 9001+: 其他
}
```

**❌ 禁止：**
- `catch (Exception e) {}`（空 catch，吞掉异常）
- `catch (Exception e) { throw new RuntimeException(e); }`（丢失异常链，应传 `cause`）
- 在 Controller 中直接 `throw`（应 try-catch 返回 `ApiResult.fail`）

---

### 5. Lion 配置规范

**三种注入方式，按场景选择：**

**方式 A：`@ConfigValue`（xframe，Spring Bean 中首选）**
```java
@Service
public class XxxServiceImpl {
    @ConfigValue(key = "Pontos.Feature.SomeConfig")
    private String someConfig;

    @ConfigValue(key = "Pontos.Feature.MaxRetry")
    private int maxRetry;
}
```
适用：Spring 管理的 Bean，配置在启动时注入，不需要热更新监听。

**方式 B：`Lion.get*()`（命令式，适合动态/复杂场景）**
```java
// 基础类型
String value = Lion.getString(GlobalAttribute.APPKEY, LionKeyConst.SOME_KEY);
int timeout = Lion.getInt(GlobalAttribute.APPKEY, LionKeyConst.TIMEOUT, 3000);  // 带默认值
boolean dryRun = Lion.getBoolean(GlobalAttribute.APPKEY, LionKeyConst.DRY_RUN, Boolean.TRUE);

// 复杂类型
List<String> list = Lion.getList(GlobalAttribute.APPKEY, LionKeyConst.EXCLUDE_LIST, String.class);
Map<String, String> map = Lion.getMap(GlobalAttribute.APPKEY, LionKeyConst.TYPE_MAP, String.class);
SparkJobConfig config = Lion.getBean(GlobalAttribute.APPKEY, LionKeyConst.SPARK_JOB_CONFIG, SparkJobConfig.class);
```
适用：运行时动态读取，或需要带默认值的场景。

**方式 C：`ConfigRepository + ConfigListener`（热更新场景）**
```java
static {
    ConfigRepository repo = Lion.getConfigRepository(GlobalAttribute.APPKEY);
    cachedConfig = JsonUtils.fromJson(repo.get("Pontos.ComplexConfig", "{}"), ComplexConfig.class);
    repo.addConfigListener("Pontos.ComplexConfig", event -> {
        cachedConfig = JsonUtils.fromJson(repo.get("Pontos.ComplexConfig", "{}"), ComplexConfig.class);
        log.info("Config reloaded: {}", cachedConfig);
    });
}
```
适用：需要实时感知配置变更的场景。

**方式 D：`@MdpConfig`（kugget/MDP 框架）**
```java
@MdpConfig("Kugget.Feature.Host:https://default.host")  // key:defaultValue
private String featureHost;
```
适用：kugget 服务中使用 MDP 框架的场景。

**Lion Key 命名规范（`*LionKeyConst.java` 常量类）：**
```java
// 文件：LionKeyConst.java（每个服务一个）
public class LionKeyConst {
    // 命名规范：ServiceName.Domain.Feature.Attribute（层级点分隔）
    public static final String MIRROR_FULL_SYNC_DEFAULT_CONFIG = "Pontos.Mirror.FullSync.DefaultSparkJobConfig";
    public static final String MIRROR_REALTIME_SYNC_PACKAGE = "Pontos.Mirror.RealtimeSync.DefaultFlinkPackage";
    public static final String BATCH_UPDATE_DRY_RUN = "Pontos.BatchUpdatePackage.DryRun";
    public static final String BLADE_CAPACITY_THRESHOLD = "Pontos.Blade.Capacity.Threshold";
}
```

**❌ 禁止：**
- 直接在代码中硬编码 Lion Key 字符串（必须定义在 `*LionKeyConst.java`）
- 混用注入方式（同一服务统一使用 `@ConfigValue` 或 `Lion.get*()`，不要混用）

---

### 6. Mafka 规范

**三种 Consumer 模式（按服务框架选择）：**

**模式 A：手动 `@PostConstruct`（pontos/worksheet，通用）**
```java
@Service
@Slf4j
public class XxxConsumer {
    @Value("${mafka.topic:}")
    private String topic;
    @Value("${mafka.group:}")
    private String group;

    @PostConstruct
    public void init() throws Exception {
        Properties props = new Properties();
        props.setProperty(ConsumerConstants.MafkaBGNamespace, "octo");
        props.setProperty(ConsumerConstants.MafkaClientAppkey, GlobalAttribute.APPKEY);
        props.setProperty(ConsumerConstants.SubscribeGroup, group);
        IConsumerProcessor consumer = MafkaClient.buildConsumerFactory(props, topic);
        consumer.recvMessageWithParallel(String.class, (message, context) -> {
            try {
                handleMsg(message);
                return ConsumeStatus.CONSUME_SUCCESS;
            } catch (Exception e) {
                log.error("consume failed, msg={}", message, e);
                return ConsumeStatus.CONSUME_FAILURE;  // 触发重试
            }
        });
    }
}
```

**模式 B：`@MafkaConsumer` 注解（hermes/xframe）**
```java
@Component
@Slf4j
public class XxxMafkaConsumer {
    @MafkaConsumer(namespace = "octo", topic = "topic_name",
                   group = "consumer_group", className = String.class)
    public boolean onReceiveMessage(String msgBody) {
        try {
            handleMsg(msgBody);
            return true;
        } catch (Exception e) {
            log.error("consume failed: ", e);
            return true;  // 注意：即使失败也返回 true，避免无限重试
        }
    }
}
```

**模式 C：`@MdpMafkaMsgReceive`（kugget/MDP）**
```java
@Service
@Slf4j
public class XxxConsumerListener {
    @MdpMafkaMsgReceive
    public ConsumeStatus receive(String msgBody) {
        try {
            handleMsg(msgBody);
            return ConsumeStatus.CONSUME_SUCCESS;
        } catch (Exception e) {
            log.error("consume failed: ", e);
            return ConsumeStatus.RECONSUME_LATER;
        }
    }
}
```

**Producer 模式（双重检查锁单例）：**
```java
public class MafkaProducerFactory {
    private volatile static IProducerProcessor producer;

    public static IProducerProcessor getProducer() {
        if (producer == null) {
            synchronized (MafkaProducerFactory.class) {
                if (producer == null) {
                    Properties props = new Properties();
                    props.setProperty(ConsumerConstants.MafkaBGNamespace, "octo");
                    props.setProperty(ConsumerConstants.MafkaClientAppkey, GlobalAttribute.APPKEY);
                    producer = MafkaClient.buildProduceFactory(props, topic);
                }
            }
        }
        return producer;
    }
}

// 发送：
MafkaProducerFactory.getProducer().sendMessage(JsonUtils.toJson(event));
// 异步发送（worksheet 风格）：
producer.sendAsyncMessage(json, partitionKey, new FutureCallback() {
    @Override public void onSuccess(AsyncProducerResult r) { log.info("sent: {}", r); }
    @Override public void onFailure(Throwable t) { log.error("send failed: ", t); }
});
```

**❌ 禁止：**
- Consumer 抛出异常不处理（必须 catch 并返回 `CONSUME_FAILURE` 或 `RECONSUME_LATER`）
- Producer 每次调用都 `buildProduceFactory`（应单例复用）
- topic/group 硬编码（应通过 `@Value` 从配置注入）

---

### 7. Pigeon RPC 规范

**Consumer（调用远程服务）— 程序化方式，不用 `@Reference`：**
```java
// 工具方法封装（推荐）
public static <T> T createPigeonService(Class<T> serviceInterface, String url,
                                         String serialize, int timeout, int retries) {
    InvokerConfig<T> config = new InvokerConfig<>(serviceInterface);
    config.setUrl(url);
    config.setSerialize(serialize);   // "hessian" / "fst" / "protostuff"
    config.setTimeout(timeout);       // ms
    config.setRetries(retries);
    return ServiceFactory.getService(config);
}

// 调用前设置 appkey
InvokerHelper.setAppkey(GlobalAttribute.APPKEY);
T service = createPigeonService(T.class, url, "hessian", 1000, 3);
result = service.remoteMethod(param);
```

**Provider（暴露 Thrift 服务）：**
```java
@ThriftServerPublisher(port = 8411)   // pontos 风格
@Slf4j
public class XxxServiceImpl implements XxxService.Iface {
    @Override
    public XxxResponse query(XxxRequest request) throws TException { ... }
}

// 或 kugget 风格
@ThriftService
public class XxxSchemaService { ... }
```

**❌ 禁止：**
- 使用 Spring `@Reference` 注解（DataMatrix 不用 Dubbo 风格，用程序化 `ServiceFactory`）
- 忘记调用 `InvokerHelper.setAppkey()`（会导致调用方 appkey 不正确）

---

### 8. Blade JDBC 规范

**标准模式：`BladeDataSource` → `JdbcTemplate`**
```java
// 初始化（通常在 @PostConstruct 或工厂类中）
BladeDataSource bladeDataSource = new BladeDataSource();
bladeDataSource.setJdbcRef(bladeMirrorDbMeta.getJdbcref());  // Zebra jdbcRef 名称
bladeDataSource.setPoolType("hikaricp");
bladeDataSource.setExtraJdbcUrlParams(
    "socketTimeout=30000&sessionVariables=blade_txn_timeout=30000,blade_stmt_timeout=30000"
);
bladeDataSource.setMaxPoolSize(20);
bladeDataSource.setMinPoolSize(4);
bladeDataSource.setCheckoutTimeout(10000);
bladeDataSource.init();

JdbcTemplate bladeJdbcTemplate = new JdbcTemplate(bladeDataSource);

// 多实例管理（按 db 名缓存）
private ConcurrentHashMap<String, JdbcTemplate> bladeTemplates = new ConcurrentHashMap<>();
```

**普通 DB 访问（Zebra + MyBatis）：**
```yaml
# application.yml
zebra:
  jdbcRef: eagleplatform_eagle_data_test  # 环境隔离
  poolType: druid
  zebraMapperScannerConfigurer:
    basePackage: com.meituan.eagle.dataserver.mapper
```
```java
@Repository
public interface XxxMapper {
    List<XxxEntity> selectByCondition(@Param("param") QueryParam param);
    int insert(XxxEntity entity);
}
```

**❌ 禁止：**
- 直接 `new JdbcTemplate(dataSource)` 绕过 Zebra（普通 DB 必须走 Zebra）
- 每次查询都 `new BladeDataSource()`（应缓存 `JdbcTemplate` 实例）

---

### 9. 通用 DataMatrix 惯用法

**`GlobalAttribute` 常量类（每个服务必须有）：**
```java
public class GlobalAttribute {
    public static final String APPKEY = "com.sankuai.eagle.dataserver";  // 各服务不同
    public static final String URL_PREFIX = "/pontos/api/v1";
    public static final String URL_INTERNAL_PREFIX = "/pontos/internal/v1";
}
```

**CAT 监控打点（外部调用必须埋点）：**
```java
Transaction t = Cat.getProducer().newTransaction("Pigeon.Call", "ServiceName.methodName");
try {
    result = pigeonService.call(param);
    t.setStatus(Transaction.SUCCESS);
} catch (Exception e) {
    t.setStatus(e);
    throw e;
} finally {
    t.complete();
}
```

**用户身份获取：**
```java
String userMis = RequestParseUtil.getUserMis(request);  // 从 HttpServletRequest 提取 MIS
```

**日志规范（`@Slf4j`，不手动声明 Logger）：**
```java
@Slf4j  // Lombok，等价于 private static final Logger log = LoggerFactory.getLogger(Xxx.class)
public class XxxService {
    log.info("action={}, param={}", action, param);
    log.error("action={} failed, param={}", action, param, e);  // 异常作为最后一个参数
}
```

**Swagger 必填注解：**
```java
@Api(tags = "模块名")           // Controller 类
@ApiOperation(value = "接口说明")  // 每个方法
@ApiParam(value = "参数说明")   // 请求参数
```

---

## 审查输出格式

```
## Spring Boot 规范审查

### 发现的问题

**[CRITICAL] 异常处理**
- `XxxController.doAction()` 直接 throw 异常，应 try-catch 返回 ApiResult.fail

**[WARNING] Lion 配置**
- `LionKeyConst.SOME_KEY` 字符串硬编码在 XxxService.java:42，应移到常量类

**[INFO] 响应封装**
- hermes 风格 ApiResult 与 pontos 风格混用，建议统一

### 无问题项
- Controller URL 前缀规范 ✅
- @Transactional rollbackFor ✅
- Mafka Consumer 异常处理 ✅
```
