import json
from typing import Optional

from app.api.svc_container import service_container
from app.infra.message_parser import MessageParser
from fastapi import APIRouter, File, Form, HTTPException, Query, UploadFile
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

router = APIRouter(prefix="/vector-store")
vector_store = service_container.vector_store
vector_loader = service_container.vector_loader


@router.get("/collections")
async def get_collections():
    """Get all collections in the vector store."""
    try:
        collections = vector_store.get_collections()

        return {
            "status": "success",
            "collections": collections
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.get("/collections:loaded")
async def get_loaded_collection():
    """Get all loaded collections in the vector store."""
    try:
        collection_name = vector_store.get_loaded_collection()

        return {
            "status": "success",
            "loaded_collection": collection_name
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/collections:load")
async def load_collection(
    name: str = Query(..., description="Collection name to load")
):
    """Load a collection to Memory."""
    try:
        vector_store.load_collection(name)

        return {
            "status": "success",
            "collection_name": name
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))    


@router.post("/collections")
async def create_collection(
    name: str = Query(..., description="Collection name to create")
):
    """Create a new collection in the vector store."""
    try:
        vector_store.create_collection(name)
        collections = vector_store.get_collections()

        return {
            "status": "success",
            "collections": collections
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.delete("/collections")
async def drop_collection(
    name: str = Query(..., description="Collection name to drop")
):
    """Drop a collection from the vector store."""
    try:
        vector_store.drop_collection(name)
        collections = vector_store.get_collections()
        
        return {
            "status": "success",
            "collections": collections
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/collections/vectors:load")
async def load_vectors(
    collection_name: str = Form(...),
    user_name: str = Form(...),
    size: int = Form(None),
    csv_file: UploadFile = File(...)
):
    """Load messages from a CSV file in the resources directory and store them in the vector store.
    
    Args:
        request: Request body containing file_name and optional size
        
    Returns:
        StreamingResponse: Server-sent events with progress updates
    """
    try:
        # Parse messages from CSV
        messages = await MessageParser.extract_user_messages(csv_file, user_name)
        
        # Use AsyncVectorLoader to process messages with progress tracking
        async def event_generator():
            async for progress in vector_loader.load_messages(collection_name, messages):
                yield f"data: {json.dumps(progress)}\n\n"
        
        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/collections/vectors:count")
async def get_vector_store_count(
    name: str = Query(..., description="Collection name to get count from")
):
    """Get the number of messages in the vector store."""
    try:
        count = vector_store.get_count(name)
        
        return {
            "status": "success",
            "collection_name": name,
            "count": count
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get(":search")
async def search_messages(
    query: str = Query(..., description="User query string to convert style"),
    top_k: int = Query(5, ge=1, le=50, description="Number of similar results to return (default: 5)")
):
    """Search for messages similar to the query.
    
    Args:
        query: User query string to convert style
        
    Returns:
        dict: List of similar messages with their scores
    """
    try:
        # Search for similar messages
        results = vector_store.search(query, top_k)
        
        # Format results
        messages = []
        for message, score in results:
            messages.append({
                "content": message.content,
                "timestamp": message.timestamp,
                "score": score
            })
        
        return {
            "status": "success",
            "collection_name": vector_store.loaded_collection._name,
            "query": query,
            "top_k": top_k,
            "messages": messages
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))