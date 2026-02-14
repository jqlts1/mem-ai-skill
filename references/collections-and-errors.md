# Collections & Error Handling Reference

## 1. Create Collection

### Endpoint
```
POST /v2/collections
```

创建一个新的 Collection，用于组织和归类笔记。

### Request Body

| Parameter | Type | Required | Description |
|:---|:---|:---|:---|
| `id` | string | No | 自定义 Collection UUID |
| `name` | string | **Yes** | Collection 名称 |
| `description` | string | No | Collection 描述 |

### 请求示例

```bash
curl "https://api.mem.ai/v2/collections" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $MEM_API_KEY" \
  -d '{
    "id": "90815ddd-4c9b-49e3-b119-897ca04367f1",
    "name": "Project Ideas",
    "description": "A collection of project ideas"
  }'
```

### 工作流示例：创建 Collection 并归入笔记

```bash
# Step 1: 创建 Collection
curl "https://api.mem.ai/v2/collections" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $MEM_API_KEY" \
  -d '{ "name": "Project Ideas", "description": "A collection of project ideas" }'

# Step 2: 创建笔记并归入该 Collection
curl "https://api.mem.ai/v2/notes" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $MEM_API_KEY" \
  -d '{
    "content": "# Great Idea\n\nBuild a mobile app that helps track daily water intake.",
    "collection_ids": ["<collection_id_from_step_1>"]
  }'
```

也可以使用 `collection_titles` 按标题匹配已有 Collection：
```json
{
  "content": "# My Note",
  "collection_titles": ["Project Ideas"]
}
```

---

## 2. Read Collection

### Endpoint
```
GET /v2/collections/{collection_id}
```

获取单个 Collection 的详细信息。

### Path Parameters

| Parameter | Type | Required | Description |
|:---|:---|:---|:---|
| `collection_id` | string | **Yes** | Collection UUID |

### 请求示例

```bash
curl --request GET \
  --url "https://api.mem.ai/v2/collections/{collection_id}" \
  --header "Authorization: Bearer $MEM_API_KEY"
```

### 响应格式

Success (200 OK):
```json
{
  "request_id": "api-request-036ed6c7-de00-459f-a89b-43d26aafe522",
  "id": "5e29c8a2-c73b-476b-9311-e2579712d4b1",
  "title": "Acme Corp",
  "description": "Anything related to Acme Corp; a software company that provides a suite of tools for managing customer relationships.",
  "created_at": "2025-04-11T04:47:14.457Z",
  "updated_at": "2025-04-11T04:47:19.702Z"
}
```

---

## 3. List Collections

### Endpoint
```
GET /v2/collections
```

分页浏览 Collection 列表。

### Query Parameters

| Parameter | Type | Description |
|:---|:---|:---|
| `limit` | integer | 返回数量上限，默认 50 |
| `cursor` | string | 分页游标（上一次请求返回的 `next_page` 值），首页省略 |
| `order_by` | string | 排序字段：`updated_at`（默认）或 `created_at` |

### 请求示例

```bash
curl "https://api.mem.ai/v2/collections?limit=20" \
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
      "title": "Project Phoenix",
      "description": "Initiatives and plans for Q1",
      "created_at": "2025-05-01T10:05:45Z",
      "updated_at": "2025-05-04T14:20:11Z"
    }
  ],
  "total": 24
}
```

---

## 4. Search Collections

### Endpoint
```
POST /v2/collections/search
```

按关键词搜索 Collection。

### Request Body

| Parameter | Type | Required | Description |
|:---|:---|:---|:---|
| `query` | string | No | 搜索关键词 |

### 请求示例

```bash
curl "https://api.mem.ai/v2/collections/search" \
  --header "Content-Type: application/json" \
  --header "Authorization: Bearer $MEM_API_KEY" \
  --data '{ "query": "recipes" }'
```

### 响应格式

Success (200 OK):
```json
{
  "request_id": "api-request-018f8d0d-5a3c-7afc-8321-2f6f6e0fefab",
  "results": [
    {
      "id": "018f8d0d-5a3c-7afc-8321-2f6f6e0fefab",
      "title": "Recipe Notes",
      "description": "Saved recipes from around the web",
      "created_at": "2025-03-18T11:00:00Z",
      "updated_at": "2025-04-22T16:12:34Z"
    }
  ],
  "total": 1
}
```

---

## 5. Delete Collection

### Endpoint
```
DELETE /v2/collections/{collection_id}
```

删除指定 Collection。

### Path Parameters

| Parameter | Type | Required | Description |
|:---|:---|:---|:---|
| `collection_id` | string | **Yes** | Collection UUID |

### 请求示例

```bash
curl "https://api.mem.ai/v2/collections/{collection_id}" \
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

---

## 6. Error Handling

### HTTP 状态码

| Status Code | Description |
|:---|:---|
| **2xx** | 请求成功 |
| **400** | 请求参数无效（Bad Request） |
| **401** | 认证失败（API Key 无效或缺失） |
| **404** | 资源不存在（笔记/Collection ID 无效） |
| **429** | 请求频率超限（Rate Limit） |
| **500** | 服务端错误 |

### 错误响应格式

```json
{
  "error": {
    "code": "invalid_parameter",
    "message": "The parameter 'content' is required",
    "param": "content"
  }
}
```

### 常见错误处理

- **400**：检查请求参数是否完整且格式正确
- **401**：确认 `Authorization: Bearer <token>` header 设置正确
- **404**：确认笔记或 Collection ID 存在
- **429**：等待一段时间后重试，考虑降低请求频率
- **500**：服务端问题，稍后重试
