---
name: mem-ai
description: >
  Mem AI 个人知识库 API 集成。支持两种写入模式：AI 智能处理（mem-it，自动提取/总结/分类）
  和直接创建笔记（create-note，原样 Markdown 存储）。支持强大的搜索与多维筛选
  （按关键词、Collection、任务状态、图片、附件等）。支持笔记 CRUD、Collection 管理。
  当用户需要保存信息、检索知识、管理笔记、整理待办事项时使用。
  触发场景：记住这个、保存到笔记、搜索我的笔记、查找关于X的内容、
  我有哪些待办、整理会议记录、创建 Collection 等。
---

# Mem AI

Mem AI 个人知识库 API 集成——智能捕获、存储、搜索、管理你的知识。

## 前置要求

所有接口通过 Bash 执行 `curl` 命令调用，需要环境变量 `MEM_API_KEY`：

```bash
export MEM_API_KEY=your_api_key_here
```

## 快速命令（脚本封装）

优先使用脚本：`scripts/memctl`（免手写 curl）

```bash
# 保存笔记（原样 Markdown）
~/.agents/skills/mem-ai-skill/scripts/memctl save "# 会议记录\n\n- 决策 A\n- Todo B"

# 搜索笔记
~/.agents/skills/mem-ai-skill/scripts/memctl search "决策 A" --limit 5

# 查看最近笔记
~/.agents/skills/mem-ai-skill/scripts/memctl list --limit 5
```

## API 概览（11 个端点）

| 接口 | 方法 | 定位 |
|---|---|---|
| `/v2/mem-it` | POST | AI 智能处理（提取/总结/分类） |
| `/v2/notes` | POST | 直接创建笔记（原样 Markdown 存储） |
| `/v2/notes/{id}` | GET | 读取单条笔记 |
| `/v2/notes` | GET | 列表浏览（分页/排序/过滤） |
| `/v2/notes/search` | POST | 关键词搜索 + 多维筛选 |
| `/v2/notes/{id}` | DELETE | 删除笔记 |
| `/v2/collections` | POST | 创建 Collection |
| `/v2/collections/{id}` | GET | 读取单个 Collection |
| `/v2/collections` | GET | 列表浏览 Collection（分页/排序） |
| `/v2/collections/search` | POST | 按关键词搜索 Collection |
| `/v2/collections/{id}` | DELETE | 删除 Collection |

## 路由决策

### 写入路由：mem-it vs create-note

**判断标准：内容是否需要 AI 处理？**

**使用 mem-it（POST /v2/mem-it）当：**
- 原始内容需要 AI 提取/总结/分类（会议记录、网页 HTML、长邮件）
- 用户说"帮我整理"、"提取要点"、"总结一下"
- 输入是非结构化的原始数据
- 参数：`input`(必填), `instructions`, `context`, `timestamp`
- 详见 [references/mem-it.md](references/mem-it.md)

**使用 create-note（POST /v2/notes）当：**
- 内容已经是整理好的 Markdown
- 用户说"记下来"、"原样保存"、"创建笔记"
- 需要指定 Collection 归属
- 需要精确控制笔记格式
- 参数：`content`(必填, Markdown, 首行自动作标题), `collection_ids`, `collection_titles`, `created_at`, `updated_at`
- 详见 [references/note-crud.md](references/note-crud.md) § Create Note

### 读取路由：search vs list vs read

**使用 search（POST /v2/notes/search）当：**
- 用户有明确的搜索意图："查找关于X的笔记"
- 需要按关键词检索
- 需要多维筛选组合（Collection + 任务状态 + 媒体类型）
- 参数：`query`, `collection_ids`, `contains_open_tasks`, `contains_tasks`, `contains_images`, `contains_files`
- 详见 [references/search.md](references/search.md)

**使用 list（GET /v2/notes）当：**
- 用户想浏览最近的笔记："看看我最近的笔记"
- 需要分页翻阅
- 按某个 Collection 查看所有笔记
- 参数：`limit`, `cursor`, `order`(updated_at|created_at), `collection_id`, `contains_open_tasks`, `contains_tasks`, `contains_images`, `contains_files`, `include_content`
- 详见 [references/note-crud.md](references/note-crud.md) § List Notes

**使用 read（GET /v2/notes/{note_id}）当：**
- 已知具体笔记 ID，需要获取完整内容
- 详见 [references/note-crud.md](references/note-crud.md) § Read Note

### 删除路由

**使用 delete（DELETE /v2/notes/{note_id}）当：**
- 用户要删除指定笔记
- 需要先确认笔记 ID（可通过 search 或 list 获取）
- 详见 [references/note-crud.md](references/note-crud.md) § Delete Note

### Collection 管理

**使用 create-collection（POST /v2/collections）当：**
- 用户要创建新的分类/集合
- 参数：`name`(必填), `description`, `id`

**使用 search-collections（POST /v2/collections/search）当：**
- 用户按关键词搜索 Collection："找到关于XX的 Collection"
- 不确定 Collection 名称，需要模糊查找
- 参数：`query`

**使用 list-collections（GET /v2/collections）当：**
- 用户想浏览所有 Collection："我有哪些 Collection"
- 需要分页翻阅 Collection 列表
- 参数：`limit`, `cursor`, `order_by`(updated_at|created_at)

**使用 read-collection（GET /v2/collections/{collection_id}）当：**
- 已知 Collection ID，需要获取详细信息

**使用 delete-collection（DELETE /v2/collections/{collection_id}）当：**
- 用户要删除指定 Collection
- 需要先确认 Collection ID（可通过 search-collections 或 list-collections 获取）

详见 [references/collections-and-errors.md](references/collections-and-errors.md)

## 组合工作流

### 1. 智能捕获
mem-it 保存内容 → search 验证是否成功保存

### 2. 任务追踪
search(`contains_open_tasks=true`) → 汇总所有未完成待办

### 3. 项目整理
创建 Collection → create-note 归类笔记到该 Collection

### 4. 知识检索
search(`query=关键词`) → read(`note_id`) 获取完整内容

### 5. 笔记清理
list 浏览笔记 → delete 删除不需要的笔记

## 错误处理

所有 API 调用都应处理错误响应。常见状态码：400（参数错误）、401（认证失败）、404（资源不存在）、429（频率限制）、500（服务端错误）。

详见 [references/collections-and-errors.md](references/collections-and-errors.md) § Error Handling

## References

- [references/mem-it.md](references/mem-it.md) — mem-it 接口详细参数与指令模板
- [references/note-crud.md](references/note-crud.md) — create / read / list / delete 完整参数
- [references/search.md](references/search.md) — search 接口的完整参数与筛选维度
- [references/collections-and-errors.md](references/collections-and-errors.md) — Collection 管理 + 错误码
