import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Any, AsyncGenerator, Dict, List

from app.infra.vector_store import VectorStore
from app.models.message import Message
from sklearn.preprocessing import normalize


logger = logging.getLogger(__name__)

class AsyncVectorLoader:
    def __init__(
        self,
        vector_store: VectorStore,
        batch_size: int = 100,
        max_workers: int = 4
    ):
        """
        Initialize AsyncVectorLoader.
        
        Args:
            vector_store: VectorStore instance for storing embeddings
            batch_size: Number of messages to process in each batch
            max_workers: Maximum number of worker threads for parallel processing
        """
        self.vector_store = vector_store
        self.batch_size = batch_size
        self.max_workers = max_workers
        self.processed_count = 0
        self.total_count = 0

    def add_batch(self, messages: List[Message], embeddings: List[List[float]]) -> None:
        """
        Add a batch of messages and their embeddings to the vector store.
        
        Args:
            messages: List of messages to add
            embeddings: List of embeddings corresponding to the messages
        """
        try:
            # Insert into vector store
            self.vector_store.add(messages=messages, embeddings=embeddings)
            
        except Exception as e:
            logger.error(f"Error adding batch to vector store: {str(e)}")
            raise

    async def process_batch(
        self,
        batch: List[Message],
        batch_num: int
    ) -> int:
        """
        Process a single batch of messages asynchronously.
        
        Args:
            batch: List of messages to process
            batch_num: Batch number for logging
            
        Returns:
            int: Number of processed messages
        """
        try:
            # Generate embeddings in a separate thread
            with ThreadPoolExecutor(max_workers=1) as executor:
                loop = asyncio.get_event_loop()
                embeddings = await loop.run_in_executor(
                    executor,
                    self.vector_store.embedding_service.get_embeddings,
                    [msg.content for msg in batch]
                )
            
            embeddings = normalize(embeddings, norm='l2').tolist()
            
            # Store in vector store in a separate thread
            await asyncio.to_thread(
                self.add_batch,
                batch,
                embeddings
            )
            
            return len(batch)
            
        except Exception as e:
            logger.error(f"Error processing batch {batch_num}: {str(e)}")
            raise

    async def load_messages(
        self,
        collection_name: str,
        messages: List[Message]
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Load messages into vector store with progress tracking.
        
        Args:
            messages: List of messages to process
            
        Yields:
            Dict containing progress information
        """
        self.total_count = len(messages)
        self.processed_count = 0
        
        try:
            self.vector_store.load_collection(collection_name)
            
            # Split messages into batches
            batches = [
                messages[i:i + self.batch_size]
                for i in range(0, self.total_count, self.batch_size)
            ]
            
            # Create tasks for parallel processing
            tasks = [
                self.process_batch(batch, i)
                for i, batch in enumerate(batches)
            ]
            
            # Process batches and track progress
            for task in asyncio.as_completed(tasks):
                try:
                    batch_count = await task
                    self.processed_count += batch_count
                    
                    # Calculate and yield progress
                    percentage = (self.processed_count / self.total_count) * 100
                    yield {
                        "status": "processing",
                        "processed": self.processed_count,
                        "total": self.total_count,
                        "percentage": round(percentage, 2)
                    }
                    
                except Exception as e:
                    logger.error(f"Error in batch processing: {str(e)}")
                    yield {
                        "status": "error",
                        "error": str(e)
                    }
                    return
            
            # Yield completion status
            yield {
                "status": "completed",
                "processed": self.total_count,
                "total": self.total_count,
                "percentage": 100.0
            }
            
        except Exception as e:
            logger.error(f"Error in message loading: {str(e)}")
            yield {
                "status": "error",
                "error": str(e)
            }

    def get_progress(self) -> Dict[str, Any]:
        """
        Get current loading progress.
        
        Returns:
            Dict containing current progress information
        """
        if self.total_count == 0:
            return {
                "status": "not_started",
                "processed": 0,
                "total": 0,
                "percentage": 0.0
            }
            
        percentage = (self.processed_count / self.total_count) * 100
        return {
            "status": "processing",
            "processed": self.processed_count,
            "total": self.total_count,
            "percentage": round(percentage, 2)
        } 