from semantic_retriever import SemanticRetriever


retriever = SemanticRetriever("knowledge")


questions = [
    "远程办公政策",
    "公司的股票代码是什么？",
]


for query in questions:

    results = retriever.retrieve(
        query,
        top_k=3,
        threshold=0.1
    )

    print()
    print("=== Query ===")
    print(query)

    print()
    print("=== Retrieved Chunks ===")

    if not results:
        print("No relevant chunks.")
        continue

    for chunk, score in results:
        print()
        print("Chunk:")
        print(chunk)
        print("Similarity:", score)