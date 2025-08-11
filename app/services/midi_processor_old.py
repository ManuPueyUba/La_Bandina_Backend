import os
import uuid
import mido
import pretty_midi
import numpy as np
from typing import List, Dict, Any, Tuple, Optional
from pathlib import Path
from datetime import datetime, timezone
from types import SimpleNamespace

from app.schemas.song import (
    NoteSchema, 
    SongResponse, 
    MidiConversionOptions,
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

    def analyze_midi_file(self, file_path: str) -> Dict[str, Any]:
        """Analyze MIDI file and return basic information"""
        try:
            midi_file = mido.MidiFile(file_path)
            pm = pretty_midi.PrettyMIDI(file_path)
            
            # Count total notes across all instruments
            total_notes = sum(len(instrument.notes) for instrument in pm.instruments)
            
            # Get tempo (BPM)
            tempo_changes = pm.get_tempo_changes()
            bpm = int(tempo_changes[1][0] * 60) if len(tempo_changes[1]) > 0 else 120
            
            # Get time signature
            time_signatures = pm.time_signature_changes
            time_sig = f"{time_signatures[0].numerator}/{time_signatures[0].denominator}" if time_signatures else "4/4"
            
            # Duration in milliseconds
            duration = int(pm.get_end_time() * 1000)
            
            # Recommended settings based on analysis
            note_density = total_notes / (duration / 1000) if duration > 0 else 0
            
            recommended_settings = {
                "remove_chords": total_notes > 50 and note_density > 2,
                "simplify_melody": total_notes > 100,
                "max_notes_per_second": min(6, max(2, int(note_density * 1.5))),
                "min_note_duration": 150 if note_density > 3 else 100
            }
            
            return {
                "tracks": len(midi_file.tracks),
                "notes": total_notes,
                "duration": duration,
                "bpm": bpm,
                "time_signature": time_sig,
                "note_density": round(note_density, 2),
                "recommended_settings": recommended_settings
            }
            
        except Exception as e:
            raise ValueError(f"Error analyzing MIDI file: {str(e)}")

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
        """Convert MIDI file to Song object - Simple version like your parser"""
        try:
            # Load MIDI data
            midi_data = pretty_midi.PrettyMIDI(file_path)
            
            # Find piano instruments first (program 0), or use instrument with most notes
            piano_instruments = [
                instrument for instrument in midi_data.instruments 
                if not instrument.is_drum and instrument.program == 0
            ]
            
            # If no piano found, use the instrument with most notes (excluding drums)
            if not piano_instruments:
                non_drum_instruments = [inst for inst in midi_data.instruments if not inst.is_drum]
                if not non_drum_instruments:
                    raise ValueError("No suitable instruments found in MIDI file")
                piano_instruments = [max(non_drum_instruments, key=lambda x: len(x.notes))]
            
            # Extract notes from the selected instrument
            raw_notes = []
            for instrument in piano_instruments:
                for note in instrument.notes:
                    # Convert MIDI note number to note name (e.g. 60 -> C4)
                    note_name = pretty_midi.note_number_to_name(note.pitch)
                    
                    raw_notes.append({
                        "key": note_name,
                        "start_time": int(note.start * 1000),  # Convert to milliseconds
                        "duration": int((note.end - note.start) * 1000)  # Convert to milliseconds
                    })
            
            if not raw_notes:
                raise ValueError("No notes found in the selected instrument")
            
            # Sort notes by start time
            raw_notes.sort(key=lambda x: x["start_time"])
            
            # Convert to NoteSchema objects
            notes = [NoteSchema(**note) for note in raw_notes]
            
            # Calculate total duration
            if raw_notes:
                last_note = raw_notes[-1]
                duration = last_note["start_time"] + last_note["duration"]
            else:
                duration = 0
            
            # Get BPM from MIDI
            tempo_changes, tempos = midi_data.get_tempo_changes()
            bpm = int(tempos[0]) if len(tempos) > 0 else 120
            
            # Calculate difficulty based on number of notes
            if not difficulty:
                if len(notes) < 50:
                    difficulty = DifficultyLevel.beginner
                elif len(notes) < 150:
                    difficulty = DifficultyLevel.intermediate
                else:
                    difficulty = DifficultyLevel.advanced
            
            # Create song object
            song = SimpleNamespace(
                id=str(uuid.uuid4()),
                title=title,
                artist=artist,
                difficulty=difficulty.value,
                category=category,
                bpm=bpm,
                duration=duration,
                notes=[{"key": n.key, "start_time": n.start_time, "duration": n.duration} for n in notes],
                key_signature=key_signature,
                time_signature="4/4",  # Default
                description=description or f"MIDI imported with {len(notes)} notes",
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
            
            # Processing info
            processing_info = {
                "notes_count": len(notes),
                "duration": duration,
                "tracks_found": len(midi_data.instruments),
                "selected_track": piano_instruments[0].name or f"Program {piano_instruments[0].program}",
                "strategy": "piano_first" if any(inst.program == 0 for inst in midi_data.instruments if not inst.is_drum) else "most_notes"
            }
            
            return song, processing_info
            
        except Exception as e:
            raise ValueError(f"Error processing MIDI file: {str(e)}")
            if not difficulty:
                difficulty = self._calculate_difficulty(processed_notes, options)
            
            # Get BPM
            tempo_changes = pm.get_tempo_changes()
            bpm = int(tempo_changes[1][0] * 60) if len(tempo_changes[1]) > 0 else 120
            
            # Create song object
            song_data = {
                "id": str(uuid.uuid4()),
                "title": title,
                "artist": artist,
                "difficulty": difficulty,
                "category": category,
                "bpm": bpm,
                "duration": duration,
                "notes": notes,
                "key_signature": key_signature,
                "time_signature": self._get_time_signature(pm),
                "description": description or f"Imported from MIDI with {len(notes)} notes",
                "created_at": None,
                "updated_at": None
            }
            
            song = SongResponse(**song_data)
            
            processing_info = {
                "original_notes": len(best_instrument.notes),
                "filtered_notes": len(raw_notes),
                "final_notes": len(processed_notes),
                "duration_ms": duration,
                "bpm": bpm,
                "processing_applied": {
                    "octave_filtering": True,
                    "chord_removal": options.remove_chords,
                    "melody_simplification": options.simplify_melody,
                    "quantization": True
                }
            }
            
            return song, processing_info
            
        except Exception as e:
            raise ValueError(f"Error converting MIDI to song: {str(e)}")

    def _process_notes(self, notes: List[Dict], options: MidiConversionOptions) -> List[Dict]:
        """Apply processing options to notes"""
        processed = notes.copy()
        
        # 1. Remove chords (keep only highest note when multiple notes play simultaneously)
        if options.remove_chords:
            processed = self._remove_chords(processed)
        
        # 2. Simplify melody (remove rapid repetitions)
        if options.simplify_melody:
            processed = self._simplify_melody(processed, options)
        
        # 3. Apply quantization
        processed = self._quantize_notes(processed, options.quantize_threshold)
        
        # 4. Limit note density
        if options.max_notes_per_second > 0:
            processed = self._limit_note_density(processed, options.max_notes_per_second)
        
        return processed

    def _remove_chords(self, notes: List[Dict]) -> List[Dict]:
        """Remove chords by keeping only the highest note in simultaneous groups"""
        if not notes:
            return notes
        
        # Group notes by start time (±50ms tolerance)
        groups = {}
        tolerance = 50
        
        for note in notes:
            time_key = round(note["start_time"] / tolerance) * tolerance
            if time_key not in groups:
                groups[time_key] = []
            groups[time_key].append(note)
        
        # Keep highest note from each group
        result = []
        for group in groups.values():
            if len(group) == 1:
                result.append(group[0])
            else:
                # Sort by pitch (higher octave and note wins)
                def note_pitch(note):
                    note_name = note["key"]
                    octave = int(note_name[-1])
                    note_letter = note_name[:-1]
                    
                    # Convert note to number for comparison
                    note_map = {"C": 0, "C#": 1, "D": 2, "D#": 3, "E": 4, "F": 5, 
                              "F#": 6, "G": 7, "G#": 8, "A": 9, "A#": 10, "B": 11}
                    note_num = note_map.get(note_letter, 0)
                    return octave * 12 + note_num
                
                highest_note = max(group, key=note_pitch)
                result.append(highest_note)
        
        return sorted(result, key=lambda x: x["start_time"])

    def _simplify_melody(self, notes: List[Dict], options: MidiConversionOptions) -> List[Dict]:
        """Remove rapid repetitions and very short intervals"""
        if not notes:
            return notes
        
        result = []
        min_interval = options.quantize_threshold * 2
        
        for note in notes:
            if not result:
                result.append(note)
                continue
            
            last_note = result[-1]
            
            # If same note and too close in time, extend duration instead of adding new note
            if (last_note["key"] == note["key"] and 
                note["start_time"] - last_note["start_time"] < min_interval):
                # Extend the last note's duration
                last_note["duration"] = max(
                    last_note["duration"],
                    note["start_time"] + note["duration"] - last_note["start_time"]
                )
            else:
                result.append(note)
        
        return result

    def _quantize_notes(self, notes: List[Dict], threshold: int) -> List[Dict]:
        """Quantize notes to avoid overlaps and normalize timing"""
        if not notes:
            return notes
        
        quantized = []
        
        for note in notes:
            new_note = note.copy()
            
            # Adjust start time if overlapping with previous note
            if quantized:
                prev_note = quantized[-1]
                prev_end = prev_note["start_time"] + prev_note["duration"]
                
                if new_note["start_time"] < prev_end:
                    if prev_end - new_note["start_time"] < threshold:
                        new_note["start_time"] = prev_end
            
            # Ensure minimum duration
            if new_note["duration"] < threshold:
                new_note["duration"] = threshold
            
            quantized.append(new_note)
        
        return quantized

    def _limit_note_density(self, notes: List[Dict], max_notes_per_second: int) -> List[Dict]:
        """Limit the density of notes to avoid overwhelming sequences"""
        if not notes or max_notes_per_second <= 0:
            return notes
        
        min_time_between_notes = 1000 // max_notes_per_second
        filtered = []
        
        for note in notes:
            if not filtered:
                filtered.append(note)
                continue
            
            last_note = filtered[-1]
            if note["start_time"] - last_note["start_time"] >= min_time_between_notes:
                filtered.append(note)
        
        return filtered

    def _calculate_difficulty(self, notes: List[Dict], options: MidiConversionOptions) -> DifficultyLevel:
        """Calculate difficulty based on note characteristics"""
        if not notes:
            return DifficultyLevel.beginner
        
        note_count = len(notes)
        duration_seconds = (notes[-1]["start_time"] + notes[-1]["duration"]) / 1000
        note_density = note_count / duration_seconds if duration_seconds > 0 else 0
        
        unique_keys = len(set(note["key"] for note in notes))
        has_sharps = any("#" in note["key"] for note in notes)
        avg_duration = sum(note["duration"] for note in notes) / note_count
        
        score = 0
        
        # Note count factor
        if note_count > 50: score += 2
        elif note_count > 25: score += 1
        
        # Density factor
        if note_density > 2: score += 2
        elif note_density > 1: score += 1
        
        # Variety factor
        if unique_keys > 8: score += 2
        elif unique_keys > 5: score += 1
        
        # Complexity factors
        if has_sharps: score += 1
        if avg_duration < 300: score += 1
        
        if score >= 5:
            return DifficultyLevel.advanced
        elif score >= 2:
            return DifficultyLevel.intermediate
        else:
            return DifficultyLevel.beginner

    def _get_time_signature(self, pm: pretty_midi.PrettyMIDI) -> str:
        """Get time signature from MIDI file"""
        if pm.time_signature_changes:
            ts = pm.time_signature_changes[0]
            return f"{ts.numerator}/{ts.denominator}"
        return "4/4"

    def convert_recording_to_midi_bytes(self, notes: List[RecordedNoteSchema], bpm: int = 120) -> bytes:
        """Convert recording notes to MIDI file bytes"""
        try:
            pm = pretty_midi.PrettyMIDI(initial_tempo=bpm)
            instrument = pretty_midi.Instrument(program=0)  # Acoustic Grand Piano
            
            for recorded_note in notes:
                # Convert note name and octave to MIDI note number
                note_name = f"{recorded_note.note}{recorded_note.octave}"
                midi_number = pretty_midi.note_name_to_number(note_name)
                
                # Convert times from milliseconds to seconds
                start_time = recorded_note.start_time / 1000.0
                end_time = (recorded_note.end_time or (recorded_note.start_time + 500)) / 1000.0
                
                # Create MIDI note
                midi_note = pretty_midi.Note(
                    velocity=int(recorded_note.velocity * 127),
                    pitch=midi_number,
                    start=start_time,
                    end=end_time
                )
                instrument.notes.append(midi_note)
            
            pm.instruments.append(instrument)
            
            # Convert to bytes
            import io
            midi_io = io.BytesIO()
            pm.write(midi_io)
            return midi_io.getvalue()
            
        except Exception as e:
            raise ValueError(f"Error converting recording to MIDI: {str(e)}")

    def cleanup_file(self, file_path: str) -> bool:
        """Delete uploaded file"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except:
            return False
