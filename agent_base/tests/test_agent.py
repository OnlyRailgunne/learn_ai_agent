from agent import Agent
from dispatcher import dispatcher
from tools import CalculatorTool
from llm import FakeLLM

def test_agent_ask():
    # 创建一个假的 LLM、内存、调度器和工具
    fake_llm = FakeLLM()
    fake_memory = None  # 可以使用 None 或者一个简单的内存对象
    fake_dispatcher = dispatcher()
    calculator_tool = CalculatorTool()
    fake_dispatcher.register_tool("calculator", calculator_tool)
    
    # 创建 Agent 实例
    my_agent = Agent(fake_llm, fake_memory, fake_dispatcher, [calculator_tool], None, "System prompt")
    
    # 测试 ask 方法
    input_text = "1+2"
    response = my_agent.ask(input_text)

    #print(response)  # 输出响应以便调试
    assert "Agent response: 计算结果是: 3" in response