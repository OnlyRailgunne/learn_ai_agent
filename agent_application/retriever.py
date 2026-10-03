from pathlib import Path


class Retriever:

    def __init__(self, knowledge_dir):
        self.knowledge_dir = Path(knowledge_dir)

    def retrieve(self, query):
        results = []

        for file in self.knowledge_dir.glob("*.txt"):
            text = file.read_text(encoding="utf-8")

            if query.lower() in text.lower():
                results.append(text)

        return results