from tools.base import Tool


class CalculatorTool(Tool):

    def run(self, state):

        expression = state.get("expression")

        result = eval(
            expression,
            {"__builtins__": {}},
            {}
        )

        state.set(
            "tool_result",
            result
        )

        return result