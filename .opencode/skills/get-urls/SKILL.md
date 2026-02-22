---
name: get-urls
description: URL保存操作。当用户提供url想要保存时使用。
---

# get-urls

收集 URL 并按日期存储，自动去重。

## 使用方式
### 保存用户直接提供 URL
用户在对话中给出一个或多个 URL，运行脚本将其保存。
脚本如下：
 ```bash
python scripts/extract_urls.py --urls "URL1" "URL2"
```

## 数据格式

详见 [reference.md](reference.md)
