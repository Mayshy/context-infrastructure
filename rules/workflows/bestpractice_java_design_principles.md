# BestPractice: Java 设计原则

> **使用方式**：`read` 本文件，边理解边执行。适用于架构审查、重构决策、代码设计评审。
> 在 `workflow_code_review.md` Phase 2（简化识别）阶段按需参考。

---

## When to Use

- 审查一个模块/类的职责划分是否合理
- 评估是否需要引入接口/抽象
- 发现"上帝类"或"贫血模型"时
- 做重构决策前（确认重构方向是否正确）
- 新服务设计阶段（包结构、层次划分）

---

## SOLID 原则速查

### SRP — 单一职责原则

**核心问题**：这个类有几个"变化的理由"？

**违反信号：**
- 类超过 300 行
- 方法名包含 `And`（`validateAndSave`, `parseAndProcess`）
- 同时包含：数据库操作 + HTTP 调用 + 业务计算 + 日志格式化
- 一个修改（如换日志框架）会影响多处不相关逻辑

**DataMatrix 典型场景：**
```java
// ❌ 违反 SRP：Service 同时做业务逻辑 + 发 Mafka 消息 + 打 CAT 点
public class MirrorFlowServiceImpl {
    public void startFlow(MirrorConfig config) {
        // 业务逻辑
        validateConfig(config);
        // Mafka 发消息
        mafkaProducer.send(JsonUtils.toJson(config));
        // CAT 打点
        Cat.getProducer().logEvent("MirrorFlow", "start");
    }
}

// ✅ 拆分职责：Mafka 发送封装到 EventPublisher，CAT 打点用 AOP
@Service
public class MirrorFlowServiceImpl {
    @Autowired private EventPublisher eventPublisher;

    public void startFlow(MirrorConfig config) {
        validateConfig(config);
        eventPublisher.publishMirrorStarted(config);  // 发消息是独立职责
    }
}
```

**重构方向：** 提取 `XxxPublisher`（消息发送）、`XxxValidator`（参数校验）、`XxxConverter`（格式转换）

---

### OCP — 开闭原则

**核心问题**：添加新功能时，是修改已有代码还是扩展新代码？

**违反信号：**
- `if (type.equals("A")) { ... } else if (type.equals("B")) { ... }` 遍布多处
- 每次新增类型都要改核心处理逻辑
- `switch` 语句中的 case 持续增长

**DataMatrix 典型场景：**
```java
// ❌ 违反 OCP：新增数据源类型需要改 processDataSource
public void processDataSource(DataSource ds) {
    if ("mysql".equals(ds.getType())) { processMysql(ds); }
    else if ("hbase".equals(ds.getType())) { processHbase(ds); }
    else if ("s3".equals(ds.getType())) { processS3(ds); }
    // 每次新增类型都要改这里
}

// ✅ Strategy 模式：新增类型只需新增 Handler 实现
public interface DataSourceHandler {
    boolean supports(String type);
    void process(DataSource ds);
}

@Component
public class DataSourceHandlerRouter {
    @Autowired private List<DataSourceHandler> handlers;

    public void process(DataSource ds) {
        handlers.stream()
            .filter(h -> h.supports(ds.getType()))
            .findFirst()
            .orElseThrow(() -> new UnsupportedOperationException("Unsupported: " + ds.getType()))
            .process(ds);
    }
}
```

**重构方向：** Strategy 模式（处理器列表）、工厂模式（按类型创建对象）

---

### LSP — 里氏替换原则

**核心问题**：子类能否在任何使用父类的地方无缝替换？

**违反信号：**
- 子类方法抛出父类未声明的异常
- 子类重写方法后行为与父类契约不符
- `instanceof` 检查频繁出现（说明子类行为不一致）
- 子类覆盖方法但不调用 `super`，且改变了核心行为

**常见陷阱（组合优于继承）：**
```java
// ❌ Square 继承 Rectangle 违反 LSP：设置宽度会同时改高度，破坏 Rectangle 契约
class Square extends Rectangle {
    @Override
    public void setWidth(int w) { super.setWidth(w); super.setHeight(w); }
}

// ✅ 组合：Square 不继承 Rectangle，各自独立
class Square {
    private int side;
    public int getArea() { return side * side; }
}
```

