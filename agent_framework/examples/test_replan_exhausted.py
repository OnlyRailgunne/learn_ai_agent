from core.runtime import Runtime
from core.state import State
from core.context import ExecutionContext
from core.result import NodeResult
from core.decision import Decision
from core.policy import Policy
from core.history import History

from graph.graph import Graph
from graph.node import Node


class StartNode(Node):

    def __init__(self, name):
        self.name = name

    def run(self, state):
        print("B running")

        state.set("base", 100)

        result = NodeResult()
        result.success = True
        result.output = "B success"

        return result


class FailNode(Node):

    def __init__(self, name):
        self.name = name

    def run(self, state):
        print(self.name, "running")

        state.set(
            "last_failed",
            self.name
        )

        result = NodeResult()
        result.success = False
        result.output = self.name + " failed"

        return result


node_b = StartNode("B")
node_c = FailNode("C")
node_d = FailNode("D")


graph = Graph()

graph.connect(
    node_b,
    node_c
)

graph.connect(
    node_b,
    node_d
)


state = State()

context = ExecutionContext(
    graph=graph,
    state=state,
    current_node=node_b
)


history = History()


runtime = Runtime(
    decision=Decision(),
    policy=Policy(),
    history=history
)


result = runtime.run(
    context
)


print()
print("===== Runtime Result =====")

print(
    "runtime success:",
    result.success
)

print(
    "final state:",
    context.state.export()
)


print()
print("===== History =====")

for index, event in enumerate(history.events):

    print(
        index,
        type(event).__name__,
        getattr(
            getattr(event, "node", None),
            "name",
            ""
        )
    )