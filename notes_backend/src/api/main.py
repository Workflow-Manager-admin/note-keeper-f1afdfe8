from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from typing import List

# Import NoteStorage and models
from src.api.models import NoteStorage, Note, NoteCreate

app = FastAPI(
    title="Notes API",
    description="CRUD API for notes management.",
    version="1.0.0",
    openapi_tags=[
        {"name": "notes", "description": "Operations on notes"}
    ]
)

# Storage instance, using in-memory by default. Pass db_path="notes.db" to use SQLite.
note_storage = NoteStorage(db_path=None)

# CORS configuration for cross-origin requests (frontend access)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", tags=["health"])
def health_check():
    """Health check endpoint for Notes API."""
    return {"message": "Healthy"}

# PUBLIC_INTERFACE
@app.get("/notes", response_model=List[Note], tags=["notes"], summary="List all notes", description="Lists all notes in the system.")
def list_notes():
    """
    List all notes.

    Returns:
        List[Note]: A list of all Note objects in storage.
    """
    return note_storage.list_notes()

# PUBLIC_INTERFACE
@app.post(
    "/notes",
    response_model=Note,
    status_code=status.HTTP_201_CREATED,
    tags=["notes"],
    summary="Create a new note",
    description="Creates a new note and returns it."
)
def create_note(note: NoteCreate):
    """
    Create a new note.

    Args:
        note (NoteCreate): The note data to create.

    Returns:
        Note: The newly created Note object.
    """
    created_note = note_storage.add_note(note)
    return created_note

# PUBLIC_INTERFACE
@app.get(
    "/notes/{note_id}",
    response_model=Note,
    tags=["notes"],
    summary="Get a note by ID",
    description="Retrieves a note by its unique integer ID."
)
def get_note(note_id: int):
    """
    Retrieve a note by ID.

    Args:
        note_id (int): The unique identifier for the note.

    Returns:
        Note: The Note object if found.

    Raises:
        HTTPException: 404 if note not found.
    """
    note = note_storage.get_note(note_id)
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Note with id {note_id} not found."
        )
    return note

# PUBLIC_INTERFACE
@app.put(
    "/notes/{note_id}",
    response_model=Note,
    tags=["notes"],
    summary="Update a note by ID",
    description="Updates a note with a given ID using the provided note data."
)
def update_note(note_id: int, note_update: NoteCreate):
    """
    Update a note by ID.

    Args:
        note_id (int): Unique identifier for the note.
        note_update (NoteCreate): Data to update (title/content).

    Returns:
        Note: Updated Note object.

    Raises:
        HTTPException: 404 if note not found.
    """
    updated = note_storage.update_note(note_id, note_update)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Note with id {note_id} not found."
        )
    return updated

# PUBLIC_INTERFACE
@app.delete(
    "/notes/{note_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["notes"],
    summary="Delete a note by ID",
    description="Deletes a note by its unique integer ID."
)
def delete_note(note_id: int):
    """
    Delete a note by ID.

    Args:
        note_id (int): Unique identifier for the note.

    Returns:
        None

    Raises:
        HTTPException: 404 if note not found.
    """
    deleted = note_storage.delete_note(note_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Note with id {note_id} not found."
        )
    return None