**DataMatrix 场景**：`MirrorConfig` 子类不应覆盖父类的 `validate()` 方法并放宽校验条件。

---

### ISP — 接口隔离原则

**核心问题**：接口的调用方是否被迫依赖它不需要的方法？

**违反信号：**
- 接口超过 7-8 个方法
- 实现类中大量 `throw new UnsupportedOperationException()`
- 调用方只用接口的 1-2 个方法，却依赖了整个接口

**DataMatrix 典型场景：**
```java
// ❌ 胖接口：所有操作都塞进一个接口
public interface IMirrorService {
    void create(MirrorConfig config);
    void delete(String mirrorId);
    void startFlow(String mirrorId);
    void stopFlow(String mirrorId);
    MirrorStatus getStatus(String mirrorId);
    List<MirrorConfig> listAll();
    void updatePackage(String mirrorId, String packageName);
    void batchUpdatePackage(List<String> mirrorIds, String packageName);
}

// ✅ 按角色拆分接口
public interface IMirrorConfigService {      // CRUD
    void create(MirrorConfig config);
    void delete(String mirrorId);
    List<MirrorConfig> listAll();
}
public interface IMirrorFlowService {        // 流程控制
    void startFlow(String mirrorId);
    void stopFlow(String mirrorId);
    MirrorStatus getStatus(String mirrorId);
}
public interface IMirrorPackageService {     // 包版本管理
    void updatePackage(String mirrorId, String packageName);
    void batchUpdatePackage(List<String> mirrorIds, String packageName);
}
```

---

### DIP — 依赖倒置原则

**核心问题**：高层模块是否依赖了具体实现（而非抽象）？

**违反信号：**
- `new ConcreteClass()` 出现在业务逻辑中（而非工厂/配置类）
- Service 直接 `new` 一个 DAO 或 HTTP Client
- 测试困难（因为依赖了具体类，无法 Mock）

```java
// ❌ 违反 DIP：Service 直接 new 具体实现
public class MirrorFlowServiceImpl {
    private MirrorConfigMapper mapper = new MirrorConfigMapper();  // 直接 new
    private PigeonReader pigeonReader = new PigeonReader("url");   // 直接 new
}

// ✅ 依赖抽象，通过 @Autowired 注入
public class MirrorFlowServiceImpl {
    @Autowired private MirrorConfigMapper mapper;          // 依赖接口/抽象
    @Autowired private IDataAccessService dataService;    // 依赖接口
}
```

**DataMatrix 注意**：`@Configuration` 中的 `@Bean` 方法是合法的 `new`（这是 DI 容器的职责）。

---

## 架构审查清单

### 包结构审查

**DataMatrix 服务标准包结构（以 pontos 为例）：**
```
com.meituan.eagle.dataserver
├── configuration/    # @Configuration 类，@Bean 定义
├── controller/       # @RestController，HTTP 入口
├── service/
│   ├── I*Service.java        # 接口
│   └── impl/*ServiceImpl.java # 实现
├── dal/              # DAO 层（Mapper 接口）
├── model/            # DTO/VO/Request/Response（不含业务逻辑）
├── entity/           # DB 实体（对应表结构）
├── consumer/         # Mafka Consumer
├── thrift/           # Pigeon/Thrift 服务提供者
├── aop/              # AOP 切面
├── constant/         # 常量（GlobalAttribute, LionKeyConst, ErrorCode）
├── enums/            # 枚举
├── exception/        # 自定义异常 + GlobalExceptionHandler
└── utils/            # 工具类（无状态静态方法）
```

**审查问题：**
- [ ] Controller 是否包含业务逻辑？（应在 Service）
- [ ] Service 是否直接操作 DB？（应通过 Mapper/DAO）
- [ ] model/ 中的类是否包含 `@Service`/`@Repository`？（模型类不应有 Spring 注解）
- [ ] utils/ 是否变成了"万能垃圾桶"？（超过 500 行应考虑拆分）

