#agent.py
class Agent:

    def __init__(self, llm, memory, dispatcher, tools, logger, system_prompt):

        self.llm = llm

        self.memory = memory

        self.dispatcher = dispatcher

        self.tools = tools

        self.logger = logger

        self.system_prompt = system_prompt
    
    def add_tool(self, tool):
        self.tools.append(tool)

    def ask(self, input_text):
        # 处理输入文本，调用工具或模型进行处理
        pre_processed_text = self.llm.generate_response(input_text)
        decision = self.llm.decide(pre_processed_text)
        tool = self.dispatcher.dispatch(decision)
        generated_response = self.llm.generate_response(tool.run(decision["arguments"]["expression"]))
        return f"Agent response: {generated_response}"
            





