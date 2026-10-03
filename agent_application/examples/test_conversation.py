from groq import Groq
import os
import json

from tools.weather import current_weather


client = Groq(api_key=os.environ["GROQ_API_KEY"])


messages = [
    {
        "role": "system",
        "content": (
            "You are a helpful assistant. "
            "Use the available tools when necessary."
        )
    }
]


tools = [
    {
        "type": "function",
        "function": {
            "name": "current_weather",
            "description": "Get the current weather of a city.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "City name"
                    }
                },
                "required": ["city"]
            }
        }
    }
]


available_tools = {
    "current_weather": current_weather
}


for user_input in [
    "东京天气怎么样？",
    "那纽约呢？",
    "东京和纽约哪个温度更高？"
]:

    print("\nUser:", user_input)

    messages.append({
        "role": "user",
        "content": user_input
    })


    # Agent Loop
    for _ in range(5):

        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )

        message = response.choices[0].message


        # 没有 Tool Call，说明 LLM 给出了最终答案
        if not message.tool_calls:

            answer = message.content

            print("Assistant:", answer)

            messages.append({
                "role": "assistant",
                "content": answer
            })

            break


        # 有 Tool Call
        messages.append(message)


        for tool_call in message.tool_calls:

            tool_name = tool_call.function.name

            arguments = json.loads(
                tool_call.function.arguments
            )

            print(
                "Tool:",
                tool_name,
                arguments
            )

            tool_result = available_tools[tool_name](**arguments)

            print(
                "Tool Result:",
                tool_result
            )

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(tool_result)
            })


print("\n=== Final Messages ===")
print(messages)