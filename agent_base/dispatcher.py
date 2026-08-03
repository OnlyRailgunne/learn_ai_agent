#dispatcher.py
class dispatcher:
    def __init__(self):
        self.tool_map = {}

    def register_tool(self,tool_name,tool):
        self.tool_map[tool_name] = tool
        return f"工具 {tool_name} 已注册"
  
    def dispatch(self,decision):
        # 根据请求选择合适的工具进行处理
        if decision["tool"] in self.tool_map:
            tool = self.tool_map[decision["tool"]]
            return tool
        else:
            return None