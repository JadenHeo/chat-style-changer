from typing import List

from app.config.config import settings
from sentence_transformers import SentenceTransformer


class EmbeddingService:
    def __init__(self, model_name: str = settings.MODEL_NAME):
        self.model = SentenceTransformer(model_name)

    def get_embedding(self, text: str) -> List[float]:
        """Get embedding for a single text."""
        return self.model.encode(text).tolist()

    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Get embeddings for multiple texts."""
        return self.model.encode(texts).tolist()