### 依赖方向审查

**合法依赖方向：**
```
Controller → Service → Mapper/DAO → DB
Controller → Service → Pigeon Client → 外部服务
Consumer → Service → Mapper/DAO
```

**违规信号：**
- Mapper/DAO 中出现 `@Autowired Service`（数据层依赖业务层）
- model/entity 中出现 `@Autowired`（数据模型依赖 Spring）
- 跨服务直接调用（pontos Controller 直接 `@Autowired` hermes 的 Service）

### 层边界审查

| 层 | 允许 | 禁止 |
|----|------|------|
| Controller | 参数校验、调用 Service、返回 ApiResult | 业务逻辑、直接操作 DB |
| Service | 业务逻辑、事务控制、调用 Mapper/Pigeon/Mafka | 直接操作 HTTP 请求/响应 |
| Mapper/DAO | SQL 查询、结果映射 | 业务逻辑、调用其他 Service |
| model/entity | 数据结构定义 | 方法中包含业务计算 |

### 常见反模式

**反模式 1：贫血模型（Anemic Domain Model）**
```java
// ❌ Entity 只有 getter/setter，所有逻辑散落在 Service 中
public class MirrorConfig {
    private String status;
    // 只有 getter/setter
}

// ✅ Entity 包含与自身状态相关的行为
public class MirrorConfig {
    private String status;
    public boolean isOnline() { return "ONLINE".equals(status); }
    public boolean canStartFlow() { return isOnline() && flowStatus == null; }
}
```

**反模式 2：工具类垃圾桶（Util Dumping Ground）**
```java
// ❌ 一个 Utils 类包含所有不知道放哪里的方法
public class DataServerUtils {
    public static String formatDate() { ... }
    public static boolean validateMirrorConfig() { ... }
    public static List<String> parseLionConfig() { ... }
    public static ApiResult wrapResult() { ... }
}

// ✅ 按职责拆分
public class DateFormatUtils { ... }
public class MirrorConfigValidator { ... }
public class LionConfigParser { ... }
```

**反模式 3：框架耦合渗透到 domain**
```java
// ❌ domain/model 类中出现框架注解
public class MirrorConfig {
    @JsonProperty("mirror_id")   // Jackson 注解渗入 domain
    @Column(name = "mirror_id")  // JPA 注解渗入 domain
    private String mirrorId;
}

// ✅ 用独立的 DTO/Entity 隔离框架依赖
public class MirrorConfigDTO {      // HTTP 层：含 Jackson 注解
    @JsonProperty("mirror_id")
    private String mirrorId;
}
public class MirrorConfigEntity {   // DB 层：含 MyBatis 注解
    private String mirrorId;
}
public class MirrorConfig {         // Domain：纯 POJO，无框架注解
    private String mirrorId;
}
```

---

## 重构决策树

```
发现问题代码
    ├─ 类超过 300 行？
    │       → 检查 SRP：有几个"变化的理由"？→ 按职责拆分
    ├─ if/else type 判断超过 3 个分支？
    │       → 检查 OCP：是否可以用 Strategy/工厂替换？
    ├─ 接口超过 8 个方法？
    │       → 检查 ISP：调用方真的都需要这些方法吗？→ 按角色拆分
    ├─ 业务逻辑中出现 new ConcreteClass()？
    │       → 检查 DIP：应通过 @Autowired 注入抽象
    ├─ instanceof 检查超过 2 处？
    │       → 检查 LSP：子类是否破坏了父类契约？→ 考虑组合
    └─ 以上都不是？
            → 可能是命名问题或代码格式问题（参考 java-code-review skill）
```

---

## 与其他 Skill/Workflow 的关系

| 问题类型 | 参考资源 |
|---------|---------|
| 并发安全 | `java-concurrency-review` skill |
| 性能问题 | `java-performance-smells` skill |
| 代码风格/命名 | `java-code-review` skill |
| Spring 规范 | `spring-boot-patterns` skill |
| 整体代码质量 | `workflow_code_review.md` |
