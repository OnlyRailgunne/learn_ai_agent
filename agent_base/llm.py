#llm.py
class FakeLLM:

    def decide(self, text):

        if "+" in text:
            return {
    "tool": "calculator",
    "arguments": {"expression": text}
}

        if "-" in text:
            return {
    "tool": "calculator",
    "arguments": {"expression": text}
}

        if "*" in text:
            return {
    "tool": "calculator",
    "arguments": {"expression": text}
}

        if "/" in text:
            return {
    "tool": "calculator",
    "arguments": {"expression": text}
}



    def generate_response(self, result):
            # 生成响应的逻辑
            return f"计算结果是: {result}"