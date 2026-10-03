from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import MessagesState
from langchain_core.messages import HumanMessage, AIMessage
from groq import Groq
import os


client = Groq(api_key=os.environ["GROQ_API_KEY"])


def llm_node(state: MessagesState):
    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {
                "role": "user",
                "content": state["messages"][-1].content,
            }
        ],
    )

    return {
        "messages": [
            AIMessage(content=response.choices[0].message.content)
        ]
    }


builder = StateGraph(MessagesState)

builder.add_node("llm", llm_node)

builder.add_edge(START, "llm")
builder.add_edge("llm", END)

graph = builder.compile()


result = graph.invoke(
    {
        "messages": [
            HumanMessage(content="用一句话介绍一下 LangGraph")
        ]
    }
)


for message in result["messages"]:
    print(type(message).__name__, ":", message.content)