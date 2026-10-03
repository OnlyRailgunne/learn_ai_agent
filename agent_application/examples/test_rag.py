from groq import Groq

from retriever import Retriever


client = Groq()
MODEL = "openai/gpt-oss-120b"


def answer_with_knowledge(user_input):

    retriever = Retriever("knowledge")

    results = retriever.retrieve("remote")

    context = "\n\n".join(results)

    messages = [
        {
            "role": "system",
            "content": (
                "Answer the user's question "
                "using the provided knowledge."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Knowledge:\n"
                f"{context}\n\n"
                f"Question:\n"
                f"{user_input}"
            ),
        },
    ]

    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
    )

    return response.choices[0].message.content


if __name__ == "__main__":

    result = answer_with_knowledge(
        "公司的远程办公政策是什么？"
    )

    print("\nFinal answer:")
    print(result)