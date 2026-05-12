# 代码质量三场景最佳实践（OpenCode + OMO 环境）

**整理日期**: 2026-05-10  
**适用环境**: OpenCode + Oh-My-OpenCode (OMO/OpenClaw)，非 Claude Code  
**技术栈**: Java 11 + Spring Boot + Blade + Maven（DataMatrix/Pontos/Athena 等）  
**参考项目**: `~/Desktop/Project/pontos/`、`~/Desktop/Project/athena/`

---

## 背景：OMO 的三层能力

| 层级 | 做什么 | 何时用 |
|------|--------|--------|
| **Sisyphus 直接分析** | 读文件 + 推理 + 报告 | 单文件/小范围快速扫描 |
| **`task()` 并行 subagent** | 多文件/多模块并行深度分析 | 大范围扫描、重构规划 |
| **Bash CLI 工具** | 确定性规则扫描（Semgrep/ast-grep/Checkstyle） | 需要可重复、CI 集成的场景 |

> **关键认知**：`pr-review-toolkit`（code-simplifier、silent-failure-hunter、type-design-analyzer）是 Claude Code 原生 subagent，在 OMO 中**完全不可见、不触发**。OMO 里要实现等效能力，需通过 `task()` 工具手动委派。

---

## 场景 A：缺陷扫描（Bug/Security/Reliability）

### 目标
发现：空指针、异常吞噬、线程安全问题、资源泄漏、SQL 注入、不当错误处理。

### 零安装路径（当前可用）

**方式 1：Sisyphus 直接扫描单个 Handler**

```
直接告诉 Sisyphus：
"扫描 pontos-server handler 包下的所有 Handler 类，
 重点找：线程池异常吞噬、静默 catch、资源未关闭、TODO 标注的可靠性问题"
```

Sisyphus 会读取文件 + 用 LLM 推理，输出带行号的问题列表。

**方式 2：task() 并行多模块深度扫描（推荐，大范围）**

```
并行委派 3 个 subagent：

task(category="deep", load_skills=[], run_in_background=true,
  prompt="""
  TASK: 扫描 pontos-server handler 包的所有 Java 文件，寻找 silent failure 模式
  EXPECTED OUTCOME: 每个问题含文件路径、行号、问题描述、严重级别（P0/P1/P2）、修复建议
  REQUIRED TOOLS: Read, Glob, Grep
  MUST DO:
    - 检查 executorService.submit() 内部的异常是否被正确处理
    - 检查 catch 块是否只有 logger.info 而非 logger.warn/error
    - 检查 ThreadPoolExecutor 的 RejectedExecutionHandler 配置
    - 检查 CompletableFuture 链中的异常处理
  MUST NOT DO: 不修改任何文件，只报告
  CONTEXT: ~/Desktop/Project/pontos/pontos-server/src/main/java/com/meituan/eagle/dataserver/handler/
  """)
```

**已发现的真实缺陷（pontos-server）**：

| 文件 | 行号 | 问题 | 严重级别 |
|------|------|------|---------|
| `MirrorFlowFullSyncResultCheckHandler.java` | 93 | `executorService.submit()` 内部异常被线程池吞掉，`setBladeMirrorTableAutoIncrementOverMaxId` 抛异常时后续代码不执行 | **P0** |
| `MirrorFlowFullSyncResultCheckHandler.java` | 58 | `ThreadPoolExecutor` 使用 `AbortPolicy`，队列满时抛 `RejectedExecutionException` 未被 catch | **P1** |
| `PropertyUtils.java` | 101-104 | `NumberFormatException` catch 后用 `logger.info`（应为 `logger.warn`），静默返回 defaultValue | **P2** |
| `MirrorFlowCrane.java` | TODO 注释处 | 已知异步可靠性问题，TODO 标注但未修复 | **P1** |

### 增强路径（安装 Semgrep 后）

```bash
# 安装
brew install semgrep

# 扫描 Java 项目（使用官方规则集）
semgrep --config=p/java ~/Desktop/Project/pontos/pontos-server/src/

# 专项：Java 安全漏洞
semgrep --config=p/owasp-top-ten ~/Desktop/Project/pontos/

# 专项：线程安全
semgrep --config=p/java-thread-safety ~/Desktop/Project/pontos/
```

**自定义规则示例（检测 executorService.submit 内异常吞噬）**：

