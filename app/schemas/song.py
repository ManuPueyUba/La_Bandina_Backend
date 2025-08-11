from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class DifficultyLevel(str, Enum):
    beginner = "beginner"
    intermediate = "intermediate"
    advanced = "advanced"


class NoteSchema(BaseModel):
    key: str = Field(..., description="Note key in format like 'C4', 'F#5', etc.")
    start_time: int = Field(..., description="Start time in milliseconds")
    duration: int = Field(..., description="Duration in milliseconds")


class RecordedNoteSchema(BaseModel):
    note: str = Field(..., description="Note name like 'C', 'F#', etc.")
    octave: int = Field(..., description="Octave number")
    start_time: int = Field(..., description="Start time in milliseconds")
    end_time: Optional[int] = Field(None, description="End time in milliseconds")
    velocity: float = Field(0.7, description="Velocity/volume of the note")


class SongBase(BaseModel):
    title: str
    artist: str
    difficulty: DifficultyLevel
    category: str
    bpm: int
    key_signature: str = "C major"
    time_signature: str = "4/4"
    description: Optional[str] = None


class SongCreate(SongBase):
    notes: List[NoteSchema]


class SongResponse(SongBase):
    id: str
    duration: int
    notes: List[NoteSchema]
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class RecordingBase(BaseModel):
    title: str
    artist: str
    bpm: int = 120
    key_signature: str = "C major"
    description: Optional[str] = None


class RecordingCreate(RecordingBase):
    notes: List[RecordedNoteSchema]


class RecordingResponse(RecordingBase):
    id: str
    duration: int
    notes: List[RecordedNoteSchema]
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class MidiUploadResponse(BaseModel):
    id: str
    filename: str
    file_size: int
    message: str


class MidiConversionOptions(BaseModel):
    min_octave: int = Field(4, ge=1, le=8)
    max_octave: int = Field(6, ge=1, le=8)
    min_note_duration: int = Field(100, ge=50)
    quantize_threshold: int = Field(50, ge=10)
    simplify_melody: bool = True
    remove_chords: bool = True
    max_notes_per_second: int = Field(4, ge=1)


class MidiConversionRequest(BaseModel):
    title: str
    artist: str = "Unknown"
    category: str = "Importada"
    key_signature: str = "C major"
    difficulty: Optional[DifficultyLevel] = None
    description: Optional[str] = None
    # Opciones son completamente opcionales - si no se proveen, se usa conversión simple
    options: Optional[Dict[str, Any]] = None


class MidiConversionResponse(BaseModel):
    song: SongResponse
    processing_info: Dict[str, Any]


class MidiFileResponse(BaseModel):
    id: str
    filename: str
    original_name: str
    file_size: int
    file_path: str  # Agregamos el file_path
    processed: bool
    song_id: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
