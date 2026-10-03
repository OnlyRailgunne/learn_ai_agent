from groq import Groq

from semantic_retriever import SemanticRetriever
from .test_retrieval_decision import decide_retrieval
from .test_query_generation import generate_query


client = Groq()
MODEL = "openai/gpt-oss-120b"

retriever = SemanticRetriever("knowledge")


def run_rag_agent(user_input):

    decision = decide_retrieval(user_input)

    print("Decision:", decision)

    if decision == "ANSWER":

        messages = [
            {
                "role": "user",
                "content": user_input,
            }
        ]

        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
        )

        return response.choices[0].message.content

    query = generate_query(user_input)

    print("Generated Query:", query)

    results = retriever.retrieve(
        query,
        top_k=3
    )

    print()
    print("=== Retrieved Knowledge ===")

    for chunk, score in results:
        print()
        print("Chunk:")
        print(chunk)
        print("Similarity:", score)

    retrieved_knowledge = "\n\n".join(
        chunk
        for chunk, score in results
    )

    messages = [
        {
            "role": "system",
            "content": (
                "Answer the user's question using only the "
                "provided company knowledge. "
                "Do not add information that is not present "
                "in the retrieved knowledge. "
                "If the retrieved knowledge does not contain "
                "the answer, say that the information is not "
                "available."
            ),
        },
        {
            "role": "user",
            "content": user_input,
        },
        {
            "role": "system",
            "content": (
                "Retrieved Knowledge:\n"
                + retrieved_knowledge
            ),
        },
    ]

    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
    )

    return response.choices[0].message.content


if __name__ == "__main__":

    result = run_rag_agent(
        "公司的远程办公政策是什么？"
    )

    print()
    print("=== Final Answer ===")
    print(result)