import json
from typing import TypedDict

from groq import Groq

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt, Command

from agent_application.tool_schemas import tool_schemas
from agent_application.tools.weather import current_weather


client = Groq()

MODEL = "openai/gpt-oss-120b"


available_tools = {
    "current_weather": current_weather,
}


class State(TypedDict):
    messages: list
    tool_calls: list
    approved: bool


def llm_node(state: State):

    print("\n=== LLM ===")

    response = client.chat.completions.create(
        model=MODEL,
        messages=state["messages"],
        tools=tool_schemas,
        tool_choice="auto",
    )

    message = response.choices[0].message

    # =========================
    # No tool call
    # =========================

    if not message.tool_calls:

        print("LLM returned final answer.")

        assistant_message = {
            "role": "assistant",
            "content": message.content,
        }

        return {
            "messages": state["messages"]
            + [assistant_message],
            "tool_calls": [],
        }

    # =========================
    # Tool call requested
    # =========================

    print("LLM requested tool.")

    tool_calls = []

    for tool_call in message.tool_calls:

        print(
            f"Tool: {tool_call.function.name}"
        )

        print(
            f"Arguments: "
            f"{tool_call.function.arguments}"
        )

        # Convert Groq SDK object
        # into normal Python dict
        tool_call_data = {
            "id": tool_call.id,
            "type": "function",
            "function": {
                "name": tool_call.function.name,
                "arguments": tool_call.function.arguments,
            },
        }

        tool_calls.append(tool_call_data)

    assistant_message = {
        "role": "assistant",
        "content": message.content,
        "tool_calls": tool_calls,
    }

    return {
        "messages": state["messages"]
        + [assistant_message],
        "tool_calls": tool_calls,
    }


def approval_node(state: State):

    print("\n=== Approval ===")

    tool_call = state["tool_calls"][0]

    tool_name = tool_call["function"]["name"]

    arguments = json.loads(
        tool_call["function"]["arguments"]
    )

    answer = interrupt(
        f"Allow {tool_name} with arguments {arguments}?"
    )

    print("Human response:", answer)

    return {
        "approved": answer == "yes"
    }


def tool_node(state: State):

    print("\n=== Tool ===")

    if not state["approved"]:

        print("Tool execution denied.")

        return {
            "messages": state["messages"]
            + [
                {
                    "role": "tool",
                    "content": "Tool execution denied.",
                }
            ]
        }

    tool_call = state["tool_calls"][0]

    tool_name = tool_call["function"]["name"]

    arguments = json.loads(
        tool_call["function"]["arguments"]
    )

    tool = available_tools[tool_name]

    result = tool(**arguments)

    print("Tool result:", result)

    return {
        "messages": state["messages"]
        + [
            {
                "role": "tool",
                "tool_call_id": tool_call["id"],
                "name": tool_name,
                "content": str(result),
            }
        ]
    }


def route_after_llm(state: State):

    if state["tool_calls"]:
        return "approval"

    return END


# =========================
# Build Graph
# =========================

builder = StateGraph(State)

builder.add_node("llm", llm_node)
builder.add_node("approval", approval_node)
builder.add_node("tool", tool_node)

builder.add_edge(START, "llm")

builder.add_conditional_edges(
    "llm",
    route_after_llm,
    {
        "approval": "approval",
        END: END,
    },
)

builder.add_edge("approval", "tool")
builder.add_edge("tool", "llm")


# =========================
# Checkpoint
# =========================

memory = MemorySaver()

graph = builder.compile(
    checkpointer=memory
)


# =========================
# Config
# =========================

config = {
    "configurable": {
        "thread_id": "llm-tool-approval-demo"
    }
}


# =========================
# Initial Messages
# =========================

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


# =========================
# First Invoke
# =========================

print("=== First invoke ===")

result = graph.invoke(
    {
        "messages": messages,
        "tool_calls": [],
        "approved": False,
    },
    config,
)

print("\nResult:")
print(result)


# =========================
# Resume after interrupt
# =========================

if "__interrupt__" in result:

    print("\n=== Resume ===")

    result = graph.invoke(
        Command(resume="yes"),
        config,
    )

    print("\nResult after resume:")
    print(result)