from app.api import api, vector_store
from app.config.config import settings
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(api.router, prefix=settings.API_V1_STR, tags=["chat"])
app.include_router(vector_store.router, prefix=settings.API_V1_STR, tags=["vector-store"])

@app.get("/")
async def root():
    return {"message": "Welcome to RAG API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True) 