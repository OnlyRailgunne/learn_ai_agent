from core.replan_result import ReplanResult
from core.state import State


class Replanner:

    def replan(
        self,
        context,
        node_result,
        history
    ):

        # =================================================
        # 1. 找最近一次 NodeExecution
        # =================================================

        latest_execution = (
            history.latest_node_execution()
        )

        if latest_execution is None:

            return ReplanResult(
                context.graph,
                None
            )

        (
            execution_index,
            execution_event
        ) = latest_execution


        # =================================================
        # 2. 从失败位置向前找最近的 Graph Transition
        # =================================================

        previous = (
            history.previous_graph_transition(
                execution_index,
                context.graph
            )
        )


        # =================================================
        # 3. DFS 风格向前回退
        # =================================================

        while previous is not None:

            (
                transition_index,
                transition
            ) = previous


            # =================================================
            # 4. 找到这段历史当时所属的 Graph
            #
            # Dynamic Planning 后：
            #
            # 当前 context.graph
            # 不一定等于
            # 这个历史 Transition 当时使用的 Graph。
            #
            # 所以优先使用 transition.graph。
            #
            # context.graph 只用于兼容旧 Event。
            # =================================================

            replan_graph = (
                transition.graph
                if getattr(
                    transition,
                    "graph",
                    None
                ) is not None
                else context.graph
            )


            # 当前准备重新规划的分叉点
            replan_origin = (
                transition.source
            )


            # =================================================
            # 5. 找这个分叉点对应的 Snapshot
            # =================================================

            snapshot_result = (
                history.snapshot_before(
                    transition_index + 1
                )
            )


            # =================================================
            # 这个分叉点没有 Snapshot
            # 继续向更早位置回退
            # =================================================

            if snapshot_result is None:

                previous = (
                    history.previous_graph_transition(
                        transition_index,
                        context.graph
                    )
                )

                continue


            (
                snapshot_index,
                snapshot
            ) = snapshot_result


            # =================================================
            # 6. 创建观察用 State
            #
            # Replanner 不直接修改 context.state。
            # =================================================

            probe_state = State()

            probe_state.restore(
                snapshot.data
            )


            # =================================================
            # 7. 在“这一段历史自己的 Graph”里
            # 查找当前 Snapshot State 下可走的 Edge
            #
            # 以前这里是：
            #
            # context.graph.available_edges_from(...)
            #
            # 现在必须是：
            #
            # replan_graph.available_edges_from(...)
            # =================================================

            candidate_edges = (
                replan_graph.available_edges_from(
                    replan_origin,
                    probe_state
                )
            )


            # =================================================
            # 8. 找这个 origin 已经尝试过哪些 target
            # =================================================

            attempted_targets = (
                history.targets_from(
                    replan_origin
                )
            )


            # =================================================
            # 9. 找第一条：
            #
            # condition 满足
            # +
            # 以前没有尝试过
            #
            # 的路线
            # =================================================

            next_node = None

            for edge in candidate_edges:

                if (
                    edge.target
                    not in attempted_targets
                ):

                    next_node = (
                        edge.target
                    )

                    break


            # =================================================
            # 10. 找到替代路线
            # =================================================

            if next_node is not None:

                print(
                    "replan origin:",
                    replan_origin.name
                )

                print(
                    "attempted:",
                    [
                        node.name
                        for node
                        in attempted_targets
                    ]
                )

                print(
                    "selected:",
                    next_node.name
                )

                print(
                    "restore snapshot:",
                    snapshot_index
                )


                # ---------------------------------
                # 注意：
                #
                # 这里也不能返回 context.graph。
                #
                # 回退到哪一段历史，
                # 就恢复那一段历史所属的 Graph。
                # ---------------------------------

                return ReplanResult(
                    graph=replan_graph,
                    entry_node=next_node,
                    snapshot=snapshot,
                    origin=replan_origin
                )


            # =================================================
            # 11. 当前分叉点路线耗尽
            # 继续往更早历史回退
            # =================================================

            print(
                "branch exhausted:",
                replan_origin.name
            )

            previous = (
                history.previous_graph_transition(
                    transition_index,
                    context.graph
                )
            )


        # =================================================
        # 12. 所有历史分叉点都耗尽
        # =================================================

        return ReplanResult(
            context.graph,
            None
        )