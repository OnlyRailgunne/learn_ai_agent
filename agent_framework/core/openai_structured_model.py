import json

from openai import OpenAI


class OpenAIStructuredModel:

    def __init__(
        self,
        model="gpt-5.6-luna",
        client=None
    ):

        self.model = model

        self.client = (
            client
            if client is not None
            else OpenAI()
        )


    def generate_structured(
        self,
        system_prompt,
        input,
        schema
    ):

        response = (
            self.client.responses.create(
                model=self.model,

                instructions=system_prompt,

                input=json.dumps(
                    input,
                    ensure_ascii=False
                ),

                text={
                    "format": {
                        "type":
                            "json_schema",

                        "name":
                            "execution_plan",

                        "schema":
                            schema,

                        "strict":
                            True
                    }
                },

                store=False
            )
        )

        # =========================================
        # 1. API Execution
        # =========================================

        if response.status != "completed":

            raise RuntimeError(
                "structured model response "
                f"not completed: "
                f"{response.status}"
            )

        # =========================================
        # 2. Structured Output
        # =========================================

        output_text = (
            response.output_text
        )

        if not output_text:

            raise RuntimeError(
                "structured model returned "
                "no output"
            )

        # =========================================
        # 3. JSON string -> Python dict
        # =========================================

        return json.loads(
            output_text
        )