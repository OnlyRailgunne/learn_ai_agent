from dispatcher import dispatcher
from tools import CalculatorTool

def test_dispatcher_register_tool():
    #calculator_tool = CalculatorTool()
    d = dispatcher()
    tool = CalculatorTool()
    d.register_tool("calculator", tool)
    assert d.tool_map["calculator"] == tool

def test_dispatcher_dispatch():
    d = dispatcher()
    tool = CalculatorTool()
    d.register_tool("calculator", tool)
    decision = {"tool": "calculator", "arguments": {"expression": "1+2"}}
    dispatched_tool = d.dispatch(decision)
    assert dispatched_tool == tool