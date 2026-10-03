from typing import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt, Command


class State(TypedDict):
    city: str
    approved: bool
    weather: str


def tool_request(state: State):
    print("\n=== Tool Request ===")
    print(f"Agent wants to call current_weather({state['city']})")

    return {}


def approval(state: State):
    print("\n=== Approval ===")

    answer = interrupt(
        f"Allow weather tool for {state['city']}?"
    )

    print("Human response:", answer)

    return {
        "approved": answer == "yes"
    }


def weather_tool(state: State):
    print("\n=== Tool Execution ===")

    if not state["approved"]:
        print("Tool execution denied.")

        return {
            "weather": "Tool execution denied."
        }

    print(f"Calling weather tool for {state['city']}")

    return {
        "weather": f"{state['city']} weather: 23°C"
    }


builder = StateGraph(State)

builder.add_node(
    "tool_request",
    tool_request
)

builder.add_node(
    "approval",
    approval
)

builder.add_node(
    "weather_tool",
    weather_tool
)

builder.add_edge(
    START,
    "tool_request"
)

builder.add_edge(
    "tool_request",
    "approval"
)

builder.add_edge(
    "approval",
    "weather_tool"
)

builder.add_edge(
    "weather_tool",
    END
)


memory = MemorySaver()

graph = builder.compile(
    checkpointer=memory
)


config = {
    "configurable": {
        "thread_id": "tool-approval-demo"
    }
}


print("=== First invoke ===")

result = graph.invoke(
    {
        "city": "Tokyo",
        "approved": False,
        "weather": "",
    },
    config
)

print("\nInterrupted:")
print(result)


print("\n=== Resume ===")

result = graph.invoke(
    Command(resume="no"),
    config
)

print("\nFinal Result:")
print(result)