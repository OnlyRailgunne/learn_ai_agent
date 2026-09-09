from core.goal import Goal
from core.state import State
from core.history import History
from core.runtime import Runtime
from core.context import ExecutionContext

from core.decision import Decision
from core.policy import Policy

from core.planner import Planner

from core.planning_llm import (
    PlanningLLM
)

from core.openai_structured_model import (
    OpenAIStructuredModel
)

from core.plan_evaluation_result import (
    PlanEvaluationResult
)


# =========================================================
# Runtime 执行阶段仍固定 KEEP
#
# 本测试只验证：
#
# Real LLM
# ↓
# Structured Planning
# ↓
# Existing Runtime
# =========================================================

class RealPlanningTestPlanner(
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


def main():

    # =====================================================
    # 1. Goal
    # =====================================================

    goal = Goal(
        "calculate 20 * 15 "
        "and answer using the result"
    )

    # =====================================================
    # 2. Real Model Provider
    # =====================================================

    model = OpenAIStructuredModel(
        model="gpt-5.6-luna"
    )

    # =====================================================
    # 3. Planning LLM
    # =====================================================

    planning_llm = PlanningLLM(
        model=model
    )

    # =====================================================
    # 4. Planner
    # =====================================================

    planner = RealPlanningTestPlanner(
        planning_llm=planning_llm
    )

    # =====================================================
    # 5. REAL INITIAL PLANNING
    # =====================================================

    print()
    print(
        "=== real llm planning ==="
    )

    plan = planner.plan(
        goal
    )

    print(
        "entry:",
        plan.entry_node.name
    )

    print(
        "initial state:",
        plan.initial_state
    )

    # =====================================================
    # 6. State
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
    # 7. Context
    # =====================================================

    context = ExecutionContext(
        graph=plan.graph,
        state=state,
        current_node=plan.entry_node,
        goal=goal
    )

    # =====================================================
    # 8. Runtime
    # =====================================================

    history = History()

    runtime = Runtime(
        decision=Decision(),
        policy=Policy(),
        planner=planner,
        history=history
    )

    # =====================================================
    # 9. Execute
    # =====================================================

    result = runtime.run(
        context
    )

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
    # 10. Assertions
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
        "real llm structured "
        "planning test passed"
    )


if __name__ == "__main__":
    main()