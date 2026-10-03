
import json
from groq import Groq

from agent_application.basic_agent import MODEL
from agent_application.tools.weather import current_weather
from agent_application.tools.exchange import exchange_rate

client = Groq()


# =========================
# 1. 可用工具
# =========================

AVAILABLE_TOOLS = {
    "current_weather": {
        "description": "查询指定城市的当前天气",
        "arguments": {"city": "城市名称，例如 Tokyo"},
    },
    "exchange_rate": {
        "description": "查询两种货币之间的汇率",
        "arguments": {
            "base": "基础货币，例如 USD",
            "target": "目标货币，例如 EUR",
        },
    },
}

TOOL_REGISTRY = {
    "current_weather": current_weather,
    "exchange_rate": exchange_rate,
}


# =========================
# 2. Planning
# =========================

def create_plan(user_goal: str):
    print("\n========== Planning ==========")

    tool_info = json.dumps(
        AVAILABLE_TOOLS,
        ensure_ascii=False,
        indent=2,
    )

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "你是一个任务规划助手。"
                    "根据用户目标生成有明确先后顺序的任务计划。"
                    "只能使用提供的工具。"
                    "如果任务需要调用工具，type 设置为 tool，"
                    "并填写 tool 和 arguments。"
                    "如果任务需要 LLM 分析，type 设置为 llm，"
                    "tool 设置为 null，arguments 设置为空对象。"
                    "只返回 JSON，不要添加其他内容。\n\n"
                    "可用工具：\n"
                    f"{tool_info}\n\n"
                    "JSON 格式："
                    '{"goal":"目标","tasks":['
                    '{"id":1,"task":"任务描述",'
                    '"type":"tool","tool":"current_weather",'
                    '"arguments":{"city":"Tokyo"}}]}'
                ),
            },
            {"role": "user", "content": user_goal},
        ],
        response_format={"type": "json_object"},
    )

    plan = json.loads(response.choices[0].message.content)

    print("Generated Plan:")
    print(json.dumps(plan, ensure_ascii=False, indent=2))

    return plan


# =========================
# 3. Plan Validation
# =========================

def validate_plan(plan: dict):
    print("\n========== Plan Validation ==========")

    tasks = plan.get("tasks", [])
    if not tasks:
        print("Plan validation failed: tasks is empty")
        return False

    for task in plan["tasks"]:
        if task["type"] == "tool":
            tool_name = task["tool"]

            if tool_name not in AVAILABLE_TOOLS:
                raise ValueError(f"Unknown tool: {tool_name}")

            print(f"Task {task['id']}: tool '{tool_name}' exists")

        elif task["type"] == "llm":
            print(f"Task {task['id']}: LLM task")

        else:
            raise ValueError(f"Unknown task type: {task['type']}")

    print("Plan validation passed.")


# =========================
# 4. 执行单个任务
# =========================

def execute_task(task: dict, results: dict):
    task_type = task["type"]

    if task_type == "tool":
        tool_name = task["tool"]
        arguments = task["arguments"]

        tool_function = TOOL_REGISTRY[tool_name]

        print(f"\nExecuting tool: {tool_name}")
        print(f"Arguments: {arguments}")

        result = tool_function(**arguments)

        print("Tool result:")
        print(result)

        return result

    elif task_type == "llm":
        print(f"\nExecuting LLM task: {task['task']}")

        previous_results = json.dumps(
            results,
            ensure_ascii=False,
            indent=2,
        )

        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "你是一个任务执行助手。"
                        "请根据用户提供的任务和之前的执行结果完成任务。"
                        "不要编造执行结果中没有的信息。"
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"当前任务：{task['task']}\n\n"
                        f"之前的执行结果：\n{previous_results}"
                    ),
                },
            ],
        )

        result = response.choices[0].message.content

        print("LLM result:")
        print(result)

        return result

    else:
        raise ValueError(f"Unknown task type: {task_type}")


# =========================
# 5. 线性执行器
# =========================

def execute_plan(plan: dict, previous_results: dict = None):
    print("\n========== Dynamic Execution ==========")

    # 保留之前的结果，避免重规划时丢失历史数据
    results = dict(previous_results or {})

    for task in plan["tasks"]:
        result = execute_task(task, results)

        results[task["id"]] = result

    print("\n========== Execution Results ==========")
    print(json.dumps(results, ensure_ascii=False, indent=2))

    return results


# =========================
# 6. Evaluation
# =========================

def evaluate_result(user_goal: str, results: dict):
    print("\n========== Evaluation ==========")

    results_text = json.dumps(
        results,
        ensure_ascii=False,
        indent=2,
    )

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "你是一个任务结果评估助手。"
                    "请根据用户目标和执行结果，判断目标是否已经满足。"
                    "如果目标已经满足，success 设置为 true。"
                    "如果目标没有满足，success 设置为 false，"
                    "并说明尚未完成的部分。"
                    "只返回 JSON，不要添加其他内容。\n\n"
                    "JSON 格式："
                    '{"success":true,"reason":"目标已经完成"}'
                ),
            },
            {
                "role": "user",
                "content": (
                    f"用户目标：{user_goal}\n\n"
                    f"执行结果：\n{results_text}"
                ),
            },
        ],
        response_format={"type": "json_object"},
    )

    evaluation = json.loads(
        response.choices[0].message.content
    )

    print("Evaluation Result:")
    print(json.dumps(evaluation, ensure_ascii=False, indent=2))

    return evaluation


