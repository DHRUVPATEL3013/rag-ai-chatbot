"""
FastAPI application entrypoint.

Run with: uvicorn app.main:app --reload
"""

# TODO:
#   app = FastAPI(title="AI Guidance Chatbot")
#   include the routers from app/api/routes/*
#   add CORS middleware for your frontend's origin
#   add a GET /health endpoint that returns {"status": "ok"}


"""
FastAPI application entrypoint.
"""

from fastapi import FastAPI

from app.api.routes.chat import router as chat_router
from fastapi.staticfiles import StaticFiles
from app.api.documents import router as documents_router
from app.api.admin import router as admin_router

from app.api.routes.feedback import router as feedback_router
from app.api.admin import router as admin_router

app = FastAPI(
    title="AI Guidance Chatbot",
    description="RAG-based internal knowledge assistant",
    version="1.0.0",
)

app.include_router(feedback_router)

app.include_router(chat_router)
app.include_router(admin_router)
app.include_router(documents_router)
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

@app.get("/health")
def health():
    return {
        "status": "ok"
    }


