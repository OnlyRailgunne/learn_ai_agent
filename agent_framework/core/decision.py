from core.replanner import Replanner
from core.decision_result import DecisionResult


class Decision:

    def decide(
        self,
        context,
        node_result,
        history,
        plan_evaluation=None
    ):

        result = DecisionResult()


        # ---------------------------------
        # 1. Node 执行失败
        # ---------------------------------

        if node_result.success == False:

            replan_result = (
                Replanner().replan(
                    context,
                    node_result,
                    history
                )
            )


            # -----------------------------
            # 没有任何可恢复路线
            # -----------------------------

            if (
                replan_result.entry_node
                is None
            ):

                result.terminate = True

                return result


            # -----------------------------
            # Replan 成功
            # -----------------------------

            result.node = (
                replan_result.entry_node
            )

            result.graph = (
                replan_result.graph
            )

            result.restore_snapshot = (
                replan_result.snapshot
            )

            result.planning_origin = (
                replan_result.origin
            )

            return result


        # ---------------------------------
        # 2. Dynamic Planner MODIFY
        # ---------------------------------

        if (
            plan_evaluation is not None
            and
            plan_evaluation.keep == False
        ):

            result.node = (
                plan_evaluation.target
            )

            result.graph = (
                plan_evaluation.graph
            )

            result.planning_origin = (
                context.current_node
            )

            return result


        # ---------------------------------
        # 3. KEEP
        #
        # 按当前 Graph 正常执行
        # ---------------------------------

        result.node = context.graph.next(
            context.current_node,
            context.state
        )

        return result