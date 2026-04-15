# Semantic Search 配置与原理总结

> 创建时间：2026-04-11  
> 背景：本 session 中完成了 semantic_search 工具的 Friday API 适配，并理解了向量搜索原理

---

## 1. 整体工作流

### 构建阶段（增量，有缓存）

```
--file-list 中的文件
  ↓
对每个文件查 manifest.json
  ├── 文件不在 manifest → 新文件，调远程接口向量化，写入缓存
  ├── 文件在 manifest，mtime 变了 → 文件有更新，重新向量化，更新缓存
  └── 文件在 manifest，mtime 没变 → 直接读 .npy，不调接口
  ↓
每 50 个文件保存一次索引（断点续传）
```

### 查询阶段（每次查询）

```
查询文本
  → 调 Friday embedding API → 得到 1 个查询向量 [1024 维]
  → 与 .knowledge_cache/embeddings.npy 中所有向量做余弦相似度
  → 取 top-k 最高分的 chunk
  → 输出原文 + 来源文件路径
```

### 缓存文件结构

```
~/.config/opencode/.knowledge_cache/
  ├── embeddings.npy    # 所有 chunk 的向量矩阵 [N × 1024]，float32
  ├── chunks.pkl        # chunk 原文 + 来源文件路径
  └── manifest.json     # 文件路径 → mtime 映射，用于增量更新判断
```

---

## 2. 向量搜索原理

### 为什么美团 embedding 模型也能正确搜索？

Embedding 模型的本质是把文本映射到高维向量空间，使**语义相近的文本在空间中距离更近**。这个规律来自语言本身的统计规律，不是某家公司特有的。

- OpenAI `text-embedding-ada-002`：「厨艺」和「烹饪」在空间中很近
- 美团 `text-embedding-miffy-002`：「厨艺」和「烹饪」在空间中也很近

**不同模型的向量空间彼此不兼容**（维度不同、坐标系不同），但在**同一个模型内部**，语义相近 = 向量相近这个规律成立。跨模型混用索引会导致搜索失效。

### 为什么用余弦相似度而不是欧氏距离？

余弦相似度只看**方向**，不看长度。同一个意思，长句和短句的向量长度不同，但方向相近。

```
相似度 = (A · B) / (|A| × |B|)    值域 [-1, 1]，越接近 1 越相似
```

### 为什么叫 brute force？

当前实现是全量扫描：查询向量和缓存里每一个 chunk 向量都算一遍余弦相似度，然后排序取 top-k。

- 几百到几千个 chunk → 毫秒级，brute force 完全够用
- 百万级 chunk → 需要换 FAISS / Annoy 等近似最近邻（ANN）索引，用树结构或量化压缩换速度（牺牲一点精度）

---

## 3. Friday API 限制与适配

| 限制项 | 具体值 | 应对方式 |
|--------|--------|----------|
| 单批次最大条数 | 4 | `batch_size=4` |
| 单条文本最大长度 | 1024 字符 | 代码截断到 1000 字符 |
| QPM 限流 | 触发返回 429 | 指数退避重试，最多 5 次（1s/2s/4s/8s/16s） |
| 并发限制 | 多 worker 易触发 429 | 建议 `--workers 1` |

**API 配置：**
- Endpoint：`https://aigc.sankuai.com/v1/openai/native`
- Model：`text-embedding-miffy-002`
- Auth：`Authorization: Bearer <FRIDAY_APP_ID>`
- AppId：`21909074838413869060`（存于 `~/.config/opencode/.env`）

---

## 4. 本次对 semantic_search 脚本的变更

### `tools/semantic_search/search/embedding.py`（完全重写）

- 用 `requests` 替换 OpenAI SDK（Python 3.14 + httpx 跨线程不安全问题）
- `batch_size` 从 32 → 4（Friday API 限制）
- 文本截断到 1000 字符（Friday API 单条长度限制）
- 新增 `self.base_url` / `self.api_key` 属性供线程复用
- 加入 429 限流重试（指数退避，最多 5 次）
- 默认 `base_url="https://aigc.sankuai.com/v1/openai/native"`
- 默认 `model="text-embedding-miffy-002"`

