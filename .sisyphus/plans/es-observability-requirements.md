# ES 客户端全链路可观测性体系 — 需求文档输出

## TL;DR

> **Quick Summary**: 把 ES 客户端可观测性需求文档写入 `contexts/survey_sessions/`，内容基于 Poros 代码分析和 Q2 OKR 整理。
>
> **Deliverables**:
> - `contexts/survey_sessions/es_observability_requirements_20260411.md`（需求文档正文）
>
> **Estimated Effort**: Quick（单文件写入）
> **Parallel Execution**: NO
> **Critical Path**: Task 1

---

## Context

### Original Request
用户要求把 ES 客户端全链路可观测性体系的需求文档写到 `/Users/shenhuayu/.config/opencode/contexts/survey_sessions/`。

### Research Findings
- **当前打点现状**（来自代码分析）：
  - `CatReportFilter`：任何 exception 都标为失败，`version_conflict` 混入 SLO 统计
  - `CatHttpProcessor`：同上，无集群维度
  - `ConfigEventReportTask`：只上报 `timeout` + `authorizedByKms` 两个字段
  - `PorosNodesSniffer.sniff()`：只打 `log.info`，无 Cat 打点
  - `SearchThrottleService`：有 `ES.QueryRisk.{riskType}` 打点，但无命中率统计

- **OKR 对应**（来自学城 2753283495）：
  - 日志定制版 SDK 完善打点（P1，主R：shenhuayu）
  - 建设日志的 SLA 大盘（P1，主R：shenhuayu）
  - SDK 打点信息提示优化（Backlog）
  - 更好的 sniffer（Backlog）
  - 收集客户端配置并上报（Backlog）

---

## Work Objectives

### Core Objective
将需求文档写入指定路径，文档内容完整覆盖：问题陈述、方案设计（4 层）、实现路径（3 Phase）、与 OKR 的对应关系。

### Concrete Deliverables
- `/Users/shenhuayu/.config/opencode/contexts/survey_sessions/es_observability_requirements_20260411.md`

### Definition of Done
- [ ] 文件存在于目标路径
- [ ] 文档结构完整（7个章节）
- [ ] 代码引用准确（基于实际 Poros 代码）

### Must Have
- 文档内容基于真实代码分析（CatReportFilter、CatHttpProcessor、PorosNodesSniffer、ConfigEventReportTask）
- 与 Q2 OKR 明确对应

### Must NOT Have
- 不要修改 Poros 代码（这是需求文档，不是实现）
- 不要创建多余文件

---

## Verification Strategy

### Test Decision
- **Infrastructure exists**: NO
- **Automated tests**: None（文档写入任务）

### QA Policy
文件写入后验证文件存在且内容完整。

---

## Execution Strategy

### Parallel Execution Waves

```
Wave ONLY (single task):
└── Task 1: 写需求文档到 contexts/survey_sessions/ [quick]

Wave FINAL:
└── F1: 验证文件写入正确
```

---

## TODOs

