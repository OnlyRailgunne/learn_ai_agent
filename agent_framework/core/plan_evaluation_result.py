class PlanEvaluationResult:

    def __init__(
        self,
        keep=True,
        graph=None,
        target=None
    ):
        self.keep = keep
        self.graph = graph
        self.target = target