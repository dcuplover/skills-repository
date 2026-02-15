---
name: publish-blog
description: 将博客文章发布到服务器。目前使用 Hexo deploy 插件手动触发。
disable-model-invocation: true
---

# publish-blog

将生成的博客文章发布到服务器。

## 当前方式

使用 Hexo 自带的 deploy 插件，在 Hexo 项目目录中执行：

```bash
hexo deploy
```

或使用 hexo-deployer-rsync 插件通过 SSH rsync 部署：

```bash
hexo deploy --type rsync
```

## 前置条件

1. blog-posts 目录中有待发布的文章
2. 文章已复制到 Hexo 项目的 `source/_posts/` 目录
3. Hexo 项目已配置好 deploy 选项

## 注意

此 Skill 设为仅手动触发（`disable-model-invocation: true`），因为发布操作有副作用，不应被 Agent 自动执行。
