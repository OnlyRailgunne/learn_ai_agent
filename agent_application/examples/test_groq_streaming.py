from groq import Groq


client = Groq()

MODEL = "openai/gpt-oss-120b"


response = client.chat.completions.create(
    model=MODEL,
    messages=[
        {
            "role": "user",
            "content": "请简单介绍一下东京。",
        }
    ],
    stream=True,
)


print("=== Streaming ===")

for chunk in response:
    content = chunk.choices[0].delta.content

    if content:
        print(content, end="", flush=True)

print()