```yaml
# ~/.semgrep/rules/executor-silent-failure.yaml
rules:
  - id: executor-submit-swallows-exception
    patterns:
      - pattern: |
          $EXEC.submit(() -> {
            ...
            $METHOD(...);
            ...
          });
      - pattern-not: |
          $EXEC.submit(() -> {
            ...
            try { ... } catch ($E) { ... throw ...; }
            ...
          });
    message: "executorService.submit() 内部异常可能被线程池吞噬，考虑用 Future.get() 或显式 try-catch"
    languages: [java]
    severity: WARNING
```

### 最佳触发时机
- PR 提交前：`semgrep --config=p/java --diff-only`
- 每次修改 Handler/Service 类后：直接问 Sisyphus "扫描这个文件有没有 silent failure"

---

## 场景 B：重构（Refactoring）

### 目标
消除重复代码、简化复杂逻辑、改善方法结构、现代化 Java 写法（Java 8+ Stream/Optional）。

### 零安装路径（Maven + OpenRewrite，当前可用）

**OpenRewrite 是最推荐的零安装重构工具**，因为项目已有 Maven：

```bash
# 迁移到 Java 11 现代写法（不改业务逻辑）
cd ~/Desktop/Project/pontos
mvn -U org.openrewrite.maven:rewrite-maven-plugin:run \
  -Drewrite.recipeArtifactCoordinates=org.openrewrite.recipe:rewrite-migrate-java:LATEST \
  -Drewrite.activeRecipes=org.openrewrite.java.migrate.Java8toJava11

# 常用 Recipe 清单：
# org.openrewrite.java.cleanup.CommonStaticAnalysis     — 常见静态分析修复
# org.openrewrite.java.cleanup.UnnecessaryThrows        — 清理无用 throws 声明
# org.openrewrite.java.cleanup.FinalizeLocalVariables   — 变量 final 化
# org.openrewrite.java.spring.boot2.SpringBoot1To2Migration — Spring Boot 升级
```

**方式 2：task() 委派重构分析**

```
"分析 MirrorFlowFullSyncResultCheckHandler.java，
 给出重构建议：
 1. 线程池错误处理模式改进
 2. 方法拆分建议（超过 30 行的方法）
 3. 是否有可用 Stream/Optional 替代的命令式循环
 不要直接修改，先给出 before/after 对比"
```

**方式 3：Sisyphus 直接重构小范围代码**

```
"重构 PropertyUtils.java 第 95-110 行：
 1. catch NumberFormatException 改用 logger.warn
 2. 用 Optional 包装返回值
 保持方法签名不变"
```

### 增强路径（安装 ast-grep 后）

```bash
# 安装
npm i -g @ast-grep/cli

# 查找所有 logger.info 在 catch 块中的用法（应改为 warn/error）
ast-grep --pattern 'catch ($E) { $$$; log.info($$$); $$$; }' \
  --lang java ~/Desktop/Project/pontos/

# 查找所有空 catch 块
ast-grep --pattern 'catch ($E) {}' --lang java ~/Desktop/Project/pontos/

# 查找可用 Optional 替代的 null 检查
ast-grep --pattern 'if ($X != null) { $$$; }' --lang java ~/Desktop/Project/pontos/
```

**自定义重构规则（ast-grep YAML）**：

```yaml
# rewrite catch-info-to-warn.yaml
id: catch-logger-info-to-warn
language: java
rule:
  pattern: catch ($E) { $$$; $LOG.info($MSG, $E); $$$; }
fix: catch ($E) { $$$; $LOG.warn($MSG, $E); $$$; }
```

### 重构工作流（推荐顺序）

1. **先扫描**：用场景 A 工具找出问题清单
2. **优先级排序**：P0（影响正确性）→ P1（影响可靠性）→ P2（代码质量）
3. **小批次重构**：每次只改一个类，运行测试验证
4. **OpenRewrite 做机械重构**：格式化、import 整理、API 迁移交给工具
5. **LLM 做逻辑重构**：业务逻辑简化、设计模式应用交给 Sisyphus

---

## 场景 C：规范 + 可读性优化

### 目标
统一代码风格、改善命名、添加必要注释、确保 Javadoc 完整、消除魔法数字。

### 零安装路径（Maven Checkstyle，当前可用）

**在 `pom.xml` 中添加 Checkstyle 插件**（推荐加在 `pontos-server/pom.xml`）：

