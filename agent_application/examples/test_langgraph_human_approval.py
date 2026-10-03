from langgraph.types import Command

from agent_application.langgraph_agent import graph


config = {
    "configurable": {
        "thread_id": "approval-test-1"
    }
}


messages = [
    {
        "role": "user",
        "content": "东京现在天气怎么样？",
    }
]


print("=== 第一次执行 ===")

result = graph.invoke(
    {
        "messages": messages,
        "tool_calls": [],
    },
    config=config,
)

print("\n=== Graph 暂停 ===")
print(result)


print("\n=== 人工批准 ===")

result = graph.invoke(
    Command(resume=False),
    config=config,
)

print("\n=== Graph 恢复完成 ===")
print(result)