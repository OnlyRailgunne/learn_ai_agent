from core.history import History
from core.event import NodeExecutionEvent, TransitionEvent
from core.result import NodeResult
from core.replanner import Replanner
from core.state import State
from core.context import ExecutionContext

from graph.graph import Graph
from graph.llm_node import LLMNode


# 1. 准备节点
node_b = LLMNode(
    name="B",
    model="gpt-5.5"
)

node_c = LLMNode(
    name="C",
    model="gpt-5.5"
)

node_d = LLMNode(
    name="D",
    model="gpt-5.5"
)


# 2. 准备 Graph
graph = Graph()

graph.connect(
    node_b,
    node_c
)

graph.connect(
    node_b,
    node_d
)


# 3. 准备 History
history = History()

history.add(
    TransitionEvent(
        source=node_b,
        target=node_c
    )
)

failed_result = NodeResult()
failed_result.success = False
failed_result.output = "C failed"

history.add(
    NodeExecutionEvent(
        node=node_c,
        result=failed_result
    )
)


# 4. 准备 Context
state = State()

context = ExecutionContext(
    graph=graph,
    state=state,
    current_node=node_c
)


# 5. 调用 Replanner
replanner = Replanner()

replanner.replan(
    context,
    failed_result,
    history
)