# Token Dashboard v2

DSH Token 用量监控仪表盘 — CLI + Web 双模式，支持 dsh-cost-meter 插件的 ledger.json 数据。

![CLI](https://img.shields.io/badge/CLI-terminal-blue) ![Web](https://img.shields.io/badge/Web-dashboard-orange) ![Python](https://img.shields.io/badge/Python-3.10+-green) ![Version](https://img.shields.io/badge/version-2.0.0-brightgreen)

## v2 新特性

- **CLI 终端仪表盘**：基于 rich 的实时表格 + 柱状图展示
- **Web 可视化仪表盘**：深色主题浏览器界面，响应式布局
- **多维度统计**：按模型 / 会话 / 日期分组聚合
- **智能数据解析**：自动兼容多种 ledger.json 格式（列表 / 嵌套 / 扁平）
- **Demo 模式**：无 ledger 数据时自动展示示例数据，方便预览
- **REST API**：提供 `/api/stats` 和 `/api/health` 接口
- **自动定位 ledger**：搜索多个候选路径（desktop / web profile）

## 安装

```bash
cd D:\code\token-dashboard
pip install -r requirements.txt
```

## 使用

### CLI 模式
```bash
python -m token_dashboard cli
```

### Web 模式
```bash
python -m token_dashboard web --port 8080
```
然后打开 http://localhost:8080

### 指定自定义 ledger 路径
```bash
# 通过环境变量指定
set LEDGER_PATH=C:\path\to\ledger.json
python -m token_dashboard cli
```

## CLI 截图（ASCII 模拟）

```
┌──────────────────────────────────────────────────────────────┐
│                      Token Dashboard                         │
├──────────────────────────────────────────────────────────────┤
│  Sessions: 42                                                │
│  Records:  1,283                                             │
│  Tokens:   15,234,567                                        │
│    Input:  9,876,543                                         │
│    Output: 5,358,024                                         │
│  Cost:     $12.3456                                          │
└──────────────────────────────────────────────────────────────┘

                           By Model
╭──────────────────┬───────┬──────────┬──────────╮
│ Model            │ Calls │ Tokens   │ Cost     │
├──────────────────┼───────┼──────────┼──────────┤
│ deepseek-chat    │   523 │ 6,543,210│  $5.2341 │
│ gpt-4o           │   412 │ 4,321,098│  $4.1230 │
│ claude-3.5-sonnet│   287 │ 3,456,789│  $2.5678 │
│ LongCat-2.0      │    61 │   913,470│  $0.4207 │
╰──────────────────┴───────┴──────────┴──────────╯

                          Daily Usage
╭────────────┬───────┬──────────┬──────────╮
│ Date       │ Calls │ Tokens   │ Cost     │
├────────────┼───────┼──────────┼──────────┤
│ 2026-09-20 │    45 │   543,210│  $0.5432 │
│ 2026-09-21 │    67 │   876,543│  $0.8765 │
│ 2026-09-22 │    89 │ 1,234,567│  $1.2345 │
│ ...        │   ... │      ... │      ... │
╰────────────┴───────┴──────────┴──────────╯

                     Top Sessions by Cost
╭──────────────────┬───────┬──────────┬──────────╮
│ Session ID       │ Calls │ Tokens   │ Cost     │
├──────────────────┼───────┼──────────┼──────────┤
│ session-0042-... │    23 │   345,678│  $0.3456 │
│ session-0038-... │    19 │   298,765│  $0.2987 │
│ session-0031-... │    15 │   256,432│  $0.2564 │
╰──────────────────┴───────┴──────────┴──────────╯
```

## API 端点

启动 Web 模式后可用：

| 端点 | 方法 | 说明 | 返回 |
|------|------|------|------|
| `/` | GET | Web 仪表盘前端页面 | HTML |
| `/api/stats` | GET | 用量统计聚合数据 | JSON |
| `/api/health` | GET | 健康检查 | JSON |

### GET /api/stats

返回完整的用量统计：

```json
{
  "total_sessions": 42,
  "total_records": 1283,
  "total_tokens": 15234567,
  "total_input_tokens": 9876543,
  "total_output_tokens": 5358024,
  "total_cost": 12.3456,
  "by_model": [
    {"model": "deepseek-chat", "calls": 523, "tokens": 6543210, "cost": 5.2341}
  ],
  "by_session": [
    {"session": "session-0042", "calls": 23, "tokens": 345678, "cost": 0.3456, "full_id": "session-0042-demo-session-id"}
  ],
  "daily": [
    {"date": "2026-09-20", "calls": 45, "tokens": 543210, "cost": 0.5432}
  ]
}
```

### GET /api/health

```json
{"status": "ok", "version": "1.0.0"}
```

## ledger.json 格式文档

Token Dashboard 自动解析 dsh-cost-meter 插件生成的 `ledger.json` 文件，支持多种格式。

### 自动搜索路径

按以下顺序查找，返回第一个存在的文件：

```
~/.dsh/profiles/desktop/plugins/dsh-cost-meter/ledger.json
~/.dsh/profiles/web/plugins/dsh-cost-meter/ledger.json
~/.dsh/cost-meter/ledger.json
```

### 支持的格式

#### 格式 A：记录列表（推荐）

```json
[
  {
    "sessionId": "session-0042-demo-session-id",
    "model": "deepseek-chat",
    "inputTokens": 15000,
    "outputTokens": 8000,
    "totalTokens": 23000,
    "cost": 0.0156,
    "timestamp": "2026-09-22T14:30:00+08:00",
    "provider": "deepseek"
  },
  {
    "sessionId": "session-0042-demo-session-id",
    "model": "gpt-4o",
    "inputTokens": 5000,
    "outputTokens": 2000,
    "totalTokens": 7000,
    "cost": 0.0350,
    "timestamp": "2026-09-22T15:00:00+08:00",
    "provider": "openai"
  }
]
```

#### 格式 B：嵌套 sessions 对象

```json
{
  "sessions": [
    {
      "session_id": "session-0031-abc",
      "model": "claude-3.5-sonnet",
      "input_tokens": 12000,
      "output_tokens": 4500,
      "total_tokens": 16500,
      "totalCost": 0.0495,
      "created_at": "2026-09-21T10:15:30Z",
      "llmProvider": "anthropic"
    }
  ]
}
```

#### 格式 C：嵌套 entries 对象

```json
{
  "entries": [
    {
      "id": "session-0028-xyz",
      "provider": "openai",
      "prompt_tokens": 8000,
      "completion_tokens": 3000,
      "total_tokens": 11000,
      "total_cost": 0.0220,
      "createdAt": "2026-09-20T09:00:00Z"
    }
  ]
}
```

### 字段映射（自动归一化）

解析器会自动将各种字段名映射到统一格式：

| 归一化字段 | 兼容的源字段名 |
|-----------|--------------|
| `session_id` | `sessionId`, `session_id`, `id` |
| `model` | `model`, `provider` |
| `input_tokens` | `inputTokens`, `input_tokens`, `prompt_tokens` |
| `output_tokens` | `outputTokens`, `output_tokens`, `completion_tokens` |
| `total_tokens` | `totalTokens`, `total_tokens` |
| `cost` | `cost`, `totalCost`, `total_cost` |
| `timestamp` | `timestamp`, `createdAt`, `created_at` |
| `provider` | `provider`, `llmProvider` |

> 所有字段均为可选，缺失时默认：`unknown`（字符串）、`0`（数字）、`""`（时间戳）。

## 配置指南

### 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `LEDGER_PATH` | 自定义 ledger.json 路径 | 自动搜索 |
| `DASHBOARD_PORT` | Web 服务端口 | `8080` |

### 命令行参数

```
python -m token_dashboard [cli|web] [--port PORT]

  cli          终端仪表盘模式
  web          Web 仪表盘模式
  --port       Web 端口（默认 8080）
```

### 自定义 ledger 路径

```bash
# PowerShell
$env:LEDGER_PATH = "C:\custom\path\ledger.json"
python -m token_dashboard cli

# CMD
set LEDGER_PATH=C:\custom\path\ledger.json
python -m token_dashboard cli

# 临时指定（单次生效）
LEDGER_PATH=C:\custom\path\ledger.json python -m token_dashboard cli
```

## 项目结构

```
token-dashboard/
├── token_dashboard/
│   ├── __init__.py      # 包信息 (__version__)
│   ├── __main__.py      # CLI 入口，分发 cli/web 子命令
│   ├── parser.py        # ledger.json 解析器（多格式兼容）
│   ├── stats.py         # 统计计算（按模型/会话/日期聚合）
│   ├── cli.py           # 终端仪表盘（rich 表格 + 面板）
│   └── webapp.py        # Flask Web 服务 + REST API
├── web/
│   ├── index.html       # 前端页面（深色主题）
│   ├── style.css        # 样式（响应式布局）
│   └── app.js           # 前端逻辑（fetch API + 渲染）
├── requirements.txt     # rich >= 13.0, flask >= 3.0
└── README.md
```

## 依赖

- Python 3.10+
- rich >= 13.0（终端表格和样式）
- flask >= 3.0（Web 服务）

## 故障排查

### CLI 显示 "No ledger.json found"

**原因**：未安装 dsh-cost-meter 插件，或 ledger 文件不在默认搜索路径。

**解决**：
1. 确认 dsh-cost-meter 插件已安装并产生过用量数据
2. 通过 `LEDGER_PATH` 环境变量手动指定路径：
   ```bash
   $env:LEDGER_PATH = "C:\Users\<用户名>\.dsh\profiles\desktop\plugins\dsh-cost-meter\ledger.json"
   python -m token_dashboard cli
   ```
3. 此时会自动展示 demo 数据，确认功能正常

### Web 页面空白或报错

**原因**：端口被占用或防火墙拦截。

**解决**：
1. 更换端口：`python -m token_dashboard web --port 8081`
2. 检查端口占用：`netstat -ano | findstr :8080`
3. 确认防火墙允许 localhost 访问

### 统计数据为空

**原因**：ledger.json 格式不兼容或字段缺失。

**解决**：
1. 用 `python -c "import json; print(json.dumps(json.load(open('ledger.json')), indent=2)[:500])"` 查看文件内容
2. 确认至少包含 `model` 和 `inputTokens`/`input_tokens` 字段
3. 参考上方「ledger.json 格式文档」调整字段名

### 中文显示乱码（Windows）

**原因**：Windows 终端默认编码非 UTF-8。

**解决**：
```bash
chcp 65001
$env:PYTHONIOENCODING = "utf-8"
python -m token_dashboard cli
```

### ImportError: No module named 'rich'

**解决**：
```bash
pip install -r requirements.txt
```

## License

MIT
