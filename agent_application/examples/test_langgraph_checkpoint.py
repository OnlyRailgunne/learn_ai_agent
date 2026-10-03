from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import MessagesState


def agent_node(state: MessagesState):
    print("Node received:", state)

    return {
        "messages": state["messages"]
    }


builder = StateGraph(MessagesState)

builder.add_node("agent", agent_node)

builder.add_edge(START, "agent")
builder.add_edge("agent", END)


memory = MemorySaver()

graph = builder.compile(
    checkpointer=memory
)


config = {
    "configurable": {
        "thread_id": "session-1"
    }
}


print("\n=== First Run ===")

result = graph.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": "Hello, my name is Tom."
            }
        ]
    },
    config
)

print("Result:", result)


print("\n=== Second Run ===")

result = graph.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": "What is my name?"
            }
        ]
    },
    config
)

print("Result:", result)