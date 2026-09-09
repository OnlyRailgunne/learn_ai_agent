from graph.node import Node
from core.result import NodeResult


class EndNode(Node):
    def run(self, state) -> NodeResult:
        return NodeResult(
            success=True,
            output=None
        )