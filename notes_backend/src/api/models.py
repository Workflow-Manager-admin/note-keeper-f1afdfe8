from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field
import sqlite3
import threading


# PUBLIC_INTERFACE
class Note(BaseModel):
    """Pydantic model for a note object."""
    id: int = Field(..., description="Unique identifier for the note")
    title: str = Field(..., description="Title of the note")
    content: str = Field(..., description="Content of the note")
    created_at: datetime = Field(..., description="Timestamp when the note was created")
    updated_at: datetime = Field(..., description="Timestamp when the note was last updated")


# PUBLIC_INTERFACE
class NoteCreate(BaseModel):
    """Pydantic model for creating a new note (excludes id and timestamps)."""
    title: str = Field(..., description="Title of the note")
    content: str = Field(..., description="Content of the note")


# Storage abstraction (in-memory with optional SQLite persistence)
class NoteStorage:
    """
    In-memory+SQLite storage management for Note objects.
    If db_path is None, stores notes in memory; if given, persists to SQLite.
    Thread-safe for demo/simple usage.
    """
    def __init__(self, db_path: Optional[str] = None):
        self._lock = threading.RLock()
        self.db_path = db_path
        self._notes = {}
        self._next_id = 1
        if db_path:
            self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """CREATE TABLE IF NOT EXISTS notes (
                    id INTEGER PRIMARY KEY,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )"""
            )

    def _from_row(self, row) -> Note:
        return Note(id=row[0], title=row[1], content=row[2],
                    created_at=datetime.fromisoformat(row[3]),
                    updated_at=datetime.fromisoformat(row[4]))

    # PUBLIC_INTERFACE
    def add_note(self, note_create: NoteCreate) -> Note:
        now = datetime.utcnow()
        with self._lock:
            if self.db_path:
                with sqlite3.connect(self.db_path) as conn:
                    cur = conn.cursor()
                    cur.execute(
                        "INSERT INTO notes (title, content, created_at, updated_at) VALUES (?, ?, ?, ?)",
                        (note_create.title, note_create.content, now.isoformat(), now.isoformat())
                    )
                    note_id = cur.lastrowid
                return Note(
                    id=note_id,
                    title=note_create.title,
                    content=note_create.content,
                    created_at=now,
                    updated_at=now
                )
            else:
                note = Note(
                    id=self._next_id,
                    title=note_create.title,
                    content=note_create.content,
                    created_at=now,
                    updated_at=now
                )
                self._notes[self._next_id] = note
                self._next_id += 1
                return note

    # PUBLIC_INTERFACE
    def get_note(self, note_id: int) -> Optional[Note]:
        with self._lock:
            if self.db_path:
                with sqlite3.connect(self.db_path) as conn:
                    cur = conn.cursor()
                    cur.execute("SELECT id, title, content, created_at, updated_at FROM notes WHERE id = ?", (note_id,))
                    row = cur.fetchone()
                if row:
                    return self._from_row(row)
                return None
            else:
                return self._notes.get(note_id)

    # PUBLIC_INTERFACE
    def list_notes(self) -> List[Note]:
        with self._lock:
            if self.db_path:
                with sqlite3.connect(self.db_path) as conn:
                    cur = conn.cursor()
                    cur.execute("SELECT id, title, content, created_at, updated_at FROM notes ORDER BY id")
                    rows = cur.fetchall()
                return [self._from_row(row) for row in rows]
            else:
                return list(self._notes.values())

    # PUBLIC_INTERFACE
    def update_note(self, note_id: int, note_create: NoteCreate) -> Optional[Note]:
        now = datetime.utcnow()
        with self._lock:
            if self.db_path:
                with sqlite3.connect(self.db_path) as conn:
                    cur = conn.cursor()
                    cur.execute(
                        "UPDATE notes SET title=?, content=?, updated_at=? WHERE id=?",
                        (note_create.title, note_create.content, now.isoformat(), note_id)
                    )
                    if cur.rowcount > 0:
                        cur.execute("SELECT id, title, content, created_at, updated_at FROM notes WHERE id=?", (note_id,))
                        row = cur.fetchone()
                        return self._from_row(row)
                    else:
                        return None
            else:
                note = self._notes.get(note_id)
                if note:
                    updated_note = Note(
                        id=note.id,
                        title=note_create.title,
                        content=note_create.content,
                        created_at=note.created_at,
                        updated_at=now
                    )
                    self._notes[note_id] = updated_note
                    return updated_note
                return None

    # PUBLIC_INTERFACE
    def delete_note(self, note_id: int) -> bool:
        with self._lock:
            if self.db_path:
                with sqlite3.connect(self.db_path) as conn:
                    cur = conn.cursor()
                    cur.execute("DELETE FROM notes WHERE id=?", (note_id,))
                    return cur.rowcount > 0
            else:
                return self._notes.pop(note_id, None) is not None

