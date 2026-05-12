# 代码审查工作流

## 元数据

- **类型**: Workflow
- **适用场景**: 合并前审查代码质量、重构后验证、agent 生成代码评估
- **相关 Skills**: `code-review-and-quality`、`code-simplification`、`performance-optimization`、`java-code-review`、`java-concurrency-review`、`java-performance-smells`、`spring-boot-patterns`
- **相关 BestPractice**: `bestpractice_java_design_principles.md`（架构/SOLID 审查时 read）
- **创建日期**: 2026-05-10
- **最后更新**: 2026-05-10

## When to Use

**触发场景（任意一条即可）：**
- 合并 PR 或 change 之前
- 完成一个功能实现后
- 需要评估另一个 agent 或模型生成的代码
- 重构已有代码后
- bug fix 后（同时审查修复和回归测试）

**排除场景（不使用此 workflow）：**
- 大型 PR（>1000 行）跨多个模块 → 用 `coding-agent` skill spawn Codex/Claude Code 在独立进程中完成
- 只需快速浏览某个文件是否有明显问题 → 直接 `read` 文件看即可，无需走完整流程

## 与 `coding-agent` skill 的边界

| 场景 | 使用方式 |
|------|---------|
| 当前 session 内，代码量 ≤ 300 行，单一逻辑变更 | 本 workflow（in-session） |
| 大型 PR、跨多文件重构、需要文件系统探索 | `coding-agent` skill（spawn 外部进程） |

---

## Step 0：语言检测（决定是否启用 Java 专项）

在开始审查前，先判断代码语言：

```bash
# 检查是否有 Java 文件
find [目标路径] -name "*.java" | head -5

# 检查是否有并发相关代码（决定是否需要 java-concurrency-review）
grep -rln "synchronized\|volatile\|@Async\|CompletableFuture\|ExecutorService\|AtomicInteger\|AtomicLong\|ReentrantLock" --include="*.java" [目标路径]

# 检查是否有 Spring Boot 代码（决定是否需要 spring-boot-patterns）
grep -rln "@RestController\|@Service\|@Configuration\|ApiResult\|MafkaClient\|InvokerConfig\|BladeDataSource\|@ConfigValue\|LionKeyConst" --include="*.java" [目标路径]
```

**判断结果：**
- 有 `.java` 文件 → Phase 1 结束后执行 **Java 专项检查**
- 有并发关键词 → Phase 1 结束后额外执行 **并发深度审查**
- 有 Spring/DataMatrix 关键词 → 执行 **Spring Boot 专项审查**
- 无 `.java` 文件 → 跳过所有 Java 专项，直接走通用三阶段

---

## Phase 1：质量五轴审查（`code-review-and-quality` skill）

加载方式：`skill({ name: "code-review-and-quality" })`

五轴覆盖：**正确性 → 可读性 → 架构 → 安全性 → 性能**

执行步骤：
1. 理解变更目标：这个 change 想做什么？实现了什么？
2. 先审查测试：测试是否存在？是否覆盖了边界情况？
3. 走查实现：逐轴检查（参见 skill 中的五轴清单）
4. 对发现的问题分级标注：`Critical:` / `Nit:` / `Optional:` / `FYI`
5. 填写 Review Checklist（skill 中有模板）

**输出**：带分级标注的 Review 报告

### Phase 1.5（仅 Java）：Java 专项 Checklist

> **触发条件**：Step 0 检测到 `.java` 文件时执行。

加载方式：`skill({ name: "java-code-review" })`

在 Phase 1 的五轴报告基础上，补充 Java 特有检查：

| 检查类别 | 核心关注点 |
|---------|-----------|
| Null Safety | 链式调用保护、Optional 正确使用、公共 API 不返回 null |
| 异常处理 | 无空 catch、异常链完整、SLF4J 参数化日志 |
| Collections | 迭代时修改、toList() 可变性假设、Set vs List 查找 |
| 并发（快扫） | check-then-act、@Async 同类调用 |
| 资源管理 | try-with-resources、Blade 连接关闭 |
| API 设计 | boolean 参数、null 返回值、入参校验 |
| Java 惯用法 | equals/hashCode 成对、magic number、命名规范 |

> 如果快扫发现并发代码，标记"需要并发深度审查"，在 Phase 1.5 结束后立即执行：

### Phase 1.55（仅 Spring/DataMatrix 代码）：Spring Boot 专项

> **触发条件**：Step 0 检测到 Spring/DataMatrix 关键词（`@RestController`、`ApiResult`、`MafkaClient`、`LionKeyConst` 等）。

加载方式：`skill({ name: "spring-boot-patterns" })`

重点检查：

| 检查类别 | 核心关注点 |
|---------|-----------|
| 响应封装 | 统一使用 `ApiResult<T>`，不直接 throw 异常 |
| Controller | URL 前缀规范、`@Api`/`@ApiOperation` 必填、无业务逻辑 |
| Service | `I*Service` 接口、`@Transactional(rollbackFor=Exception.class)` |
| 异常处理 | `@RestControllerAdvice` 覆盖、自定义异常保留异常链 |
| Lion 配置 | Key 常量化（`LionKeyConst`）、注入方式与服务框架匹配 |
| Mafka | Consumer 异常处理、Producer 单例复用 |
| Pigeon | 程序化 `ServiceFactory.getService()`，非 `@Reference` |
| Blade JDBC | `JdbcTemplate` 实例缓存，不每次 new |

