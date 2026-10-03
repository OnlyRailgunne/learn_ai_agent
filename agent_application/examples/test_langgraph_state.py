from typing import TypedDict

from langgraph.graph import StateGraph, START, END


class State(TypedDict):
    count: int


def counter_node(state: State):
    new_count = state["count"] + 1

    print("Counter:", new_count)

    return {
        "count": new_count
    }


def should_continue(state: State):
    if state["count"] < 3:
        return "continue"

    return "end"


builder = StateGraph(State)

builder.add_node("counter", counter_node)

builder.add_edge(START, "counter")

builder.add_conditional_edges(
    "counter",
    should_continue,
    {
        "continue": "counter",
        "end": END,
    },
)

graph = builder.compile()


result = graph.invoke({
    "count": 0
})

print("Final state:", result)