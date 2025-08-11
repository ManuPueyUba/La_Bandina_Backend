from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import io
import pretty_midi

from app.core.database import get_db
from app.services.song_service import SongService
from app.services.midi_processor import MidiProcessorService
from app.schemas.song import (
    SongResponse, 
    SongCreate,
    RecordingResponse,
    RecordingCreate,
    MidiUploadResponse,
    MidiConversionRequest,
    MidiConversionResponse,
    MidiFileResponse,
    DifficultyLevel
)

router = APIRouter()
song_service = SongService()
midi_processor = MidiProcessorService()


def process_notes_for_chords(notes: List[Dict[str, Any]], tolerance_ms: int = 100) -> List[Dict[str, Any]]:
    """
    Agrupa notas que empiezan al mismo tiempo (o casi) como acordes.
    Similar a la función chord-processor.ts del frontend.
    """
    if len(notes) == 0:
        return notes
    
    # Ordenar notas por tiempo de inicio
    sorted_notes = sorted(notes, key=lambda n: n['start_time'])
    
    processed_notes = []
    i = 0
    
    while i < len(sorted_notes):
        current_note = sorted_notes[i]
        simultaneous_notes = [current_note]
        
        # Buscar notas que empiecen al mismo tiempo (dentro de la tolerancia)
        for j in range(i + 1, len(sorted_notes)):
            next_note = sorted_notes[j]
            time_difference = abs(next_note['start_time'] - current_note['start_time'])
            
            if time_difference <= tolerance_ms:
                simultaneous_notes.append(next_note)
            else:
                break  # Las siguientes notas ya no son simultáneas
        
        if len(simultaneous_notes) > 1:
            # Es un acorde - ajustar todas las notas para que empiecen exactamente al mismo tiempo
            earliest_start_time = min(n['start_time'] for n in simultaneous_notes)
            longest_duration = max(n['duration'] for n in simultaneous_notes)
            
            # Crear notas del acorde con el mismo startTime y duración
            for note in simultaneous_notes:
                processed_notes.append({
                    "key": note['key'],
                    "start_time": earliest_start_time,
                    "duration": longest_duration  # Usar la duración más larga para el acorde
                })
        else:
            # Nota individual
            processed_notes.append(current_note)
        
        i += len(simultaneous_notes)
    
    return sorted(processed_notes, key=lambda n: n['start_time'])


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
        
        # Aplicar procesamiento de acordes para agrupar notas simultáneas
        processed_notes = process_notes_for_chords(converted_notes, tolerance_ms=100)
        
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
            "notes": processed_notes
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


@router.post("/midi/{file_id}/convert", response_model=MidiConversionResponse)
def convert_midi_to_song(
    file_id: str, 
    conversion_request: MidiConversionRequest,
    db: Session = Depends(get_db)
):
    """Convert MIDI file to song using the simplified processor"""
    midi_file_record = song_service.get_midi_file(db, file_id)
    if not midi_file_record:
        raise HTTPException(status_code=404, detail="MIDI file not found")
    
    try:
        # Leer el archivo MIDI como bytes
        with open(midi_file_record.file_path, 'rb') as f:
            midi_bytes = f.read()
        
        # Usar el método estático simplificado
        song_data = MidiProcessorService.convert_midi_to_song(midi_bytes, conversion_request)
        
        # Convertir las notas al formato que espera NoteSchema
        formatted_notes = []
        for note in song_data['notes']:
            # Convertir pitch MIDI a nombre de nota
            note_name = pretty_midi.note_number_to_name(note['note'])
            
            formatted_note = {
                'key': note_name,
                'start_time': note['start'],
                'duration': note['end'] - note['start']
            }
            formatted_notes.append(formatted_note)
        
        # Crear el objeto Song para guardar en la base de datos
        from app.schemas.song import SongCreate
        song_create = SongCreate(
            title=song_data['title'],
            artist=song_data['artist'],
            difficulty=song_data['difficulty'] or DifficultyLevel.beginner,
            category=song_data['category'],
            bpm=120,  # Default BPM
            key_signature=song_data['key_signature'],
            description=song_data['description'],
            notes=formatted_notes
        )
        
        # Guardar en la base de datos
        created_song = song_service.create_song(db, song_create)
        
        # Actualizar registro del archivo MIDI
        song_service.update_midi_file_processed(db, file_id, created_song.id)
        
        # Limpiar archivo temporal
        midi_processor.cleanup_file(midi_file_record.file_path)
        
        return MidiConversionResponse(
            success=True,
            message="MIDI file converted successfully",
            song=SongResponse.from_orm(created_song),
            processing_info={
                "notes_count": len(song_data['notes']),
                "total_duration": song_data['total_duration'],
                "conversion_type": "simplified"
            }
        )
        
    except Exception as e:
        # Actualizar con error
        song_service.update_midi_file_processed(db, file_id, error_message=str(e))
        # Cleanup on error
        midi_processor.cleanup_file(midi_file_record.file_path)
        raise HTTPException(status_code=500, detail=f"Error converting MIDI: {str(e)}")


@router.get("/midi/{file_id}", response_model=MidiFileResponse)
def get_midi_file_info(file_id: str, db: Session = Depends(get_db)):
    """Get MIDI file information"""
    midi_file_record = song_service.get_midi_file(db, file_id)
    if not midi_file_record:
        raise HTTPException(status_code=404, detail="MIDI file not found")
    return midi_file_record
