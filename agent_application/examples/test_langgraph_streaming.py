from typing import TypedDict

from langgraph.graph import StateGraph, START, END


class State(TypedDict):
    message: str


def node_a(state: State):
    print("=== node_a executing ===")

    return {
        "message": state["message"] + " -> A"
    }


def node_b(state: State):
    print("=== node_b executing ===")

    return {
        "message": state["message"] + " -> B"
    }


builder = StateGraph(State)

builder.add_node("node_a", node_a)
builder.add_node("node_b", node_b)

builder.add_edge(START, "node_a")
builder.add_edge("node_a", "node_b")
builder.add_edge("node_b", END)

graph = builder.compile()


print("=== Streaming ===")

for event in graph.stream(
    {"message": "start"}
):
    print("Event:", event)