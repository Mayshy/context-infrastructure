---
name: release-notes-updater
description: >
  Update a 学城 (km.sankuai.com) release notes document by reading a git commit range,
  extracting version changes from pom.xml, classifying commits into new features vs bugfix/notes,
  and prepending a new table row. Supports local repo paths and remote SSH paths.
  Use when: user says "更新 release notes", "把最近的变更写进 release notes", "把这段 commit 同步到文档",
  or provides a git range (e.g. HEAD~20..HEAD, v0.0.8..HEAD) alongside a km doc link.
---

# Release Notes Updater

Update a 学城 release notes document from a git commit range. Prepends a new row to the existing
table. **Never modifies existing rows unless the user explicitly asks.**

## Inputs

Collect from user before starting:

| Input | Required | Notes |
|-------|----------|-------|
| Git repo | ✅ | Local path (e.g. `~/Desktop/Project/pontos`) or remote SSH URL (`ssh://git@host/org/repo.git`) |
| Commit range | ✅ | e.g. `HEAD~20..HEAD`, `abc123..def456`, `v0.0.8..HEAD` |
| KM doc contentId | ✅ | From `km.sankuai.com/collabpage/<id>` |
| Time range label | optional | e.g. `2026.04.01 ～ 2026.04.30`; if omitted, infer from commit dates |

## Step 1 — Fetch git log

**Local repo:**
```bash
git -C <repo_path> log --oneline <range>
```

**Remote SSH repo** (clone to temp dir first):
```bash
TMPDIR=$(mktemp -d)
git clone --no-checkout --depth=200 <ssh_url> $TMPDIR/repo
git -C $TMPDIR/repo log --oneline <range>
```

## Step 2 — Extract version changes from pom.xml

Read the root `pom.xml` and each module's `pom.xml` to get current versions. Compare with the
versions already listed in the KM doc (read via `getDocumentCitadelMd`) to compute the diff.

```bash
# Root pom
grep -E '<version>|<artifactId>' <repo_path>/pom.xml | head -20

# Each module
for dir in <repo_path>/*/; do
  pom="$dir/pom.xml"
  [ -f "$pom" ] && echo "=== $(basename $dir) ===" && grep -m2 '<artifactId>\|<version>' "$pom"
done
```

If the project is not Maven-based, adapt to the relevant build file (e.g. `build.gradle`, `package.json`).

## Step 3 — Classify commits

For each commit, classify as:

- **新功能** — new capability, new interface, new config option, new algorithm, new behavior
- **BugFix / 注意事项** — fix, bugfix, npe, null, 修复, 兼容, 权限, 安全, 回退
- **Skip** — version bump only, merge commit with no substance, test-only, log-only, CI config

Use **semantic understanding**, not prefix matching. A commit like "改造完成" that touches core
logic is a feature; "增加测试日志行" is skippable.

When multiple commits implement the same logical change (iterative development), pick the
**final, cleanest commit hash** as the representative link.

## Step 3.5 — Gather detailed commit information (CRITICAL)

**This step is mandatory for all 新功能 and BugFix commits.** Without detailed commit info,
the generated release notes will be shallow and unhelpful.

For each significant commit (exclude Skip commits), fetch:

```bash
git -C <repo_path> show <commit_hash> --stat --format="%s%n%b"
```

**Example output:**
```
commit 21ce977d80b27b8161b964ca3e2712bad9dca532
Author: ludongyu <ludongyu@meituan.com>
Date:   Thu Jan 29 19:22:27 2026 +0800

    feature: support embedding batch process

 .../domain/embedding/CompositeEmbeddingClient.java | 52 +++++++++++++++++++-
 .../embedding/CustomHttpEmbeddingClient.java       | 23 +++++++--
 .../job/domain/embedding/EmbeddingClient.java      |  6 +++
 .../job/domain/embedding/EmbeddingHttpClient.java | 57 +++++++++++++++++++---
 .../domain/embedding/FridayEmbeddingClient.java    | 26 ++++++++--
 .../embedding/impl/EmbeddingModelServiceImpl.java |  2 +-
 6 files changed, 148 insertions(+), 18 deletions(-)
```

**Batch process multiple commits efficiently:**
```bash
for commit in <commit_hash_1> <commit_hash_2> ...; do
  echo "=== $commit ==="
  git -C <repo_path> show $commit --stat --format="%s%n%b" | head -30
  echo
done
```

**What to extract from `--stat`:**
- **File names** → understand which components changed
- **Line numbers** (`+XX/-XX`) → understand impact scale
- **Class/method names** → understand what was modified

## Step 4 — Compose detailed descriptions

**The goal is informative, detailed descriptions — not one-liners.**

Each entry should explain:
1. **What changed** — specific files, classes, methods
2. **How it works** — implementation approach
3. **Scale** — lines of code, number of files affected
4. **Why it matters** — business or technical value

