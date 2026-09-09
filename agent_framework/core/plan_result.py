class PlanResult:

    def __init__(
        self,
        graph=None,
        entry_node=None,
        initial_state=None
    ):
        self.graph = graph
        self.entry_node = entry_node
        self.initial_state = initial_state or {}