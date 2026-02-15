#!/usr/bin/env python3
"""列出待分析的 raw-docs 文件，支持按日期/hash 过滤。"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

def _find_project_root() -> Path:
    """从脚本位置向上查找包含 data/ 目录的项目根目录。"""
    current = Path(__file__).resolve().parent
    for _ in range(10):
        if (current / "data").is_dir():
            return current
        current = current.parent
    raise RuntimeError("无法找到项目根目录（未找到 data/ 目录）")


PROJECT_ROOT = _find_project_root()
DATA_DIR = PROJECT_ROOT / "data"
URLS_DIR = DATA_DIR / "urls"
RAW_DOCS_DIR = DATA_DIR / "raw-docs"


def find_pending(date_str: str | None = None, status_filter: str = "fetched") -> list[dict]:
    """
    查找指定状态的条目。

    Args:
        date_str: 指定日期（YYYY-MM-DD），None 则搜索所有日期文件
        status_filter: 要筛选的状态，默认 fetched

    Returns:
        符合条件的条目列表，每个条目附带 date_file 字段
    """
    results = []

    if date_str:
        files = [URLS_DIR / f"{date_str}.json"]
    else:
        files = sorted(URLS_DIR.glob("*.json"))

    for filepath in files:
        if not filepath.exists():
            continue
        with open(filepath, "r", encoding="utf-8") as f:
            entries = json.load(f)
        for entry in entries:
            if entry.get("status") == status_filter:
                entry["_date_file"] = filepath.name
                raw_doc = RAW_DOCS_DIR / f"{entry['hash']}.md"
                entry["_raw_doc_exists"] = raw_doc.exists()
                results.append(entry)

    return results


def main():
    parser = argparse.ArgumentParser(description="列出待分析的文档")
    parser.add_argument(
        "--date", type=str, default=None,
        help="指定日期（YYYY-MM-DD），默认搜索所有日期"
    )
    parser.add_argument(
        "--status", type=str, default="fetched",
        help="筛选状态（默认: fetched）"
    )
    parser.add_argument(
        "--json", action="store_true", dest="output_json",
        help="以 JSON 格式输出"
    )
    args = parser.parse_args()

    results = find_pending(args.date, args.status)

    if not results:
        print(f"没有找到 status={args.status} 的条目")
        return

    if args.output_json:
        # 输出干净的 JSON（去掉内部字段）
        clean = []
        for r in results:
            clean.append({
                "hash": r["hash"],
                "url": r["url"],
                "date_file": r["_date_file"],
                "raw_doc_exists": r["_raw_doc_exists"],
            })
        print(json.dumps(clean, ensure_ascii=False, indent=2))
    else:
        print(f"找到 {len(results)} 个待分析文档（status={args.status}）：\n")
        for r in results:
            exists = "✓" if r["_raw_doc_exists"] else "✗"
            print(f"  [{exists}] {r['hash']}  ←  {r['url']}")
            print(f"      日期文件: {r['_date_file']}")
        print(f"\n共 {len(results)} 条")


if __name__ == "__main__":
    main()
