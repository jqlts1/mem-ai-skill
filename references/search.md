# Search Notes API Reference

## Endpoint

```
POST /v2/notes/search
```

关键词搜索 + 多维筛选，适用于有明确搜索意图的场景。

## Authorization

Bearer authentication: `Authorization: Bearer <token>`

## Request Body

| Parameter | Type | Required | Description |
|:---|:---|:---|:---|
| `query` | string | No | 搜索关键词，用于过滤笔记 |
| `collection_ids` | array | No | Collection ID 列表，只返回属于指定 Collection 的笔记 |
| `contains_open_tasks` | boolean | No | 为 true 时只返回包含未完成任务的笔记 |
| `contains_tasks` | boolean | No | 为 true 时只返回包含任务（无论完成与否）的笔记 |
| `contains_images` | boolean | No | 为 true 时只返回包含图片的笔记 |
| `contains_files` | boolean | No | 为 true 时只返回包含文件/附件的笔记 |
| `config` | object | No | 响应配置选项 |

## Query 构造建议（语义优先）

推荐优先使用自然语言描述搜索目标，而不是机械堆砌短关键词。

- 首选：`一句自然语言`（可直接写完整意图）
- 次选：`一句自然语言 + 2~4 个核心关键词`
- 多关键词写法：使用空格分隔 3~8 个关键词（不要拼成一个长词）
- 不建议默认“先窄后宽”；向量检索通常先宽搜就能命中
- 仅在结果不理想时微调：
  - 结果太杂：补充限定词（工具名/项目名/时间词）
  - 结果太少：删掉限制词，换同义表达

### 推荐 Query 示例

```json
{ "query": "我想找之前保存的 FastClaw 笔记，重点看用途、适用场景和风险" }
```

```json
{ "query": "我想找之前保存的 FastClaw 笔记 用途 适用场景 风险 OpenClaw 托管" }
```

## 筛选组合示例

### 按关键词搜索
```json
{ "query": "sales" }
```

### 按 Collection 筛选
```json
{ "collection_ids": ["59508b41-8770-4855-aa37-302b1e09aee7"] }
```

### 查找所有未完成待办
```json
{ "contains_open_tasks": true }
```

### 组合筛选：某 Collection 下带图片的笔记
```json
{
  "collection_ids": ["59508b41-8770-4855-aa37-302b1e09aee7"],
  "contains_images": true
}
```

### 组合筛选：关键词 + 未完成任务
```json
{
  "query": "project horizon",
  "contains_open_tasks": true
}
```

## 请求示例

```bash
curl "https://api.mem.ai/v2/notes/search" \
  --header "Content-Type: application/json" \
  --header "Authorization: Bearer $MEM_API_KEY" \
  --data '{ "query": "sales" }'
```

## 响应格式

Success (200 OK):

```json
{
  "request_id": "api-request-018f8d0d-5a3c-7afc-8321-2f6f6e0fefab",
  "results": [
    {
      "id": "018f8d0d-5a3c-7afc-8321-2f6f6e0fefab",
      "title": "Recipe Notes",
      "snippet": "Dinner ideas",
      "content": "# Recipe Notes\n\n- Lemon pasta...",
      "collection_ids": ["59508b41-8770-4855-aa37-302b1e09aee7"],
      "created_at": "2025-03-18T11:00:00Z",
      "updated_at": "2025-04-22T16:12:34Z"
    }
  ],
  "total": 1
}
```

### 响应字段说明

| Field | Type | Description |
|:---|:---|:---|
| `request_id` | string | 请求唯一标识 |
| `results` | array | 匹配的笔记数组 |
| `results[].id` | string | 笔记 UUID |
| `results[].title` | string | 笔记标题 |
| `results[].snippet` | string | 内容摘要片段 |
| `results[].content` | string | 完整 Markdown 内容 |
| `results[].collection_ids` | array | 所属 Collection ID 列表 |
| `results[].created_at` | string | 创建时间 (ISO 8601) |
| `results[].updated_at` | string | 更新时间 (ISO 8601) |
| `total` | integer | 匹配结果总数 |
