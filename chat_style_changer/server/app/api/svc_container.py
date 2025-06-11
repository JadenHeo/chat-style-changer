from app.infra.llm import LLMService
from app.infra.message_parser import MessageParser
from app.infra.vector_store import VectorStore
from app.services.async_vector_loader import AsyncVectorLoader
from app.services.speech_style_converter import SpeechStyleConverter


class ServiceContainer:
    def __init__(self):
        self.vector_store = VectorStore()
        self.vector_loader = AsyncVectorLoader(self.vector_store)
        self.llm_service = LLMService()
        self.speech_style_converter = SpeechStyleConverter(self.llm_service)
    

service_container = ServiceContainer()