#!/usr/bin/env python3
"""从用户输入或 Markdown 文件中提取 URL，去重后按日期存储。"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path


def _resolve_storage_dir() -> Path:
    """确定统一存储目录，优先读取 DATA_DIR，未设置时默认 ~/.openclad/data。"""
    data_dir = os.getenv("DATA_DIR", "~/.openclad/data")
    return Path(data_dir).expanduser().resolve()


STORAGE_DIR = _resolve_storage_dir()
URLS_DIR = STORAGE_DIR / "urls"
HASHES_FILE = STORAGE_DIR / "url-hashes.json"

# URL 正则：匹配 http/https 链接
URL_PATTERN = re.compile(
    r'https?://[^\s\)\]\>\"\'\`\,\;]+'
)


def compute_hash(url: str) -> str:
    """计算 URL 的 SHA256 hash，取前 16 位。"""
    return hashlib.sha256(url.strip().encode()).hexdigest()[:16]


def load_hashes() -> dict:
    """加载全局 hash 索引。"""
    if HASHES_FILE.exists():
        with open(HASHES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_hashes(hashes: dict) -> None:
    """保存全局 hash 索引。"""
    HASHES_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(HASHES_FILE, "w", encoding="utf-8") as f:
        json.dump(hashes, f, ensure_ascii=False, indent=2)


def load_today_urls(date_str: str) -> list:
    """加载当天的 URL 文件。"""
    filepath = URLS_DIR / f"{date_str}.json"
    if filepath.exists():
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_today_urls(date_str: str, urls: list) -> None:
    """保存当天的 URL 文件。"""
    URLS_DIR.mkdir(parents=True, exist_ok=True)
    filepath = URLS_DIR / f"{date_str}.json"
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(urls, f, ensure_ascii=False, indent=2)


def extract_urls_from_markdown(filepath: str) -> list[str]:
    """从 Markdown 文件中提取所有 URL。"""
    path = Path(filepath)
    if not path.exists():
        print(f"错误：文件不存在 - {filepath}", file=sys.stderr)
        return []
    content = path.read_text(encoding="utf-8")
    urls = URL_PATTERN.findall(content)
    # 清理尾部标点
    cleaned = []
    for url in urls:
        url = url.rstrip(".,;:!?)")
        if url:
            cleaned.append(url)
    return list(dict.fromkeys(cleaned))  # 保序去重


def add_urls(urls: list[str], source: str) -> tuple[int, int]:
    """
    将 URL 列表添加到存储中。

    Returns:
        (new_count, skipped_count)
    """
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    timestamp = now.isoformat(timespec="seconds")

    hashes = load_hashes()
    today_urls = load_today_urls(date_str)

    new_count = 0
    skipped_count = 0

    for url in urls:
        url = url.strip()
        if not url:
            continue

        url_hash = compute_hash(url)

        if url_hash in hashes:
            skipped_count += 1
            continue

        # 新 URL
        entry = {
            "url": url,
            "hash": url_hash,
            "source": source,
            "added_at": timestamp,
            "status": "pending",
            "tags": [],
        }
        today_urls.append(entry)
        hashes[url_hash] = {
            "url": url,
            "added_at": date_str,
        }
        new_count += 1

    save_today_urls(date_str, today_urls)
    save_hashes(hashes)

    return new_count, skipped_count


def main():
    parser = argparse.ArgumentParser(
        description="收集 URL 并按日期存储，自动去重"
    )
    parser.add_argument(
        "--urls", nargs="+", help="直接提供的 URL 列表"
    )
    parser.add_argument(
        "--markdown", type=str, help="从 Markdown 文件中提取 URL"
    )
    parser.add_argument(
        "--source", type=str, default=None,
        help="来源标记（默认：user_input 或 Markdown 文件路径）"
    )

    args = parser.parse_args()

    all_urls: list[str] = []
    source = "user_input"

    if args.urls:
        all_urls.extend(args.urls)
        source = args.source or "user_input"

    if args.markdown:
        md_urls = extract_urls_from_markdown(args.markdown)
        all_urls.extend(md_urls)
        source = args.source or args.markdown

    if not all_urls:
        print("错误：请通过 --urls 或 --markdown 提供至少一个 URL", file=sys.stderr)
        sys.exit(1)

    new_count, skipped_count = add_urls(all_urls, source)
    print(f"完成：新增 {new_count} 个 URL，跳过 {skipped_count} 个重复")


if __name__ == "__main__":
    main()
