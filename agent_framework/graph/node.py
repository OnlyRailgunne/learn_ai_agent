from core.result import NodeResult


class Node:
    def __init__(self, name):
        self.name = name

    def run(self, state) -> NodeResult:
        raise NotImplementedError

    def __str__(self):
        return f"{self.__class__.__name__}({self.name})"