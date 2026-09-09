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

from core.groq_structured_model import (
    GroqStructuredModel
)

from core.plan_evaluation_result import (
    PlanEvaluationResult
)


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

    # =============================================
    # Goal
    # =============================================

    goal = Goal(
        "calculate 20 * 15 "
        "and answer using the result"
    )

    # =============================================
    # Real Groq Model
    # =============================================

    model = GroqStructuredModel(
        model="openai/gpt-oss-20b"
    )

    # =============================================
    # Planning LLM
    # =============================================

    planning_llm = PlanningLLM(
        model=model
    )

    # =============================================
    # Planner
    # =============================================

    planner = RealPlanningTestPlanner(
        planning_llm=planning_llm
    )

    # =============================================
    # Real Initial Planning
    # =============================================

    print()
    print(
        "=== real groq planning ==="
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

    # =============================================
    # State
    # =============================================

    state = State()

    for key, value in (
        plan.initial_state.items()
    ):

        state.set(
            key,
            value
        )

    # =============================================
    # Context
    # =============================================

    context = ExecutionContext(
        graph=plan.graph,
        state=state,
        current_node=plan.entry_node,
        goal=goal
    )

    # =============================================
    # Runtime
    # =============================================

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

    # =============================================
    # Result
    # =============================================

    print()

    print(
        "result:",
        result.success
    )

    print(
        "final state:",
        result.state.export()
    )

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

    print()
    print(
        "real groq structured "
        "planning test passed"
    )


if __name__ == "__main__":
    main()