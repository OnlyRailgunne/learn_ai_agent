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
# B
#
# 初始成功 Node
# =========================================================

class StartNode(Node):

    def __init__(self, name):
        self.name = name

    def run(self, state):

        print("B running")

        # 这个值会进入 Snapshot
        state.set(
            "mode",
            "E"
        )

        state.set(
            "base",
            100
        )

        result = NodeResult()

        result.success = True
        result.output = "B success"

        return result


# =========================================================
# C
#
# 第一条正常路线
#
# 会失败并污染 State
# =========================================================

class FailNode(Node):

    def __init__(self, name):
        self.name = name

    def run(self, state):

        print(
            self.name,
            "running"
        )

        # 故意污染当前 State
        state.set(
            "dirty",
            True
        )

        print(
            self.name,
            "changed state:",
            state.export()
        )

        result = NodeResult()

        result.success = False
        result.output = (
            self.name + " failed"
        )

        return result


# =========================================================
# D
#
# condition 不满足
#
# 如果 D 被运行，
# 说明 Replanner condition 判断错误
# =========================================================

class ForbiddenNode(Node):

    def __init__(self, name):
        self.name = name

    def run(self, state):

        print(
            "ERROR:",
            self.name,
            "should not run"
        )

        result = NodeResult()

        result.success = True
        result.output = "unexpected"

        return result


# =========================================================
# E
#
# condition 满足
#
# Replanner 应该选择这里
# =========================================================

class SuccessNode(Node):

    def __init__(self, name):
        self.name = name

    def run(self, state):

        print("E running")

        print(
            "E sees mode:",
            state.get("mode")
        )

        print(
            "E sees dirty:",
            state.get("dirty")
        )

        print(
            "E sees state:",
            state.export()
        )

        result = NodeResult()

        result.success = True
        result.output = "E success"

        return result


# =========================================================
# Edge Conditions
# =========================================================

def allow_d(state):

    return (
        state.get("mode")
        == "D"
    )


def allow_e(state):

    return (
        state.get("mode")
        == "E"
    )


# =========================================================
# Nodes
# =========================================================

node_b = StartNode("B")

node_c = FailNode("C")

node_d = ForbiddenNode("D")

node_e = SuccessNode("E")

end_node = EndNode("End")


# =========================================================
# Graph
#
# B
# ├── C      无条件，第一次正常执行一定走这里
# ├── D      condition: mode == D
# └── E      condition: mode == E
#
# E → End
#
#
# B 执行后：
#
# mode == E
#
# 所以：
#
# B → C
# C failed
#
# Replan 时：
#
# C 已尝试
# D condition=False
# E condition=True
#
# 应选择：
#
# E
# =========================================================

graph = Graph()


# 第一条必须是 C
# 正常 Graph.next() 会先走这里

graph.connect(
    node_b,
    node_c
)


# D 在当前 Snapshot State 下不可走

graph.connect(
    node_b,
    node_d,
    condition=allow_d
)


# E 在当前 Snapshot State 下可以走

graph.connect(
    node_b,
    node_e,
    condition=allow_e
)


graph.connect(
    node_e,
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

print(
    "===== Runtime Result ====="
)

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

print(
    "===== History ====="
)

for index, event in enumerate(
    history.events
):

    event_type = (
        type(event).__name__
    )

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

    elif event_type == "PlanningChoiceEvent":

        print(
            index,
            event_type,
            event.source.name,
            "=>",
            event.target.name
        )


# =========================================================
# Snapshots
# =========================================================

print()

print(
    "===== Snapshots ====="
)

for (
    event_index,
    snapshot
) in history.snapshots.items():

    print(
        event_index,
        snapshot.data
    )