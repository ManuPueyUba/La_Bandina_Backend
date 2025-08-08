from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import io

from app.core.database import get_db
from app.services.song_service import SongService
from app.services.midi_processor import MidiProcessorService
from app.schemas.song import (
    SongResponse, 
    SongCreate,
    RecordingResponse,
    RecordingCreate,
    MidiUploadResponse,
    MidiAnalysisResponse,
    MidiConversionRequest,
    MidiConversionResponse,
    MidiFileResponse
)

router = APIRouter()
song_service = SongService()
midi_processor = MidiProcessorService()


# Song endpoints
@router.post("/songs", response_model=SongResponse)
def create_song(song: SongCreate, db: Session = Depends(get_db)):
    """Create a new song"""
    return song_service.create_song(db, song)


@router.get("/songs", response_model=List[SongResponse])
def get_songs(
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
    difficulty: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get songs with optional filtering"""
    return song_service.get_songs(db, skip=skip, limit=limit, category=category, difficulty=difficulty)


@router.get("/songs/{song_id}", response_model=SongResponse)
def get_song(song_id: str, db: Session = Depends(get_db)):
    """Get song by ID"""
    song = song_service.get_song(db, song_id)
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    return song


@router.delete("/songs/{song_id}")
def delete_song(song_id: str, db: Session = Depends(get_db)):
    """Delete song by ID"""
    if not song_service.delete_song(db, song_id):
        raise HTTPException(status_code=404, detail="Song not found")
    return {"message": "Song deleted successfully"}


# Recording endpoints
@router.post("/recordings", response_model=RecordingResponse)
def create_recording(recording: RecordingCreate, db: Session = Depends(get_db)):
    """Create a new recording"""
    return song_service.create_recording(db, recording)


@router.get("/recordings", response_model=List[RecordingResponse])
def get_recordings(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get recordings"""
    return song_service.get_recordings(db, skip=skip, limit=limit)


@router.get("/recordings/{recording_id}", response_model=RecordingResponse)
def get_recording(recording_id: str, db: Session = Depends(get_db)):
    """Get recording by ID"""
    recording = song_service.get_recording(db, recording_id)
    if not recording:
        raise HTTPException(status_code=404, detail="Recording not found")
    return recording


@router.delete("/recordings/{recording_id}")
def delete_recording(recording_id: str, db: Session = Depends(get_db)):
    """Delete recording by ID"""
    if not song_service.delete_recording(db, recording_id):
        raise HTTPException(status_code=404, detail="Recording not found")
    return {"message": "Recording deleted successfully"}


@router.post("/recordings/{recording_id}/export-midi")
def export_recording_to_midi(recording_id: str, db: Session = Depends(get_db)):
    """Export recording as MIDI file"""
    recording = song_service.get_recording(db, recording_id)
    if not recording:
        raise HTTPException(status_code=404, detail="Recording not found")
    
    try:
        midi_bytes = midi_processor.convert_recording_to_midi_bytes(recording.notes, recording.bpm)
        
        # Create file-like object
        midi_io = io.BytesIO(midi_bytes)
        
        # Generate filename
        safe_title = "".join(c for c in recording.title if c.isalnum() or c in (' ', '-', '_')).strip()
        filename = f"{safe_title}.mid"
        
        return StreamingResponse(
            io.BytesIO(midi_bytes),
            media_type="audio/midi",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exporting MIDI: {str(e)}")


@router.post("/recordings/{recording_id}/convert-to-song", response_model=SongResponse)
def convert_recording_to_song(
    recording_id: str, 
    title: Optional[str] = None,
    difficulty: Optional[str] = "beginner",
    category: Optional[str] = "Grabaciones",
    db: Session = Depends(get_db)
):
    """Convert recording to song for tutorial use"""
    recording = song_service.get_recording(db, recording_id)
    if not recording:
        raise HTTPException(status_code=404, detail="Recording not found")
    
    try:
        # Convertir RecordedNoteSchema a NoteSchema
        converted_notes = []
        for recorded_note in recording.notes:
            # Combinar note + octave en key (ej: "C" + 4 = "C4")
            key = f"{recorded_note.note}{recorded_note.octave}"
            
            # Calcular duration desde start_time y end_time
            start_time = recorded_note.start_time
            end_time = recorded_note.end_time if recorded_note.end_time else start_time + 500  # 500ms por defecto
            duration = end_time - start_time
            
            converted_notes.append({
                "key": key,
                "start_time": start_time,
                "duration": duration
            })
        
        # Crear SongCreate con los datos convertidos
        song_data = {
            "title": title or f"{recording.title} (Tutorial)",
            "artist": recording.artist,
            "difficulty": difficulty,
            "category": category,
            "bpm": recording.bpm,
            "key_signature": recording.key_signature,
            "time_signature": "4/4",  # Por defecto
            "description": f"Convertido de grabación: {recording.description or recording.title}",
            "notes": converted_notes
        }
        
        from app.schemas.song import SongCreate
        song_create = SongCreate(**song_data)
        
        # Crear la canción
        created_song = song_service.create_song(db, song_create)
        return created_song
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error converting recording to song: {str(e)}")


# MIDI processing endpoints
@router.post("/midi/upload", response_model=MidiUploadResponse)
async def upload_midi_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload a MIDI file for processing"""
    if not file.filename.lower().endswith(('.mid', '.midi')):
        raise HTTPException(status_code=400, detail="File must be a MIDI file (.mid or .midi)")
    
    try:
        # Read file content
        content = await file.read()
        
        # Save file and create database record
        file_id, file_path = await midi_processor.save_midi_file(content, file.filename)
        
        # Validate MIDI file
        if not midi_processor.validate_midi_file(file_path):
            midi_processor.cleanup_file(file_path)
            raise HTTPException(status_code=400, detail="Invalid MIDI file")
        
        # Create database record
        midi_file_record = song_service.create_midi_file_record(
            db, 
            file_id, 
            f"{file_id}.mid",
            file.filename,
            len(content),
            file_path
        )
        
        return MidiUploadResponse(
            id=file_id,
            filename=file.filename,
            file_size=len(content),
            message="MIDI file uploaded successfully"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")


@router.get("/midi/{file_id}/analyze", response_model=MidiAnalysisResponse)
def analyze_midi_file(file_id: str, db: Session = Depends(get_db)):
    """Analyze uploaded MIDI file"""
    midi_file_record = song_service.get_midi_file(db, file_id)
    if not midi_file_record:
        raise HTTPException(status_code=404, detail="MIDI file not found")
    
    try:
        analysis = midi_processor.analyze_midi_file(midi_file_record.file_path)
        
        return MidiAnalysisResponse(
            id=file_id,
            tracks=analysis["tracks"],
            notes=analysis["notes"],
            duration=analysis["duration"],
            bpm=analysis["bpm"],
            time_signature=analysis["time_signature"],
            recommended_settings=analysis["recommended_settings"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing MIDI file: {str(e)}")


@router.post("/midi/{file_id}/convert", response_model=MidiConversionResponse)
def convert_midi_to_song(
    file_id: str, 
    conversion_request: MidiConversionRequest,
    db: Session = Depends(get_db)
):
    """Convert MIDI file to song"""
    midi_file_record = song_service.get_midi_file(db, file_id)
    if not midi_file_record:
        raise HTTPException(status_code=404, detail="MIDI file not found")
    
    try:
        # Convert MIDI to song
        song, processing_info = midi_processor.convert_midi_to_song(
            midi_file_record.file_path,
            conversion_request.title,
            conversion_request.artist,
            conversion_request.category,
            conversion_request.key_signature,
            conversion_request.difficulty,
            conversion_request.description,
            conversion_request.options
        )
        
        # Save song to database
        from app.schemas.song import SongCreate, NoteSchema
        song_create = SongCreate(
            title=song.title,
            artist=song.artist,
            difficulty=song.difficulty,
            category=song.category,
            bpm=song.bpm,
            key_signature=song.key_signature,
            time_signature=song.time_signature,
            description=song.description,
            notes=song.notes
        )
        
        saved_song = song_service.create_song(db, song_create)
        
        # Update MIDI file record
        song_service.update_midi_file_processed(db, file_id, saved_song.id)
        
        # Clean up uploaded file
        midi_processor.cleanup_file(midi_file_record.file_path)
        
        return MidiConversionResponse(
            song=saved_song,
            processing_info=processing_info
        )
        
    except Exception as e:
        # Update MIDI file record with error
        song_service.update_midi_file_processed(db, file_id, error_message=str(e))
        raise HTTPException(status_code=500, detail=f"Error converting MIDI file: {str(e)}")


@router.get("/midi/{file_id}", response_model=MidiFileResponse)
def get_midi_file_info(file_id: str, db: Session = Depends(get_db)):
    """Get MIDI file information"""
    midi_file_record = song_service.get_midi_file(db, file_id)
    if not midi_file_record:
        raise HTTPException(status_code=404, detail="MIDI file not found")
    return midi_file_record
