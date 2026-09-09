PLAN_SCHEMA = {
    "type": "object",

    "properties": {

        "entry": {
            "type": "string"
        },

        "steps": {
            "type": "array",

            "items": {
                "type": "object",

                "properties": {

                    "id": {
                        "type": "string"
                    },

                    "capability": {
                        "type": "string"
                    },

                    "arguments": {
                        "type": "object"
                    }
                },

                "required": [
                    "id",
                    "capability",
                    "arguments"
                ]
            }
        },

        "edges": {
            "type": "array",

            "items": {
                "type": "object",

                "properties": {

                    "source": {
                        "type": "string"
                    },

                    "target": {
                        "type": "string"
                    }
                },

                "required": [
                    "source",
                    "target"
                ]
            }
        }
    },

    "required": [
        "entry",
        "steps",
        "edges"
    ]
}


class PlanningLLM:

    def __init__(
        self,
        model
    ):
        self.model = model


    def plan(
        self,
        goal,
        capabilities
    ):

        system_prompt = (
            self._build_system_prompt()
        )

        planning_input = {
            "goal": self._goal_text(
                goal
            ),

            "capabilities": capabilities
        }

        raw_plan = (
            self.model.generate_structured(
                system_prompt=system_prompt,
                input=planning_input,
                schema=PLAN_SCHEMA
            )
        )

        print()
        print(
            "raw llm plan:",
            raw_plan
        )

        # =========================================
        # 不再 normalize
        #
        # LLM 直接输出 Planner 已经认识的格式：
        #
        # {
        #     entry,
        #     steps,
        #     edges
        # }
        #
        # Planner 后面负责 Validation。
        # =========================================

        return raw_plan


    def _build_system_prompt(
        self
    ):

        return """
You are a planning model.

Your only job is to create a small finite
execution plan for the user's goal.

Do not execute tools.

Do not solve the task yourself.

Do not invent capabilities.

Only use capabilities provided in the input.

Use as few steps as necessary.

The output must be one JSON object with
exactly these three top-level fields:

- entry
- steps
- edges

"entry" is the id of the first step.

"steps" contains only step objects.

Each step contains:

- id
- capability
- arguments

"capability" must be one of the available
capabilities.

"arguments" MUST be a JSON object.

For example:

"arguments": {
    "some_argument": "some value"
}

Use only argument names defined by the
selected capability.

If a capability has no arguments, use:

"arguments": {}

"edges" contains only edge objects.

Each edge contains:

- source
- target

Example structural form:

{
    "entry": "step1",

    "steps": [
        {
            "id": "step1",
            "capability": "some_capability",
            "arguments": {}
        }
    ],

    "edges": [
        {
            "source": "step1",
            "target": "__END__"
        }
    ]
}

Never put edge objects inside "steps".

Never put step objects inside "edges".

Do not create unnecessary repeated steps.

Do not create self-loops.

Do not create cycles.

Every step must be reachable from entry.

Every execution path must eventually
reach "__END__".

Use "__END__" only as an edge target
to represent successful termination.
""".strip()


    def _goal_text(
        self,
        goal
    ):

        if isinstance(
            goal,
            str
        ):
            return goal

        for attribute in [
            "description",
            "text",
            "value",
            "goal"
        ]:

            if hasattr(
                goal,
                attribute
            ):

                return getattr(
                    goal,
                    attribute
                )

        raise TypeError(
            "cannot extract text from Goal"
        )