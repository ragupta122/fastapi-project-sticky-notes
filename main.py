from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

app = FastAPI(title="Sticky Notes")


# ---------- what a note looks like ----------

class NoteIn(BaseModel):
    """What a caller must send us."""
    title: str = Field(min_length=1, max_length=80)
    body: str = ""


class Note(NoteIn):
    """What we send back: the same thing, plus an id."""
    id: int


# ---------- storage ----------

notes: list[Note] = []
next_id = 1


def find_note(note_id: int) -> Note:
    """Return the note, or raise a clean 404."""
    for note in notes:
        if note.id == note_id:
            return note
    raise HTTPException(status_code=404, detail=f"Note {note_id} not found")


# ---------- the four operations ----------

@app.get("/api/notes")
def list_notes() -> list[Note]:
    return notes


@app.get("/api/notes/{note_id}")
def get_note(note_id: int) -> Note:
    return find_note(note_id)


@app.post("/api/notes", status_code=201)
def create_note(payload: NoteIn) -> Note:
    global next_id
    note = Note(id=next_id, **payload.model_dump())
    notes.append(note)
    next_id += 1
    return note


@app.put("/api/notes/{note_id}")
def replace_note(note_id: int, payload: NoteIn) -> Note:
    for index, note in enumerate(notes):
        if note.id == note_id:
            updated = Note(id=note_id, **payload.model_dump())
            notes[index] = updated
            return updated
    raise HTTPException(status_code=404, detail=f"Note {note_id} not found")


@app.delete("/api/notes/{note_id}", status_code=204)
def delete_note(note_id: int) -> None:
    notes.remove(find_note(note_id))


# ---------- serve the web page (MUST be last) ----------

app.mount("/", StaticFiles(directory="static", html=True), name="static")