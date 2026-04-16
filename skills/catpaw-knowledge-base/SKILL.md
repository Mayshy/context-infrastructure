---
name: ckb
description: "Manage and search CatPaw knowledge bases through the `ckb` CLI. Use when the user wants to list, inspect, create, update, or search KBs, or mentions 知识库管理, knowledge-base CRUD/search operations, KB management, 知识库搜索, 知识库检索, knowledge base name, docId, docKey, or `ckb`."
---

# CKB — CatPaw Knowledge Base CLI

Use the `/app/skills/catpaw-knowledge-base/ckb` CLI to manage and search CatPaw knowledge bases. Authentication, preflight validation, and error handling are built into the CLI — the agent should call the CLI and interpret its output, not reimplement these flows.

## Command reference

Run `/app/skills/catpaw-knowledge-base/ckb help` to see all available commands. This is always up to date.

## ID resolution

`detail`, `update`, and `search` require a KB identifier (`--doc-id` or `--doc-key`), but users usually refer to a KB by name. The agent is responsible for resolving identifiers:

1. If the user already provided a `docId` or `docKey` from earlier output, reuse it directly.
2. If the user provided a KB name or keyword, run `/app/skills/catpaw-knowledge-base/ckb list`, match `displayTitle` in the output, then extract `ID` (for `--doc-id`) or `DocKey` (for `--doc-key`).
3. If the user did not specify a KB, run `/app/skills/catpaw-knowledge-base/ckb list` and infer the best match from context. Prefer `INDEXED` KBs for search.
4. Only ask the user when multiple matches remain genuinely ambiguous.

Never fabricate identifiers. `docId` and `docKey` must come from actual CLI output. If a previous `list` call in the current turn already contains the target KB, reuse that ID directly.

## Authentication & misId fallback

The CLI authenticates by reading the user's misId (the `X-User-Id` header) from the OpenClaw context file (`/root/.openclaw/openclaw.json`). Authentication will fail with an error containing `"请向用户询问 misId"` when the file is absent, unreadable, or does not contain the `X-User-Id` field.

When this happens:

1. Ask the user for their misId (MIS 号).
2. Set the `CATPAW_MIS_ID` environment variable with the value they provide, then rerun the command. For example:
   ```bash
   CATPAW_MIS_ID="zhangsan" /app/skills/catpaw-knowledge-base/ckb list
   ```
3. The CLI will use this environment variable as a fallback — it still prefers the file-based source when available.

Do not hard-code or cache the misId outside of a single command invocation. If the user provides a misId, use it consistently for all subsequent commands in the same conversation by always setting `CATPAW_MIS_ID`.

## Search result handling

For `/app/skills/catpaw-knowledge-base/ckb search`, synthesize the returned content chunks into a coherent answer for the user. Cite source URLs when available. Never paste raw search chunks or raw JSON unless the user explicitly asks.

## Output handling

The CLI defaults  defaults to human-readable text output. Do not pass `--output json` unless the user explicitly wants raw JSON. Interpret and summarize CLI results for the user.

## Unsupported operations

Deleting a KB, removing a base URL, or removing specific sub-documents is not supported via CLI. Direct the user to:

- [管理平台](https://catpaw.sankuai.com/docs/manager)
- [操作手册](https://km.sankuai.com/collabpage/2717287519)

## Common patterns

```bash
# List all visible KBs (user-facing)
/app/skills/catpaw-knowledge-base/ckb list

# Resolve KB by name, then get detail
/app/skills/catpaw-knowledge-base/ckb list
/app/skills/catpaw-knowledge-base/ckb detail --doc-id 123

# Create a KB with source URLs
/app/skills/catpaw-knowledge-base/ckb create --name "ABC Docs" --url "https://km.sankuai.com/page/abc"

# Create an empty KB
/app/skills/catpaw-knowledge-base/ckb create --name "ABC Docs"

# Resolve KB by name, then update metadata
/app/skills/catpaw-knowledge-base/ckb list
/app/skills/catpaw-knowledge-base/ckb update --doc-key "uuid-from-list" --name "New Title"

# Resolve KB by name, then search
/app/skills/catpaw-knowledge-base/ckb list
/app/skills/catpaw-knowledge-base/ckb search --doc-key "uuid-from-list" --query "如何配置认证"
```