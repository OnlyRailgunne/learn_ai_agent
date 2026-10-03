from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import MessagesState
from langchain_core.messages import HumanMessage, AIMessage


def add_message(state: MessagesState):
    return {
        "messages": [
            AIMessage(content="Hello from LangGraph")
        ]
    }


builder = StateGraph(MessagesState)

builder.add_node("add_message", add_message)

builder.add_edge(START, "add_message")
builder.add_edge("add_message", END)

graph = builder.compile()


result = graph.invoke({
    "messages": [
        HumanMessage(content="Hello")
    ]
})


for message in result["messages"]:
    print(type(message).__name__, ":", message.content)