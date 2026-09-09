from graph.node import Node
from core.result import NodeResult


class LLMNode(Node):
    def __init__(self, name, model):
        super().__init__(name)
        self.model = model

    def run(self, state):
        response = f"Response from {self.model}"

        state.set("llm_response", response)

        return NodeResult(
            success=True,
            output=response
        )