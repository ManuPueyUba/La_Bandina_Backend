import os
import uuid
import tempfile
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional

import mido
import pretty_midi

from ..schemas.song import (
    MidiConversionRequest, 
    DifficultyLevel,
    RecordedNoteSchema
)


class MidiProcessorService:
    """Service for processing MIDI files and converting them to songs"""

    def __init__(self, upload_dir: str = "uploads/midi"):
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    async def save_midi_file(self, file_content: bytes, filename: str) -> Tuple[str, str]:
        """Save uploaded MIDI file and return file_id and file_path"""
        file_id = str(uuid.uuid4())
        file_extension = Path(filename).suffix
        file_path = self.upload_dir / f"{file_id}{file_extension}"
        
        with open(file_path, "wb") as f:
            f.write(file_content)
            
        return file_id, str(file_path)

    def validate_midi_file(self, file_path: str) -> bool:
        """Validate if file is a valid MIDI file"""
        try:
            mido.MidiFile(file_path)
            return True
        except:
            return False

    @staticmethod
    def convert_midi_to_song(midi_data: bytes, request: MidiConversionRequest) -> Dict[str, Any]:
        """
        Convierte datos MIDI a formato Song, similar a parser.py
        Solo extrae notas de instrumentos de piano de manera simple
        """
        try:
            # Guardar archivo temporal y cargarlo con PrettyMIDI
            with tempfile.NamedTemporaryFile(suffix='.mid', delete=False) as temp_file:
                temp_file.write(midi_data)
                temp_file_path = temp_file.name

            midi_data_pm = pretty_midi.PrettyMIDI(temp_file_path)
            os.unlink(temp_file_path)

            # Encontrar instrumentos de piano (program 0) o el que tenga más notas
            piano_instruments = []
            all_instruments = []
            
            for instrument in midi_data_pm.instruments:
                if not instrument.is_drum:
                    all_instruments.append(instrument)
                    if instrument.program == 0:  # Piano
                        piano_instruments.append(instrument)
            
            # Usar pianos si existen, sino el instrumento con más notas
            if piano_instruments:
                selected_instruments = piano_instruments
            else:
                selected_instruments = sorted(all_instruments, key=lambda x: len(x.notes), reverse=True)[:1]
            
            # Extraer notas de los instrumentos seleccionados
            notes = []
            for instrument in selected_instruments:
                for note in instrument.notes:
                    note_dict = {
                        'note': note.pitch,
                        'start': int(note.start * 1000),  # Convertir a milisegundos
                        'end': int(note.end * 1000),
                        'velocity': note.velocity
                    }
                    notes.append(note_dict)
            
            # Ordenar notas por tiempo de inicio
            notes.sort(key=lambda x: x['start'])
            
            # Si no hay notas, levantar error
            if not notes:
                raise ValueError("No se encontraron notas en el archivo MIDI")
            
            # Calcular duración total
            total_duration = max(note['end'] for note in notes) if notes else 0
            
            return {
                'title': request.title,
                'artist': request.artist,
                'category': request.category,
                'key_signature': request.key_signature,
                'difficulty': request.difficulty,
                'description': request.description,
                'total_duration': total_duration,
                'notes': notes
            }
            
        except Exception as e:
            raise Exception(f"Error procesando archivo MIDI: {str(e)}")

    def cleanup_file(self, file_path: str) -> bool:
        """Delete uploaded file"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except:
            return False
