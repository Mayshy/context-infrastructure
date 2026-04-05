# 中国大模型能力调研报告

**调研日期**: 2026-04-05
**调研对象**: 阿里千问(Qwen)、深度求索(DeepSeek)、智谱AI(GLM)、月之暗面(Kimi/Moonshot)、MiniMax
**调研目的**: 为 oh-my-opencode 配置提供指导

---

## 核心结论速查

| 模型 | 最新旗舰 | 开源 | API兼容 | 核心优势 | 参考价格 |
|------|---------|------|---------|---------|---------|
| **DeepSeek** | V3.2 / R1 | ✅ MIT | OpenAI兼容 | 性价比极高，推理能力强 | $0.28/MTok |
| **Qwen** | Qwen3 | ✅ Apache 2.0 | OpenAI兼容 | 统一思维模式，262K超长上下文 | 云平台定价 |
| **GLM** | GLM-5-Turbo / Z1-32B | ✅ Apache 2.0 | OpenAI兼容 | Agent工程化，深度研究能力 | ¥0.1-10/MTok |
| **Kimi** | K2.5 / K2 | ✅ Apache 2.0 | OpenAI+Anthropic兼容 | 编码SOTA，256K上下文 | ¥1-21/MTok |
| **MiniMax** | M2.7 | ⚠️ M2.5开源 | 独立API | Agent RL，SWE-bench 80.2% | ¥29-119/月 |

---

## 一、DeepSeek（深度求索）

### 1.1 最新旗舰模型

**DeepSeek-V3.2** (2025年12月)
- 架构: MoE，671B总参，37B激活
- 训练成本: 仅266万H800 GPU小时（极低成本）
- 支持Thinking模式和非Thinking模式

**DeepSeek-R1** (2025年1月)
- 专注推理能力，Chain-of-Thought王者
- 可蒸馏到小型模型
- GitHub 92k stars

### 1.2 核心能力

| 能力 | 规格 |
|------|------|
| 上下文 | 128K tokens |
| 多模态 | DeepSeek-VL系列 |
| 推理 | R1模型CoT能力极强 |
| 工具调用 | 完整支持 |

### 1.3 基准测试 (DeepSeek-V3)

| 基准 | 分数 | 对比 |
|------|------|------|
| MMLU | 88.5% | 与GPT-4o持平 |
| HumanEval | 82.6% | 强编码能力 |
| MATH-500 | 90.2% | 数学极强 |
| GPQA-Diamond | 59.1% | 超越GPT-4o |
| DROP | 91.6% F1 | 推理优秀 |

### 1.4 价格优势

| 类型 | 价格(/1M tokens) |
|------|-----------------|
| 输入(缓存命中) | $0.028 |
| 输入(缓存未命中) | $0.28 |
| 输出 | $0.42 |

**行业最低价之一**

### 1.5 开源与API

- 完全开源(MIT许可)
- OpenAI兼容API: `api.deepseek.com`
- HuggingFace: 102k stars (V3), 92k stars (R1)

---

## 二、Qwen（阿里云通义千问）

### 2.1 最新旗舰模型

**Qwen3** (2025年5月14日)
- 参数: 0.6B - 235B
- 架构: Dense和MoE双架构
- 统一思维/非思维模式（无需切换模型）

### 2.2 核心能力

| 能力 | 规格 |
|------|------|
| 上下文 | **262K tokens**（业界最长之一） |
| 多模态 | Qwen2.5-VL系列 |
| 推理 | Thinking budget机制，动态分配 |
| 工具 | Function calling + MCP支持 |
| 语言 | 119种语言（从29种大幅扩展） |

### 2.3 独特卖点

- **统一思维模式**: 一个模型同时处理快问快答和深度推理
- **Thinking Budget**: 用户可动态分配计算资源
- **超级Agent**: 代理任务达到SOTA，超越更大的MoE模型
- Apache 2.0许可，完全开源

### 2.4 开源与API

