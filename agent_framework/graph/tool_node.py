from graph.node import Node
from core.result import NodeResult


class ToolNode(Node):
    def __init__(self, name, tool):
        super().__init__(name)
        self.tool = tool

    def run(self, state):
        result = self.tool.run(state)

        return NodeResult(
            success=True,
            output=result
        )