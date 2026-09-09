from core.goal import Goal
from core.state import State
from core.history import History
from core.runtime import Runtime
from core.context import ExecutionContext

from core.decision import Decision
from core.policy import Policy

from core.planner import Planner

from core.plan_validation_error import (
    PlanValidationError
)

from core.plan_evaluation_result import (
    PlanEvaluationResult
)


# =========================================================
# Fake Planning LLM
#
# 这里直接模拟 Planner 边界收到的 normalized plan。
# =========================================================

class FakePlanningLLM:

    def __init__(
        self,
        mode
    ):
        self.mode = mode


    def plan(
        self,
        goal,
        capabilities
    ):

        # =================================================
        # 缺少 required argument
        # =================================================

        if self.mode == "missing":

            return {
                "entry": "calculate",

                "steps": [
                    {
                        "id": "calculate",
                        "capability": "calculator",
                        "arguments": {}
                    }
                ],

                "edges": [
                    {
                        "source": "calculate",
                        "target": "__END__"
                    }
                ]
            }

        # =================================================
        # 未知 argument
        # =================================================

        if self.mode == "unknown":

            return {
                "entry": "calculate",

                "steps": [
                    {
                        "id": "calculate",
                        "capability": "calculator",

                        "arguments": {
                            "formula": "20 * 15"
                        }
                    }
                ],

                "edges": [
                    {
                        "source": "calculate",
                        "target": "__END__"
                    }
                ]
            }

        # =================================================
        # 参数类型错误
        # =================================================

        if self.mode == "wrong_type":

            return {
                "entry": "calculate",

                "steps": [
                    {
                        "id": "calculate",
                        "capability": "calculator",

                        "arguments": {
                            "expression": 300
                        }
                    }
                ],

                "edges": [
                    {
                        "source": "calculate",
                        "target": "__END__"
                    }
                ]
            }

        # =================================================
        # 合法 Plan
        # =================================================

        return {
            "entry": "calculate",

            "steps": [
                {
                    "id": "calculate",
                    "capability": "calculator",

                    "arguments": {
                        "expression":
                            "20 * 15"
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
# Dynamic Planning 固定 KEEP
# =========================================================

class ContractTestPlanner(
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
# Invalid Contract Test
# =========================================================

def test_invalid_contracts():

    print()
    print(
        "=== invalid capability contracts ==="
    )

    cases = [
        (
            "missing",
            "missing required argument"
        ),

        (
            "unknown",
            "unknown arguments"
        ),

        (
            "wrong_type",
            "invalid argument type"
        )
    ]

    goal = Goal(
        "calculate 20 * 15"
    )

    for mode, expected_error in cases:

        planner = ContractTestPlanner(
            planning_llm=FakePlanningLLM(
                mode=mode
            )
        )

        try:

            planner.plan(
                goal
            )

        except PlanValidationError as error:

            print(
                mode,
                "rejected:",
                error
            )

            assert (
                expected_error
                in str(error)
            )

            continue

        raise AssertionError(
            f"{mode} plan should "
            f"have been rejected"
        )


# =========================================================
# Valid Contract + Runtime
# =========================================================

def test_valid_contract():

    print()
    print(
        "=== valid capability contract ==="
    )

    goal = Goal(
        "calculate 20 * 15 "
        "and answer"
    )

    planner = ContractTestPlanner(
        planning_llm=FakePlanningLLM(
            mode="valid"
        )
    )

    # =====================================================
    # Planning
    # =====================================================

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
    # State
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
    # Context
    # =====================================================

    context = ExecutionContext(
        graph=plan.graph,
        state=state,
        current_node=plan.entry_node,
        goal=goal
    )

    # =====================================================
    # Runtime
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

    assert (
        result.state.get(
            "llm_response"
        )
        == "Response from gpt-5.5"
    )

    print(
        "valid capability "
        "contract executed"
    )


def main():

    test_invalid_contracts()

    test_valid_contract()

    print()

    print(
        "capability contract "
        "test passed"
    )


if __name__ == "__main__":
    main()