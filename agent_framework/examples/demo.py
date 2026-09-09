from core.runtime import Runtime
from core.state import State
from core.context import ExecutionContext
from core.decision import Decision
from core.policy import Policy
from core.history import History

from core.goal import Goal
from core.planner import Planner

from graph.tool_node import ToolNode
from graph.llm_node import LLMNode
from graph.end_node import EndNode

from tools.calculator import CalculatorTool


# =========================
# 1. 创建已有执行能力
# =========================

calculator = CalculatorTool()

tool_node = ToolNode(
    name="Calculator",
    tool=calculator
)

llm_node = LLMNode(
    name="LLM",
    model="gpt-5.5"
)

end_node = EndNode(
    name="End"
)


# =========================
# 2. 创建 Goal
# =========================

goal = Goal(
    "calculate 20 * 15 and explain"
)


# =========================
# 3. Planner 根据 Goal 生成 Graph
# =========================

planner = Planner(
    calculator_node=tool_node,
    response_node=llm_node,
    end_node=end_node
)

plan_result = planner.plan(goal)


# =========================
# 4. 创建运行时状态
# =========================

state = State()
history = History()
for key, value in plan_result.initial_state.items():
    state.set(key, value)

# 如果你当前 CalculatorTool 还是从 State
# 或 ToolNode 内部固定读取表达式，
# 这里继续保持你原来的输入方式。
#
# 例如你之前如果有：
#
# state.set("expression", "100 * 3")
#
# 就继续保留。
#
# 不要为了 Planner 改 CalculatorTool。


# =========================
# 5. 创建 ExecutionContext
# =========================

context = ExecutionContext(
    graph=plan_result.graph,
    state=state,
    current_node=plan_result.entry_node,
    goal=goal
)


# =========================
# 6. 创建原有 Decision / Policy / Runtime
# =========================

decision = Decision()
policy = Policy()

runtime = Runtime(
    decision=decision,
    policy=policy,
    history=history,
    planner=planner
)


# =========================
# 7. 执行
# =========================

result = runtime.run(context)


# =========================
# 8. 查看结果
# =========================

print(result.success)
print(result.state.export())