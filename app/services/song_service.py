import uuid
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.song import Song, Recording, MidiFile
from app.schemas.song import (
    SongCreate, 
    SongResponse, 
    RecordingCreate, 
    RecordingResponse,
    MidiFileResponse
)


class SongService:
    """Service for managing songs and recordings"""

    def create_song(self, db: Session, song_data: SongCreate) -> SongResponse:
        """Create a new song"""
        song_id = str(uuid.uuid4())
        
        # Calculate duration from notes
        duration = 0
        if song_data.notes:
            last_note = max(song_data.notes, key=lambda n: n.start_time + n.duration)
            duration = last_note.start_time + last_note.duration
        
        # Convert notes to JSON format
        notes_json = [
            {
                "key": note.key,
                "startTime": note.start_time,
                "duration": note.duration
            }
            for note in song_data.notes
        ]
        
        db_song = Song(
            id=song_id,
            title=song_data.title,
            artist=song_data.artist,
            difficulty=song_data.difficulty.value,
            category=song_data.category,
            bpm=song_data.bpm,
            duration=duration,
            notes=notes_json,
            key_signature=song_data.key_signature,
            time_signature=song_data.time_signature,
            description=song_data.description
        )
        
        db.add(db_song)
        db.commit()
        db.refresh(db_song)
        
        return self._song_to_response(db_song)

    def get_song(self, db: Session, song_id: str) -> Optional[SongResponse]:
        """Get song by ID"""
        db_song = db.query(Song).filter(Song.id == song_id).first()
        if db_song:
            return self._song_to_response(db_song)
        return None

    def get_songs(
        self, 
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        category: Optional[str] = None,
        difficulty: Optional[str] = None
    ) -> List[SongResponse]:
        """Get songs with optional filtering"""
        query = db.query(Song)
        
        if category:
            query = query.filter(Song.category == category)
        if difficulty:
            query = query.filter(Song.difficulty == difficulty)
        
        db_songs = query.order_by(desc(Song.created_at)).offset(skip).limit(limit).all()
        return [self._song_to_response(song) for song in db_songs]

    def delete_song(self, db: Session, song_id: str) -> bool:
        """Delete song by ID"""
        db_song = db.query(Song).filter(Song.id == song_id).first()
        if db_song:
            db.delete(db_song)
            db.commit()
            return True
        return False

    def create_recording(self, db: Session, recording_data: RecordingCreate) -> RecordingResponse:
        """Create a new recording"""
        recording_id = str(uuid.uuid4())
        
        # Calculate duration from notes
        duration = 0
        if recording_data.notes:
            max_end_time = 0
            for note in recording_data.notes:
                end_time = note.end_time or (note.start_time + 500)  # Default 500ms if no end time
                max_end_time = max(max_end_time, end_time)
            duration = max_end_time
        
        # Convert notes to JSON format
        notes_json = [
            {
                "note": note.note,
                "octave": note.octave,
                "startTime": note.start_time,
                "endTime": note.end_time,
                "velocity": note.velocity
            }
            for note in recording_data.notes
        ]
        
        db_recording = Recording(
            id=recording_id,
            title=recording_data.title,
            artist=recording_data.artist,
            duration=duration,
            notes=notes_json,
            bpm=recording_data.bpm,
            key_signature=recording_data.key_signature,
            description=recording_data.description
        )
        
        db.add(db_recording)
        db.commit()
        db.refresh(db_recording)
        
        return self._recording_to_response(db_recording)

    def get_recording(self, db: Session, recording_id: str) -> Optional[RecordingResponse]:
        """Get recording by ID"""
        db_recording = db.query(Recording).filter(Recording.id == recording_id).first()
        if db_recording:
            return self._recording_to_response(db_recording)
        return None

    def get_recordings(
        self, 
        db: Session, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[RecordingResponse]:
        """Get recordings"""
        db_recordings = db.query(Recording).order_by(desc(Recording.created_at)).offset(skip).limit(limit).all()
        return [self._recording_to_response(recording) for recording in db_recordings]

    def delete_recording(self, db: Session, recording_id: str) -> bool:
        """Delete recording by ID"""
        db_recording = db.query(Recording).filter(Recording.id == recording_id).first()
        if db_recording:
            db.delete(db_recording)
            db.commit()
            return True
        return False

    def create_midi_file_record(
        self, 
        db: Session, 
        file_id: str, 
        filename: str,
        original_name: str,
        file_size: int,
        file_path: str
    ) -> MidiFileResponse:
        """Create MIDI file record in database"""
        db_midi_file = MidiFile(
            id=file_id,
            filename=filename,
            original_name=original_name,
            file_size=file_size,
            file_path=file_path,
            processed=False
        )
        
        db.add(db_midi_file)
        db.commit()
        db.refresh(db_midi_file)
        
        return self._midi_file_to_response(db_midi_file)

    def update_midi_file_processed(
        self, 
        db: Session, 
        file_id: str, 
        song_id: Optional[str] = None,
        error_message: Optional[str] = None
    ) -> Optional[MidiFileResponse]:
        """Update MIDI file processing status"""
        db_midi_file = db.query(MidiFile).filter(MidiFile.id == file_id).first()
        if db_midi_file:
            db_midi_file.processed = True
            if song_id:
                db_midi_file.song_id = song_id
            if error_message:
                db_midi_file.error_message = error_message
            
            db.commit()
            db.refresh(db_midi_file)
            return self._midi_file_to_response(db_midi_file)
        return None

    def get_midi_file(self, db: Session, file_id: str) -> Optional[MidiFileResponse]:
        """Get MIDI file record by ID"""
        db_midi_file = db.query(MidiFile).filter(MidiFile.id == file_id).first()
        if db_midi_file:
            return self._midi_file_to_response(db_midi_file)
        return None

    def _song_to_response(self, db_song: Song) -> SongResponse:
        """Convert database Song to SongResponse"""
        # Convert notes from JSON to schema objects
        from app.schemas.song import NoteSchema
        notes = [
            NoteSchema(
                key=note["key"],
                start_time=note["startTime"],
                duration=note["duration"]
            )
            for note in db_song.notes
        ]
        
        return SongResponse(
            id=db_song.id,
            title=db_song.title,
            artist=db_song.artist,
            difficulty=db_song.difficulty,
            category=db_song.category,
            bpm=db_song.bpm,
            duration=db_song.duration,
            notes=notes,
            key_signature=db_song.key_signature,
            time_signature=db_song.time_signature,
            description=db_song.description,
            created_at=db_song.created_at,
            updated_at=db_song.updated_at
        )

    def _recording_to_response(self, db_recording: Recording) -> RecordingResponse:
        """Convert database Recording to RecordingResponse"""
        # Convert notes from JSON to schema objects
        from app.schemas.song import RecordedNoteSchema
        notes = [
            RecordedNoteSchema(
                note=note["note"],
                octave=note["octave"],
                start_time=note["startTime"],
                end_time=note.get("endTime"),
                velocity=note.get("velocity", 0.7)
            )
            for note in db_recording.notes
        ]
        
        return RecordingResponse(
            id=db_recording.id,
            title=db_recording.title,
            artist=db_recording.artist,
            duration=db_recording.duration,
            notes=notes,
            bpm=db_recording.bpm,
            key_signature=db_recording.key_signature,
            description=db_recording.description,
            created_at=db_recording.created_at,
            updated_at=db_recording.updated_at
        )

    def _midi_file_to_response(self, db_midi_file: MidiFile) -> MidiFileResponse:
        """Convert database MidiFile to MidiFileResponse"""
        return MidiFileResponse(
            id=db_midi_file.id,
            filename=db_midi_file.filename,
            original_name=db_midi_file.original_name,
            file_size=db_midi_file.file_size,
            processed=db_midi_file.processed,
            song_id=db_midi_file.song_id,
            error_message=db_midi_file.error_message,
            created_at=db_midi_file.created_at
        )
