#!/usr/bin/env python3
"""
Session Log Scanner — extracts work session summaries from opencode SQLite DB.

Supplements observer.py's file-based scan by capturing conversation decisions,
architectural discussions, and technical judgments that leave no file trace.

DB: ~/.local/share/opencode/opencode.db
Schema used:
  session(id, title, directory, time_updated, ...)
  message(id, session_id, data JSON with role field)
  part(id, message_id, session_id, data JSON with type/text fields)
"""

import sqlite3
import json
from datetime import datetime, date
from pathlib import Path
from typing import Optional

DEFAULT_DB_PATH = Path.home() / ".local" / "share" / "opencode" / "opencode.db"

EXCLUDE_TITLE_PATTERNS = [
    "%subagent%",
    "Heartbeat%",
    "Autonomous%",
    "Daily AI News%",
    "Verify task completion%",
]

MAX_TEXT_CHARS_PER_PART = 2000
MAX_CHARS_PER_SESSION = 6000
MAX_TOTAL_CHARS = 20000


def _build_exclude_clause() -> tuple[str, list]:
    conditions = " AND ".join(f"s.title NOT LIKE ?" for _ in EXCLUDE_TITLE_PATTERNS)
    return conditions, list(EXCLUDE_TITLE_PATTERNS)


def _day_range_ms(target_date: date) -> tuple[int, int]:
    start = int(datetime(target_date.year, target_date.month, target_date.day, 0, 0, 0).timestamp() * 1000)
    end = int(datetime(target_date.year, target_date.month, target_date.day, 23, 59, 59).timestamp() * 1000) + 999
    return start, end


def scan_sessions(target_date: date, db_path: Optional[Path] = None) -> str:
    """
    Scan work sessions for target_date and return a formatted digest string.
    Returns empty string if no relevant sessions found or DB unavailable.
    """
    db_path = db_path or DEFAULT_DB_PATH

    if not db_path.exists():
        return ""

    start_ms, end_ms = _day_range_ms(target_date)
    exclude_clause, exclude_params = _build_exclude_clause()

    try:
        conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
        conn.row_factory = sqlite3.Row
    except sqlite3.OperationalError as e:
        print(f"[session_log_scanner] Cannot open DB: {e}")
        return ""

    try:
        query = f"""
            SELECT s.id, s.title, s.directory
            FROM session s
            WHERE s.time_updated BETWEEN ? AND ?
              AND {exclude_clause}
            ORDER BY s.time_updated DESC
        """
        params = [start_ms, end_ms] + exclude_params
        sessions = conn.execute(query, params).fetchall()

        if not sessions:
            return ""

        sections = []
        total_chars = 0

        for sess in sessions:
            if total_chars >= MAX_TOTAL_CHARS:
                break

            session_id = sess["id"]
            title = sess["title"]
            directory = sess["directory"]

            parts_query = """
                SELECT p.data
                FROM part p
                JOIN message m ON p.message_id = m.id
                WHERE p.session_id = ?
                  AND json_extract(p.data, '$.type') = 'text'
                  AND json_extract(m.data, '$.role') = 'assistant'
                  AND json_extract(p.data, '$.text') IS NOT NULL
                  AND length(json_extract(p.data, '$.text')) > 50
                ORDER BY p.time_created ASC
            """
            parts = conn.execute(parts_query, [session_id]).fetchall()

            if not parts:
                continue

            texts = []
            session_chars = 0
            for row in parts:
                try:
                    data = json.loads(row["data"])
                    text = data.get("text", "").strip()
                except (json.JSONDecodeError, KeyError):
                    continue

                if not text:
                    continue

                if len(text) > MAX_TEXT_CHARS_PER_PART:
                    text = text[:MAX_TEXT_CHARS_PER_PART] + "...[truncated]"

                texts.append(text)
                session_chars += len(text)

                if session_chars >= MAX_CHARS_PER_SESSION:
                    break

            if not texts:
                continue

            proj_name = Path(directory).name if directory and directory != "/" else "root"
            combined = "\n\n".join(texts)
            section = (
                f"### Session: {title}\n"
                f"Project: {proj_name} ({directory})\n\n"
                f"{combined}"
            )

            sections.append(section)
            total_chars += len(section)

        if not sections:
            return ""

        header = (
            f"## Session Log Digest — {target_date.isoformat()}\n"
            f"以下是当日 {len(sections)} 个工作 session 的 AI 回复摘要，"
            f"供你提炼决策性内容写入 OBSERVATIONS.md。\n"
            f"（已过滤自动化/subagent sessions）\n\n"
        )
        return header + "\n\n---\n\n".join(sections)

    finally:
        conn.close()


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Scan opencode session logs for a given date")
    parser.add_argument("date", nargs="?", default=date.today().isoformat(), help="Target date YYYY-MM-DD")
    parser.add_argument("--db", default=None, help="Path to opencode.db")
    parser.add_argument("--stats", action="store_true", help="Show stats only")
    args = parser.parse_args()

    target = date.fromisoformat(args.date)
    db_path = Path(args.db) if args.db else None

    result = scan_sessions(target, db_path)

    if not result:
        print(f"No work sessions found for {target.isoformat()}")
        return

    if args.stats:
        print(f"Date: {target.isoformat()}")
        print(f"Sessions: {result.count('### Session:')}")
        print(f"Total chars: {len(result)}")
        print(f"Lines: {result.count(chr(10))}")
    else:
        print(result)


if __name__ == "__main__":
    main()
