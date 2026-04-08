#!/usr/bin/env python3
"""
L2 Reflector Agent (Trigger Script)
Instructs OpenCode-Builder to perform memory garbage collection directly on the file.
"""
import os
import sys
from opencode_client import OpenCodeClient
from datetime import datetime

WORKSPACE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
KNOWLEDGE_BASE = os.path.join(WORKSPACE, "periodic_jobs", "ai_heartbeat", "docs", "KNOWLEDGE_BASE.md")

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
   - skills/: 技术方法论、工作流、最佳实践
3. GC：重写 OBSERVATIONS.md，删除已晋升及过期 🟢 记录

晋升门槛：跨项目通用 + 多次验证 + 有明确适用场景
完成后回复简短晋升汇报。
"""

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

    print(f"Triggering Reflector using {provider_id}/{model_id}...")
    client = OpenCodeClient()

    session_id = client.create_session(f"Heartbeat L2 Reflector - {target_date}")
    if not session_id:
        print("Failed to create session")
        return

    print(f"Created session: {session_id}")

    prompt = PROMPT_TEMPLATE.format(kb_path=KNOWLEDGE_BASE, workspace=WORKSPACE)
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
