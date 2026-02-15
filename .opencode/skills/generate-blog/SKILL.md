---
name: generate-blog
description: 从知识库中标记为 blog_ready 的文档生成 Hexo 格式的博客文章，输出到 blog-posts 目录。
allowed-tools: Read, Write, Glob, Grep
---

# generate-blog

从知识库生成 Hexo 格式的博客文章。

## 执行步骤

1. **扫描知识库**：用 Glob 查找 `knowledge-base/*.md`，筛选 frontmatter 中 `blog_ready: true` 且 `blog_generated: false` 的文档。

2. **生成博客文章**：
   - 读取知识库文档内容
   - 按 Hexo 文章格式重新组织（参考 [reference/hexo-post-spec.md](reference/hexo-post-spec.md)）
   - 生成合适的标题、摘要
   - 添加 Hexo frontmatter（title、date、tags、categories）
   - 输出到 `blog-posts/{topic}.md`

3. **更新知识库状态**：将知识库文档的 `blog_generated` 改为 `true`。

## 写作风格

- 以教学和分享为主，语气友好但专业
- 包含代码示例和实际应用场景
- 结构清晰：引言 → 核心内容 → 示例 → 总结
- 适当加入个人理解和见解，不要纯粹搬运

## Hexo 文章格式

详见 [reference/hexo-post-spec.md](reference/hexo-post-spec.md)
