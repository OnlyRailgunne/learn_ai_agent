#tools.py
class CalculatorTool:

    name = "calculator"

    description = "计算数学表达式"

    def run(self, expression):
        try:
            # 使用 eval 计算数学表达式
            result = eval(expression)
            return result
        except Exception as e:
            return f"计算错误: {str(e)}"