from pydantic_settings import BaseSettings
from functools import lru_cache
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "RAG API"
    
    # Embedding Model Settings
    MODEL_NAME: str = "dragonkue/snowflake-arctic-embed-l-v2.0-ko"
    MODEL_DIM: int = 1024
    # MODEL_NAME: str = "snunlp/KR-SBERT-V40K-klueNLI-augSTS"
    # MODEL_DIM: int = 768

    # Milvus Settings
    MILVUS_HOST: str = os.getenv("MILVUS_HOST", "localhost")
    MILVUS_PORT: int = int(os.getenv("MILVUS_PORT", "19530"))
    
    # ChromaDB Settings
    CHROMA_PERSIST_DIRECTORY: str = ".chroma"
    
    # API Keys (if needed)
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    class Config:
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings() 