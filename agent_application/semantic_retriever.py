from pathlib import Path

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


class SemanticRetriever:

    def __init__(self, knowledge_dir):
        self.knowledge_dir = Path(knowledge_dir)
        self.model = SentenceTransformer(
            "all-MiniLM-L6-v2"
        )

    def retrieve(self, query, top_k=3, threshold=0.1):

        documents = []

        for file in self.knowledge_dir.glob("*.txt"):
            text = file.read_text(encoding="utf-8")

            chunks = text.split("\n\n")

            for chunk in chunks:
                chunk = chunk.strip()

                if chunk:
                    documents.append(chunk)

        query_embedding = self.model.encode(
            [query]
        )

        document_embeddings = self.model.encode(
            documents
        )

        similarities = cosine_similarity(
            query_embedding,
            document_embeddings
        )[0]

        top_indices = similarities.argsort()[::-1][:top_k]

        results = [
            (documents[index], similarities[index])
            for index in top_indices
            if similarities[index] >= threshold
        ]

        return results