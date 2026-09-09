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
# B：正常执行
# =========================================================

class StartNode(Node):

    def __init__(self, name):
        self.name = name

    def run(self, state):

        print("B running")

        # B 正常产生的数据
        state.set(
            "base",
            100
        )

        result = NodeResult()
        result.success = True
        result.output = "B success"

        return result


# =========================================================
# C：故意失败，并污染 State
# =========================================================

class FailNode(Node):

    def __init__(self, name):
        self.name = name

    def run(self, state):

        print("C running")

        # 模拟 Node 执行过程中修改了 State
        state.set(
            "dirty",
            True
        )

        print(
            "C changed state:",
            state.export()
        )

        result = NodeResult()
        result.success = False
        result.output = "C failed"

        return result


# =========================================================
# D：Replan 后的新路线
# =========================================================

class SuccessNode(Node):

    def __init__(self, name):
        self.name = name

    def run(self, state):

        print("D running")

        print(
            "D sees base:",
            state.get("base")
        )

        print(
            "D sees dirty:",
            state.get("dirty")
        )

        print(
            "D sees state:",
            state.export()
        )

        result = NodeResult()
        result.success = True
        result.output = "D success"

        return result


# =========================================================
# 创建 Node
# =========================================================

node_b = StartNode(
    "B"
)

node_c = FailNode(
    "C"
)

node_d = SuccessNode(
    "D"
)

end_node = EndNode(
    "End"
)


# =========================================================
# 创建 Graph
#
#       ┌──> C (failed)
# B ────┤
#       └──> D ───> End
#
# 注意：
#
# B -> C 必须先 connect
#
# 因为 Graph.next() 当前是按 Edge 顺序选择，
# 所以第一次正常运行时会选择 C。
# =========================================================

graph = Graph()

graph.connect(
    node_b,
    node_c
)

graph.connect(
    node_b,
    node_d
)

graph.connect(
    node_d,
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
# Result
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

for index, event in enumerate(
    history.events
):
    print(
        index,
        type(event).__name__
    )


# =========================================================
# Snapshot
# =========================================================

print()
print("===== Snapshots =====")

for event_index, snapshot in history.snapshots.items():
    print(
        event_index,
        snapshot.data
    )