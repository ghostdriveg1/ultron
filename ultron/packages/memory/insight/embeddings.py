import openai

class EmbeddingGenerator:
    def __init__(self):
        self.client = openai.OpenAI()
        self.model = "text-embedding-3-small"

    def generate(self, text: str) -> list[float]:
        response = self.client.embeddings.create(input=[text], model=self.model)
        return response.data[0].embedding

    def generate_batch(self, texts: list[str]) -> list[list[float]]:
        response = self.client.embeddings.create(input=texts, model=self.model)
        return [data.embedding for data in response.data]