### `tools/semantic_search/search/cli.py`

- 默认 `--endpoint` 改为 Friday URL
- 默认 `--model` 改为 `text-embedding-miffy-002`
- `process_file` 函数内独立创建 `EmbeddingClient`（避免 httpx 跨线程复用导致崩溃）

### `.env`

- 新增 `FRIDAY_APP_ID=21909074838413869060`

### `.venv`

- 在 `~/.config/opencode/` 创建了 Python 虚拟环境
- 安装依赖：`openai`, `numpy`, `tqdm`, `pyyaml`, `requests`

---

## 5. 当前向量化覆盖范围

### 已建索引（14 个文件，截至 2026-04-11）

```
contexts/survey_sessions/
  ├── superpowers_vs_oh_my_openagent_20260409.md
  ├── iterm2_terminal_ai_survey_20260405.md
  ├── unix_file_read_cmd.md
  ├── spine_protection_survey_20260406.md
  ├── oh_my_openagent_survey_20260405.md
  ├── chinese_llm_survey_20260405.md
  ├── datamatrix_kb_selection_20260405.md
  └── macos_terminal_ai_dev_survey_20260405.md

contexts/memory/
  └── OBSERVATIONS.md
```

> 注：manifest.json 中同一文件存在相对路径和绝对路径两份记录（历史遗留），实际向量内容相同，可忽略。

### 未建索引（尚未向量化）

```
contexts/draft/
  └── datamatrix_migrate.md

contexts/projects/datamatrix-kb/    （31 个文件）
  ├── 00_overview/   architecture.md, service_map.md, tech_stack.md
  ├── 01_services/   athena, hermes, kugget, pontos, worksheet 的 design.md
  ├── 02_km_summaries/  9 个文件
  ├── 03_requirements/  product_backlog.md
  ├── 04_cross_cutting/ data_lineage.md, eagle_integration.md
  ├── 05_runbooks/  es_index_ops.md, spark_flink_debug.md
  ├── 06_migration/ 8 个文件
  └── AGENTS.md

contexts/projects/poros-kb/         （13 个文件）
  ├── 00_overview/   architecture.md, module_map.md, tech_stack.md
  ├── 01_modules/    5 个 design.md
  ├── 02_km_summaries/ es7_compat_es8.md, poros_java_api_client.md, INDEX.md
  ├── 03_features/   circuit_breaker.md, dsl_filter.md, high_risk_query_throttle.md
  └── AGENTS.md
```

### 建完整索引的命令

```bash
cd ~/.config/opencode
source .venv/bin/activate
export FRIDAY_APP_ID=21909074838413869060

# 生成全量文件列表（排除 AGENTS.md / INDEX.md 等纯目录文件，可按需调整）
find contexts -name "*.md" \
  ! -name "AGENTS.md" \
  ! -name "INDEX.md" \
  ! -name "README.md" \
  > /tmp/all_search_files.txt

# 建索引 + 查询（--workers 1 避免 429）
python tools/semantic_search/main.py \
  --file-list /tmp/all_search_files.txt \
  --query "你的查询" \
  --top-k 5 \
  --workers 1 \
  --cache-dir .knowledge_cache
```

> 第一次全量建索引约需 10-20 分钟（受 Friday API QPM 限制）。之后未修改的文件不重新向量化。

---

## 6. 待办事项

- [ ] 把 `FRIDAY_APP_ID` 写入 `~/.zshrc`，避免每次手动 export
- [ ] 跑一次全量索引，覆盖 projects/ 下的 44 个文件
- [ ] 考虑在 SOUL.md 中增加语义搜索触发规则（涉及用户知识库时自动调用）