- GitHub: 27k stars
- HuggingFace / ModelScope
- 通过SGLang、vLLM本地部署

---

## 三、GLM（智谱AI）

### 3.1 最新旗舰模型

**GLM-5-Turbo** (2025)
- 专注Agent工程化
- SWE-bench Verified达开源SOTA，与Claude Opus 4.5持平

**GLM-4-32B-0414系列** (2025年4月)
- GLM-Z1-32B: 推理模型，数学/代码/逻辑强化
- GLM-Z1-Rumination-32B: 深度研究写作+搜索集成

### 3.2 核心能力

| 能力 | 规格 |
|------|------|
| 上下文 | 128K（部分达1M） |
| 多模态 | GLM-4.6V视觉 |
| 推理 | GLM-Z1系列强化学习 |
| 工具 | AutoGLM自主规划执行 |

### 3.3 基准测试 (GLM-4-32B)

| 基准 | 分数 |
|------|------|
| IFEval | 87.6% |
| BFCL-v3 | 69.6% |
| TAU-Bench | 68.7% |
| SimpleQA | 88.1% |

### 3.4 独特技术

- **GLM-OS概念**: Agent操作系统，AutoGLM+GLM-PC
- **CogAgent-9B**: 开源GUI Agent模型
- **深度研究**: GLM-Z1-Rumination专注复杂写作和研究

### 3.5 开源与API

- THUDM组织完全开源
- Apache 2.0许可
- OpenAI兼容API via bigmodel.cn

---

## 四、Kimi（Moonshot AI）

### 4.1 最新旗舰模型

**Kimi K2** (2025)
- 架构: MoE，1T总参，32B激活
- Muon优化器
- 超级代码和Agent能力

**Kimi K2.5** (最新)
- 多模态（视觉+文本）
- 256K上下文
- Thinking和非Thinking模式

### 4.2 核心能力

| 能力 | 规格 |
|------|------|
| 上下文 | **256K tokens** |
| 多模态 | K2.5原生支持 |
| 推理 | K2 Thinking，300+步工具调用 |
| 工具 | 原生ToolCalls，搜索/记忆/Excel/代码 |

### 4.3 基准测试 (Kimi K2) - **全球SOTA**

| 基准 | K2分数 | DeepSeek-V3 | Claude Sonnet 4 |
|------|--------|-------------|-----------------|
| LiveCodeBench v6 | **53.7%** | 46.9% | 48.5% |
| SWE-bench Agentic | **65.8%** | 38.8% | 72.7% |
| AIME 2024 | **69.6%** | 59.4% | 43.4% |
| MATH-500 | **97.4%** | 94.0% | 94.0% |

**编码、 数学、工具使用均为全球SOTA**

### 4.4 价格

| 模型 | 缓存命中 | 输入 | 输出 |
|------|----------|------|------|
| Kimi K2.5 | ¥0.70/MTok | ¥4/MTok | ¥21/MTok |
| Kimi K2 | ¥1/MTok | ¥4/MTok | ¥16/MTok |

### 4.5 开源与API

- **K2完全开源** (2025年7月)
- Apache 2.0许可
- HuggingFace: moonshotai/Kimi-K2-Instruct
- OpenAI + Anthropic双兼容API

---

## 五、MiniMax

### 5.1 最新旗舰模型

**MiniMax M2.7** (2025)
- "开启模型的自我进化"
- Agent Harness能力极强
- SWE-Pro 56.22%, VIBE-Pro 55.6%

**MiniMax M2.5** (早期旗舰)
- 编码/Agent SOTA，设计用于Agent Universe
- **SWE-Bench Verified: 80.2%**（行业最高之一）

### 5.2 核心能力

| 能力 | 规格 |
|------|------|
| 上下文 | 极长上下文（BrowseComp测试达1M） |
| 多模态 | 文本专用（其他模态独立模型） |
| 推理 | RL强化学习优化，任务分解 |
| 工具 | 原生工具调用，100+ TPS |
| Agent | Forge框架，Agent RL |

