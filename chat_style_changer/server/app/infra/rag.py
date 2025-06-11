from typing import Any, Dict

from .vector_store import VectorStore


class RAGService:
    def __init__(self, collection_name: str = "documents"):
        self.vector_store = VectorStore(collection_name)

    def query(self, query: str, n_results: int = 5) -> Dict[str, Any]:
        """Query the RAG system with a question."""
        # Search for relevant documents
        search_results = self.vector_store.search(query, n_results)
        
        # Combine the retrieved documents into context
        context = "\n".join(search_results["documents"][0])
        
        return 