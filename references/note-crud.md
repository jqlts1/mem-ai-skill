# Note CRUD API Reference

## 1. Create Note

### Endpoint
```
POST /v2/notes
```

直接创建笔记，内容原样存储为 Markdown。

### Request Body

| Parameter | Type | Required | Description | Constraints |
|:---|:---|:---|:---|:---|
| `content` | string | **Yes** | Markdown 格式笔记内容。**第一行自动作为标题** | 最大 ~200k 字符 |
| `id` | string | No | 自定义笔记 UUID | 合法 UUID |
| `collection_ids` | array | No | 要归入的 Collection ID 列表（不存在的 ID 会被忽略） | |
| `collection_titles` | array | No | 要归入的 Collection 标题列表（大小写不敏感精确匹配） | 每个标题最大 ~1k 字符 |
| `created_at` | string | No | 创建时间 (ISO 8601)，默认当前时间 | |
| `updated_at` | string | No | 更新时间 (ISO 8601)，默认与 created_at 相同 | |

### 请求示例

```bash
curl "https://api.mem.ai/v2/notes" \
  --header "Content-Type: application/json" \
  --header "Authorization: Bearer $MEM_API_KEY" \
  --data '{
    "content": "# Sales Call with Acme Corp\n\nContact: John Smith (john@acme.com)\nInterested in enterprise plan. Follow up next week.",
    "collection_ids": ["90815ddd-4c9b-49e3-b119-897ca04367f1"]
  }'
```

### 响应格式

Success (200 OK):
```json
{
  "request_id": "api-request-036ed6c7-de00-459f-a89b-43d26aafe522",
  "id": "5e29c8a2-c73b-476b-9311-e2579712d4b1",
  "title": "Sales Call with Acme Corp",
  "content": "# Sales Call with Acme Corp\n\nContact: John Smith ...",
  "collection_ids": ["59508b41-8770-4855-aa37-302b1e09aee7"],
  "created_at": "2025-04-11T04:47:14.457Z",
  "updated_at": "2025-04-11T04:47:19.702Z"
}
```

---

## 1.5 Update Note (Upsert)

### Endpoint
```
POST /v2/notes
```

Mem API 没有独立的 `PATCH/PUT` 更新端点。更新笔记时，使用已有 `id` 再次调用 `POST /v2/notes`，即可覆盖内容。

### 推荐流程

1. `GET /v2/notes/{note_id}` 读取原内容
2. 在本地合并/修改内容
3. `POST /v2/notes` 携带同一个 `id` 写回

### 请求示例

```bash
# 覆盖更新同一条笔记
curl "https://api.mem.ai/v2/notes" \
  --header "Content-Type: application/json" \
  --header "Authorization: Bearer $MEM_API_KEY" \
  --data '{
    "id": "5e29c8a2-c73b-476b-9311-e2579712d4b1",
    "content": "# Sales Call with Acme Corp\n\nUpdated follow-up: schedule demo next Tuesday.",
    "collection_ids": ["59508b41-8770-4855-aa37-302b1e09aee7"]
  }'
```

### 响应特征

- `id` 保持不变
- `created_at` 保持原值
- `updated_at` 会刷新

---

## 2. Read Note

### Endpoint
```
GET /v2/notes/{note_id}
```

获取单条笔记完整内容。

### Path Parameters

| Parameter | Type | Required | Description |
|:---|:---|:---|:---|
| `note_id` | string | **Yes** | 笔记 UUID |

### 请求示例

```bash
curl --request GET \
  --url https://api.mem.ai/v2/notes/{note_id} \
  --header 'Authorization: Bearer <token>'
```

### 响应格式

Success (200 OK):
```json
{
  "request_id": "api-request-036ed6c7-de00-459f-a89b-43d26aafe522",
  "id": "5e29c8a2-c73b-476b-9311-e2579712d4b1",
  "title": "Sales Call with Acme Corp",
  "content": "# Sales Call with Acme Corp\n\nContact: John Smith ...",
  "collection_ids": ["59508b41-8770-4855-aa37-302b1e09aee7"],
  "created_at": "2025-04-11T04:47:14.457Z",
  "updated_at": "2025-04-11T04:47:19.702Z"
}
```

---

## 3. List Notes

### Endpoint
```
GET /v2/notes
```

分页浏览笔记列表，支持排序和多维过滤。

### Query Parameters

| Parameter | Type | Description |
|:---|:---|:---|
| `limit` | integer | 返回数量上限，默认 50 |
| `cursor` | string | 分页游标（上一次请求返回的 `next_page` 值），首页请求时省略 |
| `order` | string | 排序字段：`updated_at`（默认）或 `created_at` |
| `collection_id` | string | 按 Collection ID 过滤 |
| `contains_open_tasks` | boolean | 为 true 时只返回包含未完成任务的笔记 |
| `contains_tasks` | boolean | 为 true 时只返回包含任务的笔记 |
| `contains_images` | boolean | 为 true 时只返回包含图片的笔记 |
| `contains_files` | boolean | 为 true 时只返回包含文件/附件的笔记 |
| `include_content` | boolean | 为 true 时在结果中包含完整 Markdown 内容 |

### 请求示例

```bash
curl "https://api.mem.ai/v2/notes?limit=20&order=updated_at&include_content=true" \
  --header "Authorization: Bearer $MEM_API_KEY"
```

### 分页示例

```bash
# 第一页
curl "https://api.mem.ai/v2/notes?limit=10" \
  --header "Authorization: Bearer $MEM_API_KEY"

# 下一页（使用返回的 next_page 值）
curl "https://api.mem.ai/v2/notes?limit=10&cursor=eyJvcmRl..." \
  --header "Authorization: Bearer $MEM_API_KEY"
```

### 响应格式

Success (200 OK):
```json
{
  "next_page": "eyJvcmRlcl9ieSI6InVwZGF0ZWRfYXQi...",
  "request_id": "api-request-018f8d0d-5a3c-7afc-8321-2f6f6e0fefab",
  "results": [
    {
      "id": "018f8d0d-5a3c-7afc-8321-2f6f6e0fefab",
      "title": "Weekly Planning",
      "snippet": "Quarterly kickoff prep",
      "content": "# Weekly Planning\n\n## Priorities...",
      "collection_ids": ["59508b41-8770-4855-aa37-302b1e09aee7"],
      "created_at": "2025-05-01T10:05:45Z",
      "updated_at": "2025-05-04T14:20:11Z"
    }
  ],
  "total": 12
}
```

注意：`next_page` 为 null 或不存在时表示已到最后一页。

---

## 4. Delete Note

### Endpoint
```
DELETE /v2/notes/{note_id}
```

删除指定笔记。

### Path Parameters

| Parameter | Type | Required | Description |
|:---|:---|:---|:---|
| `note_id` | string | **Yes** | 笔记 UUID |

### 请求示例

```bash
curl "https://api.mem.ai/v2/notes/{note_id}" \
  --header "Content-Type: application/json" \
  --header "Authorization: Bearer $MEM_API_KEY" \
  --request DELETE
```

### 响应格式

Success (200 OK):
```json
{
  "request_id": "api-request-036ed6c7-de00-459f-a89b-43d26aafe522"
}
```
