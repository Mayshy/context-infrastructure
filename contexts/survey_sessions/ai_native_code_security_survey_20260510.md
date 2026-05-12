# AI-Native 代码安全工具全景调研（2024–2026）

**调研日期**: 2026-05-10  
**范围**: LLM-based SAST、AI-first 漏洞检测、Agentic 修复工具、AI 实验室安全产品  
**对比基准**: CodeRabbit、Qodo、Snyk Code（已知工具）

---

## 核心结论

1. **2026 年出现了真正的 AI-Native 分水岭**：Anthropic（Claude Security，2026-02）和 OpenAI（Codex Security，2026-03）相继发布独立安全扫描产品，标志着 AI 实验室直接入场代码安全。
2. **"AI-Native" vs "AI-Assisted" 的本质区别**：AI-Native 工具完全用 LLM 替代规则引擎做推理；AI-Assisted 工具在传统 SAST 上叠加 LLM 做降噪/修复。
3. **Agentic 修复是最热赛道**：Pixee、Mobb、Corgea 等工具不只是找漏洞，而是自主生成 PR 修复，平均 merge rate 达 76%。
4. **学术界已验证 LLM 超越传统 SAST**：IRIS（GPT-4）检测到 69/120 个漏洞，传统工具只检测 27；vEcho 发现 51 个 0-day。
5. **"Vibe Coding" 安全子赛道兴起**：专门针对 AI 生成代码（Lovable/Bolt/Cursor 产出）的扫描工具正在形成独立品类。

---

## 一、AI 实验室直接产品

