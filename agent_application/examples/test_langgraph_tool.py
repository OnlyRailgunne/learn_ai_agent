from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import MessagesState
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from groq import Groq
import os


client = Groq(api_key=os.environ["GROQ_API_KEY"])


def llm_node(state: MessagesState):
    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {
                "role": "user",
                "content": state["messages"][0].content,
            }
        ],
    )

    return {
        "messages": [
            AIMessage(content=response.choices[0].message.content)
        ]
    }


def weather_tool_node(state: MessagesState):
    # 这里暂时模拟 Tool 执行
    weather_result = "东京现在 23°C，晴天"

    return {
        "messages": [
            ToolMessage(
                content=weather_result,
                tool_call_id="weather-1",
            )
        ]
    }


builder = StateGraph(MessagesState)

builder.add_node("llm", llm_node)
builder.add_node("weather_tool", weather_tool_node)

builder.add_edge(START, "llm")
builder.add_edge("llm", "weather_tool")
builder.add_edge("weather_tool", END)

graph = builder.compile()


result = graph.invoke(
    {
        "messages": [
            HumanMessage(content="东京现在天气怎么样？")
        ]
    }
)


for message in result["messages"]:
    print(type(message).__name__, ":", message.content)