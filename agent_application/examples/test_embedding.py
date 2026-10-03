from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


model = SentenceTransformer("all-MiniLM-L6-v2")

texts = [
    "远程办公一周最多三天",
    "员工每周最多可以在家工作三天",
    "今天东京天气很好",
]

embeddings = model.encode(texts)

similarities = cosine_similarity(embeddings)

print("=== Similarity ===")

for i in range(len(texts)):
    for j in range(i + 1, len(texts)):
        print()
        print(f"Text {i}:", texts[i])
        print(f"Text {j}:", texts[j])
        print("Similarity:", similarities[i][j])