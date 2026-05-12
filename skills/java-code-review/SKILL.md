---
name: java-code-review
description: Java 专项代码审查 checklist，覆盖 Null Safety、异常处理、Collections/Streams、并发、资源管理、API 设计、Java 惯用法。仅在审查 Java 代码时由 workflow_code_review 调用，不独立触发。技术栈：Java 8+、Spring Boot、Flink、Pigeon、Blade JDBC。
---

# Java Code Review — 专项 Checklist

本 skill 由 `workflow_code_review` 在检测到 Java 代码时调用，作为通用五轴审查（`code-review-and-quality`）的语言层深化。**不独立使用。**

## 使用方式

在 workflow_code_review 的 Phase 1 完成后，针对 Java 文件执行本 checklist，补充 Java 特有的检查项。

---

## 1. Null Safety

```java
// ❌ NPE 风险：链式调用无保护
String name = user.getProfile().getName().toUpperCase();

// ✅ Optional 保护
String name = Optional.ofNullable(user.getProfile())
    .map(Profile::getName)
    .map(String::toUpperCase)
    .orElse("");

// ✅ 早返回
if (user.getProfile() == null) return "";
```

**检查项：**
- [ ] 链式方法调用是否有 null 保护
- [ ] `Optional.get()` 前是否有 `isPresent()` 检查
- [ ] 公共 API 是否返回 null（应返回 `Optional` 或空集合）
- [ ] 构造器/方法参数是否用 `Objects.requireNonNull()` 校验

---

## 2. 异常处理

```java
// ❌ 吞异常
try { process(); } catch (Exception e) { }

// ❌ 丢失 stack trace
catch (IOException e) {
    throw new RuntimeException(e.getMessage()); // 只传 message，丢失原因链
}

// ✅ 正确处理
catch (IOException e) {
    log.error("处理文件失败: {}", filename, e); // SLF4J 参数化 + 传 e
    throw new ProcessingException("文件处理失败", e); // 保留原因链
}
```

**检查项：**
- [ ] 无空 catch 块
- [ ] catch `Exception`/`Throwable` 是否有充分理由
- [ ] 异常链是否完整（`new XxxException(msg, cause)`）
- [ ] 日志是否用 SLF4J 参数化（`log.error("msg: {}", val, e)`），不用 `String.format`

---

## 3. Collections & Streams

```java
// ❌ 迭代时修改集合
for (Item item : items) {
    if (item.isExpired()) items.remove(item); // ConcurrentModificationException
}
// ✅
items.removeIf(Item::isExpired);

// ❌ 假设 toList() 可变
List<String> names = users.stream().map(User::getName).collect(Collectors.toList());
names.add("extra"); // Java 16+ toList() 返回不可变列表！

// ✅ 需要可变时显式指定
.collect(Collectors.toCollection(ArrayList::new));
```

**检查项：**
- [ ] 无迭代时修改集合（用 `removeIf`/`Iterator`）
- [ ] `Collectors.toList()` vs `List.copyOf()` vs `toUnmodifiableList()` 语义是否匹配
- [ ] Stream 是否在紧密循环内重复创建（应预计算）
- [ ] 大集合 `contains()` 是否用了 `Set` 而非 `List`（O(1) vs O(n)）

---

## 4. 并发（简要）

> 检测到并发代码时，触发 `java-concurrency-review` skill 做深度检查。

**快速扫描项：**
- [ ] 共享可变状态是否有同步保护（`ConcurrentHashMap`、`AtomicXxx`、`synchronized`）
- [ ] check-then-act 模式是否原子（用 `computeIfAbsent` 替代 `containsKey + put`）
- [ ] `@Async` 方法是否 public、是否从不同 Bean 调用（同类调用绕过代理）
- [ ] `CompletableFuture` 是否处理了异常（`exceptionally`/`handle`）

---

## 5. 资源管理

```java
// ❌ 资源泄漏
FileInputStream fis = new FileInputStream(file);
process(fis); // 抛异常则 fis 不关闭

// ✅ try-with-resources
try (FileInputStream fis = new FileInputStream(file)) {
    process(fis);
}

// ❌ 多资源嵌套（内层构造失败，外层不关闭）
try (BufferedWriter w = new BufferedWriter(new FileWriter(file))) { }

// ✅ 分开声明
try (FileWriter fw = new FileWriter(file);
     BufferedWriter w = new BufferedWriter(fw)) { }
```

**检查项：**
- [ ] 所有 `Closeable`/`AutoCloseable` 是否用 try-with-resources
- [ ] Blade JDBC `Connection`/`PreparedStatement` 是否正确关闭
- [ ] Pigeon 客户端资源是否复用（不在每次请求时重建）

---

## 6. API 设计

```java
// ❌ boolean 参数语义不明
process(data, true, false); // true/false 是什么？

// ✅ 枚举或命名参数
process(data, ProcessMode.ASYNC, ErrorHandling.STRICT);

// ❌ 返回 null 表示"未找到"
public User findById(Long id) { return users.get(id); }

// ✅ Optional
public Optional<User> findById(Long id) {
    return Optional.ofNullable(users.get(id));
}
```

**检查项：**
- [ ] boolean 参数是否应改为枚举
- [ ] 方法参数 > 3 个时是否考虑 Parameter Object / Builder
- [ ] 公共 API 入参是否有 null/边界校验

---

## 7. Java 惯用法

**equals/hashCode：**
- [ ] 重写 `equals` 必须同时重写 `hashCode`
- [ ] `hashCode` 不包含可变字段（会破坏 HashMap）
- [ ] 使用 `Objects.equals()` 而非 `==` 比较对象

**toString：**
- [ ] 领域对象有 `toString()`（便于日志调试）
- [ ] `toString()` 不包含密码、token 等敏感字段

**命名（Clean Code 核心）：**
- [ ] 无 `data`、`result`、`temp`、`flag` 等无意义变量名
- [ ] boolean 变量用 `is`/`has`/`can`/`should` 前缀
- [ ] 方法名是动词+名词（`processPayment`、`findByEmail`）
- [ ] 常量用 `UPPER_SNAKE_CASE`，无 magic number（应提取为命名常量）

**函数设计（Clean Code 核心）：**
- [ ] 方法 > 30 行时检查是否违反单一职责
- [ ] 深嵌套（3+ 层）是否可用 guard clause 改写
- [ ] 重复逻辑（3+ 处）是否已提取

---

## 输出格式

补充在 `code-review-and-quality` 的 Review 报告之后：

```markdown
### Java 专项检查

#### Null Safety
- [ 问题描述 + 行号 + 建议 ]

#### 异常处理
- ...

#### Java 惯用法
- ...
```

---

## Quick Reference

| 类别 | 最高频问题 |
|------|-----------|
| Null Safety | 链式调用、`Optional.get()` 无检查 |
| 异常处理 | 空 catch、丢失原因链、`String.format` 日志 |
| Collections | 迭代时修改、`toList()` 可变性假设 |
| 并发 | check-then-act、`@Async` 同类调用 |
| 资源管理 | try-with-resources 缺失、Blade 连接泄漏 |
| API 设计 | boolean 参数、null 返回值 |
| 惯用法 | equals/hashCode 不成对、magic number |
