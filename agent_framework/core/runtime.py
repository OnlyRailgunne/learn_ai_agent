from core.runtime_result import RuntimeResult

from graph.end_node import EndNode

from core.event import (
    NodeExecutionEvent,
    TransitionEvent,
    PlanningChoiceEvent
)

from core.snapshot import Snapshot


class Runtime:

    def __init__(
        self,
        decision,
        policy,
        history,
        planner=None
    ):
        self.decision = decision
        self.policy = policy
        self.history = history
        self.planner = planner


    def run(
        self,
        context
    ):

        while context.current_node:

            # ---------------------------------
            # 1. Node 执行
            # ---------------------------------

            current_node = (
                context.current_node
            )

            node_result = (
                current_node.run(
                    context.state
                )
            )


            # ---------------------------------
            # 2. 记录 NodeExecutionEvent
            #
            # Node 已经执行完，
            # 先成为 History 中的事实。
            # ---------------------------------

            self.history.add(
                NodeExecutionEvent(
                    current_node,
                    node_result
                )
            )


            # ---------------------------------
            # 3. Dynamic Planning Evaluate
            #
            # Planner 观察：
            #
            # Goal
            # 当前 State
            # NodeResult
            # History
            # 当前 Graph
            #
            # 然后返回：
            #
            # KEEP
            # 或
            # MODIFY + target
            # ---------------------------------

            plan_evaluation = None

            if self.planner is not None:

                plan_evaluation = (
                    self.planner.evaluate(
                        goal=context.goal,
                        context=context,
                        node_result=node_result,
                        history=self.history
                    )
                )


            # ---------------------------------
            # 4. Decision
            #
            # Decision 现在同时看到：
            #
            # NodeResult
            # PlanEvaluationResult
            #
            # 失败：
            # → Replanner
            #
            # 成功 + MODIFY：
            # → Planner target
            #
            # 成功 + KEEP：
            # → graph.next()
            # ---------------------------------

            decision_result = (
                self.decision.decide(
                    context,
                    node_result,
                    self.history,
                    plan_evaluation
                )
            )


            # ---------------------------------
            # 5. Policy
            # ---------------------------------

            decision_result = (
                self.policy.allow(
                    decision_result
                )
            )


            # ---------------------------------
            # 6. 无路可走
            # ---------------------------------

            if decision_result.terminate:

                return RuntimeResult(
                    success=False,
                    state=context.state
                )


            # ---------------------------------
            # 7. 保存 apply 前真实执行位置
            # ---------------------------------

            previous_node = (
                context.current_node
            )


            # ---------------------------------
            # 8. Decision 成为事实
            # ---------------------------------

            context.apply(
                decision_result
            )


            # ---------------------------------
            # 9. Planning Choice
            #
            # 现在这里不只可能来自 Replanner，
            # 也可能来自 Dynamic Planner。
            #
            # Replan 例子：
            #
            # 实际位置 D
            # planning origin C
            # 选择 E
            #
            # PlanningChoiceEvent(C → E)
            #
            #
            # Dynamic Planning 例子：
            #
            # Calculator 成功
            # Planner 主动选择 End
            #
            # PlanningChoiceEvent(
            #     Calculator → End
            # )
            # ---------------------------------

            if (
                decision_result.planning_origin
                is not None
            ):

                self.history.add(
                    PlanningChoiceEvent(
                        decision_result
                        .planning_origin,

                        context.current_node
                    )
                )


            # ---------------------------------
            # 10. Runtime 真实 Transition
            #
            # 描述 Runtime 实际从哪里移动到哪里。
            # ---------------------------------

            self.history.add(
                TransitionEvent(
                    previous_node,
                    context.current_node,
                    context.graph
                )
            )


            # ---------------------------------
            # 11. 成功 Node 后创建 Snapshot
            # ---------------------------------

            if node_result.success:

                snapshot = Snapshot(
                    context.state.export()
                )

                self.history.add_snapshot(
                    snapshot
                )


            # ---------------------------------
            # 12. EndNode
            # ---------------------------------

            if isinstance(
                context.current_node,
                EndNode
            ):

                return RuntimeResult(
                    success=True,
                    state=context.state
                )


        return RuntimeResult(
            success=False,
            state=context.state
        )