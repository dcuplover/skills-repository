---
name: analyze-knowledge
description: 分析抓取的网页内容，提取知识点与现有知识库比对。新知识写入知识库，与已有知识冲突的写入讨论列表，已知且一致的跳过。
allowed-tools: Bash(python *), Read, Write, Grep, Glob
---

# analyze-knowledge

分析抓取的内容，提取知识并与现有知识库比对。

## 范围控制

**不要扫描全部 raw-docs**，通过以下方式确定分析范围：

> **注意**：下面的 `<SKILL_DIR>` 指本 SKILL.md 所在的目录，请根据实际路径替换。

### 默认：只分析当天

先运行辅助脚本列出待分析文件（status=fetched）：

```bash
python <SKILL_DIR>/scripts/list_pending.py
```

### 指定日期

```bash
python <SKILL_DIR>/scripts/list_pending.py --date 2026-02-14
```

### 指定特定 hash

用户可以直接指明要分析哪些 hash，跳过列出步骤，直接读取对应的 `data/raw-docs/{hash}.md`。

### 查看其他状态

```bash
# 查看已分析的
python <SKILL_DIR>/scripts/list_pending.py --status analyzed
# 查看失败的
python <SKILL_DIR>/scripts/list_pending.py --status failed
```

## 执行步骤

1. **确定分析范围**：运行 `list_pending.py` 获得待分析文档列表（仅 `status: fetched` 的条目）。

2. **逐个分析**：按列表逐个读取 `data/raw-docs/{hash}.md`，理解其中的观点、技巧、知识点。

3. **比对现有知识库**：用 Grep 搜索 `knowledge-base/` 目录，找到与提取知识相关的已有文档。

4. **分类处理**：

   ### 新知识（知识库中不存在相关内容）
   - 创建 `knowledge-base/{topic}.md`
   - 使用 [reference/knowledge-template.md](reference/knowledge-template.md) 模板
   - 标记 `blog_ready: false`（需要后续手动确认后改为 true）

   ### 冲突（与已有知识存在矛盾或不一致）
   - 创建 `discussions/{topic}.md`
   - 使用 [reference/discussion-template.md](reference/discussion-template.md) 模板
   - 包含旧观点、新观点、来源对比

   ### 已知且一致
   - 跳过，但可在现有文档的 `sources` 字段追加新来源

5. **更新状态**：将对应日期 JSON 文件中的条目 `status` 更新为 `analyzed`。

## 分析规则

详见 [reference/analysis-rules.md](reference/analysis-rules.md)

## 重要原则

- **宁可多创建讨论，不要默默覆盖**：任何有疑问的都放入 discussions
- **保留知识来源**：每条知识都要记录出处 URL 和日期
- **topic 命名**：使用简洁的英文短横线命名，如 `python-async-patterns`、`css-grid-layout`
