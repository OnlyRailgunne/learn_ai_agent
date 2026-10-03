import json

from groq import Groq

client = Groq()

MODEL = "openai/gpt-oss-120b"


def analyst_agent(user_input):
    """Agent A：分析用户需求，生成结构化任务。"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "你是一个需求分析 Agent。"
                    "请将用户需求整理成 JSON 格式的任务描述。"
                    "必须包含 topic、task、requirements 三个字段。"
                    "requirements 必须是字符串列表。"
                    "只输出合法 JSON，不要输出 Markdown 代码块。"
                ),
            },
            {
                "role": "user",
                "content": user_input,
            },
        ],
    )

    task_json = response.choices[0].message.content

    task = json.loads(task_json)

    return task


def executor_agent(task):
    """Agent B：执行 Agent A 给出的任务。"""

    task_text = json.dumps(task, ensure_ascii=False)

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "你是一个任务执行 Agent。"
                    "请严格根据收到的 JSON 任务完成工作。"
                    "返回完整的执行结果。"
                ),
            },
            {
                "role": "user",
                "content": task_text,
            },
        ],
    )

    result = response.choices[0].message.content

    return result


def reviewer_agent(task, result):
    """Agent A：检查 Agent B 的结果，并生成最终回答。"""

    task_text = json.dumps(task, ensure_ascii=False)

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "你是一个结果审核 Agent。"
                    "请检查执行结果是否满足任务要求。"
                    "如果结果基本满足要求，就直接整理成最终回答。"
                    "如果存在明显问题，请修正后再输出。"
                    "只输出最终回答，不要解释审核过程。"
                ),
            },
            {
                "role": "user",
                "content": (
                    f"原始任务：\n{task_text}\n\n"
                    f"执行结果：\n{result}"
                ),
            },
        ],
    )

    final_result = response.choices[0].message.content

    return final_result


def main():
    user_input = "帮我分析一下远程办公的优缺点，并给出一个简短总结。"

    print("=== User Input ===")
    print(user_input)

    # 1. Agent A 创建任务
    task = analyst_agent(user_input)

    print("\n=== Agent A: Task ===")
    print(json.dumps(task, ensure_ascii=False, indent=2))

    # 2. Agent B 执行任务
    result = executor_agent(task)

    print("\n=== Agent B: Result ===")
    print(result)

    # 3. Agent A 接收 Agent B 的结果并审核
    final_result = reviewer_agent(task, result)

    print("\n=== Agent A: Final Result ===")
    print(final_result)


if __name__ == "__main__":
    main()