- [ ] 1. 将 ES 可观测性需求文档写入目标路径

  **What to do**:

  在 `/Users/shenhuayu/.config/opencode/contexts/survey_sessions/es_observability_requirements_20260411.md` 写入以下完整内容：

  ---

  ```markdown
  # ES 客户端全链路可观测性体系 — 需求文档

  > **作者**: shenhuayu
  > **日期**: 2026-04-11
  > **状态**: 草稿
  > **对应 OKR**: Q2 日志定制版 SDK 完善打点 + SLA 大盘（P1，主R：shenhuayu）

  ---

  ## 一、背景与问题陈述

  ### 当前状态：三个独立的"看不见"

  **问题 1：SLO 大盘基本失效**

  当前 `CatReportFilter`（服务端）和 `CatHttpProcessor`（客户端）的打点逻辑是：任何 exception 都标记为失败。

  ```java
  // CatReportFilter.java
  if (exception == null) {
      poros.setStatus(Transaction.SUCCESS);
  } else {
      poros.setStatus(exception);  // ← version_conflict 也被标为失败
      Cat.logError(exception);
  }
  \```

  问题：`version_conflict_engine_exception` 是业务正常行为（乐观锁冲突），不是 ES 故障。当业务写入量大时，这类异常会大量混入 SLO 统计，导致 SLO 大盘严重失真。参考 Zebra 的做法，需要区分"业务预期异常"和"系统故障异常"。

  **问题 2：sniffer 健康状态不可见**

  当前 `PorosNodesSniffer` 的 `sniff()` 只打了 `log.info`，没有 Cat 打点。

  ```java
  // PorosNodesSniffer.java
  public List<Node> sniff() throws IOException {
      log.info("start sniff nodes.");
      Node[] porosHosts = eagleApiProxy.getPorosNodes();
      log.info("sniffed nodes succeed, nodes[{}]", Arrays.deepToString(porosHosts));
      // ← 没有 Cat 打点，sniffer 成功/失败/节点变化全部不可见
      return Lists.newArrayList(porosHosts);
  }
  \```

  影响：无法知道某个业务方的 sniffer 是否正常工作，节点发现失败时只能靠日志排查，且 `ES.{cluster}` 维度的监控大盘中没有 sniffer 数据。

  **问题 3：客户端配置收集不完整**

  当前 `ConfigEventReportTask` 只上报了两个字段：

  ```java
  configMap.put("timeout", String.valueOf(timeoutMillis));
  configMap.put("authorizedByKms", authorizeByKms ? "true" : "false");
  \```

  实际上 `PorosRestClientBuilder` 有更多关键配置：`maxRetryTimeoutMillis`（固定 90000ms）、`throttleHighRiskQuery`、`queryTemplateRateLimit`、`callPorosAsync`、是否集群组模式等。这些配置直接影响业务方的查询行为，但平台侧完全看不见。

  已知后果：某业务方超时配置不合理，平台侧无感知，只能等 TT 工单上来后才能排查。

  **问题 4：mtrace 引发长尾问题，无主动感知机制**

  火焰图显示 mtrace 的 ThreadLocal 在某些场景下占用 50-60% CPU，导致查询长尾。当前没有任何机制能主动发现"这个业务方正在被 mtrace 拖累"，只能靠人工排查。

  ---

  ## 二、目标

  **核心目标**：把 ES 客户端从"黑盒"变成"白盒"——平台侧能主动发现问题，而不是被动响应工单。

  **量化目标**（Q2）：
  - SLO 大盘准确率：过滤业务预期异常后，SLO 误报率降低 ≥80%
  - 配置可见性：接入 SDK 的业务方，关键配置（超时/版本/限流开关）100% 可见
  - sniffer 健康度：所有集群的 sniffer 成功率可在 Cat 大盘查询
  - 主动发现：能通过大盘识别出"配置异常"的业务方，无需等工单

  **不在范围内**：
  - 自动修复配置（本期只做"看见"，不做"干预"）
  - ES 服务端的可观测性（Eagle 平台已有）
  - 链路追踪（MTrace 集成，另立项）

  ---

  ## 三、方案设计

  ### Layer 1：精准 SLO — 异常分类体系

  **核心思路**：建立异常分类白名单，将 ES 异常分为三类：

  | 类别 | 定义 | SLO 计入方式 | 示例 |
  |------|------|------------|------|
  | **系统故障** | ES 集群本身的问题 | 计入失败 | `ConnectException`、`SocketTimeoutException`、`circuit_breaking_exception` |
  | **业务预期异常** | 业务方正常使用中的预期错误 | 不计入失败，单独打点 | `version_conflict_engine_exception`、`index_not_found_exception`（业务自己处理） |
  | **业务逻辑错误** | 业务方的 DSL 写错了 | 计入失败，但区分 appKey 维度 | `parsing_exception`、`search_phase_execution_exception` |

  **实现方案**：

  ```java
  // 新增：ExceptionClassifier（建议放 poros-common）
  public enum ExceptionCategory {
      SYSTEM_FAILURE,      // 计入 SLO 失败
      BUSINESS_EXPECTED,   // 不计入 SLO，打 Cat.logEvent("ES.BusinessException")
      BUSINESS_LOGIC_ERROR // 计入 SLO 失败，但打额外维度
  }

  public class ExceptionClassifier {
      private static final Set<String> BUSINESS_EXPECTED = ImmutableSet.of(
          "version_conflict_engine_exception"
          // 可通过 Lion 动态扩展白名单
      );

      public static ExceptionCategory classify(Exception e) { ... }
  }
  \```

  **打点变更**（`CatReportFilter` + `CatHttpProcessor`）：
  - 系统故障：保持现有逻辑（`setStatus(exception)`）
  - 业务预期异常：`setStatus(Transaction.SUCCESS)` + `Cat.logEvent("ES.BusinessException.{clusterName}", exceptionType)`
  - 新增 Cat 维度：`ES.SLO.{clusterName}` 单独统计，与现有打点并行（灰度期间两套并存）

  ---

  ### Layer 2：sniffer 健康度打点

  **改动位置**：`PorosNodesSniffer.sniff()` + `PorosRestClientBuilder` 匿名 sniffer

  **打点设计**：

  ```java
  @Override
  public List<Node> sniff() throws IOException {
      long start = System.currentTimeMillis();
      try {
          Node[] porosHosts = eagleApiProxy.getPorosNodes();
          List<Node> nodes = Lists.newArrayList(porosHosts);

          // 新增打点
          Cat.logEvent("ES." + clusterName + ".sniffer", "success|nodeCount=" + nodes.size());
          Cat.newCompletedTransactionWithDuration("ES.sniffer", clusterName, System.currentTimeMillis() - start);

          // 节点变化检测
          if (nodeCountChanged(nodes)) {
              Cat.logEvent("ES." + clusterName + ".snifferNodeChange",
                  "from=" + lastNodeCount + "|to=" + nodes.size());
          }

          return nodes;
      } catch (Exception e) {
          Cat.logEvent("ES." + clusterName + ".sniffer", "failure|error=" + e.getClass().getSimpleName());
          throw e;
      }
  }
  \```

  **可观测内容**：
  - sniffer 成功率（按集群维度）
  - sniffer 耗时（P99/P999）
  - 节点数量变化（扩缩容、故障摘除时可见）

  ---

  ### Layer 3：客户端配置完整上报

  **扩充 `ConfigEventReportTask` 上报的配置项**：

  | 配置项 | 当前状态 | 目标 |
  |--------|---------|------|
  | `timeout` | ✅ 已上报 | 保持 |
  | `authorizedByKms` | ✅ 已上报 | 保持 |
  | `sdkVersion` | ❌ 未上报 | 新增：从 MANIFEST.MF 读取 |
  | `maxRetryTimeoutMillis` | ❌ 未上报（硬编码 90000ms） | 新增 |
  | `throttleHighRiskQuery` | ❌ 未上报 | 新增 |
  | `queryTemplateRateLimit` | ❌ 未上报 | 新增 |
  | `callPorosAsync` | ❌ 未上报 | 新增 |
  | `isClusterGroup` | ❌ 未上报 | 新增 |
  | `mtraceEnabled` | ❌ 未上报 | 新增 |
  | `appKey` | ❌ 未上报 | 新增（便于关联业务方） |

  **上报时机**：保持现有每小时一次，增加"Lion 配置变更时立即上报"。

  **Cat 大盘价值**：
  - 按 `ES.{clusterName}.clientConfig` 过滤，看某个集群下所有业务方的配置分布
  - 自动识别"超时配置 < 500ms 的业务方"（异常配置告警）
  - 识别"未开启限流的高 QPS 业务方"

  ---

  ### Layer 4：mtrace 影响检测（可选，Q2 后期）

  **思路**：在 `CatHttpProcessor` 中，对每个请求采样（1%）记录 mtrace 是否激活，当某个 appKey 的 P99 耗时异常时，关联 mtrace 状态，提供"关闭 mtrace 可能有效"的诊断建议。

  ---

  ## 四、实现路径

  ### Phase 1（2周）：精准 SLO + sniffer 打点

  优先级最高，直接影响 SLO 大盘准确性。

  - [ ] 实现 `ExceptionClassifier`，定义异常分类规则（白名单 + Lion 动态扩展）
  - [ ] 改造 `CatReportFilter`（服务端）：接入异常分类
  - [ ] 改造 `CatHttpProcessor`（客户端）：接入异常分类
  - [ ] 改造 `PorosNodesSniffer`：增加 sniffer 成功/失败/耗时/节点变化打点
  - [ ] 单元测试：覆盖各类异常分类场景
  - [ ] 灰度验证：选 2-3 个业务方，对比改造前后 SLO 数值变化

  **验收标准**：
  - Cat 大盘中 `ES.BusinessException.{clusterName}` 有数据
  - `ES.{clusterName}.sniffer` 有成功/失败打点
  - 选定灰度业务方的 SLO 数值与预期一致（version_conflict 不再计入失败）

  ### Phase 2（2周）：配置完整上报 + 大盘建设

  - [ ] 扩充 `ConfigEventReportTask` 上报字段（8个新字段）
  - [ ] 增加 Lion 变更触发的即时上报
  - [ ] 在 Cat 上建立"客户端配置大盘"
  - [ ] 建立 SLO 大盘（基于 Phase 1 的精准打点）

  **验收标准**：
  - 任意一个集群，能在 Cat 大盘看到所有接入业务方的 SDK 版本分布
  - 超时配置异常的业务方能被自动标记

  ### Phase 3（可选，1-2周）：mtrace 影响检测

  - [ ] 采样记录 mtrace 激活状态
  - [ ] 关联耗时异常和 mtrace 状态
  - [ ] 提供诊断建议输出

  ---

  ## 五、影响范围评估

  **代码改动**：
  - `poros-client`：`CatHttpProcessor`、`PorosNodesSniffer`、`PorosRestClientBuilder`、`ConfigEventReportTask`
  - `poros-service`：`CatReportFilter`
  - 新增：`ExceptionClassifier`（建议放 `poros-common`）

  **兼容性**：
  - 新增打点不影响现有逻辑，零风险
  - 异常分类改变了 SLO 打点语义，需要提前通知依赖 SLO 大盘的团队

  **发布策略**：
  - Phase 1 打点增量先灰度（新增并行打点，不修改现有打点）
  - 稳定后再切换 SLO 计算逻辑
  - Phase 2 配置上报无风险，可直接发布

  ---

  ## 六、与 OKR 的对应关系

  | OKR 项 | 本需求覆盖 |
  |--------|---------|
  | 日志定制版 SDK 完善打点（P1，主R：shenhuayu） | Phase 1+2 直接对应 |
  | 建设日志的 SLA 大盘（P1，主R：shenhuayu） | Phase 2 大盘建设 |
  | SDK 打点信息提示优化（SLO 大盘失效，Backlog） | Phase 1 精准 SLO |
  | 更好的 sniffer（Backlog） | Phase 1 sniffer 打点 |
  | 收集客户端配置并上报（Backlog） | Phase 2 配置上报 |

  **结论**：本需求把 5 个分散的 Backlog 项整合成一个系统性工程，同时满足 2 个 OKR 指标。

  ---

  ## 七、开放问题

  1. **异常分类白名单的边界**：`version_conflict` 肯定排除，但 `index_not_found_exception` 是否排除？取决于业务方的使用模式，需要和几个主要业务方确认。

  2. **SLO 大盘切换时机**：新旧打点并行运行后，建议并行观察 2 周后再切换 SLO 大盘的数据源。

  3. **限流协同设计的衔接**：Phase 2 的限流命中率大盘，与 Q2 OKR 里"限流服务端 & 客户端协同设计（联系齐飞）"有关联。本期先做"看见"，下期再做"客户端感知限流并降级"。

  4. **配置大盘的权限**：客户端配置上报后，需要确认 Cat 大盘的访问控制范围。

  ---

  ## 附录：当前打点现状速查

  | 打点位置 | Cat 类型 | 维度 | 缺失内容 |
  |---------|---------|------|---------|
  | `CatReportFilter`（服务端） | Transaction | `operationType` × `appKey` | 异常分类；业务预期异常未区分 |
  | `CatHttpProcessor`（客户端） | Transaction | `operationType` × `index` | 异常分类；无集群维度 |
  | `ConfigEventReportTask` | Event | `ES.{cluster}.clientConfig` | 只有 timeout + authorizedByKms |
  | `PorosNodesSniffer` | log.info only | 无 | 全部缺失 |
  | `SearchThrottleService` | Event | `ES.QueryRisk.{riskType}` | 无命中率统计维度 |
  ```

  ---

  **Must NOT do**:
  - 不要修改任何 Poros 源代码
  - 不要创建其他文件

  **Recommended Agent Profile**:
  > 纯文件写入任务，无需复杂推理。
  - **Category**: `quick`
  - **Skills**: []

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave ONLY
  - **Blocks**: F1
  - **Blocked By**: None

  **References**:
  - `poros-service/src/main/java/com/sankuai/meituan/poros/service/filter/CatReportFilter.java` — 当前打点逻辑参考
  - `poros-client/src/main/java/com/sankuai/meituan/poros/client/CatHttpProcessor.java` — 客户端打点参考
  - `poros-client/src/main/java/com/sankuai/meituan/poros/client/PorosNodesSniffer.java` — sniffer 现状参考
  - `poros-common/src/main/java/org/elasticsearch/client/task/ConfigEventReportTask.java` — 配置上报现状参考

  **Acceptance Criteria**:
  - [ ] 文件存在：`/Users/shenhuayu/.config/opencode/contexts/survey_sessions/es_observability_requirements_20260411.md`
  - [ ] 文件大小 > 5KB（内容完整）

  **QA Scenarios**:

  ```
  Scenario: 文件写入成功
    Tool: Bash
    Steps:
      1. ls -la /Users/shenhuayu/.config/opencode/contexts/survey_sessions/es_observability_requirements_20260411.md
      2. wc -c /Users/shenhuayu/.config/opencode/contexts/survey_sessions/es_observability_requirements_20260411.md
    Expected Result: 文件存在，大小 > 5000 bytes
    Evidence: .sisyphus/evidence/task-1-file-written.txt
  ```

  **Commit**: YES
  - Message: `docs: add ES observability requirements doc`
  - Files: `contexts/survey_sessions/es_observability_requirements_20260411.md`

---

## Final Verification Wave

- [ ] F1. **文件验证** — `quick`
  确认文件存在于目标路径，内容完整（包含 7 个章节标题）。
  Output: `File [EXISTS/MISSING] | Size [N bytes] | Sections [N/7] | VERDICT: APPROVE/REJECT`

---

## Commit Strategy

- **1**: `docs: add ES observability requirements doc` — `contexts/survey_sessions/es_observability_requirements_20260411.md`

---

## Success Criteria

```bash
ls -la /Users/shenhuayu/.config/opencode/contexts/survey_sessions/es_observability_requirements_20260411.md
# Expected: 文件存在，大小 > 5KB
```
