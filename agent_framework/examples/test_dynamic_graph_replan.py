from core.runtime import Runtime
from core.state import State
from core.context import ExecutionContext
from core.decision import Decision
from core.policy import Policy
from core.history import History
from core.result import NodeResult
from core.goal import Goal
from core.plan_evaluation_result import (
    PlanEvaluationResult
)

from graph.node import Node
from graph.graph import Graph
from graph.end_node import EndNode


# =====================================================
# 测试 Node
# =====================================================

class SuccessNode(Node):

    def __init__(
        self,
        name,
        state_key=None
    ):
        super().__init__(name)

        self.state_key = (
            state_key
        )


    def run(
        self,
        state
    ):

        print(
            self.name,
            "running"
        )

        if self.state_key is not None:

            state.set(
                self.state_key,
                True
            )

        result = NodeResult()

        result.success = True
        result.output = (
            self.name + " success"
        )

        return result


class FailNode(Node):

    def __init__(
        self,
        name,
        state_key=None
    ):
        super().__init__(name)

        self.state_key = (
            state_key
        )


    def run(
        self,
        state
    ):

        print(
            self.name,
            "running"
        )

        if self.state_key is not None:

            state.set(
                self.state_key,
                True
            )

        result = NodeResult()

        result.success = False
        result.output = (
            self.name + " failed"
        )

        return result


# =====================================================
# 测试 Planner
# =====================================================

class DynamicTestPlanner:

    def __init__(
        self,
        node_a,
        node_b,
        node_c,
        node_d,
        node_x,
        end_node
    ):

        self.node_a = node_a
        self.node_b = node_b
        self.node_c = node_c
        self.node_d = node_d
        self.node_x = node_x
        self.end_node = end_node

        self.graph_v2 = None
        self.graph_v3 = None


    def evaluate(
        self,
        goal,
        context,
        node_result,
        history
    ):

        # =================================================
        # A 成功后：
        #
        # Graph v1:
        #
        # A → End
        #
        # 改成 Graph v2:
        #
        # A → B
        #
        # B → C
        # B → D
        #
        # D → End
        # =================================================

        if (
            context.current_node
            is self.node_a
            and
            node_result.success
        ):

            graph = Graph()

            graph.connect(
                self.node_a,
                self.node_b
            )

            # C 必须先 connect，
            # 这样正常 graph.next(B)
            # 会先选择 C。

            graph.connect(
                self.node_b,
                self.node_c
            )

            graph.connect(
                self.node_b,
                self.node_d
            )

            graph.connect(
                self.node_d,
                self.end_node
            )

            self.graph_v2 = graph

            print(
                "evaluate:",
                self.node_a.name,
                "-> MODIFY ->",
                self.node_b.name
            )

            return PlanEvaluationResult(
                keep=False,
                graph=graph,
                target=self.node_b
            )


        # =================================================
        # C 成功后：
        #
        # 再次 MODIFY。
        #
        # Graph v3:
        #
        # C → X
        #
        # X 会失败。
        # =================================================

        if (
            context.current_node
            is self.node_c
            and
            node_result.success
        ):

            graph = Graph()

            graph.connect(
                self.node_c,
                self.node_x
            )

            self.graph_v3 = graph

            print(
                "evaluate:",
                self.node_c.name,
                "-> MODIFY ->",
                self.node_x.name
            )

            return PlanEvaluationResult(
                keep=False,
                graph=graph,
                target=self.node_x
            )


        # =================================================
        # 其他情况保持当前 Plan
        # =================================================

        print(
            "evaluate:",
            context.current_node.name,
            "-> KEEP"
        )

        return PlanEvaluationResult(
            keep=True
        )


# =====================================================
# 创建 Nodes
# =====================================================

node_a = SuccessNode(
    "A",
    "a"
)

node_b = SuccessNode(
    "B",
    "b"
)

node_c = SuccessNode(
    "C",
    "c"
)

node_d = SuccessNode(
    "D",
    "d"
)

node_x = FailNode(
    "X",
    "x"
)

end_node = EndNode(
    "End"
)


# =====================================================
# 初始 Graph v1
#
# A → End
# =====================================================

graph = Graph()

graph.connect(
    node_a,
    end_node
)


# =====================================================
# Goal
# =====================================================

goal = Goal(
    "dynamic graph replan test"
)


# =====================================================
# State / History / Planner
# =====================================================

state = State()

history = History()

planner = DynamicTestPlanner(
    node_a=node_a,
    node_b=node_b,
    node_c=node_c,
    node_d=node_d,
    node_x=node_x,
    end_node=end_node
)


# =====================================================
# Context
# =====================================================

context = ExecutionContext(
    graph=graph,
    state=state,
    current_node=node_a,
    goal=goal
)


# =====================================================
# Runtime
# =====================================================

runtime = Runtime(
    decision=Decision(),
    policy=Policy(),
    history=history,
    planner=planner
)


# =====================================================
# Run
# =====================================================

result = runtime.run(
    context
)


# =====================================================
# 输出
# =====================================================

print()
print(
    "result:",
    result.success
)

print(
    "final state:",
    result.state.export()
)


# =====================================================
# 验证
# =====================================================

assert result.success is True


# -----------------------------------------------------
# A、B 执行成功
# -----------------------------------------------------

assert (
    result.state.get("a")
    is True
)

assert (
    result.state.get("b")
    is True
)


# -----------------------------------------------------
# C 和 X 属于失败路线。
#
# Replanner 回到 B Snapshot 后，
# C / X 对 State 的修改应该消失。
# -----------------------------------------------------

assert (
    result.state.get("c")
    is None
)

assert (
    result.state.get("x")
    is None
)


# -----------------------------------------------------
# 替代路线 D 成功执行
# -----------------------------------------------------

assert (
    result.state.get("d")
    is True
)


# -----------------------------------------------------
# Replanner 最后应该恢复 Graph v2，
# 而不是继续使用失败时的 Graph v3。
# -----------------------------------------------------

assert (
    context.graph
    is planner.graph_v2
)


print()
print(
    "dynamic graph replan test passed"
)