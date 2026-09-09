from core.runtime import Runtime
from core.state import State
from core.context import ExecutionContext
from core.result import NodeResult
from core.decision import Decision
from core.policy import Policy
from core.history import History

from graph.graph import Graph
from graph.node import Node
from graph.end_node import EndNode


# =========================================================
# B：第一层分叉点
#
# B
# ├── C
# └── F
# =========================================================

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


# =========================================================
# C：第二层分叉点
#
# C
# ├── D
# └── E
# =========================================================

class BranchNode(Node):

    def __init__(self, name):
        self.name = name

    def run(self, state):

        print("C running")

        state.set("branch", "C")

        result = NodeResult()
        result.success = True
        result.output = "C success"

        return result


# =========================================================
# D / E：都失败
# =========================================================

class FailNode(Node):

    def __init__(self, name):
        self.name = name

    def run(self, state):

        print(self.name, "running")

        # 故意污染 State
        state.set(
            "failed_at",
            self.name
        )

        print(
            self.name,
            "changed state:",
            state.export()
        )

        result = NodeResult()
        result.success = False
        result.output = self.name + " failed"

        return result


# =========================================================
# F：B 的备用路线，最终成功
# =========================================================

class SuccessNode(Node):

    def __init__(self, name):
        self.name = name

    def run(self, state):

        print("F running")

        print(
            "F sees state:",
            state.export()
        )

        result = NodeResult()
        result.success = True
        result.output = "F success"

        return result


# =========================================================
# Node
# =========================================================

node_b = StartNode("B")
node_c = BranchNode("C")

node_d = FailNode("D")
node_e = FailNode("E")

node_f = SuccessNode("F")

end_node = EndNode("End")


# =========================================================
# Graph
#
#        ┌── D failed
# B → C ┤
# │      └── E failed
# │
# └── F → End
#
# Edge 顺序非常重要：
#
# B 首先选择 C
# C 首先选择 D
# =========================================================

graph = Graph()

graph.connect(
    node_b,
    node_c
)

graph.connect(
    node_b,
    node_f
)

graph.connect(
    node_c,
    node_d
)

graph.connect(
    node_c,
    node_e
)

graph.connect(
    node_f,
    end_node
)


# =========================================================
# State
# =========================================================

state = State()


# =========================================================
# Context
# =========================================================

context = ExecutionContext(
    graph=graph,
    state=state,
    current_node=node_b
)


# =========================================================
# History
# =========================================================

history = History()


# =========================================================
# Runtime
# =========================================================

runtime = Runtime(
    decision=Decision(),
    policy=Policy(),
    history=history
)


# =========================================================
# Run
# =========================================================

result = runtime.run(
    context
)


# =========================================================
# Runtime Result
# =========================================================

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


# =========================================================
# History
# =========================================================

print()
print("===== History =====")

for index, event in enumerate(history.events):

    event_type = type(event).__name__

    if event_type == "NodeExecutionEvent":

        print(
            index,
            event_type,
            event.node.name,
            event.result.success
        )

    elif event_type == "TransitionEvent":

        source_name = (
            event.source.name
            if event.source is not None
            else "None"
        )

        target_name = (
            event.target.name
            if event.target is not None
            else "None"
        )

        print(
            index,
            event_type,
            source_name,
            "->",
            target_name
        )


# =========================================================
# Snapshots
# =========================================================

print()
print("===== Snapshots =====")

for event_index, snapshot in history.snapshots.items():

    print(
        event_index,
        snapshot.data
    )