# =========================
# 7. Replanning
# =========================


def replan(
    user_goal: str,
    evaluation: dict,
    previous_plan: dict,
    previous_results: dict,
):
    print("\n========== Replanning ==========")

    # 1. 整理历史执行结果
    results_text = json.dumps(
        previous_results,
        ensure_ascii=False,
        indent=2,
    )

    # 2. 整理评估结果
    evaluation_text = json.dumps(
        evaluation,
        ensure_ascii=False,
        indent=2,
    )

    # 3. 整理可用工具信息
    tool_info = json.dumps(
        AVAILABLE_TOOLS,
        ensure_ascii=False,
        indent=2,
    )

    # 4. 将原计划中的任务与执行结果对应起来
    completed_tasks = []

    for task in previous_plan.get("tasks", []):
        task_id = str(task["id"])

        if task_id in previous_results:
            completed_tasks.append({
                "id": task["id"],
                "task": task["task"],
                "type": task["type"],
                "result": previous_results[task_id],
            })

    completed_tasks_text = json.dumps(
        completed_tasks,
        ensure_ascii=False,
        indent=2,
    )

    # 5. 请求 LLM 生成新计划
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "你是一个任务重新规划助手。"
                    "根据用户原始目标、评估结果和已完成任务，"
                    "只生成补全目标所必需的新任务。"
                    "已完成且结果有效的任务不得重复执行。"
                    "如果目标已经完成，返回空 tasks 列表。"
                    "只能使用提供的工具。"
                    "工具任务的 type 设置为 tool，"
                    "并填写 tool 和 arguments。"
                    "LLM 任务的 type 设置为 llm，"
                    "tool 设置为 null，arguments 设置为空对象。"
                    "只返回 JSON，不要添加其他内容。\n\n"
                    f"可用工具：\n{tool_info}\n\n"
                    "JSON 格式："
                    '{"goal":"目标","tasks":['
                    '{"id":1,"task":"任务描述",'
                    '"type":"llm","tool":null,"arguments":{}}]}'
                ),
            },
            {
                "role": "user",
                "content": (
                    f"用户原始目标：{user_goal}\n\n"
                    f"评估结果：\n{evaluation_text}\n\n"
                    f"已完成的任务：\n{completed_tasks_text}\n\n"
                    f"之前的执行结果：\n{results_text}"
                ),
            },
        ],
        response_format={"type": "json_object"},
    )

    # 6. 解析新计划
    new_plan = json.loads(
        response.choices[0].message.content
    )

    print("New Plan:")
    print(
        json.dumps(
            new_plan,
            ensure_ascii=False,
            indent=2,
        )
    )

    return new_plan

# =========================
# 8. 为新计划分配任务 ID
# =========================

def assign_new_task_ids(plan: dict, results: dict):
    existing_ids = [
        task_id
        for task_id in results
        if isinstance(task_id, int)
    ]

    next_id = max(existing_ids, default=0) + 1

    for task in plan["tasks"]:
        task["id"] = next_id
        next_id += 1

    print("\nReassigned task IDs:")
    print([task["id"] for task in plan["tasks"]])

    return plan


# =========================
# 9. 主流程：Evaluation + Replanning Loop
# =========================

if __name__ == "__main__":
    user_goal = (
        "帮我查询东京当前天气，"
        "根据天气分析适合的活动，"
        "最后给出活动建议。"
    )

    max_replans = 2
    replan_count = 0

    # 第一次 Planning
    plan = create_plan(user_goal)
    validate_plan(plan)

    # 第一次 Execution
    results = execute_plan(plan)

    # 第一次 Evaluation
    evaluation = evaluate_result(user_goal, results)

    evaluation["success"] = False
    evaluation["reason"] = "临时测试重规划流程"

    # 评估失败时，自动重规划并再次执行
    while (
        not evaluation["success"]
        and replan_count < max_replans
    ):
        replan_count += 1

        print(
            f"\n========== Replan Round "
            f"{replan_count}/{max_replans} =========="
        )

        # 生成新计划
        new_plan = replan(
            user_goal,
            evaluation,
            plan,
            results,
        )

        validate_plan(new_plan)

        # 为新任务分配不重复的 ID
        new_plan = assign_new_task_ids(
            new_plan,
            results,
        )

        # 执行新计划，并保留历史结果
        results = execute_plan(
            new_plan,
            previous_results=results,
        )

        # 再次评估
        evaluation = evaluate_result(
            user_goal,
            results,
        )


    # 最终结果
    print("\n========== Final Result ==========")
    print("Success:", evaluation["success"])
    print("Reason:", evaluation["reason"])
    print("Replan Count:", replan_count)

    print("\nAll Results:")
    print(json.dumps(results, ensure_ascii=False, indent=2))