import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import upload, chat

app = FastAPI(title="AI Research Assistant API")

# Allowed origins: local dev + production frontend (set via env var)
allowed_origins = ["http://localhost:3000", "http://127.0.0.1:3000"]

frontend_url = os.getenv("FRONTEND_URL")
if frontend_url:
    allowed_origins.append(frontend_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router)
app.include_router(chat.router)

@app.get("/")
def health_check():
    return {"status": "ok", "message": "AI Research Assistant API is running"}