```xml
<build>
  <plugins>
    <plugin>
      <groupId>org.apache.maven.plugins</groupId>
      <artifactId>maven-checkstyle-plugin</artifactId>
      <version>3.3.1</version>
      <configuration>
        <!-- 使用 Google Java Style（或自定义） -->
        <configLocation>google_checks.xml</configLocation>
        <failsOnError>true</failsOnError>
        <consoleOutput>true</consoleOutput>
        <!-- 只检查 src/main/java，跳过测试 -->
        <sourceDirectories>${project.build.sourceDirectory}</sourceDirectories>
      </configuration>
      <executions>
        <execution>
          <id>validate</id>
          <phase>validate</phase>
          <goals><goal>check</goal></goals>
        </execution>
      </executions>
    </plugin>
  </plugins>
</build>
```

```bash
# 运行检查
mvn checkstyle:check -pl pontos-server

# 生成报告（HTML）
mvn checkstyle:checkstyle -pl pontos-server
```

**方式 2：task() 委派可读性审查**

```
"审查 MirrorFlowCreateHandler.java 的可读性：
 1. 方法名是否准确描述意图
 2. 魔法数字是否应提取为常量
 3. 注释是否与代码同步（过时注释）
 4. 变量名是否清晰（单字母变量、缩写）
 5. 是否有超过 50 行的方法需要拆分
 输出：每条建议 + 行号 + 改进示例"
```

**方式 3：Sisyphus 直接改善命名**

```
"重命名 MirrorFlowFullSyncResultCheckHandler.java 中的以下变量，
 使其更清晰地表达业务含义：
 - checkResult → syncValidationResult
 - cnt → pendingRecordCount
 保持方法签名不变，只改局部变量名"
```

### 增强路径（PMD + SpotBugs）

```bash
# PMD：代码规范扫描（Maven 插件，零安装）
mvn pmd:check -pl pontos-server

# SpotBugs：字节码级缺陷扫描（需先 compile）
mvn compile spotbugs:check -pl pontos-server
```

**在 `pom.xml` 添加 PMD**：

```xml
<plugin>
  <groupId>org.apache.maven.plugins</groupId>
  <artifactId>maven-pmd-plugin</artifactId>
  <version>3.21.2</version>
  <configuration>
    <rulesets>
      <ruleset>/rulesets/java/quickstart.xml</ruleset>
    </rulesets>
    <failOnViolation>false</failOnViolation>
    <printFailingErrors>true</printFailingErrors>
  </configuration>
</plugin>
```

### 可读性审查 Checklist（人工 + AI 配合）

```
□ 类名：是否准确描述职责（Handler/Service/Manager/Util 语义正确）
□ 方法名：动词 + 名词，是否描述"做什么"而非"怎么做"
□ 变量名：无单字母（循环变量除外），无缩写（cnt→count，idx→index）
□ 魔法数字：所有字面量是否有命名常量
□ 注释：TODO 是否有 owner 和 deadline，过时注释是否清理
□ 方法长度：超过 30 行的方法是否可拆分
□ 嵌套深度：超过 3 层嵌套是否可用 early return 简化
□ Javadoc：public API 是否有完整文档
```

---

## 工具选型速查表

| 场景 | 零安装（当前可用） | 增强（安装后） | 最佳 ROI |
|------|-------------------|---------------|---------|
| 缺陷扫描 | Sisyphus + task() | Semgrep p/java | **task() 并行扫描** |
| 重构 | OpenRewrite (Maven) + Sisyphus | ast-grep 自定义规则 | **OpenRewrite 机械重构** |
| 规范 | Maven Checkstyle/PMD | Semgrep 自定义规则 | **Checkstyle + Sisyphus 配合** |

## 推荐安装优先级

```bash
# P0：最高 ROI，扫描能力质变
brew install semgrep

# P1：精准 AST 级重构，自定义规则
npm i -g @ast-grep/cli

# P2：Java 字节码级缺陷（需要 Maven 集成）
# → 在 pom.xml 加 spotbugs-maven-plugin（零额外安装）
```

---

## 典型工作流示例

### 日常 PR 前检查（5 分钟）

```
1. git diff --name-only HEAD  # 看改了哪些文件
2. 告诉 Sisyphus："扫描这些改动文件：[文件列表]，重点找 silent failure 和异常处理问题"
3. Sisyphus 输出问题列表
4. 修复 P0/P1，记录 P2 到 TODO
```

### 模块级深度扫描（30 分钟）

```
1. task() 并行 3 个 subagent 扫描 handler/service/crane 三个包
2. 汇总问题，按严重级别排序
3. P0 立即修复，P1 本迭代修复，P2 下迭代
4. OpenRewrite 做机械重构（不改业务逻辑）
```

### 新功能开发后规范检查

```
1. mvn checkstyle:check -pl [模块名]
2. Sisyphus 审查可读性（命名/注释/魔法数字）
3. 确认无新增 TODO 未标注 owner
```
