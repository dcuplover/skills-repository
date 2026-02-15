---
name: fetch-content
description: 抓取待处理的 URL 网页内容，转为 Markdown 存储到 raw-docs 目录。默认处理当天的 URL 文件，也可指定日期。
allowed-tools: Bash(python *), Read, Write
---

# fetch-content

抓取 URL 网页内容并转为 Markdown 存储。

## 执行步骤

> **注意**：下面的 `<SKILL_DIR>` 指本 SKILL.md 所在的目录，请根据实际路径替换。

1. 运行抓取脚本（默认处理当天）：
   ```bash
   python <SKILL_DIR>/scripts/fetch_page.py
   ```
   或指定日期：
   ```bash
   python <SKILL_DIR>/scripts/fetch_page.py --date 2026-02-14
   ```

2. 脚本会自动：
   - 读取 `data/urls/YYYY-MM-DD.json` 中 `status: pending` 的条目
   - 用 requests 抓取网页内容
   - 用 BeautifulSoup + markdownify 转为 Markdown
   - 添加 frontmatter（source_url、fetch_time、hash）
   - 存入 `data/raw-docs/{hash}.md`
   - 更新日期 JSON 中该条目 `status: fetched`

3. 抓取失败的 URL 会标记为 `status: failed` 并记录错误信息。

## 输出

每个成功抓取的 URL 生成一个 `data/raw-docs/{hash}.md` 文件，格式：

```markdown
---
source_url: https://example.com/article
fetch_time: 2026-02-14T10:30:00
hash: a1b2c3d4e5f67890
title: 文章标题
---

（网页正文内容，已转为 Markdown）
```
