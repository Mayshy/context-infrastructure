#!/Users/shenhuayu/.config/opencode/.venv/bin/python
import os
import sys
import time
from datetime import datetime, date, timedelta
from opencode_client import OpenCodeClient
from session_log_scanner import scan_sessions

DEFAULT_PROVIDER = "meituan"
DEFAULT_MODEL = "claude-sonnet-4-6"
DEFAULT_AGENT = "oracle"

WORKSPACE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
KNOWLEDGE_BASE = os.path.join(WORKSPACE, "periodic_jobs", "ai_heartbeat", "docs", "KNOWLEDGE_BASE.md")
OBSERVATIONS_PATH = os.path.join(WORKSPACE, "contexts", "memory", "OBSERVATIONS.md")

PROMPT_TEMPLATE = """
【目标】：执行观测记忆提取并直接持久化到磁盘。
【基准日期】：{target_date}

【幂等性约束】：在执行任何写入前，**必须先**读取 OBSERVATIONS.md，检查是否已存在 `Date: {target_date}` 的条目。若存在，则**不要进行任何文件修改**，直接回复「Entry for {target_date} already exists, skipping」即可。

【SOP 路径】：
{kb_path}

【工作区路径】：
{workspace}

【任务内容】：
1. **获取 Context**：请阅读上述 SOP 以及其中引用的 L3 约束文件。
2. **幂等性检查**：读取 OBSERVATIONS.md，若已有 `Date: {target_date}` 则跳过后续步骤。
3. **扫描与过滤**：自主扫描根目录（{workspace}）下的变动。
4. **Session 日志摘要**（额外信息源）：以下是当日 opencode session 的 AI 回复摘要，包含 file-based 扫描无法捕获的对话决策、架构讨论、技术判断。请结合文件变动和这些 session 内容，提炼更完整的观测记录。
{session_digest}
5. **写入记忆**：将针对 {target_date} 的 🔴 🟡 🟢 观测结果直接写入或追加到 `{observations_path}`。**鼓励使用命令行 append**（如 `echo "..." >> OBSERVATIONS.md` 或 `tee -a`），避免对大文件做全文编辑。
6. **KB 健康度检查**（新增）：扫描 `{workspace}/contexts/projects/` 下所有项目 KB，执行以下检查：
   a. 若当日 session 涉及某个项目的代码变更、踩坑或架构讨论，检查对应 KB 中是否已记录：
       - 踩坑 → 是否已追加到对应服务的 `01_services/<service>/gotchas.md`
      - 架构决策 → 是否已创建 ADR 到 `03_requirements/decisions/`
   b. 扫描各 KB 的 `AGENTS.md` 维护历史，找出"下一步"中超过 14 天未处理的待办项，在 OBSERVATIONS.md 中用 🟡 标注（格式：`🟡 KB 待办逾期：<kb名>/<待办内容>，<天数>天未处理`）。
   c. 若发现 KB 中存在内容明显过时的 `[TODO: 需更新]` 标注，在 OBSERVATIONS.md 中用 🟢 标注提醒。
   **注意**：此步骤只做检查和记录，不直接修改 KB 文件。KB 修改由 AI 在对话中主动完成。
7. **范围约束**：**仅执行 L1 Observer 任务**。不要执行 SOP 中提到的 L2 Reflector 任务（即不要修改 `rules/` 下的任何文件，不要进行规则晋升或垃圾回收）。
8. **格式规范**：
   - 日期 Header 必须严格使用 `Date: YYYY-MM-DD` 格式（Date 首字母大写，冒号后空格，日期为 ISO 格式）。
   - 在结果文件中提到任何文件或目录时，**必须使用相对于根目录的完整路径**（例如：`rules/skills/workflow_deep_research_survey.md`），不要只写文件名。
9. **汇报**：完成后，在此回复一个简短的 Walkthrough，说明从 session 日志中提炼了哪些内容（如有），以及 KB 健康度检查结果（发现了哪些逾期待办或 TODO）。
"""

def main():
    import argparse
    from dotenv import load_dotenv
    
    parser = argparse.ArgumentParser(description='L1 Observer Agent')
    parser.add_argument('date', nargs='?', default=(datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
                        help='Target date (YYYY-MM-DD), defaults to yesterday')
    parser.add_argument('--model', default=None,
                        help='Model ID to use (format: provider/model-id, default: minimax/MiniMax-M2.7)')
    parser.add_argument('--no-delete', action='store_true',
                        help='Keep session after completion (default: delete)')
    args = parser.parse_args()

    target_date = args.date
    delete_after = not args.no_delete

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

    if os.path.exists(OBSERVATIONS_PATH):
        with open(OBSERVATIONS_PATH, "r", encoding="utf-8") as f:
            content = f.read()
        if f"Date: {target_date}" in content:
            print(f"Idempotent skip: entry for {target_date} already exists in OBSERVATIONS.md")
            return

    print(f"Scanning session logs for {target_date}...")
    try:
        target_date_obj = datetime.strptime(target_date, "%Y-%m-%d").date()
        session_digest = scan_sessions(target_date_obj)
        if session_digest:
            digest_lines = session_digest.count('\n')
            print(f"  Session digest: {len(session_digest)} chars, {digest_lines} lines")
        else:
            print("  No work sessions found for this date")
            session_digest = "(当日无工作 session 记录)"
    except Exception as e:
        print(f"  Session scan failed (non-fatal): {e}")
        session_digest = "(session 日志扫描失败，跳过)"

    print(f"Triggering Observer for date: {target_date} using {provider_id}/{model_id}...")

    client = OpenCodeClient()

    session_id = client.create_session(f"Heartbeat L1 - {target_date}")
    if not session_id:
        print("Failed to create session")
        return

    print(f"Created session: {session_id}")

    prompt = PROMPT_TEMPLATE.format(
        kb_path=KNOWLEDGE_BASE,
        target_date=target_date,
        workspace=WORKSPACE,
        observations_path=OBSERVATIONS_PATH,
        session_digest=session_digest,
    )

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
