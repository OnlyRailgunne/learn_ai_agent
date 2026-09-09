import json

from groq import Groq


class GroqStructuredModel:

    def __init__(
        self,
        model="openai/gpt-oss-120b",
        client=None
    ):

        self.model = model

        self.client = (
            client
            if client is not None
            else Groq()
        )


    def generate_structured(
        self,
        system_prompt,
        input,
        schema
    ):

        # =========================================
        # 我们仍然把期望结构告诉模型，
        # 但不让 Groq Provider 强制验证 schema。
        #
        # Framework 自己已经有完整 Validation。
        # =========================================

        prompt = (
            system_prompt
            + "\n\n"
            + "EXPECTED JSON STRUCTURE:\n"
            + json.dumps(
                schema,
                ensure_ascii=False,
                indent=2
            )
            + "\n\n"
            + "PLANNING INPUT:\n"
            + json.dumps(
                input,
                ensure_ascii=False,
                indent=2
            )
        )

        response = (
            self.client
            .chat
            .completions
            .create(

                model=self.model,

                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],

                # =================================
                # 不再使用：
                #
                # json_schema + strict=True
                #
                # Groq 只负责保证：
                #
                # 返回合法 JSON object
                # =================================

                response_format={
                    "type": "json_object"
                },

                reasoning_effort="low",

                max_completion_tokens=1024
            )
        )

        content = (
            response
            .choices[0]
            .message
            .content
        )

        if not content:

            raise RuntimeError(
                "Groq returned no output"
            )

        return json.loads(
            content
        )