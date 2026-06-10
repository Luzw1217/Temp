# ReAct Demo

ReAct（Reasoning + Acting）循环演示项目。

## ReAct 原理

ReAct 是将 **推理（Reasoning）** 与 **行动（Acting）** 融合的提示技术，核心循环为：

```
Thought → Action → Observation → Thought → Action → Observation → ... → Final Answer
```

- **Thought**：模型分析当前状态，决定下一步做什么
- **Action**：调用某个工具（如计算器、搜索 API）
- **Observation**：获取工具返回的观察结果
- 重复直到得到最终答案

## 项目结构

```
react_demo/
├── main.py          # 命令行版演示
├── web_app.py       # Flask 网页版（实时刷新每一步）
├── requirements.txt
├── readme.md
└── templates/
    └── index.html   # 前端页面
```

## 安装依赖

```bash
pip install flask
```

## 运行

### 命令行版

```bash
python main.py
```

### 网页版

```bash
python web_app.py
```

然后访问：http://127.0.0.1:5000

## 测试问题

> "今天是 2026-06-09，3 天后是几号？那天距离 2026-12-31 还有多少天？"

预期 ReAct 推理路径：

1. Thought：需要先确定今天日期 → Action：`date` → Observation：`2026-06-09`
2. Thought：计算 3 天后日期 → Action：`calc(2026-06-09 + 3)` → Observation：`2026-06-12`
3. Thought：计算到 2026-12-31 的天数 → Action：`calc(days(2026-06-12, 2026-12-31))` → Observation：`202 天`
4. Final Answer：3 天后是 2026-06-12，距离 2026-12-31 还有 202 天
