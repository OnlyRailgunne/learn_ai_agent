import json
import os

from groq import Groq

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import MessagesState
from agent_application.basic_agent import current_weather

from langchain_core.messages import (
    HumanMessage,
    AIMessage,
    ToolMessage,
)


client = Groq(api_key=os.environ["GROQ_API_KEY"])


# =========================
# LLM Node
# =========================

def llm_node(state: MessagesState):
    messages = []

    for message in state["messages"]:

        if isinstance(message, HumanMessage):
            messages.append({
                "role": "user",
                "content": message.content,
            })

        elif isinstance(message, AIMessage):

            if message.tool_calls:
                tool_calls = []

                for tool_call in message.tool_calls:
                    tool_calls.append({
                        "id": tool_call["id"],
                        "type": "function",
                        "function": {
                            "name": tool_call["name"],
                            "arguments": json.dumps(
                                tool_call["args"]
                            ),
                        },
                    })

                messages.append({
                    "role": "assistant",
                    "content": message.content or "",
                    "tool_calls": tool_calls,
                })

            else:
                messages.append({
                    "role": "assistant",
                    "content": message.content,
                })

        elif isinstance(message, ToolMessage):
            messages.append({
                "role": "tool",
                "content": message.content,
                "tool_call_id": message.tool_call_id,
                "name": message.name,
            })

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=messages,
        tools=[
            {
                "type": "function",
                "function": {
                    "name": "current_weather",
                    "description": "Get the current weather for a city",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "city": {
                                "type": "string",
                                "description": "City name",
                            }
                        },
                        "required": ["city"],
                    },
                },
            }
        ],
    )

    message = response.choices[0].message

    if message.tool_calls:

        tool_call = message.tool_calls[0]

        print("LLM requested tool:", tool_call.function.name)
        print("Arguments:", tool_call.function.arguments)

        return {
            "messages": [
                AIMessage(
                    content=message.content or "",
                    tool_calls=[
                        {
                            "name": tool_call.function.name,
                            "args": json.loads(
                                tool_call.function.arguments
                            ),
                            "id": tool_call.id,
                            "type": "tool_call",
                        }
                    ],
                )
            ]
        }

    return {
        "messages": [
            AIMessage(
                content=message.content or ""
            )
        ]
    }


# =========================
# Tool Node
# =========================

def weather_tool_node(state: MessagesState):

    tool_call = state["messages"][-1].tool_calls[0]

    city = tool_call["args"]["city"]

    # 暂时模拟天气 Tool
    weather_result = current_weather(city)

    print("Tool executed:", city)
    print("tool result:", weather_result)

    return {
        "messages": [
            ToolMessage(
                content=weather_result,
                tool_call_id=tool_call["id"],
                name=tool_call["name"],
            )
        ]
    }


# =========================
# Conditional Edge
# =========================

def should_continue(state: MessagesState):

    last_message = state["messages"][-1]

    if isinstance(last_message, AIMessage):
        if last_message.tool_calls:
            return "tool"

    return "end"


# =========================
# Build Graph
# =========================

builder = StateGraph(MessagesState)

builder.add_node("llm", llm_node)
builder.add_node("weather_tool", weather_tool_node)

builder.add_edge(
    START,
    "llm",
)

builder.add_conditional_edges(
    "llm",
    should_continue,
    {
        "tool": "weather_tool",
        "end": END,
    },
)

builder.add_edge(
    "weather_tool",
    "llm",
)


graph = builder.compile()


# =========================
# Run
# =========================

result = graph.invoke(
    {
        "messages": [
            HumanMessage(
                content="东京现在天气怎么样？"
            )
        ]
    }
)


print("\n=== messages ===")

for message in result["messages"]:

    print(
        type(message).__name__,
        ":",
        message.content,
    )