class ExecutionContext:

    def __init__(
        self,
        graph,
        state,
        current_node,
        goal=None
    ):
        self.graph = graph
        self.state = state
        self.current_node = current_node
        self.goal = goal

    def apply(
        self,
        decision_result
    ):

        # ---------------------------------
        # 先恢复历史 State
        # ---------------------------------

        if (
            decision_result.restore_snapshot
            is not None
        ):

            self.state.restore(
                decision_result
                .restore_snapshot
                .data
            )


        # ---------------------------------
        # 再应用新的 State changes
        # ---------------------------------

        for (
            key,
            value
        ) in decision_result.changes.items():

            self.state.set(
                key,
                value
            )


        # ---------------------------------
        # Graph 更新
        # ---------------------------------

        if (
            decision_result.graph
            is not None
        ):
            self.graph = (
                decision_result.graph
            )


        # ---------------------------------
        # current_node 更新
        # ---------------------------------

        if (
            decision_result.node
            is not None
        ):
            self.current_node = (
                decision_result.node
            )