#!/Users/shenhuayu/.config/opencode/.venv/bin/python
"""
L2 Reflector Agent (Trigger Script)
Instructs OpenCode-Builder to perform memory garbage collection directly on the file.
"""
import os
import sys
from opencode_client import OpenCodeClient
from datetime import datetime, timedelta

WORKSPACE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
KNOWLEDGE_BASE = os.path.join(WORKSPACE, "periodic_jobs", "ai_heartbeat", "docs", "KNOWLEDGE_BASE.md")
OBSERVATIONS_PATH = os.path.join(WORKSPACE, "contexts", "memory", "OBSERVATIONS.md")
ARCHIVE_DIR = os.path.join(WORKSPACE, "contexts", "memory", "archive")
SKILLS_DRAFTS_DIR = os.path.expanduser("~/.config/opencode/skills/__drafts__")

ARCHIVE_LINE_THRESHOLD = 200

PROMPT_TEMPLATE = """
执行记忆系统的"反思与晋升"任务。

SOP: {kb_path}

步骤：
1. 读取 {workspace}/contexts/memory/OBSERVATIONS.md，分析 🔴 和高优 🟡 条目
2. 将具有普适性的内容晋升到 rules/，按职责边界分类：
   - SOUL.md: Agent 身份与核心价值观
   - USER.md: 用户画像与人生哲学
   - COMMUNICATION.md: 沟通风格（仅限沟通，不含技术知识）
   - WORKSPACE.md: 目录路由
   - rules/workflows/: 技术方法论、工作流、最佳实践
3. GC：重写 OBSERVATIONS.md，删除已晋升及过期 🟢 记录
4. Skill 草稿生成（详见 SOP 4.4 节）：
   - 扫描所有 🔴 High 条目，识别满足以下条件的晋升候选：
     a) 同一主题在 ≥2 个不同日期出现（语义相似即算）
     b) 具有跨 session 可复用价值，适合编码为操作指南
     c) ~/.config/opencode/skills/ 下尚无覆盖该主题的 skill（关键词快速匹配判断）
   - 对每个候选，在 {skills_drafts_dir} 目录写入草稿文件
   - 草稿命名：DRAFT_YYYYMMDD_<topic-slug>.md（YYYYMMDD 为今日日期）
   - 草稿格式参照现有 skill SKILL.md（YAML frontmatter + 触发场景 + 核心知识 + 操作指南 + 来源条目）
   - 不自动发布到正式 skills 目录，只写 __drafts__/

晋升门槛：跨项目通用 + 多次验证 + 有明确适用场景

完成后**必须执行以下两步**：
5. 将本次执行的完整汇报 summary 写入文件 `{summary_path}`，格式如下：
   ```
   # Reflector Summary — {target_date}

   ## 晋升内容
   （列出晋升到 rules/ 的条目，或"无"）

   ## GC 结果
   （删除了哪些条目，OBSERVATIONS.md 从 N 行减少到 M 行）

   ## Skill 草稿
   （生成了哪些草稿文件，或"无候选"）

   ## 备注
   （其他说明）
   ```
6. 在 Chat 中回复上述 summary 的简短版本（格式见 SOP 6 节）。
"""

ARCHIVE_ADDON = """

【额外任务：归档已解决事件】

当前 OBSERVATIONS.md 已超过 {threshold} 行（当前 {current_lines} 行），需执行去重聚合归档。

**判断标准**：对每一条 🔴/🟡 条目，判断它描述的问题或事件是否已在后续条目中明确解决、修复或完结。若是，则该条目及其对应的"解决"条目均属于"已完结事件"，可以归档。

**归档规则**：
- 归档目标目录：`{archive_dir}/`
- 文件命名：按自然周归档，文件名为该周**周一**日期，格式 `YYYY-MM-DD.md`（例如 2026-04-13.md 代表 4月13日那一周）
- 若目标文件已存在，追加内容；若不存在，新建并写入标题 `# Archive: week of YYYY-MM-DD`
- 归档内容保留原始格式（含日期 Header 和 🔴🟡🟢 标记），不做摘要压缩

**不可归档的条目**：
- 仍然有效的约束（如"Jackson 2.17.0 有内存泄漏，必须用 2.17.2"这类永久生效的技术约束）
- 尚未解决的问题
- 项目状态类条目（项目仍在进行中）

**执行顺序**：先完成步骤1-3（晋升+GC），再执行归档。归档后，从 OBSERVATIONS.md 中删除已归档条目。

归档汇报：说明归档了哪些事件、写入哪个文件、OBSERVATIONS.md 减少了多少行。
"""


