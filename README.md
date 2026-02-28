# Mem AI Skill for Claude Code

Mem AI 个人知识库 API 集成 Skill，让 Claude 能够智能调用 [Mem.ai](https://mem.ai) 的全部 API 能力。

## 功能概览

支持 11 个 API 端点，覆盖笔记和 Collection 的完整生命周期：

| 能力 | 说明 |
|---|---|
| **AI 智能处理 (mem-it)** | 自动提取、总结、分类原始内容（会议记录、网页、邮件等） |
| **笔记 CRUD** | 创建、读取、列表、搜索、删除笔记 |
| **多维搜索** | 按关键词、Collection、任务状态、图片、附件等组合筛选 |
| **Collection 管理** | 创建、读取、列表、搜索、删除 Collection |

### 路由决策

Skill 内置路由决策树，Claude 会根据用户意图自动选择正确的 API：

- "帮我整理这段会议记录" → `mem-it`（AI 智能处理）
- "记下来：明天下午三点开会" → `create-note`（原样保存）
- "搜索关于项目A的笔记" → `search`（关键词检索）
- "看看我最近的笔记" → `list`（分页浏览）
- "我有哪些未完成的待办" → `search(contains_open_tasks=true)`

## 安装

将 `mem-ai/` 目录复制到你的 Claude Code Skills 目录中，或直接使用打包好的 `mem-ai.skill` 文件。

## 配置 API Key

使用前需要将 Mem.ai 的 API Key 配置为环境变量 `MEM_API_KEY`。

### 获取 API Key

1. 登录 [mem.ai](https://mem.ai)
2. 进入 Settings → API
3. 创建一个新的 API Key

### macOS

**临时生效（当前终端会话）：**

```bash
export MEM_API_KEY=sk-mem-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

**永久生效：**

```bash
# zsh（macOS 默认 shell）
echo 'export MEM_API_KEY=sk-mem-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx' >> ~/.zshrc
source ~/.zshrc

# bash
echo 'export MEM_API_KEY=sk-mem-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx' >> ~/.bash_profile
source ~/.bash_profile
```

### Linux

```bash
# bash（大多数 Linux 默认 shell）
echo 'export MEM_API_KEY=sk-mem-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx' >> ~/.bashrc
source ~/.bashrc

# zsh
echo 'export MEM_API_KEY=sk-mem-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx' >> ~/.zshrc
source ~/.zshrc
```

### 验证配置

```bash
echo $MEM_API_KEY
# 应输出你的 API Key
```

快速测试 API 连通性：

```bash
curl -s "https://api.mem.ai/v2/collections?limit=1" \
  --header "Authorization: Bearer $MEM_API_KEY"
```

## 脚本封装（推荐）

新增了可直接调用的 Python CLI：`scripts/memctl`

```bash
# 保存笔记
~/.agents/skills/mem-ai-skill/scripts/memctl save "# 今日记录\n\n完成了 A/B 测试"

# 搜索笔记
~/.agents/skills/mem-ai-skill/scripts/memctl search "A/B 测试" --limit 5

# 查看最近笔记
~/.agents/skills/mem-ai-skill/scripts/memctl list --limit 5

# 读取笔记
~/.agents/skills/mem-ai-skill/scripts/memctl read <note_id>

# 更新笔记（同 id 覆盖；支持 replace/append/prepend）
~/.agents/skills/mem-ai-skill/scripts/memctl update <note_id> --file ./note.md

# 删除笔记
~/.agents/skills/mem-ai-skill/scripts/memctl delete <note_id>
```

也可用别名简化：

```bash
ln -sf ~/.agents/skills/mem-ai-skill/scripts/memctl ~/.local/bin/memctl
memctl list --limit 5
```

## Skill 目录结构

```
mem-ai/
├── SKILL.md                          # 路由决策树 + 工作流 + API 概览
├── scripts/
│   ├── memctl                        # Bash 入口
│   └── memctl.py                     # Python CLI（save/search/list/read/update/delete）
└── references/
    ├── mem-it.md                     # mem-it 接口参数、指令模板、示例
    ├── note-crud.md                  # create / update(upsert) / read / list / delete 完整参数
    ├── search.md                     # search 接口参数与筛选维度
    └── collections-and-errors.md     # Collection 完整 CRUD + 错误码
```

## License

MIT
