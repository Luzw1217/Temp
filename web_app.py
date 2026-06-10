"""
Flask 网页版 ReAct 演示。
简化版：使用普通 AJAX 请求，不依赖 SSE。
"""

import json
from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

# =====================================================================
# 工具定义
# =====================================================================

from datetime import datetime, timedelta


def date_tool() -> str:
    return "2026-06-09"


def calc_tool(expression: str) -> str:
    expression = expression.strip()
    if "+" in expression:
        parts = expression.split("+")
        date_str = parts[0].strip()
        days = int(parts[1].strip())
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        result = dt + timedelta(days=days)
        return result.strftime("%Y-%m-%d")
    if "," in expression:
        parts = expression.replace(" ", "").split(",")
        date1 = datetime.strptime(parts[0], "%Y-%m-%d")
        date2 = datetime.strptime(parts[1], "%Y-%m-%d")
        return str(abs((date2 - date1).days))
    allowed = set("0123456789+-*/().")
    if all(c in allowed for c in expression):
        result = eval(expression)  # noqa: S307
        return str(int(result) if result == int(result) else result)
    return "不支持的表达式"


TOOLS = {"date": date_tool, "calc": calc_tool}

# =====================================================================
# ReAct 核心逻辑
# =====================================================================

def run_react():
    """执行 ReAct 循环，返回所有步骤。"""
    steps = []
    context = {}

    plan = [
        {
            "thought": (
                "问题要求计算「3 天后是几号」以及「距离 2026-12-31 还有多少天」。"
                "首先，我需要确认今天的日期。使用 date 工具获取。"
            ),
            "action_type": "date",
            "action_input": "",
            "extract": "today",
        },
        {
            "thought": "今天日期是 {today}。现在计算 3 天后的日期，使用 calc 工具。",
            "action_type": "calc",
            "action_input": "{today} + 3",
            "extract": "three_days_later",
        },
        {
            "thought": (
                "3 天后是 {three_days_later}。"
                "现在需要计算距离 2026-12-31 还有多少天，使用 calc 工具。"
            ),
            "action_type": "calc",
            "action_input": "{three_days_later}, 2026-12-31",
            "extract": "days_remaining",
        },
    ]

    for i, step_def in enumerate(plan, 1):
        thought = step_def["thought"]
        action_type = step_def["action_type"]
        action_input = step_def["action_input"]

        for key, val in context.items():
            thought = thought.replace(f"{{{key}}}", str(val))
            action_input = action_input.replace(f"{{{key}}}", str(val))

        if action_type == "date":
            observation = TOOLS["date"]()
        elif action_type == "calc":
            observation = TOOLS["calc"](action_input)
        else:
            observation = ""

        context[step_def["extract"]] = observation

        steps.append({
            "step": i,
            "thought": thought,
            "action_type": action_type,
            "action_input": action_input if action_input else "(无参数)",
            "observation": observation,
        })

    final_answer = (
        f"3 天后是 {context.get('three_days_later', '?')}，"
        f"距离 2026-12-31 还有 {context.get('days_remaining', '?')} 天。"
    )

    return {"steps": steps, "final_answer": final_answer}


# =====================================================================
# Flask 路由
# =====================================================================

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/react", methods=["POST"])
def api_react():
    try:
        result = run_react()
        return jsonify({"success": True, "data": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


if __name__ == "__main__":
    print("ReAct Web Demo 启动中...")
    print("访问地址：http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000, debug=False)
