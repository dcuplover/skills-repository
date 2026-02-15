#!/usr/bin/env python3
"""抓取 URL 网页内容，转为 Markdown 存储。"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import urljoin, urlparse

try:
    import requests
    from bs4 import BeautifulSoup
    from markdownify import markdownify as md
except ImportError as e:
    print(f"缺少依赖：{e}。请运行 pip install requests beautifulsoup4 markdownify", file=sys.stderr)
    sys.exit(1)

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
IMAGES_DIR = RAW_DOCS_DIR / "images"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
TIMEOUT = 30


def _detect_encoding(resp: requests.Response) -> str:
    """
    多策略检测网页编码，优先级：
    1. HTTP Content-Type header 中的 charset
    2. HTML <meta> 标签中的 charset
    3. UTF-8（对中文页面最安全的默认值）
    """
    import re as _re

    # 1. Content-Type header 中明确声明的 charset
    ct = resp.headers.get("Content-Type", "")
    m = _re.search(r'charset=([^\s;]+)', ct, _re.IGNORECASE)
    if m:
        return m.group(1).strip()

    # 2. HTML meta 标签中的 charset（用原始字节搜索，避免解码问题）
    raw = resp.content[:4096]  # 只看前 4KB
    # <meta charset="utf-8">
    m = _re.search(rb'<meta[^>]+charset=["\']?([^"\'\s;>]+)', raw, _re.IGNORECASE)
    if m:
        return m.group(1).decode("ascii", errors="ignore")
    # <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
    m = _re.search(rb'content=["\'][^"\']*charset=([^"\'\s;]+)', raw, _re.IGNORECASE)
    if m:
        return m.group(1).decode("ascii", errors="ignore")

    # 3. 默认 UTF-8（比 apparent_encoding 对中文更可靠）
    return "utf-8"


def _download_image(img_url: str, save_dir: Path, session: requests.Session) -> str | None:
    """
    下载单张图片，返回本地文件名。失败返回 None。
    """
    try:
        resp = session.get(img_url, headers=HEADERS, timeout=TIMEOUT, stream=True)
        resp.raise_for_status()

        # 从 Content-Type 推断扩展名
        content_type = resp.headers.get("Content-Type", "")
        ext_map = {
            "image/jpeg": ".jpg",
            "image/png": ".png",
            "image/gif": ".gif",
            "image/webp": ".webp",
            "image/svg+xml": ".svg",
            "image/bmp": ".bmp",
        }
        ext = ext_map.get(content_type.split(";")[0].strip(), "")
        if not ext:
            # 从 URL 路径推断
            parsed_path = urlparse(img_url).path
            ext = os.path.splitext(parsed_path)[1].lower()
            if ext not in (".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".bmp"):
                ext = ".jpg"  # 兜底

        # 用图片 URL 的 hash 做文件名，避免冲突
        img_hash = hashlib.sha256(img_url.encode()).hexdigest()[:12]
        filename = f"{img_hash}{ext}"
        filepath = save_dir / filename

        save_dir.mkdir(parents=True, exist_ok=True)
        with open(filepath, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)

        return filename
    except Exception:
        return None


def fetch_and_convert(url: str, url_hash: str) -> tuple[str, str, int]:
    """
    抓取网页并转为 Markdown，同时下载图片到本地。

    Returns:
        (title, markdown_content, image_count)
    """
    session = requests.Session()
    resp = session.get(url, headers=HEADERS, timeout=TIMEOUT)
    resp.raise_for_status()
    resp.encoding = _detect_encoding(resp)

    soup = BeautifulSoup(resp.text, "html.parser")

    # 提取标题
    title = ""
    if soup.title and soup.title.string:
        title = soup.title.string.strip()

    # 移除 script、style、nav、footer 等无关元素
    for tag in soup(["script", "style", "nav", "footer", "header", "aside", "iframe"]):
        tag.decompose()

    # 尝试找正文区域
    article = soup.find("article") or soup.find("main") or soup.find("body")
    if article is None:
        article = soup

    # 下载图片并替换 src 为本地路径
    img_dir = IMAGES_DIR / url_hash
    image_count = 0
    for img_tag in article.find_all("img"):
        src = img_tag.get("src") or img_tag.get("data-src") or ""
        if not src or src.startswith("data:"):
            continue

        # 处理相对 URL
        abs_url = urljoin(url, src)
        local_name = _download_image(abs_url, img_dir, session)
        if local_name:
            # 使用相对于 raw-docs 目录的路径
            img_tag["src"] = f"images/{url_hash}/{local_name}"
            image_count += 1
        else:
            # 下载失败，保留原始 URL
            img_tag["src"] = abs_url

    markdown_content = md(str(article), heading_style="ATX")
    # 清理多余空行
    lines = markdown_content.split("\n")
    cleaned = []
    blank_count = 0
    for line in lines:
        if line.strip() == "":
            blank_count += 1
            if blank_count <= 2:
                cleaned.append("")
        else:
            blank_count = 0
            cleaned.append(line)

    return title, "\n".join(cleaned).strip(), image_count


def process_urls(date_str: str) -> None:
    """处理指定日期的 URL 文件。"""
    filepath = URLS_DIR / f"{date_str}.json"
    if not filepath.exists():
        print(f"没有找到 {date_str} 的 URL 文件：{filepath}")
        return

    with open(filepath, "r", encoding="utf-8") as f:
        entries = json.load(f)

    RAW_DOCS_DIR.mkdir(parents=True, exist_ok=True)

    fetched_count = 0
    failed_count = 0
    skipped_count = 0

    for entry in entries:
        if entry.get("status") != "pending":
            skipped_count += 1
            continue

        url = entry["url"]
        url_hash = entry["hash"]
        output_path = RAW_DOCS_DIR / f"{url_hash}.md"

        try:
            print(f"正在抓取：{url}")
            title, content, img_count = fetch_and_convert(url, url_hash)

            # 写入 Markdown 文件（含 frontmatter）
            fetch_time = datetime.now().isoformat(timespec="seconds")
            frontmatter = (
                f"---\n"
                f"source_url: {url}\n"
                f"fetch_time: {fetch_time}\n"
                f"hash: {url_hash}\n"
                f"title: {title}\n"
                f"images: {img_count}\n"
                f"---\n\n"
            )
            output_path.write_text(frontmatter + content, encoding="utf-8")

            entry["status"] = "fetched"
            fetched_count += 1
            print(f"  ✓ 已保存：{output_path.name}（{img_count} 张图片）")

        except Exception as e:
            entry["status"] = "failed"
            entry["error"] = str(e)
            failed_count += 1
            print(f"  ✗ 抓取失败：{e}", file=sys.stderr)

    # 回写更新后的状态
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)

    print(f"\n完成：抓取 {fetched_count} 个，失败 {failed_count} 个，跳过 {skipped_count} 个")


def main():
    parser = argparse.ArgumentParser(description="抓取 URL 网页内容并转为 Markdown")
    parser.add_argument(
        "--date", type=str, default=None,
        help="指定日期（YYYY-MM-DD），默认为当天"
    )
    args = parser.parse_args()

    date_str = args.date or datetime.now().strftime("%Y-%m-%d")
    process_urls(date_str)


if __name__ == "__main__":
    main()
