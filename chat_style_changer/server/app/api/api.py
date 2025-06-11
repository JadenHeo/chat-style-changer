from typing import Optional

from app.api.svc_container import service_container
from app.infra.message_parser import MessageParser
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

vector_store = service_container.vector_store
llm_service = service_container.llm_service
speech_style_converter = service_container.speech_style_converter


class ConvertSpeechStyleRequest(BaseModel):
    query: str
    context_messages: Optional[str] = None

@router.post("/convert")
async def convert_speech_style(req: ConvertSpeechStyleRequest):
    try:
        results = vector_store.search(req.query, 20)
        context_messages = []
        if req.context_messages:
            context_messages = MessageParser.from_str(req.context_messages)

        for msg in context_messages:
            print(msg)

        converted_sentence = speech_style_converter.convert(
            target_sentence=req.query, 
            similar_utterances=[msg.content for msg, _ in results],
            context_messages=context_messages
            )
        
        return {
            "status": "success",
            "converted": converted_sentence
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))