import sqlite3
import sys

from langgraph.graph import StateGraph, START, END
from langgraph.graph import MessagesState
from langgraph.checkpoint.sqlite import SqliteSaver


DB_PATH = "agent_checkpoint.db"

config = {
    "configurable": {
        "thread_id": "session-1"
    }
}


def agent_node(state: MessagesState):
    print("\nNode received:")

    for message in state["messages"]:
        print(f"{message.type}: {message.content}")

    return {}


def create_graph():
    conn = sqlite3.connect(
        DB_PATH,
        check_same_thread=False,
    )

    memory = SqliteSaver(conn)

    builder = StateGraph(MessagesState)

    builder.add_node("agent", agent_node)

    builder.add_edge(START, "agent")
    builder.add_edge("agent", END)

    graph = builder.compile(
        checkpointer=memory
    )

    return graph


def save():
    graph = create_graph()

    print("=== SAVE ===")

    result = graph.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "Hello, my name is Tom.",
                }
            ]
        },
        config,
    )

    print("\nSaved State:")
    print(result)


def load():
    graph = create_graph()

    print("=== LOAD ===")

    state = graph.get_state(config)

    print("\nRestored State:")
    print(state.values)


if len(sys.argv) != 2:
    print("Usage:")
    print("  python -m agent_application.examples.test_langgraph_sqlite_checkpoint save")
    print("  python -m agent_application.examples.test_langgraph_sqlite_checkpoint load")
    sys.exit(1)


mode = sys.argv[1]

if mode == "save":
    save()
elif mode == "load":
    load()
else:
    print("Unknown mode:", mode)