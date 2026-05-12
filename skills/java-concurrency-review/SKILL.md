---
name: java-concurrency-review
description: Java 并发代码深度审查。仅在 workflow_code_review 检测到并发相关代码时调用（synchronized、volatile、@Async、CompletableFuture、ExecutorService、Flink 算子状态）。不独立触发。技术栈：Spring Boot @Async、CompletableFuture、Flink Streaming、Pigeon 异步调用。
---

# Java 并发代码审查

本 skill 由 `workflow_code_review` 在检测到以下关键词时调用：
`synchronized`、`volatile`、`@Async`、`CompletableFuture`、`ExecutorService`、`AtomicXxx`、`Lock`、Flink 算子 `processElement`/`onTimer`。

---

## 触发检测命令

```bash
# 快速扫描是否有并发代码
grep -rn "synchronized\|volatile\|@Async\|CompletableFuture\|ExecutorService\|AtomicInteger\|AtomicLong\|ReentrantLock\|ConcurrentHashMap" --include="*.java" [目标目录]
```

---

## 1. Spring @Async 陷阱（DataMatrix/Spring Boot 场景）

```java
// ❌ 陷阱1：同类内调用绕过代理，@Async 静默失效
@Service
public class OrderService {
    public void processOrder(Order order) {
        sendConfirmation(order); // 直接调用，不走代理，同步执行！
    }

    @Async
    public void sendConfirmation(Order order) { ... }
}

// ✅ 注入独立 Bean
@Autowired private EmailService emailService; // 独立 Bean
emailService.sendConfirmation(order); // 走代理，真正异步

// ❌ 陷阱2：@Async 方法非 public，代理无法拦截
@Async
private void processInBackground() { } // 静默同步执行

// ✅ 必须 public
@Async
public void processInBackground() { }

// ❌ 陷阱3：未配置 @EnableAsync
// ✅ 配置类必须有 @EnableAsync

// ❌ 陷阱4：默认 SimpleAsyncTaskExecutor 每次创建新线程
// ✅ 配置线程池
@Bean
public Executor taskExecutor() {
    ThreadPoolTaskExecutor executor = new ThreadPoolTaskExecutor();
    executor.setCorePoolSize(10);
    executor.setMaxPoolSize(50);
    executor.setQueueCapacity(100);
    executor.setThreadNamePrefix("async-");
    executor.setRejectedExecutionHandler(new CallerRunsPolicy());
    executor.initialize();
    return executor;
}
```

**检查项：**
- [ ] `@Async` 方法是否 public
- [ ] 调用方是否从不同 Bean 调用（非同类 `this.method()`）
- [ ] 是否配置了 `@EnableAsync`
- [ ] 是否配置了自定义线程池（非默认 SimpleAsyncTaskExecutor）
- [ ] 如需传播 SecurityContext，是否用 `DelegatingSecurityContextAsyncTaskExecutor`

---

## 2. CompletableFuture

```java
// ❌ 异常被静默吞掉
CompletableFuture.supplyAsync(() -> riskyOperation());
// riskyOperation 抛异常时，没有任何日志或处理

// ✅ 必须处理异常
CompletableFuture.supplyAsync(() -> riskyOperation())
    .exceptionally(ex -> {
        log.error("操作失败", ex);
        return fallbackValue;
    });

// ✅ 或用 handle() 统一处理成功/失败
.handle((result, ex) -> {
    if (ex != null) { log.error("失败", ex); return fallback; }
    return result;
});

// ✅ 超时保护（Java 9+）
CompletableFuture.supplyAsync(() -> callPigeonService())
    .orTimeout(3, TimeUnit.SECONDS)       // 超时抛 TimeoutException
    .completeOnTimeout(defaultVal, 3, TimeUnit.SECONDS); // 超时返回默认值

// ❌ I/O 密集任务用 ForkJoinPool.commonPool（阻塞公共池）
CompletableFuture.supplyAsync(() -> pigeonCall()); // 默认用 commonPool

// ✅ I/O 任务用独立线程池
ExecutorService ioPool = Executors.newFixedThreadPool(20);
CompletableFuture.supplyAsync(() -> pigeonCall(), ioPool);
```

**检查项：**
- [ ] 所有 `CompletableFuture` 链是否有 `exceptionally`/`handle`/`whenComplete`
- [ ] Pigeon 异步调用是否有超时保护
- [ ] I/O 密集的 `supplyAsync` 是否用了独立线程池

---

