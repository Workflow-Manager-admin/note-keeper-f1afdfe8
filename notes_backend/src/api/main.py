from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import NoteStorage only
from src.api.models import NoteStorage

app = FastAPI()

# Storage instance, using in-memory by default. Pass db_path="notes.db" to use SQLite.
note_storage = NoteStorage(db_path=None)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def health_check():
    """Health check endpoint for Notes API."""
    return {"message": "Healthy"}
