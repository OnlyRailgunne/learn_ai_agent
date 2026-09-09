#replan_result.py
class ReplanResult:

    def __init__(
        self,
        graph,
        entry_node,
        snapshot=None,
        origin=None
    ):
        self.graph = graph
        self.entry_node = entry_node
        self.snapshot = snapshot
        self.origin = origin