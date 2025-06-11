import os
from datetime import datetime
from typing import List, Optional, Tuple

from app.config.config import settings
from app.models.message import Message
from pymilvus import (Collection, CollectionSchema, DataType, FieldSchema,
                      connections, utility)

from .embedding import EmbeddingService


class VectorStore:
    def __init__(self):
        # Milvus connection
        connections.connect(uri=settings.MILVUS_URL, token=settings.MILVUS_TOKEN)
        
        # Initialize embedding service
        self.embedding_service = EmbeddingService()
        self.loaded_collection = None

    def get_collections(self) -> List[str]:
        """Get all collections in the database."""
        return utility.list_collections()
    
    def get_loaded_collection(self) -> Optional[str]:
        """Get all loaded collections in the database."""
        return self.loaded_collection.name if self.loaded_collection else None
    
    def load_collection(self, collection_name: str):
        """Load a collection into memory."""
        if self.loaded_collection:
            self.loaded_collection.release()
            self.loaded_collection = None

        collection = Collection(collection_name)
        collection.load()
        self.loaded_collection = collection

    def create_collection(self, collection_name: str):
        """Create a new collection with the specified schema."""
        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=settings.MODEL_DIM),
            FieldSchema(name="chatroom_id", dtype=DataType.INT64),
            FieldSchema(name="timestamp", dtype=DataType.VARCHAR, max_length=65535),
            FieldSchema(name="content", dtype=DataType.VARCHAR, max_length=65535),
        ]
        schema = CollectionSchema(fields=fields, description="Document collection")
        collection = Collection(name=collection_name, schema=schema)
        
        # Create index for embedding field
        index_params = {
            "metric_type": "COSINE",
            "index_type": "IVF_FLAT",
            "params": {"nlist": 128}
        }
        collection.create_index(field_name="embedding", index_params=index_params)
        self.load_collection(collection_name)
    
    def delete_collection(self, collection_name: str):
        """Delete a collection from the database."""
        try:
            utility.drop_collection(collection_name)
        except Exception as e:
            print(f"Error deleting collection {collection_name}: {e}")
            raise e

    def add(self, messages: List[Message], embeddings: List[List[float]]):
        """Add documents to the vector store."""            
        chatroom_ids = [msg.chatroom_id for msg in messages]
        timestamps = [msg.timestamp.strftime("%Y-%m-%d %H:%M:%S") for msg in messages]  # Convert datetime to string
        contents = [msg.content for msg in messages]

        # Prepare data for insertion
        documents = [
            embeddings,  # embedding field
            chatroom_ids,   # text field
            timestamps,   # datetime field as string
            contents,   # text field
        ]

        # Insert data
        self.loaded_collection.insert(documents)
        self.loaded_collection.flush()

    def search(self, query: str, top_k: int = 5) -> List[Tuple[Message, float]]:
        """
        Search for similar documents.
        
        Args:
            query: The search query string
            top_k: Number of results to return
            
        Returns:
            List of tuples containing (Message, score) pairs
        """
        # Get query embedding
        query_embedding = self.embedding_service.get_embedding(query)
        
        # Search parameters
        search_params = {
            "metric_type": "COSINE",
            "params": {"nprobe": 16}
        }
        
        # Search
        results = self.loaded_collection.search(
            data=[query_embedding],
            anns_field="embedding",
            param=search_params,
            limit=top_k,
            output_fields=["chatroom_id", "timestamp", "content"]
        )
        
        # Convert results to Message objects with scores
        messages_with_scores = []
        for hits in results:
            for hit in hits:
                # Parse timestamp string back to datetime
                timestamp_str = hit.entity.get('timestamp')
                timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                
                message = Message(
                    chatroom_id=hit.entity.get('chatroom_id'),
                    timestamp=timestamp,
                    content=hit.entity.get('content')
                )
                messages_with_scores.append((message, hit.score))
        
        return messages_with_scores

    def get_count(self, collection_name: str) -> int:
        """Get the total number of documents in the collection."""
        return Collection(collection_name).num_entities

    def drop_collection(self, collection_name: str):
        """Drop a collection from the vector store."""
        collection = Collection(collection_name)
        collection.release()
        self.loaded_collection = None
        collection.drop()
