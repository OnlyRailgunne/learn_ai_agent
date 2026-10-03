from groq import Groq


client = Groq()
MODEL = "openai/gpt-oss-120b"


def decide_retrieval(user_input):

    messages = [
        {
            "role": "system",
            "content": (
                "Decide whether the user's question requires "
                "information from the company knowledge base.\n"
                "If it requires company-specific information, "
                "return exactly RETRIEVE.\n"
                "Otherwise, return exactly ANSWER."
            ),
        },
        {
            "role": "user",
            "content": user_input,
        },
    ]

    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
    )

    return response.choices[0].message.content.strip()


if __name__ == "__main__":

    questions = [
        "公司的远程办公政策是什么？",
        "你好，你是谁？",
    ]

    for question in questions:

        decision = decide_retrieval(question)

        print()
        print("Question:", question)
        print("Decision:", decision)