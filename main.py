"""
命令行版 ReAct 演示。
演示如何用 Thought → Action → Observation 循环解决多步问题。
不依赖外部 LLM，用模拟逻辑保证稳定复现。
"""

from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Literal

# =====================================================================
# 工具定义
# =====================================================================

def date_tool() -> str:
    """返回今天的日期（固定为演示日期）。"""
    return "2026-06-09"


def calc_tool(expression: str) -> str:
    """计算器工具，支持日期加减天数、日期差计算。

    支持格式：
      - date + N    ：日期加 N 天
      - days(date1, date2) ：计算两日期间天数
    """
    expression = expression.strip()

    # 日期 + 天数
    if "+" in expression:
        parts = expression.split("+")
        date_str = parts[0].strip()
        days = int(parts[1].strip())
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        result = dt + timedelta(days=days)
        return result.strftime("%Y-%m-%d")

    # 两日期间天数
    if "," in expression:
        parts = expression.replace(" ", "").split(",")
        date1 = datetime.strptime(parts[0], "%Y-%m-%d")
        date2 = datetime.strptime(parts[1], "%Y-%m-%d")
        return str(abs((date2 - date1).days))

    # 普通算术表达式（安全 eval，仅允许数字和基本运算符）
    allowed = set("0123456789+-*/().")
    if all(c in allowed for c in expression):
        result = eval(expression)  # noqa: S307
        return str(int(result) if result == int(result) else result)
    return "不支持的表达式"


TOOLS = {
    "date": date_tool,
    "calc": calc_tool,
}

# =====================================================================
# ReAct 循环核心
# =====================================================================

@dataclass
class Step:
    """ReAct 循环中的单一步骤。"""
    thought: str
    action_type: Literal["date", "calc", "final"]
    action_input: str
    observation: str


def run_react(question: str, max_steps: int = 6) -> list[Step]:
    """执行 ReAct 循环，返回每一步的记录。

    本实现使用预定义逻辑模拟 ReAct 行为，
    实际 LLM 调用时只需替换 react_step 函数即可。
    """
    steps = []
    context: dict = {}  # 存放中间结果，供后续推理使用

    # 预定义的 ReAct 轨迹
    # 实际使用 LLM 时，这里会替换为 LLM 生成逻辑
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
            "thought": (
                "今天日期是 {today}。"
                "现在计算 3 天后的日期，使用 calc 工具。"
            ),
            "action_type": "calc",
            "action_input": "{today} + 3",
            "extract": "three_days_later",
        },
        {
            "thought": (
                "3 天后是 {three_days_later}。"
                "现在需要计算 {three_days_later} 距离 2026-12-31 还有多少天，"
                "使用 calc 工具计算日差。"
            ),
            "action_type": "calc",
            "action_input": "{three_days_later}, 2026-12-31",
            "extract": "days_remaining",
        },
        {
            "thought": (
                "从 {three_days_later} 到 2026-12-31 一共 {days_remaining} 天。"
                "现在可以给出最终答案了。"
            ),
            "action_type": "final",
            "action_input": "",
            "extract": None,
        },
    ]

    for i, step_def in enumerate(plan):
        if i >= max_steps:
            break

        thought = step_def["thought"]

        if step_def["action_type"] == "final":
            steps.append(Step(
                thought=thought,
                action_type="final",
                action_input="",
                observation="（已得到所有中间结果，可生成最终答案）",
            ))
            break

        action_type = step_def["action_type"]
        action_input = step_def["action_input"]

        # 替换上下文占位符
        for key, val in context.items():
            thought = thought.replace(f"{{{key}}}", str(val))
            action_input = action_input.replace(f"{{{key}}}", str(val))

        # 调用工具
        if action_type == "date":
            observation = TOOLS["date"]()
        elif action_type == "calc":
            observation = TOOLS["calc"](action_input)
        else:
            observation = ""

        # 存入上下文
        context[step_def["extract"]] = observation

        steps.append(Step(
            thought=thought,
            action_type=action_type,
            action_input=action_input,
            observation=observation,
        ))

    return steps


# =====================================================================
# 演示
# =====================================================================

QUESTION = (
    "今天是 2026-06-09，"
    "3 天后是几号？那天距离 2026-12-31 还有多少天？"
)


def print_react_trace(steps: list[Step], question: str) -> None:
    """格式化打印 ReAct 推理轨迹。"""
    print("=" * 60)
    print("ReAct 演示")
    print("=" * 60)
    print(f"问题：{question}\n")

    for i, step in enumerate(steps, 1):
        if step.action_type == "final":
            print(f"▶ Step {i} — Final Answer")
            print(f"  {step.thought}")
            print(f"  【最终答案】")
            print(f"  3 天后是 {steps[1].observation}，")
            print(f"  距离 2026-12-31 还有 {steps[2].observation} 天。")
        else:
            print(f"▶ Step {i}")
            print(f"  Thought：{step.thought}")
            print(f"  Action：{step.action_type}({step.action_input or '()'})")
            print(f"  Observation：{step.observation}")
        print()


def main() -> None:
    print("\n开始 ReAct 推理演示...")
    steps = run_react(QUESTION)
    print_react_trace(steps, QUESTION)


if __name__ == "__main__":
    main()

'''
第三次修改测试
'''