### Phase 1.6（仅 Java 并发代码）：并发深度审查

> **触发条件**：Step 0 检测到并发关键词，**或** Phase 1.5 快扫发现并发代码。

加载方式：`skill({ name: "java-concurrency-review" })`

重点检查：
- Spring `@Async` 五大陷阱（同类调用、非 public、未配置线程池等）
- `CompletableFuture` 异常处理和超时保护
- check-then-act 竞态条件
- Flink 算子托管状态 vs 实例变量
- 死锁风险（锁顺序）

---

## Phase 2：简化识别（`code-simplification` skill）

加载方式：`skill({ name: "code-simplification" })`

仅在 Phase 1 发现可读性问题时执行，或代码明显比必要复杂时。

执行步骤：
1. 先理解代码（Chesterton's Fence）：搞清楚为什么这么写，再考虑是否需要改
2. 识别简化机会：深嵌套、超长函数、重复逻辑、无意义命名
3. 逐个简化，每次改完跑测试
4. 验证简化后是否真的更易读（否则回退）

**约束**：
- 行为必须完全不变
- 不混入功能改动
- 单次简化 > 500 行 → 考虑 codemod 而非手动

**Java 简化额外关注（来自 clean-code 原则）：**
- Guard clause 替代深嵌套（3+ 层 if）
- 超过 30 行的方法是否违反单一职责
- magic number 是否提取为命名常量
- 重复逻辑（3+ 处）是否提取为方法

---

## Phase 3：性能检测（`performance-optimization` skill）

加载方式：`skill({ name: "performance-optimization" })`

仅在以下情况执行：
- Phase 1 的性能轴发现疑点
- 代码涉及数据库查询、列表接口、前端渲染

执行步骤：
1. **先测量，再优化**（没有数据不动手）
2. 识别瓶颈：N+1 查询、无界数据拉取、主线程阻塞、缺失缓存
3. 修复具体瓶颈，不做预防性优化
4. 验证：对比修复前后的测量数据

### Phase 3.5（仅 Java）：Java 性能嗅探

> **触发条件**：Phase 3 执行且代码是 Java。

加载方式：`skill({ name: "java-performance-smells" })`

补充通用 `performance-optimization` 未覆盖的 Java 特有模式：

| 嗅探类别 | 快速判断 |
|---------|---------|
| 字符串操作 | 循环内 `+=`？→ `StringBuilder` |
| Regex | 循环内 `.matches()`？→ 静态 `Pattern` 常量 |
| Stream | 紧密循环内重复创建 Stream？→ 预计算 |
| Boxing | 循环内 `Long`/`Integer` 变量？→ 基本类型 |
| 集合查找 | `List.contains()` 在循环内？→ `Set` |
| Spark/Flink | `mapPartitions` 内每行 new 重对象？→ partition 级复用 |
| Blade JDBC | 无界查询？→ 分页；`rewriteBatchedStatements` 对 upsert 无效 |

---

## 完整流程图

```
开始审查
    │
    ├─ Step 0：语言检测
    │       ├─ 有 .java？→ 标记"Java 专项"
    │       └─ 有并发关键词？→ 标记"并发深度"
    │
    ├─ Phase 1：质量五轴（code-review-and-quality）
    │       └─ [Java] Phase 1.5：Java checklist（java-code-review）
    │               ├─ [Spring] Phase 1.55：Spring Boot 专项（spring-boot-patterns）
    │               └─ [并发] Phase 1.6：并发深度（java-concurrency-review）
    │
    ├─ Phase 2：简化识别（code-simplification）[条件执行]
    │       ├─ [Java] 额外：guard clause / magic number / 单一职责
    │       └─ [架构问题] read bestpractice_java_design_principles.md
    │
    └─ Phase 3：性能检测（performance-optimization）[条件执行]
            └─ [Java] Phase 3.5：Java 性能嗅探（java-performance-smells）
```

---

## 最终验证清单

```markdown
## Code Review 完成确认

- [ ] 所有 Critical 问题已解决
- [ ] 所有 Important 问题已解决或明确推迟（附理由）
- [ ] 测试通过
- [ ] Build 成功
- [ ] 简化后行为未变（如有简化）
- [ ] 性能改动有前后对比数据（如有性能改动）
--- Java 专项（如适用）---
- [ ] Null Safety 检查通过
- [ ] 异常链完整，无空 catch
- [ ] 并发代码经过深度审查（如有）
- [ ] 资源管理：try-with-resources 到位
--- Spring Boot 专项（如适用）---
- [ ] ApiResult<T> 统一，无裸 throw
- [ ] Lion Key 已在 LionKeyConst 常量化
- [ ] Mafka Consumer 异常处理到位
- [ ] @Transactional(rollbackFor=Exception.class) 写操作全覆盖
```

## 常见合理化陷阱（提醒自己不要犯）

| 合理化 | 现实 |
|--------|------|
| "能跑就行" | 能跑但难读、不安全、架构差的代码会产生复利债务 |
| "AI 生成的应该没问题" | AI 代码需要更多审查，不是更少——它自信且合理，即使是错的 |
| "测试过了就没问题" | 测试发现不了架构问题、安全漏洞、可读性问题 |
| "以后再清理" | 以后永远不来。Review 是质量关卡，用好它 |
| "Java 代码不需要专项检查" | NPE、空 catch、@Async 同类调用——这些 bug 在 review 时发现比在生产发现便宜 100 倍 |
