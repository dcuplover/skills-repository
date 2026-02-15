---
name: run-pipeline
description: 按顺序执行完整的知识处理流水线：收集URL → 抓取内容 → 分析知识 → 生成博客。
disable-model-invocation: true
---

# run-pipeline

一键执行完整的知识处理流水线。

> **路径说明**：下面命令中的 `<SKILLS_ROOT>` 指 skills 目录的父目录（如 `.opencode/skills`、`.openclaw/skills` 等），请根据当前终端实际情况替换。

## 流程

按以下顺序依次执行：

### 1. 收集 URL（/get-urls）

从订阅列表中提取新 URL：

```bash
python <SKILLS_ROOT>/get-urls/scripts/extract_urls.py --markdown data/subscriptions.md
```

如果用户还提供了额外的 URL，也一并处理：

```bash
python <SKILLS_ROOT>/get-urls/scripts/extract_urls.py --urls $ARGUMENTS
```

### 2. 抓取内容（/fetch-content）

抓取当天新增的所有 pending URL：

```bash
python <SKILLS_ROOT>/fetch-content/scripts/fetch_page.py
```

### 3. 分析知识（/analyze-knowledge）

读取抓取的内容，与知识库比对，分类处理。此步骤由 Agent 语义理解驱动：
- 读取 `data/raw-docs/` 中新抓取的文档
- 对比 `knowledge-base/` 现有知识
- 新知识 → `knowledge-base/{topic}.md`
- 冲突 → `discussions/{topic}.md`

### 4. 生成博客（/generate-blog）

将标记为 `blog_ready: true` 的知识文档转为 Hexo 博客文章。

## 注意

- 每一步完成后确认结果再进入下一步
- 如果某一步失败，报告错误并停止
- 发布（/publish-blog）不包含在自动流水线中，需手动触发