### 5.3 基准测试 (MiniMax M2.5)

| 基准 | 分数 |
|------|------|
| SWE-Bench Verified | **80.2%** |
| Multi-SWE-Bench | **51.3%**（行业最高） |
| BrowseComp | 76.3% |

### 5.4 独特卖点

- **Forge框架**: 原生Agent RL训练框架
- **极致性价比**: $0.3-1/小时连续Agent工作
- **自我进化**: 模型持续自我改进能力

### 5.5 价格

**订阅制** (含M2.7使用):
| 套餐 | 价格 | 请求数/5小时 |
|------|------|-------------|
| Starter | ¥29/月 | 600 |
| Plus | ¥49/月 | 1500 |
| Max | ¥119/月 | 4500 |

**API**: M2.5约$0.3/MTok输入，$2.4/MTok输出

### 5.6 开源

⚠️ **M2.5完全开源**，M2.7仅API

---

## 六、横向对比与配置建议

### 6.1 各模型优势总结

| 模型 | 第一优势 | 第二优势 | 推荐场景 |
|------|---------|---------|---------|
| **DeepSeek** | 性价比 | 推理(R1) | 成本敏感，深度推理任务 |
| **Qwen** | 超长上下文 | 多语言 | 多语言任务，长文档处理 |
| **GLM** | Agent工程 | 深度研究 | 企业Agent，自主研究 |
| **Kimi** | 编码SOTA | 数学SOTA | 编程任务，高难度数学 |
| **MiniMax** | Agent RL | SWE-bench | 软件工程，Agent自动化 |

### 6.2 oh-my-opencode 配置建议

基于调研结果，建议配置如下：

```json
{
  "model_routing": {
    "coding": {
      "primary": "kimi-k2.5",
      "reasoning": "deepseek-r1",
      "fallback": "qwen3"
    },
    "agent": {
      "primary": "minimax-m2.7",
      "secondary": "glm-5-turbo"
    },
    "research": {
      "deep_think": "glm-z1-rumination",
      "fast": "deepseek-v3"
    },
    "creative": {
      "primary": "qwen3"
    }
  },
  "context_requirements": {
    "minimax-m2.7": { "optimal": "128k", "max": "1m" },
    "kimi-k2.5": { "optimal": "128k", "max": "256k" },
    "qwen3": { "optimal": "128k", "max": "262k" },
    "deepseek-v3": { "optimal": "64k", "max": "128k" },
    "glm-5-turbo": { "optimal": "64k", "max": "128k" }
  }
}
```

### 6.3 关键发现

1. **2025是中国大模型开源元年**: Kimi K2、Qwen3、DeepSeek V3/R1、GLM-4-32B、MiniMax M2.5均已完全开源

2. **编码能力排名** (基于SWE-bench):
   - MiniMax M2.5: 80.2% 🥇
   - Kimi K2: 65.8% 🥈
   - GLM-4-32B: 30.7% 🥉

3. **性价比之王**: DeepSeek ($0.28/MTok输入)

4. **超长上下文**: Qwen3 (262K) > Kimi K2.5 (256K)

5. **API兼容性**: 全部支持OpenAI兼容API，方便迁移

---

## 信息来源

- [DeepSeek-V3 GitHub](https://github.com/deepseek-ai/DeepSeek-V3)
- [DeepSeek API文档](https://platform.deepseek.com/api-docs)
- [Qwen3 GitHub](https://github.com/QwenLM/Qwen3)
- [Kimi-K2 GitHub](https://github.com/MoonshotAI/Kimi-K2)
- [GLM HuggingFace](https://huggingface.co/THUDM)
- [MiniMax平台文档](https://platform.minimaxi.com/docs/guides/models-intro)
- [MiniMax M2.5 HuggingFace](https://huggingface.co/MiniMaxAI/MiniMax-M2.5)

---

*报告生成时间: 2026-04-05*
