import json
from typing import TypedDict

from groq import Groq

from langgraph.config import get_stream_writer
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt

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


def llm_node(state: State):

    print("\n=== LLM ===")

    writer = get_stream_writer()

    response = client.chat.completions.create(
        model=MODEL,
        messages=state["messages"],
        tools=tool_schemas,
        tool_choice="auto",
        stream=True,
    )

    content_parts = []
    tool_calls = {}

    for chunk in response:

        delta = chunk.choices[0].delta

        if delta.content:

            print(
                delta.content,
                end="",
                flush=True
            )

            content_parts.append(
                delta.content
            )

            writer(
                {
                    "type": "token",
                    "content": delta.content,
                }
            )

        if delta.tool_calls:

            for tool_call in delta.tool_calls:

                index = tool_call.index

                if index not in tool_calls:

                    tool_calls[index] = {
                        "id": "",
                        "type": "function",
                        "function": {
                            "name": "",
                            "arguments": "",
                        },
                    }

                if tool_call.id:

                    tool_calls[index]["id"] = (
                        tool_call.id
                    )

                if tool_call.function:

                    if tool_call.function.name:

                        tool_calls[index][
                            "function"
                        ][
                            "name"
                        ] = tool_call.function.name

                    if tool_call.function.arguments:

                        tool_calls[index][
                            "function"
                        ][
                            "arguments"
                        ] += (
                            tool_call.function.arguments
                        )

    content = "".join(content_parts)

    if not tool_calls:

        print(
            "\nLLM returned final answer."
        )

        assistant_message = {
            "role": "assistant",
            "content": content,
        }

        return {
            "messages": (
                state["messages"]
                + [assistant_message]
            ),
            "tool_calls": [],
        }

    print(
        "\nLLM requested tool."
    )

    tool_call_list = list(
        tool_calls.values()
    )

    for tool_call in tool_call_list:

        tool_name = (
            tool_call["function"]["name"]
        )

        arguments = (
            tool_call["function"]["arguments"]
        )

        print(
            f"Tool: {tool_name}"
        )

        print(
            f"Arguments: {arguments}"
        )

        writer(
            {
                "type": "tool_call",
                "tool": tool_name,
                "arguments": arguments,
            }
        )

    assistant_message = {
        "role": "assistant",
        "content": content,
        "tool_calls": tool_call_list,
    }

    return {
        "messages": (
            state["messages"]
            + [assistant_message]
        ),
        "tool_calls": tool_call_list,
    }


def tool_node(state: State):

    print("\n=== Tool ===")

    writer = get_stream_writer()

    tool_call = state["tool_calls"][0]

    tool_name = (
        tool_call["function"]["name"]
    )

    arguments = json.loads(
        tool_call["function"]["arguments"]
    )

    print(
        f"等待人工批准 Tool：{tool_name}"
    )

    approval = interrupt(
        {
            "type": "tool_approval",
            "tool": tool_name,
            "arguments": arguments,
        }
    )

    print(
        "人工审批结果：",
        approval
    )

    if not approval:

        writer(
            {
                "type": "tool_rejected",
                "tool": tool_name,
            }
        )

        return {
            "messages": (
                state["messages"]
                + [
                    {
                        "role": "tool",
                        "tool_call_id": tool_call["id"],
                        "name": tool_name,
                        "content": "Tool execution denied.",
                    }
                ]
            ),
            "tool_calls": [],
        }

    tool = available_tools[tool_name]

    result = tool(**arguments)

    print(
        "Tool result:",
        result
    )

    writer(
        {
            "type": "tool_result",
            "tool": tool_name,
            "content": str(result),
        }
    )

    tool_message = {
        "role": "tool",
        "tool_call_id": tool_call["id"],
        "name": tool_name,
        "content": str(result),
    }

    return {
        "messages": (
            state["messages"]
            + [tool_message]
        ),
        "tool_calls": [],
    }


def route_after_llm(state: State):

    if state["tool_calls"]:
        return "tool"

    return END


builder = StateGraph(State)

builder.add_node(
    "llm",
    llm_node
)

builder.add_node(
    "tool",
    tool_node
)

builder.add_edge(
    START,
    "llm"
)

builder.add_conditional_edges(
    "llm",
    route_after_llm,
    {
        "tool": "tool",
        END: END,
    },
)

builder.add_edge(
    "tool",
    "llm"
)


checkpointer = MemorySaver()

graph = builder.compile(
    checkpointer=checkpointer
)