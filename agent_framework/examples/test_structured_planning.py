from core.goal import Goal
from core.state import State
from core.history import History
from core.runtime import Runtime
from core.context import ExecutionContext

from core.decision import Decision
from core.policy import Policy

from core.planner import Planner
from core.planning_llm import PlanningLLM

from core.plan_evaluation_result import (
    PlanEvaluationResult
)


# =========================================================
# Fake Model Provider
#
# 注意：
# 现在 Fake 的已经不是 PlanningLLM。
#
# 它只模拟：
#
# 真正模型 API
# ↓
# 返回 Structured Output
# =========================================================

class FakeStructuredModel:

    def __init__(
        self
    ):
        self.last_system_prompt = None
        self.last_input = None
        self.last_schema = None


    def generate_structured(
        self,
        system_prompt,
        input,
        schema
    ):

        # 保存下来，
        # 后面测试 PlanningLLM 有没有正确传递信息

        self.last_system_prompt = (
            system_prompt
        )

        self.last_input = input

        self.last_schema = schema

        print(
            "model received goal:",
            input["goal"]
        )

        print(
            "model received capabilities:",
            [
                capability["name"]
                for capability
                in input["capabilities"]
            ]
        )

        # =================================================
        # 模拟真正 LLM 根据 Goal + Capabilities
        # 返回 Structured Output
        # =================================================

        return {
            "entry": "calculate",

            "steps": [

                {
                    "id": "calculate",
                    "capability": "calculator",

                    "arguments": {
                        "expression": "20 * 15"
                    }
                },

                {
                    "id": "answer",
                    "capability": "answer",
                    "arguments": {}
                }
            ],

            "edges": [

                {
                    "source": "calculate",
                    "target": "answer"
                },

                {
                    "source": "answer",
                    "target": "__END__"
                }
            ]
        }


# =========================================================
# 本测试只验证 Initial Planning
#
# Dynamic Planning 已经单独完整验证过，
# 所以运行期间统一 KEEP。
# =========================================================

class StructuredTestPlanner(
    Planner
):

    def evaluate(
        self,
        goal,
        context,
        node_result,
        history
    ):

        print(
            "evaluate:",
            context.current_node.name,
            "-> KEEP"
        )

        return PlanEvaluationResult(
            keep=True
        )


# =========================================================
# Complete Integration Test
# =========================================================

def main():

    # =====================================================
    # 1. Goal
    # =====================================================

    goal = Goal(
        "calculate 20 * 15 "
        "and answer"
    )

    # =====================================================
    # 2. Model Provider
    # =====================================================

    model = FakeStructuredModel()

    # =====================================================
    # 3. 真正的 PlanningLLM
    # =====================================================

    planning_llm = PlanningLLM(
        model=model
    )

    # =====================================================
    # 4. Planner
    # =====================================================

    planner = StructuredTestPlanner(
        planning_llm=planning_llm
    )

    # =====================================================
    # 5. Initial Planning
    #
    # Planner
    # ↓
    # PlanningLLM
    # ↓
    # FakeStructuredModel
    # ↓
    # raw plan
    # ↓
    # validation
    # ↓
    # parse
    # ↓
    # compile
    # =====================================================

    plan = planner.plan(
        goal
    )

    print()
    print(
        "entry:",
        plan.entry_node.name
    )

    print(
        "initial state:",
        plan.initial_state
    )

    # =====================================================
    # 6. 验证 PlanningLLM → Model 边界
    # =====================================================

    assert (
        model.last_system_prompt
        is not None
    )

    assert (
        model.last_input
        is not None
    )

    assert (
        model.last_schema
        is not None
    )

    assert (
        model.last_input[
            "goal"
        ]
        == "calculate 20 * 15 and answer"
    )

    capability_names = [
        capability["name"]
        for capability
        in model.last_input[
            "capabilities"
        ]
    ]

    assert (
        capability_names
        == [
            "calculator",
            "answer"
        ]
    )

    print(
        "planning llm input verified"
    )

    # =====================================================
    # 7. State
    # =====================================================

    state = State()

    for key, value in (
        plan.initial_state.items()
    ):

        state.set(
            key,
            value
        )

    # =====================================================
    # 8. Context
    # =====================================================

    context = ExecutionContext(
        graph=plan.graph,
        state=state,
        current_node=plan.entry_node,
        goal=goal
    )

    # =====================================================
    # 9. Runtime
    # =====================================================

    history = History()

    runtime = Runtime(
        decision=Decision(),
        policy=Policy(),
        planner=planner,
        history=history
    )

    result = runtime.run(
        context
    )

    # =====================================================
    # 10. Result
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
    # 11. Assertions
    # =====================================================

    assert result.success

    assert (
        result.state.get(
            "expression"
        )
        == "20 * 15"
    )

    assert (
        result.state.get(
            "tool_result"
        )
        == 300
    )

    assert (
        result.state.get(
            "llm_response"
        )
        == "Response from gpt-5.5"
    )

    print()
    print(
        "real planning llm "
        "integration test passed"
    )


if __name__ == "__main__":
    main()