### 1. Claude Security（Anthropic）
**发布**: 2026-02-20（Limited Research Preview）  
**官网**: [anthropic.com/product/security](https://www.anthropic.com/product/security)  
**模型**: Claude Opus 4.6  
**AI-Native 程度**: ⭐⭐⭐⭐⭐（完全 LLM 推理，无规则引擎）

**核心机制**:
- 像安全研究员一样读代码：跨文件追踪变量、推断信任边界
- **对抗性验证**：每个发现由第二个 Claude agent 作为"攻击者"挑战，过滤误报
- 发现 → 生成 patch → 在 Claude Code 中开 branch 供人工审核
- Anthropic Frontier Red Team 实战验证：在开源软件中发现 500+ 此前未知漏洞

**差异化**:
- 能找业务逻辑漏洞、跨文件数据流、访问控制绕过——规则引擎无法检测的类别
- 不自动合并，人工审核每个 patch

**定价**: Enterprise/Team 计划，公开 preview 阶段免费申请  
**来源**: [augmunt.com 深度分析](https://www.augmunt.com/en/blog/claude-code-security-2026/) | [securepilot.app 对比](https://www.securepilot.app/blog/free-ai-code-security-tools)

---

### 2. Codex Security（OpenAI）
**发布**: 2026-03-06（Public Research Preview，前身 Aardvark 于 2025-10 内测）  
**模型**: OpenAI internal models  
**AI-Native 程度**: ⭐⭐⭐⭐⭐

**核心机制**:
- AI agent + sandbox 验证（与 Claude Security 的纯推理不同）
- 沙箱中运行代码验证漏洞可利用性，降低误报
- 生成代码修复 + 解释

**差异化**: 沙箱执行验证是独特优势，比纯静态推理更确定性  
**定价**: 公开 preview 期间免费  
**来源**: [heyuan110.com 对比分析](https://www.heyuan110.com/posts/ai/2026-03-13-ai-code-security-tools-compared/)

---

### 3. Claude Code Security Reviews（Anthropic，轻量版）
**发布**: 2025-08-06（GA），2026-03-16 更新  
**官网**: [anthropic.com/news/automate-security-reviews-with-claude-code](https://anthropic.com/news/automate-security-reviews-with-claude-code)  
**AI-Native 程度**: ⭐⭐⭐⭐

**产品形态**:
- `/security-review` 命令：终端内按需扫描
- GitHub Actions 集成：每个 PR 自动触发
- 多 agent 并行分析 diff + 全代码库上下文，验证步骤过滤误报
- 内联 PR 评论，不阻断工作流

**来源**: [Anthropic 官方文档](https://docs.anthropic.com/en/docs/claude-code/code-review) | [support.anthropic.com](https://support.anthropic.com/en/articles/11932705-automated-security-reviews-in-claude-code)

---

## 二、AI-Native SAST 新创公司

### 4. ZeroPath
**官网**: [zeropath.com](https://zeropath.com/products/sast)  
**成立**: ~2024  
**荣誉**: RSAC 2026 Innovation Sandbox Top 10 Finalist  
**AI-Native 程度**: ⭐⭐⭐⭐⭐（"第一个 AI-Native AppSec 平台"）

**核心技术**:
- 完全 LLM 驱动，不依赖规则数据库
- Tree-of-Thoughts (ToT) + ReAct 框架做业务逻辑漏洞分析
- Monte Carlo Tree Self-refine (MCTSr) 验证可利用性
- 自然语言策略引擎：用英语写规则（"flag endpoints that return full user objects including passwords"）
- 每月 300k+ 次代码扫描

**实战验证**:
- 发现 FFmpeg 中 7 个漏洞、curl 中 170+ 个有效 bug
- 在 Better Auth 中发现完整账户接管漏洞
- 自主发现 Netflix、Salesforce、Hulu 项目中的 Critical 0-day

**声称指标**: 2x 漏洞检测量，75% 更少误报  
**定价**: 联系销售；支持 on-prem/self-hosted/BYOK  
**来源**: [zeropath.com/blog/0day-discoveries](https://zeropath.com/blog/0day-discoveries) | [awesomeagents.ai 对比](https://awesomeagents.ai/tools/best-ai-security-scanning-tools-2026/)

---

### 5. Corgea（含 BLAST + Beagle LLM）
**官网**: [corgea.com](https://corgea.com)  
**发布**: BLAST 于 2024-10，Beagle LLM 后续发布  
**AI-Native 程度**: ⭐⭐⭐⭐⭐（自研 AppSec 专用 LLM）

**核心技术**:
- **BLAST**：AI-native SAST，用 AST + LLM 上下文理解检测业务逻辑漏洞
- **Beagle**：基于 Llama 3.1 fine-tune 的 AppSec 专用模型，分析 100k+ 漏洞训练
  - 多权重模块：误报检测、自动修复、质量检查各自独立权重
  - 2-3 天完成一个训练周期（假设 → 数据生成 → 验证 → 部署）
- **CodeIQ**：项目级代码理解，AST + AI 上下文拉取，避免 RAG 的语义漂移问题

**差异化**: 唯一有自研专用 AppSec LLM 的初创公司（非调用 GPT-4/Claude API）  
**语言支持**: 25+ 语言  
**定价**: 联系销售  
**来源**: [Corgea 文档](https://docs.corgea.app/introduction) | [Beagle 发布博客](https://corgea.com/blog/announcing-beagle-the-next-generation-of-appsec-llms)

---

### 6. Endor Labs / AURI
**官网**: [endorlabs.com/platform](https://www.endorlabs.com/platform)  
**AI-Native 程度**: ⭐⭐⭐⭐⭐（多 agent 架构）

**核心技术**:
- **AURI**：AI-native AppSec 平台，专为 Agentic 开发设计
- 多 agent + sub-agent：检测、评估可利用性、分类、修复各自独立 agent
- Code Context Graph：映射代码、依赖、容器镜像、服务的真实连接关系
- 可利用性分析：追踪第一方代码 → 直接/传递依赖 → 容器镜像层
- 给 AI Coding Agent（Copilot/Cursor 等）提供安全上下文层

**定位**: 传统 AppSec 工具的"升级版"，而非替代品  
**Best AI-Native** 评级来源: [aicodereview.cc 32工具对比](https://aicodereview.cc/blog/best-sast-tools-2026)  
**来源**: [endorlabs.com](https://www.endorlabs.com/platform)

---

## 三、Agentic 修复工具（Fix-First 范式）

### 7. Pixee
**官网**: [pixee.ai](https://pixee.ai)  
**融资**: $15M seed（2025-05）  
**创始人**: Arshan Dabirsiaghi（Contrast Security 联创）、Surag Patel  
**AI-Native 程度**: ⭐⭐⭐⭐（Hybrid：Agentic AI + 确定性 codemod）

**核心定位**: Fix-First（不是又一个扫描器，而是自动修复现有扫描器的发现）

**核心技术**:
- 开源 **codemodder** 框架：可识别、描述、重写代码的安全变换库
- 接入 10+ 扫描器：Snyk、Checkmarx、Veracode、SonarQube、Semgrep 等（SARIF 摄入）
- 可利用性路径追踪：98% 误报消除
- CI/CD 验证后才开 PR，确保修复不引入新问题

**实战指标**:
- 76% 开发者 merge rate（自动生成的 PR）
- 91% 修复时间减少（企业用户）
- MTTR 从 252 天降至 7 天

**定价**: 开源项目免费；企业版联系销售  
**语言**: Java、Python、JavaScript/TypeScript、C#、Go  
**来源**: [aicodereview.cc Pixee 评测](https://aicodereview.cc/tool/pixee) | [stackpick.net](https://stackpick.net/tools/pixee/)

---

### 8. Mobb.ai
**官网**: [mobb.ai](https://www.mobb.ai)  
**AI-Native 程度**: ⭐⭐⭐⭐（确定性修复引擎，无 LLM 幻觉）

**核心定位**: AppSec 团队专用修复工具，与 SAST 工具协同而非竞争

**核心技术**:
- **确定性修复逻辑**：不是 LLM 生成，而是验证过的安全变换，无幻觉
- 支持 Checkmarx、Fortify、Snyk、SonarQube、Semgrep、Opengrep 等
- 直接在 GitHub/GitLab PR 中修复代码
- 自动分类误报

**定价**: 免费试用  
**来源**: [mobb.ai/blog/top-ai-code-fixing-tools](https://www.mobb.ai/blog/top-ai-code-fixing-tools)

---

### 9. Vercel deepsec（开源）
**GitHub**: [vercel-labs/deepsec](https://github.com/vercel-labs/deepsec)  
**Stars**: 1,133（发布 10 天）  
**发布**: 2026-04-30  
**License**: Apache-2.0  
**AI-Native 程度**: ⭐⭐⭐⭐⭐（纯 agent 驱动）

**核心定位**: 大型存量代码库的深度漏洞挖掘，发现长期潜伏的问题

**核心技术**:
- 使用最强模型（Claude/Codex）+ 最大 thinking 配置
- 两阶段：regex matcher 快速扫描候选点 → AI agent 深度调查
- 支持 Vercel AI Gateway + Sandbox microVM
- 设计用于大型代码库，单次扫描可能花费数千美元

**适用场景**: 不是 CI/CD 每次扫描，而是深度一次性审计  
**来源**: [github.com/vercel-labs/deepsec](https://github.com/vercel-labs/deepsec/)

---

## 四、AI Coding 工具内置安全功能

### 10. GitHub Copilot Autofix
**发布**: Beta 2024-03-20 → GA 2024-08-14  
**官网**: [docs.github.com](https://docs.github.com/en/code-security/concepts/code-scanning/copilot-autofix-for-code-scanning)  
**AI-Native 程度**: ⭐⭐⭐（AI 生成修复，但检测仍依赖 CodeQL 规则引擎）

**核心机制**:
- CodeQL 发现漏洞 → GPT-5.3-Codex 生成修复建议
- 覆盖 JS/TS/Java/Python 90%+ 告警类型
- 修复建议含自然语言解释 + 代码预览（可接受/编辑/拒绝）
- 可跨文件修复，包含依赖变更
- **数据**: 有修复建议的漏洞修复速度 3x 更快；XSS 快 7x，SQL 注入快 12x

**2024-10 扩展**: 支持 ESLint、JFrog SAST、Black Duck Polaris 等第三方工具  
**定价**: 无需独立 Copilot 订阅；公共仓库免费；私有仓库需 GitHub Code Security 许可  
**来源**: [GitHub Changelog 2024-08-14](https://github.blog/changelog/2024-08-14-copilot-autofix-for-codeql-code-scanning-alerts-is-now-generally-available) | [GitHub Blog 2024-03-20](https://github.blog/news-insights/product-news/found-means-fixed-introducing-code-scanning-autofix-powered-by-github-copilot-and-codeql/)

---

### 11. Cursor BugBot
**发布**: Beta 2025-07-24 → GA；Autofix 2026-02-26；自学习规则 2026-04-08  
**官网**: [cursor.com/docs/bugbot](https://cursor.com/docs/bugbot)  
**AI-Native 程度**: ⭐⭐⭐⭐

**核心机制**:
- 自动分析 PR diff，理解代码意图
- 发现逻辑 bug、边界情况、安全问题
- **BugBot Autofix**：发现 bug 后自动 spawn Cloud Agent 修复，push 到现有 branch
- **BUGBOT.md**：自定义审查规则（含安全规则，如 `eval()`/`exec()` 检测）
- **自学习规则**（2026-04）：从历史 PR 评论中学习团队标准，自动生成规则
- MCP 集成：AI 工具可直接与 BugBot 交互

**定价**: Team/Enterprise 计划  
**来源**: [cursor.com/docs/bugbot](https://cursor.com/docs/bugbot) | [cursor.com/blog/bugbot-out-of-beta](https://cursor.com/blog/bugbot-out-of-beta)

---

## 五、传统工具 AI 升级（AI-Assisted，非 AI-Native）

### 12. Semgrep Assistant / Semgrep Multimodal
**发布**: GA 2024-03-20；Multimodal（含 AI-powered detection）2026  
**官网**: [semgrep.dev](https://semgrep.dev/blog/2024/assistant-ga-launch/)  
**AI-Native 程度**: ⭐⭐⭐（检测引擎仍是规则，AI 做分类/修复/规则生成）

**核心功能**:
- **Auto-triage**：AI 判断误报，人工认同率 97%
- **Auto-fix**：GPT-4 生成修复建议
- **Custom rule writing**：用自然语言 + 好/坏代码示例生成 Semgrep 规则
- **AI-powered detection**（Multimodal）：检测 IDOR、broken authorization 等业务逻辑漏洞
- **Assistant Memories**：组织级定制修复指导，按 project/rule 粒度
- 模型：OpenAI 主，AWS Bedrock 备用

**定价**: Team/Enterprise 计划包含 Assistant；开源引擎永久免费  
**来源**: [semgrep.dev/blog](https://semgrep.dev/blog/2024/assistant-ga-launch/) | [Multimodal 文档](https://semgrep.dev/docs/semgrep-assistant/overview)

---

### 13. Aikido Security
**官网**: [aikido.dev](https://www.aikido.dev)  
**AI-Native 程度**: ⭐⭐⭐（AI AutoTriage + AutoFix，底层 Semgrep-based）

**核心定位**: All-in-one DevSecOps（15+ 安全扫描器合一）

**功能**:
- SAST + SCA + Secrets + Container + IaC + DAST + CSPM + Runtime
- AI AutoTriage：LLM + 硬编码规则过滤误报，声称 95% 噪声减少
- AI AutoFix：一键生成 SAST 修复
- AI 代码审查：理解代码库的 PR 评论
- 自定义规则：从历史 PR 评论学习团队规范
- 可达性分析：过滤不可达的依赖漏洞

**定价**: $350/月起（10 用户）  
**来源**: [aikido.dev](https://www.aikido.dev/use-cases/secure-your-source-code) | [thectoclub.com 评测](https://thectoclub.com/tools/aikido-security-review/)

---

### 14. Greptile
**官网**: [greptile.com](https://www.greptile.com/ai-code-review)  
**用户**: 9,000+ 团队  
**AI-Native 程度**: ⭐⭐⭐⭐（全代码库上下文 + swarm agents）

**核心机制**:
- 构建代码图（codegraph）：每个函数、类、文件、目录的连接关系
- Swarm of agents：并行审查变更，评估超出 diff 范围的影响
- **TREX agent**：自动为每个 PR 编写并运行测试（沙箱执行）
- 从历史 PR 评论持续学习团队标准
- 支持 MCP：与 Claude Code、Cursor、Codex、Devin 集成

**定价**: $30/seat/月（含 50 次审查）；额外 $1/次；OSS 免费  
**自托管**: 支持（AWS/GCP/Azure，可 BYOLLM）  
**来源**: [greptile.com/pricing](https://www.greptile.com/pricing)

---

### 15. Bearer CLI
**GitHub**: [Bearer/bearer](https://github.com/Bearer/bearer)（开源）  
**状态**: 已被 Cycode 收购  
**AI-Native 程度**: ⭐⭐（规则引擎 + 数据流分析，无 LLM）

**独特定位**: 隐私优先 SAST（数据流 + PII/PHI 检测）

**核心功能**:
- 追踪敏感数据（PII、PHI、财务数据）在代码中的流动
- 120+ 数据类型分类
- 生成 GDPR/CCPA/HIPAA 合规报告（DPIA、RoPA）
- 按敏感数据影响度优先排序漏洞

**语言**: Go、Python、PHP、JS/TS、Ruby、Java  
**定价**: OSS 免费；企业版联系  
**来源**: [docs.bearer.com](https://docs.bearer.com/) | [stackpick.net/tools/bearer](https://stackpick.net/tools/bearer/)

---

## 六、"Vibe Coding" 安全子赛道（2025-2026 新兴）

专门针对 AI 生成代码（Lovable/Bolt/Cursor/v0 产出）的安全工具：

| 工具 | 定位 | 特点 |
|------|------|------|
| **VibeSafe** ([vibesafeio/vibesafe-action](https://github.com/vibesafeio/vibesafe-action)) | PR 安全扫描 | 2026-03 发布，免费开源，30秒设置，Supabase RLS 检测 |
| **SecurePilot** ([securepilot.app](https://www.securepilot.app)) | 即时扫描 | 无安装，165+ 规则，专注 AI 代码 smell，免费 |
| **VaultGuard** ([vaultguard.sh](https://vaultguard.sh)) | Early access | AI 生成代码的 secrets + 配置错误检测 |
| **VibeEval** ([vibe-eval.com](https://vibe-eval.com)) | AI-codegen 专用 DAST+SAST | 发布 gapbench 公开 benchmark，针对 Supabase/Next.js 栈 |

**背景数据**: Escape 研究扫描 5,600 个 vibe-coded 应用，发现 2,000+ 漏洞、400+ 暴露的 secrets

---

## 七、学术研究：LLM for Static Analysis

| 论文 | 发布 | 核心发现 |
|------|------|---------|
| **IRIS** ([arXiv:2405.17238](https://arxiv.org/abs/2405.17238)) | 2024-05 | GPT-4 + 静态分析检测 69/120 Java 漏洞，传统工具仅 27；误报减少 80% |
| **vEcho** ([arXiv:2603.01154](https://arxiv.org/abs/2603.01154)) | 2026-03 | 65% 检测率（IRIS 46%）；发现 51 个 0-day，含 Apache RCE，已获 CVE |
| **SAILOR** ([arXiv:2604.06506](https://arxiv.org/abs/2604.06506)) | 2026-04 | LLM 指导符号执行，在 6.8M 行 C/C++ 代码中发现 379 个未知内存安全漏洞；Claude Code 对比仅找 12 个 |
| **Argus** ([arXiv:2604.06633](https://arxiv.org/abs/2604.06633)) | 2026-04 | 多 agent SAST 框架，发现多个 CVE 级 0-day |
| **LSAST** ([arXiv:2409.15735](https://arxiv.org/abs/2409.15735)) | 2024-09 | 本地 LLM + SAST 混合，隐私保护前提下提升检测准确率 |
| **VULSOLVER** ([arxiv.org/pdf/2509.00882](https://www.arxiv.org/pdf/2509.00882)) | 2025-09 | 约束求解框架，OWASP Benchmark 100% recall；发现 15 个新漏洞 |

---

## 八、AI-Native vs AI-Assisted 判断框架

```
AI-Native（完全 LLM 推理）:
  ✓ 不依赖预定义规则数据库
  ✓ 能检测此前未见过的漏洞类型
  ✓ 理解业务逻辑和上下文
  ✓ 随模型升级自动提升能力
  示例: Claude Security, Codex Security, ZeroPath, Corgea BLAST

AI-Assisted（传统引擎 + LLM 增强）:
  ✓ 规则引擎做检测，LLM 做降噪/修复/解释
  ✓ 可预测、可审计、确定性结果
  ✓ 成熟的语言支持和规则库
  示例: Semgrep Assistant, GitHub Copilot Autofix, Aikido, Snyk Code

Agentic Fix-First（独立修复层）:
  ✓ 不替代扫描器，而是自动修复扫描器的发现
  ✓ 生成可合并的 PR
  示例: Pixee, Mobb, Corgea（修复功能）
```

---

## 九、工具速查表

| 工具 | 类型 | AI-Native? | 定价 | GitHub Stars | 发布年份 |
|------|------|-----------|------|-------------|---------|
| Claude Security | AI-Native SAST | ⭐⭐⭐⭐⭐ | Enterprise | N/A | 2026 |
| Codex Security | AI-Native SAST | ⭐⭐⭐⭐⭐ | Free preview | N/A | 2026 |
| ZeroPath | AI-Native SAST | ⭐⭐⭐⭐⭐ | 联系销售 | 私有 | 2024 |
| Corgea (BLAST) | AI-Native SAST | ⭐⭐⭐⭐⭐ | 联系销售 | 私有 | 2024 |
| Endor Labs (AURI) | AI-Native SAST | ⭐⭐⭐⭐⭐ | 联系销售 | 私有 | 2024 |
| Pixee | Agentic Fix | ⭐⭐⭐⭐ | OSS 免费；企业联系 | ~500 | 2023 |
| Mobb.ai | Agentic Fix | ⭐⭐⭐⭐ | 免费试用 | 私有 | 2022 |
| vercel-labs/deepsec | AI Agent Scanner | ⭐⭐⭐⭐⭐ | 开源（自费模型） | 1,133 | 2026-04 |
| Copilot Autofix | AI-Assisted Fix | ⭐⭐⭐ | GHAS 包含 | N/A | 2024 |
| Cursor BugBot | AI Code Review | ⭐⭐⭐⭐ | Team/Enterprise | N/A | 2025 |
| Claude Code /security-review | AI Code Review | ⭐⭐⭐⭐ | All plans | N/A | 2025 |
| Greptile | AI Code Review | ⭐⭐⭐⭐ | $30/seat/月 | 私有 | 2023 |
| Semgrep Multimodal | AI-Assisted SAST | ⭐⭐⭐ | Team/Enterprise | 10k+ | 2024 |
| Aikido | All-in-One | ⭐⭐⭐ | $350/月起 | 私有 | 2022 |
| Bearer | Privacy SAST | ⭐⭐ | 开源免费 | ~2k | 2023 |
| VibeSafe | Vibe Coding 安全 | ⭐⭐ | 免费开源 | ~200 | 2026-03 |
| SecurePilot | Vibe Coding 安全 | ⭐⭐ | 免费 | N/A | 2025 |

---

## 十、与传统工具对比（下游分析用）

| 维度 | 传统 SAST（SonarQube/Checkmarx） | AI-Assisted（Snyk Code/Semgrep） | AI-Native（Claude Security/ZeroPath） |
|------|--------------------------------|--------------------------------|--------------------------------------|
| 检测原理 | 规则匹配 + AST | ML + 数据流 + 规则 | LLM 推理（无规则） |
| 业务逻辑漏洞 | ❌ | 部分 | ✅ |
| 跨文件追踪 | 有限 | ✅ | ✅ |
| 误报率 | 30-70% | 10-30% | 声称 <5% |
| 新漏洞类型 | 需更新规则 | 需更新规则 | 自动适应 |
| 可解释性 | 规则引用 | 部分 | 自然语言解释 |
| 确定性 | ✅ | 部分 | ❌（LLM 不确定） |
| 合规/审计 | ✅ 成熟 | ✅ | 仍在建设 |
| 自托管 | ✅ | 部分 | 部分（ZeroPath 支持） |
| 成本 | 中等 | 中等 | 高（大型代码库） |

---

## 参考来源

- [Anthropic Claude Security 官网](https://www.anthropic.com/product/security)
- [OpenAI vs Anthropic vs Snyk 对比](https://www.heyuan110.com/posts/ai/2026-03-13-ai-code-security-tools-compared/)
- [ZeroPath 0-day 发现博客](https://zeropath.com/blog/0day-discoveries)
- [Pixee 评测 aicodereview.cc](https://aicodereview.cc/tool/pixee)
- [32 SAST 工具对比](https://aicodereview.cc/blog/best-sast-tools-2026)
- [GitHub Copilot Autofix GA](https://github.blog/changelog/2024-08-14-copilot-autofix-for-codeql-code-scanning-alerts-is-now-generally-available)
- [Cursor BugBot 文档](https://cursor.com/docs/bugbot)
- [Semgrep Assistant GA](https://semgrep.dev/blog/2024/assistant-ga-launch/)
- [vercel-labs/deepsec GitHub](https://github.com/vercel-labs/deepsec/)
- [IRIS 论文 arXiv:2405.17238](https://arxiv.org/abs/2405.17238)
- [vEcho 论文 arXiv:2603.01154](https://arxiv.org/abs/2603.01154)
- [SAILOR 论文 arXiv:2604.06506](https://arxiv.org/abs/2604.06506)
- [AI Code Review 市场状态 2026](https://aicodereview.cc/blog/state-of-ai-code-review-2026)
- [Free AI Code Security Tools 2026](https://www.securepilot.app/blog/free-ai-code-security-tools)
