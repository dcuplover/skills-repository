# Hexo 文章格式规范

## Frontmatter

每篇文章必须以 YAML frontmatter 开头：

```yaml
---
title: 文章标题
date: 2026-02-14 10:30:00
updated: 2026-02-14 10:30:00
tags:
  - Python
  - 异步编程
categories:
  - 技术笔记
excerpt: 文章摘要，会显示在列表页
---
```

### 字段说明

| 字段 | 必填 | 说明 |
|------|------|------|
| title | 是 | 文章标题 |
| date | 是 | 发布日期，格式 `YYYY-MM-DD HH:mm:ss` |
| updated | 否 | 更新日期 |
| tags | 建议 | 标签列表 |
| categories | 建议 | 分类列表 |
| excerpt | 建议 | 摘要 |

## 文章结构

```markdown
---
(frontmatter)
---

引言段落（1-2 句简要说明本文内容）

## 核心概念

（介绍主题的核心概念）

## 实践示例

（代码示例 + 解释）

## 注意事项

（常见坑点和最佳实践）

## 总结

（简要回顾要点）

## 参考

- [来源标题](URL)
```

## 文件命名

- 使用英文短横线命名：`python-async-patterns.md`
- 与知识库文档的 topic 名保持一致
