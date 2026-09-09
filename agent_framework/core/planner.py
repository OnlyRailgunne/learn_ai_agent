from core.plan_step import PlanStep
from core.plan_edge import PlanEdge
from core.structured_plan_result import StructuredPlanResult
from core.plan_result import PlanResult

from graph.graph import Graph
from graph.tool_node import ToolNode
from graph.llm_node import LLMNode
from graph.end_node import EndNode

from tools.calculator import CalculatorTool
from core.plan_validation_error import (
    PlanValidationError
)

class Planner:

    def __init__(
        self,
        planning_llm=None
    ):
        self.planning_llm = planning_llm


    def available_capabilities(
        self
    ):

        return [
            {
                "name": "calculator",

                "description": (
                    "Calculate a mathematical "
                    "expression"
                ),

                "arguments": {

                    "expression": {
                        "type": "string",

                        "required": True,

                        "description": (
                            "The mathematical "
                            "expression to calculate"
                        )
                    }
                }
            },

            {
                "name": "answer",

                "description": (
                    "Generate a natural language "
                    "answer using the current "
                    "execution state"
                ),

                "arguments": {}
            }
        ]


    def plan(
        self,
        goal
    ):

        if self.planning_llm is None:
            raise RuntimeError(
                "Planner requires planning_llm "
                "for initial planning"
            )

        capabilities = (
            self.available_capabilities()
        )

        raw_plan = self.planning_llm.plan(
            goal,
            capabilities
        )

        self._validate_raw_plan(
            raw_plan,
            capabilities
        )

        structured_plan = (
            self._parse_structured_plan(
                raw_plan
            )
        )

        return self._compile(
            structured_plan
        )


    def _parse_structured_plan(
        self,
        raw_plan
    ):

        steps = []

        for item in raw_plan["steps"]:

            step = PlanStep(
                step_id=item["id"],
                capability=item["capability"],
                arguments=item.get(
                    "arguments",
                    {}
                )
            )

            steps.append(step)

        edges = []

        for item in raw_plan["edges"]:

            edge = PlanEdge(
                source=item["source"],
                target=item["target"]
            )

            edges.append(edge)

        return StructuredPlanResult(
            entry=raw_plan["entry"],
            steps=steps,
            edges=edges
        )


    def _compile(
        self,
        plan
    ):

        graph = Graph()

        nodes = {}

        initial_state = {}

        # =========================================
        # 1. PlanStep -> Node
        # =========================================

        for step in plan.steps:

            node = self._build_node(
                step
            )

            nodes[step.id] = node

            # 第一版：
            # step arguments 先直接变成
            # initial state
            for key, value in (
                step.arguments.items()
            ):
                initial_state[key] = value

        # =========================================
        # 2. EndNode
        # =========================================

        end_node = EndNode(
            name="End"
        )

        # =========================================
        # 3. PlanEdge -> Graph Edge
        # =========================================

        for edge in plan.edges:

            if edge.source not in nodes:
                raise ValueError(
                    f"unknown source step: "
                    f"{edge.source}"
                )

            source = nodes[
                edge.source
            ]

            if edge.target == "__END__":

                target = end_node

            else:

                if edge.target not in nodes:
                    raise ValueError(
                        f"unknown target step: "
                        f"{edge.target}"
                    )

                target = nodes[
                    edge.target
                ]

            graph.connect(
                source,
                target
            )

        # =========================================
        # 4. Entry
        # =========================================

        if plan.entry not in nodes:
            raise ValueError(
                f"unknown entry step: "
                f"{plan.entry}"
            )

        entry_node = nodes[
            plan.entry
        ]

        # =========================================
        # 5. Runtime-ready Plan
        # =========================================

        return PlanResult(
            graph=graph,
            entry_node=entry_node,
            initial_state=initial_state
        )


    def _build_node(
        self,
        step
    ):

        if step.capability == "calculator":

            return ToolNode(
                name=step.id,
                tool=CalculatorTool()
            )

        if step.capability == "answer":

            return LLMNode(
                name=step.id,
                model="gpt-5.5"
            )

        raise ValueError(
            "unknown capability: "
            f"{step.capability}"
        )


    def evaluate(
        self,
        goal,
        context,
        node_result,
        history
    ):

        description = (
            goal.description.lower()
        )


        # ---------------------------------
        # 情况 1：
        #
        # calculate ... and explain
        #
        # Calculator 已经执行成功，
        # 但 Goal 还要求 explain。
        #
        # 动态生成新的未来：
        #
        # Calculator
        #     ↓
        #    LLM
        #     ↓
        #    End
        # ---------------------------------

        if (
            node_result.success
            and
            context.current_node
            is self.calculator_node
            and
            "and explain" in description
        ):

            future_graph = Graph()

            future_graph.connect(
                self.calculator_node,
                self.response_node
            )

            future_graph.connect(
                self.response_node,
                self.end_node
            )

            print(
                "evaluate:",
                context.current_node.name,
                "-> MODIFY ->",
                self.response_node.name
            )

            return PlanEvaluationResult(
                keep=False,
                graph=future_graph,
                target=self.response_node
            )


        # ---------------------------------
        # 情况 2：
        #
        # 只要求 calculate
        #
        # Calculator 成功以后
        # 直接结束
        # ---------------------------------

        if (
            node_result.success
            and
            context.current_node
            is self.calculator_node
            and
            "and answer" not in description
            and
            "and explain" not in description
        ):

            future_graph = Graph()

            future_graph.connect(
                self.calculator_node,
                self.end_node
            )

            print(
                "evaluate:",
                context.current_node.name,
                "-> MODIFY ->",
                self.end_node.name
            )

            return PlanEvaluationResult(
                keep=False,
                graph=future_graph,
                target=self.end_node
            )


        # ---------------------------------
        # KEEP
        # ---------------------------------

        print(
            "evaluate:",
            context.current_node.name,
            "-> KEEP"
        )

        return PlanEvaluationResult(
            keep=True
        )


    def _validate_raw_plan(
        self,
        raw_plan,
        capabilities
    ):

        # =================================================
        # 1. Plan 本身
        # =================================================

        if not isinstance(
            raw_plan,
            dict
        ):
            raise PlanValidationError(
                "plan must be a dict"
            )

        required_fields = [
            "entry",
            "steps",
            "edges"
        ]

        for field in required_fields:

            if field not in raw_plan:
                raise PlanValidationError(
                    f"missing plan field: {field}"
                )

        # =================================================
        # 2. 基本类型
        # =================================================

        if not isinstance(
            raw_plan["entry"],
            str
        ):
            raise PlanValidationError(
                "entry must be a string"
            )

        if not isinstance(
            raw_plan["steps"],
            list
        ):
            raise PlanValidationError(
                "steps must be a list"
            )

        if not isinstance(
            raw_plan["edges"],
            list
        ):
            raise PlanValidationError(
                "edges must be a list"
            )

        if not raw_plan["steps"]:
            raise PlanValidationError(
                "plan must contain at least one step"
            )

        # =================================================
        # 3. Available capabilities
        # =================================================

        capability_map = {
            capability["name"]: capability
            for capability in capabilities
        }

        # =================================================
        # 4. Validate Steps
        # =================================================

        step_ids = set()

        for index, step in enumerate(
            raw_plan["steps"]
        ):

            if not isinstance(
                step,
                dict
            ):
                raise PlanValidationError(
                    f"step {index} must be a dict"
                )

            if "id" not in step:
                raise PlanValidationError(
                    f"step {index} missing id"
                )

            if "capability" not in step:
                raise PlanValidationError(
                    f"step {index} missing capability"
                )

            step_id = step["id"]

            capability = step[
                "capability"
            ]

            # -----------------------------------------
            # Step ID
            # -----------------------------------------

            if not isinstance(
                step_id,
                str
            ):
                raise PlanValidationError(
                    f"step {index} id must be a string"
                )

            if not step_id:
                raise PlanValidationError(
                    f"step {index} id cannot be empty"
                )

            if step_id == "__END__":
                raise PlanValidationError(
                    "__END__ is reserved "
                    "and cannot be used as step id"
                )

            if step_id in step_ids:
                raise PlanValidationError(
                    f"duplicate step id: {step_id}"
                )

            step_ids.add(
                step_id
            )

            # -----------------------------------------
            # Capability
            # -----------------------------------------

            if not isinstance(
                capability,
                str
            ):
                raise PlanValidationError(
                    f"step {step_id} capability "
                    f"must be a string"
                )

            if (
                capability
                not in capability_map
            ):
                raise PlanValidationError(
                    f"unknown capability: {capability}"
                )

            # -----------------------------------------
            # Arguments
            # -----------------------------------------

            arguments = step.get(
                "arguments",
                {}
            )

            if not isinstance(
                arguments,
                dict
            ):
                raise PlanValidationError(
                    f"step {step_id} arguments "
                    f"must be a dict"
                )

            self._validate_step_arguments(
                step_id=step_id,
                capability_name=capability,
                arguments=arguments,
                capability_map=capability_map
            )

        # =================================================
        # 5. Entry
        # =================================================

        entry = raw_plan["entry"]

        if entry not in step_ids:
            raise PlanValidationError(
                f"unknown entry step: {entry}"
            )

        # =================================================
        # 6. Graph structures
        # =================================================

        adjacency = {
            step_id: []
            for step_id in step_ids
        }

        reverse_adjacency = {
            step_id: []
            for step_id in step_ids
        }

        end_sources = set()

        seen_edges = set()

        # =================================================
        # 7. Validate Edges
        # =================================================

        for index, edge in enumerate(
            raw_plan["edges"]
        ):

            if not isinstance(
                edge,
                dict
            ):
                raise PlanValidationError(
                    f"edge {index} must be a dict"
                )

            if "source" not in edge:
                raise PlanValidationError(
                    f"edge {index} missing source"
                )

            if "target" not in edge:
                raise PlanValidationError(
                    f"edge {index} missing target"
                )

            source = edge[
                "source"
            ]

            target = edge[
                "target"
            ]

            # -----------------------------------------
            # Types
            # -----------------------------------------

            if not isinstance(
                source,
                str
            ):
                raise PlanValidationError(
                    f"edge {index} source "
                    f"must be a string"
                )

            if not isinstance(
                target,
                str
            ):
                raise PlanValidationError(
                    f"edge {index} target "
                    f"must be a string"
                )

            # -----------------------------------------
            # References
            # -----------------------------------------

            if source not in step_ids:
                raise PlanValidationError(
                    f"unknown edge source: {source}"
                )

            if (
                target != "__END__"
                and target not in step_ids
            ):
                raise PlanValidationError(
                    f"unknown edge target: {target}"
                )

            # -----------------------------------------
            # Duplicate edge
            # -----------------------------------------

            edge_key = (
                source,
                target
            )

            if edge_key in seen_edges:
                raise PlanValidationError(
                    f"duplicate edge: "
                    f"{source} -> {target}"
                )

            seen_edges.add(
                edge_key
            )

            # -----------------------------------------
            # Direct self-loop
            # -----------------------------------------

            if source == target:
                raise PlanValidationError(
                    f"self-loop is not allowed: "
                    f"{source} -> {target}"
                )

            # -----------------------------------------
            # Build graph
            # -----------------------------------------

            adjacency[
                source
            ].append(
                target
            )

            if target == "__END__":

                end_sources.add(
                    source
                )

            else:

                reverse_adjacency[
                    target
                ].append(
                    source
                )

        # =================================================
        # 8. Plan 必须有 END
        # =================================================

        if not end_sources:
            raise PlanValidationError(
                "plan has no transition to __END__"
            )

        # =================================================
        # 9. 所有 Step 必须从 Entry 可达
        # =================================================

        reachable = set()

        stack = [
            entry
        ]

        while stack:

            node = stack.pop()

            if node in reachable:
                continue

            reachable.add(
                node
            )

            for target in adjacency[
                node
            ]:

                if target == "__END__":
                    continue

                stack.append(
                    target
                )

        unreachable = (
            step_ids
            - reachable
        )

        if unreachable:

            raise PlanValidationError(
                "unreachable steps: "
                + ", ".join(
                    sorted(
                        unreachable
                    )
                )
            )

        # =================================================
        # 10. Cycle Detection
        # =================================================

        cycle = self._find_plan_cycle(
            adjacency
        )

        if cycle is not None:

            raise PlanValidationError(
                "cycle detected: "
                + " -> ".join(
                    cycle
                )
            )

        # =================================================
        # 11. 每个 Step 都必须能够最终到达 END
        # =================================================

        can_reach_end = set(
            end_sources
        )

        stack = list(
            end_sources
        )

        while stack:

            node = stack.pop()

            for previous in (
                reverse_adjacency[
                    node
                ]
            ):

                if (
                    previous
                    in can_reach_end
                ):
                    continue

                can_reach_end.add(
                    previous
                )

                stack.append(
                    previous
                )

        cannot_reach_end = (
            reachable
            - can_reach_end
        )

        if cannot_reach_end:

            raise PlanValidationError(
                "steps cannot reach __END__: "
                + ", ".join(
                    sorted(
                        cannot_reach_end
                    )
                )
            )


    def _find_plan_cycle(
        self,
        adjacency
    ):

        # =================================================
        # state:
        #
        # 0 = 尚未访问
        # 1 = 当前 DFS 路径中
        # 2 = 已完成
        # =================================================

        state = {
            node: 0
            for node in adjacency
        }

        path = []

        path_index = {}

        def dfs(
            node
        ):

            state[node] = 1

            path_index[
                node
            ] = len(
                path
            )

            path.append(
                node
            )

            for target in adjacency[
                node
            ]:

                if target == "__END__":
                    continue

                # =====================================
                # 尚未访问
                # =====================================

                if state[
                    target
                ] == 0:

                    cycle = dfs(
                        target
                    )

                    if cycle is not None:
                        return cycle

                # =====================================
                # target 还在当前 DFS 路径中
                #
                # 说明存在：
                #
                # A -> B -> C -> A
                # =====================================

                elif state[
                    target
                ] == 1:

                    start = (
                        path_index[
                            target
                        ]
                    )

                    return (
                        path[
                            start:
                        ]
                        + [
                            target
                        ]
                    )

            # =========================================
            # 当前 Node DFS 完成
            # =========================================

            path.pop()

            path_index.pop(
                node,
                None
            )

            state[
                node
            ] = 2

            return None

        # =================================================
        # 每个 component 都检查
        # =================================================

        for node in adjacency:

            if state[
                node
            ] != 0:
                continue

            cycle = dfs(
                node
            )

            if cycle is not None:
                return cycle

        return None


    def _validate_step_arguments(
        self,
        step_id,
        capability_name,
        arguments,
        capability_map
    ):

        capability = (
            capability_map[
                capability_name
            ]
        )

        contract = capability.get(
            "arguments",
            {}
        )

        # =============================================
        # 1. 不允许未知参数
        # =============================================

        unknown_arguments = (
            set(arguments.keys())
            - set(contract.keys())
        )

        if unknown_arguments:

            raise PlanValidationError(
                f"unknown arguments for "
                f"{capability_name}: "
                + ", ".join(
                    sorted(
                        unknown_arguments
                    )
                )
            )

        # =============================================
        # 2. 检查 required 参数
        # =============================================

        for argument_name, spec in (
            contract.items()
        ):

            required = spec.get(
                "required",
                False
            )

            if (
                required
                and argument_name
                not in arguments
            ):

                raise PlanValidationError(
                    f"missing required argument "
                    f"for {capability_name}: "
                    f"{argument_name}"
                )

            # 参数是 optional，
            # 并且 LLM 没有提供
            if argument_name not in arguments:
                continue

            # =========================================
            # 3. 类型检查
            # =========================================

            expected_type = spec.get(
                "type"
            )

            value = arguments[
                argument_name
            ]

            if not self._argument_matches_type(
                value,
                expected_type
            ):

                raise PlanValidationError(
                    f"invalid argument type "
                    f"for {capability_name}."
                    f"{argument_name}: "
                    f"expected {expected_type}, "
                    f"got "
                    f"{type(value).__name__}"
                )


    def _argument_matches_type(
        self,
        value,
        expected_type
    ):
    
        if expected_type == "string":
        
            return isinstance(
                value,
                str
            )
    
        if expected_type == "integer":
        
            return (
                isinstance(
                    value,
                    int
                )
                and not isinstance(
                    value,
                    bool
                )
            )
    
        if expected_type == "number":
        
            return (
                isinstance(
                    value,
                    (int, float)
                )
                and not isinstance(
                    value,
                    bool
                )
            )
    
        if expected_type == "boolean":
        
            return isinstance(
                value,
                bool
            )
    
        raise RuntimeError(
            "unsupported capability "
            f"argument type: "
            f"{expected_type}"
        )
             