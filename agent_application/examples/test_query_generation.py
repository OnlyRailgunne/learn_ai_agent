from groq import Groq


client = Groq()
MODEL = "openai/gpt-oss-120b"


def generate_query(user_input):

    messages = [
        {
            "role": "system",
            "content": (
                "Convert the user's question into a short search query "
                "for a company knowledge base. "
                "Return only the search query."
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
        "远程办公一周最多可以几天？",
        "在家工作的时候需要满足什么条件？",
    ]

    for question in questions:

        query = generate_query(question)

        print()
        print("Question:", question)
        print("Generated Query:", query)