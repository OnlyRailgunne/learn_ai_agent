class Event:
    pass


class NodeExecutionEvent(Event):

    def __init__(self, node, result):
        self.node = node
        self.result = result


class TransitionEvent(Event):

    def __init__(
        self,
        source,
        target,
        graph=None
    ):
        self.source = source
        self.target = target
        self.graph = graph


class PlanningChoiceEvent(Event):

    def __init__(self, source, target):
        self.source = source
        self.target = target