### Description writing rules

**For 新功能 (New Features):**
```
**① Feature title** [[hash](url)]
详细描述（2-4句）：
- 具体修改了哪些类/方法（文件名 + 类名）
- 如何实现的（核心逻辑）
- 影响范围（涉及多少文件、多少行代码）
- 对业务的价值或意义
```

**For BugFix (Bug Fixes):**
```
① 修复描述 [[hash](url)]
修复的问题说明：
- 修复了哪个类/方法的什么问题
- 触发条件和影响范围
- 修复方案
```

**Bad example (too shallow):**
```
**① Embedding batch support** [[21ce977d](url)]
支持 batch process。
```

**Good example (detailed, informative):**
```
**① Embedding Batch 处理能力** [[21ce977d](https://git.sankuai.com/org/repo/commits/21ce977d)]
`CompositeEmbeddingClient`、`CustomHttpEmbeddingClient`、`FridayEmbeddingClient` 等多个 EmbeddingClient
实现类新增 batch process 支持。`EmbeddingClient.java` 接口新增方法定义，`EmbeddingHttpClient.java`
支持异步批量请求。共涉及 6 个文件，148 行新增代码，显著提升 embedding 批量处理效率。
```

### Commit link format

Derive the HTTPS web URL from the SSH remote:
```
ssh://git@git.sankuai.com/arts-repo/dataserver.git → https://git.sankuai.com/arts-repo/dataserver
```

Format: `[[<short_hash>](https://git.sankuai.com/<org>/<repo>/commits/<short_hash>)]`

### 版本变化 cell

Only list modules whose version actually changed:
```
**common** 0.0.7 → **0.0.9**

**dal** 0.0.6 → **0.0.7**
```

If no version changed: `版本无变化` or describe the upgrade that happened (e.g., "realtime-job 升级 dataserver-dal 包至 0.0.6")

### 更新时间 cell

```
:[font]{size=14}2026.04.01 ～ 2026.04.30[/font]
```
If the user didn't provide a time range, use the date of the oldest and newest commit in the range.

## Step 5 — Insert into document

1. `oa-skills citadel getDocumentCitadelMd --contentId <id> --output /tmp/rn_update.citadelmd`
2. Parse the `:::table{...}` block; find the end of the header row (first `[...]` sub-array)
3. Insert the new data row **immediately after the header row** (before any existing data rows)
4. Validate the full JSON block is parseable with Python before writing
5. `oa-skills citadel convertMdToJson --file /tmp/rn_update.citadelmd` — confirm no errors
6. `oa-skills citadel updateDocumentByMd --contentId <id> --file /tmp/rn_update.citadelmd`

**Safety rules (non-negotiable):**
- Never modify, reorder, or delete any existing table rows
- Never change the header row
- Never change the document title or version list at the top (unless user explicitly asks)
- If the doc has no table yet, create one with the standard 4-column format — see `references/table-template.md`

## JSON safety rules (CitadelMD gotchas)

- Escape straight ASCII `"` inside content values: `\"双写\"` not `"双写"`
- `colwidth` must use expanded multiline format: `[\n  68\n]` not `[68]`
- `numCell` must be `0` or `null`; never `true`/`false` in header cells
- Content strings support full CitadelMD inline syntax: `**bold**`, `` `code` ``, `[text](url)`
- After editing, always validate with Python `json.loads()` before submitting

## Common pitfalls to avoid

1. **Don't use commit subject as description** — commit messages like "fix bug" or "update" are useless
   without context. Always `git show --stat` to understand the actual change.

2. **Don't group unrelated commits** — each logical feature should be its own entry with its own
   description. If 3 commits are all part of the same feature, pick the representative commit.

3. **Don't skip Step 3.5** — it's not optional. Shallow descriptions are the #1 complaint about
   release notes. The `--stat` output reveals the actual code change, which is what matters.

4. **Don't invent technical details** — if you don't understand what a commit does from reading the
   `--stat` output, say so and write a generic but accurate description. Don't make up class names
   or implementation details.

## Full example output

**Input:** 30 commits from HEAD~30..HEAD in a modelserver project

**New row content should look like:**

| 版本变化 | 新功能 | BugFix | 更新时间 |
|---------|--------|--------|---------|
| realtime-job 升级 dataserver-dal 至 0.0.6 | **① Embedding Batch 处理能力** [[21ce977d](url)] `CompositeEmbeddingClient` 等多个 client 新增 batch 支持... | **① TimestampFormatter 参数优化** [[a1ba9d71](url)] 解决时间戳限制过长问题... | 2025.10.23 ～ 2026.03.30 |

See `references/table-template.md` for a complete copy-pasteable new row template and the
standard 4-column header structure.