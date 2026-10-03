from agent_application.langgraph_agent import graph


messages = [
    {
        "role": "system",
        "content": (
            "You are a helpful assistant. "
            "Use the available tools when necessary."
        ),
    },
    {
        "role": "user",
        "content": "东京现在天气怎么样？",
    },
]


print("=== Streaming ===")

for event in graph.stream(
    {
        "messages": messages,
        "tool_calls": [],
    }
):
    print("\n--- Event ---")
    print(event)