# URL 数据格式参考

> 存储根目录优先由环境变量 `DATA_DIR` 决定；未设置时默认使用 `artifacts/`。

## artifacts/urls/YYYY-MM-DD.json

按日期存储当天收集的 URL，文件名格式为 `YYYY-MM-DD.json`。

```json
[
  {
    "url": "https://example.com/article",
    "hash": "a1b2c3d4e5f67890",
    "source": "user_input",
    "added_at": "2026-02-14T10:30:00",
    "status": "pending",
    "tags": []
  }
]
```

### 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| url | string | 原始 URL |
| hash | string | URL 的 SHA256 前 16 位，用于去重 |
| source | string | 来源：`user_input` 或 Markdown 文件路径 |
| added_at | string | ISO 8601 格式的添加时间 |
| status | string | 状态：`pending` → `fetched` → `analyzed` |
| tags | array | 用户可选标签 |

## artifacts/url-hashes.json

全局 hash 去重索引，用于跨日期快速判重。

```json
{
  "a1b2c3d4e5f67890": {
    "url": "https://example.com/article",
    "added_at": "2026-02-14"
  }
}
```

每次添加新 URL 时，先查此文件。若 hash 已存在则跳过。
