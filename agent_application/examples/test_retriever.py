from retriever import Retriever


retriever = Retriever("knowledge")

query = "remote"

results = retriever.retrieve(query)

print("=== query ===")
print(query)

print("\n=== retrieved results ===")

for result in results:
    print(result)