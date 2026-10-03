# Token Dashboard

DSH Token 用量监控仪表盘 — CLI + Web 双模式。

![CLI Preview](https://img.shields.io/badge/CLI-terminal-blue) ![Web Preview](https://img.shields.io/badge/Web-dashboard-orange) ![Python](https://img.shields.io/badge/Python-3.10+-green)

## 功能

- 自动读取 dsh-cost-meter 插件的 `ledger.json` 数据
- **CLI 模式**：终端实时展示费用/用量（rich 表格 + 柱状图）
- **Web 模式**：浏览器可视化仪表盘（深色主题）
- 按模型 / 会话 / 日期分组统计
- 无 ledger 时自动展示 demo 数据

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
python -m token-dashboard web --port 8080
```
然后打开 http://localhost:8080

## 项目结构

```
token-dashboard/
├── token_dashboard/
│   ├── __init__.py      # 包信息
│   ├── __main__.py      # 入口
│   ├── parser.py        # ledger.json 解析器
│   ├── stats.py         # 统计计算
│   ├── cli.py           # 终端仪表盘 (rich)
│   └── webapp.py        # Flask Web 服务
├── web/
│   ├── index.html       # 前端页面
│   ├── style.css        # 深色主题样式
│   └── app.js           # 前端逻辑
├── requirements.txt
└── README.md
```

## 依赖

- Python 3.10+
- rich >= 13.0
- flask >= 3.0

## License

MIT
