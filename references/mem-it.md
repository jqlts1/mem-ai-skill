# Mem It API Reference

## Endpoint

```
POST /v2/mem-it
```

AI 智能处理接口——自动提取、总结、分类原始内容。

## Authorization

Bearer authentication: `Authorization: Bearer <token>`

## Request Body

| Parameter | Type | Required | Description | Constraints |
|:---|:---|:---|:---|:---|
| `input` | string | **Yes** | 任意原始内容：网页 HTML、邮件、会议记录、文章、简单文本 | 最大 ~1M 字符 (~1 MB) |
| `instructions` | string | No | 处理指令——告诉 AI 如何处理这些内容 | 最大 ~10 KB |
| `context` | string | No | 背景信息——帮助 Mem 理解内容与已有知识的关联 | 最大 ~10k 字符 |
| `timestamp` | string | No | 内容产生时间 (ISO 8601)，默认当前时间 | ISO 8601 格式 |

## Instructions 指令模板

根据输入类型选择合适的指令：

### 会议记录
```
"Extract action items and decisions"
"Create a summary with action items and decisions"
```

### 网页/文章
```
"Extract key findings and save as a research note"
"Summarize the main points"
```

### 邮件
```
"Extract action items and follow-ups"
"Capture important information and deadlines"
```

### 想法/灵感
```
"Add to my reading list"
"Save as a project idea"
```

### 通用
```
"Extract the key findings"
"Create a summary"
"Organize into categories"
"Highlight specific types of information"
```

## Context 使用技巧

- 提供项目名称或主题，帮助 AI 关联已有笔记
- 说明内容来源（如"Weekly product planning meeting"）
- 指明内容所属的工作流或项目

## 请求示例

### 基本用法
```bash
curl "https://api.mem.ai/v2/mem-it" \
  --header "Content-Type: application/json" \
  --header "Authorization: Bearer $MEM_API_KEY" \
  --data '{ "input": "Check out the new research paper on quantum computing by MIT." }'
```

### 会议记录处理
```bash
curl "https://api.mem.ai/v2/mem-it" \
  --header "Content-Type: application/json" \
  --header "Authorization: Bearer $MEM_API_KEY" \
  --data '{
    "input": "[08:47:19] Kevin: Here'\''s what we learned from user testing...[09:15:22] Meeting ended.",
    "instructions": "Create a summary with action items and decisions",
    "context": "Weekly product planning meeting",
    "timestamp": "2025-04-01T08:47:19Z"
  }'
```

### 带上下文的操作项
```bash
curl "https://api.mem.ai/v2/mem-it" \
  --header "Content-Type: application/json" \
  --header "Authorization: Bearer $MEM_API_KEY" \
  --data '{
    "input": "Let'\''s move the deadline to next Friday and update the stakeholders.",
    "instructions": "Add this to my action items",
    "context": "This is related to Project Horizon"
  }'
```

### 网页内容提取
```bash
curl "https://api.mem.ai/v2/mem-it" \
  --header "Content-Type: application/json" \
  --header "Authorization: Bearer $MEM_API_KEY" \
  --data '{
    "input": "<!DOCTYPE html><html><head><title>Market Analysis 2025</title>...</html>",
    "instructions": "Extract key findings and save as a research note"
  }'
```

## 响应格式

Success (200 OK):
```json
{
  "request_id": "api-request-036ed6c7-de00-459f-a89b-43d26aafe522"
}
```

注意：mem-it 是异步处理，返回 `request_id` 表示请求已接受，AI 将在后台处理内容。
