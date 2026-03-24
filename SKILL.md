---
name: mem-ai
description: >
  Mem AI 个人知识库 API 集成。支持 AI 整理写入（mem-it）、原样 Markdown 笔记写入、
  语义搜索、笔记 CRUD、Collection 管理与待办筛选。当用户需要保存信息、记住内容、
  搜索历史方案、查找待办、整理会议记录、沉淀网页/文章/聊天内容、创建或维护 Collection 时使用。
  触发场景包括：记住这个、保存到笔记、原样记下、帮我整理后保存、查我的笔记、找之前关于 X 的内容、
  我有哪些待办、把这条补充到原笔记、创建 Collection。
---

# Mem AI

Mem AI 用于把信息沉淀成可搜索、可追加、可回忆的个人知识库。

## 最优先入口

默认先用封装命令 `scripts/memctl`，不要先手写 `curl`。
本文中的相对路径都以当前 skill 根目录为基准解析。
只有在以下场景才直接调用底层 API：
- 需要 `mem-it`
- 需要 Collection 创建 / 搜索 / 删除
- 需要调试原始响应

保存到 Mem 时，默认不要使用三反引号代码块。优先使用普通标题、列表、短段落和行内命令，保证预览和搜索效果。

## 快速路由

### 写入：`mem-it` vs `save`

**使用 `mem-it` 当：**
- 输入是原始材料，需要 AI 提取 / 总结 / 分类
- 用户说“帮我整理”“提取要点”“总结后保存”
- 内容是会议记录、网页正文、长文本、邮件、聊天纪要

**使用 `save` / `POST /v2/notes` 当：**
- 内容已经是整理好的 Markdown
- 用户说“记下来”“原样保存”“创建笔记”
- 需要精确控制正文格式或 Collection 归属

### 读取：`search` vs `list` vs `read`

**使用 `search` 当：**
- 用户明确在找某类历史内容
- 需要语义检索或组合筛选
- 目标是“先找到候选，再展开全文”
- 输入里出现明显属于用户个人语境的专有名词，且需要先补知识背景再判断

**使用 `list` 当：**
- 用户要看最近笔记
- 用户要浏览某个 Collection
- 用户没有明确关键词，只是想翻一翻

**使用 `read` 当：**
- 已知 `note_id`
- 用户已经从候选结果中选中某一条

### 更新与删除

**使用 `update` 当：**
- 用户要补充进展、追加记录、整体改写
- 推荐流程：先 `read`，再决定 `replace` / `append` / `prepend`

**使用 `delete` 当：**
- 用户明确要求删除指定笔记
- 删除前先确认目标 `note_id` 或明确候选项

### Collection 管理

直接调用 Collection API 当：
- 用户要创建 Collection
- 用户要查有哪些 Collection
- 用户要按 Collection 过滤、归类、迁移或删除

详见 `references/collections-and-errors.md`。

## 搜索默认策略

Mem 搜索默认走“语义优先”，不是机械堆关键词。

推荐顺序：
1. 一句自然语言描述目标
2. 必要时补 2~4 个核心关键词
3. 如果出现明显属于用户个人语境的专有名词（如人名、内部简称、项目黑话），且该名词会影响理解或检索结果，先去用户的知识库搜索一次再继续
4. 结果不理想时，再微调限定词

推荐写法：
- `我想找之前关于支付回调幂等的方案，重点看问题和修复思路`
- `我想找之前保存的 OpenClaw skill 笔记 用途 工作流 风险`

如果结果很多，默认先返回 3~5 条最相关结果，再让用户选一条展开，不要直接贴全文。

详见 `references/search.md`。

## 标题命名规则

标题首先服务检索和回忆，不追求短促或营销感。

优先写清：
- 主题
- 用途 / 作用
- 场景 / 任务词
- 必要时补一个限制词

推荐模板：
- `主题：作用/用途`
- `主题：作用/用途 + 场景`
- `工具/对象：适用任务 + 关键限制`

示例：
- `Mem AI 搜索：按项目和场景检索历史方案`
- `Chrome DevTools MCP：AI 前端调试、性能分析与网页自动化辅助`
- `Playwright：回归测试与批量网页流程自动化`

## 常用命令速览

```bash
scripts/memctl save "# 标题\n\n正文"
scripts/memctl search "关键词" --limit 5
scripts/memctl list --limit 5
scripts/memctl read <note_id>
scripts/memctl update <note_id> --file ./note.md --mode replace
scripts/memctl delete <note_id>
```

## 任务级工作流

### 1. 原始材料整理入库

适用：会议记录、长消息、网页、邮件、聊天摘要

流程：
1. 判断是否需要 AI 整理
2. 需要则调用 `mem-it`
3. 保存后给用户一个有结果感的总结
4. 必要时再用 `search` 验证是否已可检索

读 `references/mem-it.md`。

### 2. 搜索旧方案或历史决策

流程：
1. 用自然语言查询 `search`
2. 先返回 3~5 条候选
3. 用户选中后再 `read`
4. 若没有命中，改写 query 再搜一轮

读 `references/search.md` 和 `references/response-patterns.md`。

### 3. 追加进展到既有笔记

流程：
1. `read <note_id>`
2. 决定 `append` / `prepend` / `replace`
3. 多行内容优先 `--file`
4. 默认保留现有 Collection 归属
5. 回用户时说明是追加还是覆盖

### 4. 任务清单排查

流程：
1. 用 `search --open-tasks`
2. 先按相关度或主题分组概括
3. 仅在用户需要时展开全文

### 5. Collection 整理

流程：
1. 先明确是否已有目标 Collection
2. 不确定时先搜索或列出 Collection
3. 明确目标后再创建、归类或迁移

## 用户可见回复要求

不要只说“已保存”“找到了”。
默认让用户感知到这条操作的价值：
- 保存了什么
- 最关键的标题 / 主题是什么
- 是否归入某个 Collection
- 如果是整理类内容，提炼出了什么
- 如果是搜索，最相关的几条分别是什么

具体模板见 `references/response-patterns.md`。

## 高风险与常见坑

以下场景优先检查：
- 更新时不要丢失旧内容与 Collection
- 删除前先确认目标
- 多行更新优先用 `--file`
- 搜索结果很多时先摘要，不要直接贴全文
- 默认不要写三反引号代码块

详见 `references/gotchas.md`。

## References

- `references/mem-it.md` — AI 整理写入的参数与指令模板
- `references/note-crud.md` — create / read / list / delete / upsert 细节
- `references/search.md` — 语义搜索与筛选维度
- `references/collections-and-errors.md` — Collection 管理与错误处理
- `references/response-patterns.md` — 用户可见回复模板
- `references/gotchas.md` — 高频坑点与处理原则
