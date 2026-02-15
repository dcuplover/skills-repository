---
name: get-urls
description: 从用户输入或 Markdown 订阅列表收集 URL，通过 hash 索引自动去重，按日期存储到 JSON 文件。用于收集待阅读的文章链接。
allowed-tools: Bash(python *), Read, Write
---

# get-urls

收集 URL 并按日期存储，自动去重。

## 使用方式

### 方式一：用户直接提供 URL

用户在对话中给出一个或多个 URL，运行脚本将其保存。

### 方式二：从 Markdown 文件提取

用户提供一个 Markdown 文件路径（或使用默认订阅列表 `data/subscriptions.md`），脚本从中提取所有 URL。

## 执行步骤

> **注意**：下面的 `<SKILL_DIR>` 指本 SKILL.md 所在的目录，请根据实际路径替换。

1. 运行提取脚本：
   ```bash
   python <SKILL_DIR>/scripts/extract_urls.py --urls "URL1" "URL2"
   ```
   或从 Markdown 文件提取：
   ```bash
   python <SKILL_DIR>/scripts/extract_urls.py --markdown data/subscriptions.md
   ```

2. 脚本会自动：
   - 对每个 URL 计算 SHA256 hash（取前 16 位）
   - 读取 `data/url-hashes.json` 检查是否已存在
   - 新 URL 追加到 `data/urls/YYYY-MM-DD.json`（当天日期）
   - 同步更新 `data/url-hashes.json`
   - 输出新增/跳过数量

## 数据格式

详见 [reference.md](reference.md)