def get_observations_line_count():
    if not os.path.exists(OBSERVATIONS_PATH):
        return 0
    with open(OBSERVATIONS_PATH, "r", encoding="utf-8") as f:
        return sum(1 for _ in f)


def get_week_monday(d: datetime) -> str:
    monday = d - timedelta(days=d.weekday())
    return monday.strftime("%Y-%m-%d")

DEFAULT_PROVIDER = "meituan"
DEFAULT_MODEL = "claude-sonnet-4-6"
DEFAULT_AGENT = "oracle"

def main():
    import argparse
    from dotenv import load_dotenv

    parser = argparse.ArgumentParser(description='L2 Reflector Agent')
    parser.add_argument('--model', default=None,
                        help='Model ID to use (format: provider/model-id, default: minimax/MiniMax-M2.7)')
    parser.add_argument('--no-delete', action='store_true',
                        help='Keep session after completion (default: delete)')
    parser.add_argument('--threshold', type=int, default=ARCHIVE_LINE_THRESHOLD,
                        help=f'Line count threshold to trigger archiving (default: {ARCHIVE_LINE_THRESHOLD})')
    args = parser.parse_args()

    delete_after = not args.no_delete
    target_date = datetime.now().strftime("%Y-%m-%d")

    if args.model and "/" in args.model:
        provider_id, model_id = args.model.split("/", 1)
        agent = None
    else:
        provider_id = DEFAULT_PROVIDER
        model_id = args.model or DEFAULT_MODEL
        agent = DEFAULT_AGENT

    dotenv_path = os.path.join(WORKSPACE, ".env")
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path)

    current_lines = get_observations_line_count()
    needs_archive = current_lines >= args.threshold
    print(f"OBSERVATIONS.md: {current_lines} lines (threshold: {args.threshold}) -> archive: {needs_archive}")

    os.makedirs(SKILLS_DRAFTS_DIR, exist_ok=True)
    os.makedirs(ARCHIVE_DIR, exist_ok=True)
    summary_path = os.path.join(ARCHIVE_DIR, f"reflector-{target_date}.md")
    prompt = PROMPT_TEMPLATE.format(
        kb_path=KNOWLEDGE_BASE,
        workspace=WORKSPACE,
        skills_drafts_dir=SKILLS_DRAFTS_DIR,
        summary_path=summary_path,
        target_date=target_date,
    )
    if needs_archive:
        os.makedirs(ARCHIVE_DIR, exist_ok=True)
        week_monday = get_week_monday(datetime.now())
        archive_file = os.path.join(ARCHIVE_DIR, f"{week_monday}.md")
        prompt += ARCHIVE_ADDON.format(
            threshold=args.threshold,
            current_lines=current_lines,
            archive_dir=ARCHIVE_DIR,
            archive_file=archive_file,
            week_monday=week_monday,
        )

    print(f"Triggering Reflector using {provider_id}/{model_id}...")
    client = OpenCodeClient()

    session_id = client.create_session(f"Heartbeat L2 Reflector - {target_date}")
    if not session_id:
        print("Failed to create session")
        return

    print(f"Created session: {session_id}")

    print("Sending prompt via prompt_async...")
    ok = client.prompt_async(session_id, prompt, provider_id=provider_id, model_id=model_id, agent=agent)
    if not ok:
        print("Failed to send prompt")
        if delete_after:
            client.delete_session(session_id)
        return

    print("Waiting for session to complete (this may take several minutes)...")
    if client.wait_for_session_complete(session_id, poll_interval=30, max_wait=7200):
        print("Session completed successfully")
    else:
        print("Session did not complete within timeout")

    if delete_after:
        client.delete_session(session_id)
        print(f"Session {session_id} deleted")
    else:
        print(f"Session {session_id} retained")

if __name__ == "__main__":
    main()
