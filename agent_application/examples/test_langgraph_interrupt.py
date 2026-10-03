from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt, Command
from typing import TypedDict


class State(TypedDict):
    message: str


def request_approval(state: State):
    print("\nNode started")

    answer = interrupt(
        "Do you want to continue?"
    )

    print("Human response:", answer)

    return {
        "message": answer
    }


builder = StateGraph(State)

builder.add_node(
    "request_approval",
    request_approval
)

builder.add_edge(
    START,
    "request_approval"
)

builder.add_edge(
    "request_approval",
    END
)


memory = MemorySaver()

graph = builder.compile(
    checkpointer=memory
)


config = {
    "configurable": {
        "thread_id": "interrupt-demo"
    }
}


print("=== First invoke ===")

result = graph.invoke(
    {
        "message": "Waiting for approval..."
    },
    config
)

print("\nInterrupted:")
print(result)


print("\n=== Resume ===")

result = graph.invoke(
    Command(resume="yes"),
    config
)

print("\nFinal Result:")
print(result)