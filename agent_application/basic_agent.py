import json

from groq import Groq


client = Groq()
MODEL = "openai/gpt-oss-120b"


# =========================
# 1. Tool Schemas
# =========================

from agent_application.tool_schemas import tool_schemas


# =========================
# 2. Available Tools
# =========================

from agent_application.tools.weather import current_weather
from agent_application.tools.exchange import exchange_rate

available_tools = {
    "current_weather": current_weather,
    "exchange_rate": exchange_rate,
}



# =========================
# 3. Agent Loop
# =========================

def run_agent(user_input, messages=None):

    if messages is None:
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a helpful assistant. "
                    "Use the available tools when necessary."
                ),
            },
        ]

    messages.append(
        {
            "role": "user",
            "content": user_input,
        }
    )

    max_iterations = 5

    for _ in range(max_iterations):

        print("\n=== messages before LLM call ===")

        for message_item in messages:
            print(message_item)

        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=tool_schemas,
            tool_choice="auto",
        )

        message = response.choices[0].message

        if not message.tool_calls:
            messages.append(message)
            return message.content, messages

        messages.append(message)

        for tool_call in message.tool_calls:

            tool_name = tool_call.function.name

            arguments = json.loads(
                tool_call.function.arguments
            )

            print(
                f"LLM requested tool: "
                f"{tool_name}({arguments})"
            )

            tool = available_tools[tool_name]

            result = tool(**arguments)

            print(f"Tool result: {result}")

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": tool_name,
                    "content": str(result),
                }
            )

    raise RuntimeError(
        "Agent exceeded maximum iterations"
    )

if __name__ == "__main__":

    result = run_agent(
        "东京现在天气怎么样？如果现在温度高于20°C，帮我查一下100美元是多少欧元。"
    )

    print()
    print("Final answer:")
    print(result)