## 3. 经典并发 Bug

### Check-Then-Act 竞态条件

```java
// ❌ 两步操作非原子
if (!map.containsKey(key)) {
    map.put(key, computeValue()); // 另一线程可能在此间隙插入
}

// ✅ 原子操作
map.computeIfAbsent(key, k -> computeValue());

// ❌ 计数器竞态
if (count < MAX) {
    count++; // 非原子
}

// ✅
AtomicInteger count = new AtomicInteger();
count.updateAndGet(c -> c < MAX ? c + 1 : c);
```

### volatile 可见性

```java
// ❌ 其他线程可能永远看不到 running=false
private boolean running = true;
public void stop() { running = false; }
public void run() { while (running) { } } // 可能死循环

// ✅
private volatile boolean running = true;
```

### Double-Checked Locking

```java
// ❌ 没有 volatile，可能看到部分构造的对象
private static Singleton instance;
if (instance == null) {
    synchronized (Singleton.class) {
        if (instance == null) instance = new Singleton();
    }
}

// ✅ volatile 保证可见性和有序性
private static volatile Singleton instance;

// ✅ 或 Holder 类（更简洁）
private static class Holder {
    static final Singleton INSTANCE = new Singleton();
}
```

### 死锁：锁顺序

```java
// ❌ Thread1: lock(A)->lock(B), Thread2: lock(B)->lock(A) → 死锁
public void transfer(Account from, Account to) {
    synchronized (from) { synchronized (to) { ... } }
}

// ✅ 固定锁顺序
Account first  = from.getId() < to.getId() ? from : to;
Account second = from.getId() < to.getId() ? to : from;
synchronized (first) { synchronized (second) { ... } }
```

---

## 4. 线程安全集合

| 场景 | 错误选择 | 正确选择 |
|------|---------|---------|
| 并发读写 | `HashMap` | `ConcurrentHashMap` |
| 频繁迭代 | `ConcurrentHashMap` | `CopyOnWriteArrayList` |
| 生产者-消费者 | `ArrayList` | `BlockingQueue` |
| 有序并发 | `TreeMap` | `ConcurrentSkipListMap` |

```java
// ❌ ConcurrentHashMap.compute() 内嵌套 compute → 死锁风险
map.compute(key1, (k, v) -> {
    return map.compute(key2, ...); // 死锁！
});
```

---

## 5. Flink 算子状态（DataMatrix 场景）

```java
// ❌ Flink 算子中使用实例变量存储状态（非托管状态，checkpoint 不保存）
public class MyFunction extends RichMapFunction<String, String> {
    private Map<String, Integer> counter = new HashMap<>(); // 危险！

    @Override
    public String map(String value) {
        counter.merge(value, 1, Integer::sum);
        return value;
    }
}

// ✅ 使用 Flink 托管状态
public class MyFunction extends RichMapFunction<String, String> {
    private transient ValueState<Integer> counter;

    @Override
    public void open(Configuration parameters) {
        ValueStateDescriptor<Integer> descriptor =
            new ValueStateDescriptor<>("counter", Integer.class);
        counter = getRuntimeContext().getState(descriptor);
    }
}

// ❌ processElement 中共享可变对象（Flink 多线程场景）
private static final StringBuilder sb = new StringBuilder(); // 静态共享！

// ✅ 每次创建或用 ThreadLocal
```

**检查项：**
- [ ] Flink 算子状态是否用托管状态（`ValueState`/`MapState`/`ListState`）
- [ ] 算子中是否有静态可变字段
- [ ] `onTimer` 是否有状态清理（防止状态膨胀）

---

## 审查 Checklist

### 🔴 高风险（直接 Bug）
- [ ] check-then-act 无原子保护
- [ ] double-checked locking 无 `volatile`
- [ ] `@Async` 同类调用（静默同步）
- [ ] `CompletableFuture` 无异常处理
- [ ] Flink 算子用实例变量存状态

### 🟡 中风险（潜在问题）
- [ ] 线程池未配置（用默认 SimpleAsyncTaskExecutor）
- [ ] Pigeon 异步调用无超时
- [ ] `ConcurrentHashMap.compute()` 内嵌套操作
- [ ] 共享 `volatile` 字段的复合操作

### 🟢 规范项
- [ ] 线程池有命名（`setThreadNamePrefix`，便于排查）
- [ ] `ExecutorService` 有 shutdown 处理
- [ ] 并发类有 `@ThreadSafe`/`@NotThreadSafe` 注释
