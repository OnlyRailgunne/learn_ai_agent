class PlanStep:

    def __init__(
        self,
        step_id,
        capability,
        arguments=None
    ):
        self.id = step_id
        self.capability = capability
        self.arguments = arguments or {}