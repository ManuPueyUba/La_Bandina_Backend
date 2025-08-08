#!/usr/bin/env python3
"""
Script para poblar la base de datos con canciones de ejemplo
"""

import asyncio
import sys
import os

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.services.song_service import SongService
from app.schemas.song import SongCreate, NoteSchema

def create_sample_songs():
    """Crear canciones de ejemplo"""
    songs = [
        {
            "title": "Happy Birthday",
            "artist": "Traditional",
            "difficulty": "beginner",
            "category": "Tradicional",
            "bpm": 120,
            "key_signature": "C major",
            "time_signature": "3/4",
            "description": "La melodía tradicional de cumpleaños. Perfecta para principiantes.",
            "notes": [
                {"key": "C4", "start_time": 0, "duration": 500},
                {"key": "C4", "start_time": 500, "duration": 500},
                {"key": "D4", "start_time": 1000, "duration": 1000},
                {"key": "C4", "start_time": 2000, "duration": 1000},
                {"key": "F4", "start_time": 3000, "duration": 1000},
                {"key": "E4", "start_time": 4000, "duration": 2000},
                
                {"key": "C4", "start_time": 6000, "duration": 500},
                {"key": "C4", "start_time": 6500, "duration": 500},
                {"key": "D4", "start_time": 7000, "duration": 1000},
                {"key": "C4", "start_time": 8000, "duration": 1000},
                {"key": "G4", "start_time": 9000, "duration": 1000},
                {"key": "F4", "start_time": 10000, "duration": 2000},
                
                {"key": "C4", "start_time": 12000, "duration": 500},
                {"key": "C4", "start_time": 12500, "duration": 500},
                {"key": "C5", "start_time": 13000, "duration": 1000},
                {"key": "A4", "start_time": 14000, "duration": 1000},
                {"key": "F4", "start_time": 15000, "duration": 1000},
                {"key": "E4", "start_time": 16000, "duration": 1000},
                {"key": "D4", "start_time": 17000, "duration": 2000},
                
                {"key": "A#4", "start_time": 19000, "duration": 500},
                {"key": "A#4", "start_time": 19500, "duration": 500},
                {"key": "A4", "start_time": 20000, "duration": 1000},
                {"key": "F4", "start_time": 21000, "duration": 1000},
                {"key": "G4", "start_time": 22000, "duration": 1000},
                {"key": "F4", "start_time": 23000, "duration": 2000}
            ]
        },
        {
            "title": "Twinkle Twinkle Little Star",
            "artist": "Traditional",
            "difficulty": "beginner",
            "category": "Infantil",
            "bpm": 120,
            "key_signature": "C major",
            "time_signature": "4/4",
            "description": "Una canción infantil clásica ideal para aprender.",
            "notes": [
                {"key": "C4", "start_time": 0, "duration": 500},
                {"key": "C4", "start_time": 500, "duration": 500},
                {"key": "G4", "start_time": 1000, "duration": 500},
                {"key": "G4", "start_time": 1500, "duration": 500},
                {"key": "A4", "start_time": 2000, "duration": 500},
                {"key": "A4", "start_time": 2500, "duration": 500},
                {"key": "G4", "start_time": 3000, "duration": 1000},
                
                {"key": "F4", "start_time": 4000, "duration": 500},
                {"key": "F4", "start_time": 4500, "duration": 500},
                {"key": "E4", "start_time": 5000, "duration": 500},
                {"key": "E4", "start_time": 5500, "duration": 500},
                {"key": "D4", "start_time": 6000, "duration": 500},
                {"key": "D4", "start_time": 6500, "duration": 500},
                {"key": "C4", "start_time": 7000, "duration": 1000}
            ]
        },
        {
            "title": "Mary Had a Little Lamb",
            "artist": "Traditional",
            "difficulty": "beginner",
            "category": "Infantil",
            "bpm": 100,
            "key_signature": "C major",
            "time_signature": "4/4",
            "description": "Una melodía simple y repetitiva perfecta para principiantes.",
            "notes": [
                {"key": "E4", "start_time": 0, "duration": 600},
                {"key": "D4", "start_time": 600, "duration": 600},
                {"key": "C4", "start_time": 1200, "duration": 600},
                {"key": "D4", "start_time": 1800, "duration": 600},
                {"key": "E4", "start_time": 2400, "duration": 600},
                {"key": "E4", "start_time": 3000, "duration": 600},
                {"key": "E4", "start_time": 3600, "duration": 1200},
                
                {"key": "D4", "start_time": 4800, "duration": 600},
                {"key": "D4", "start_time": 5400, "duration": 600},
                {"key": "D4", "start_time": 6000, "duration": 1200},
                {"key": "E4", "start_time": 7200, "duration": 600},
                {"key": "G4", "start_time": 7800, "duration": 600},
                {"key": "G4", "start_time": 8400, "duration": 1200},
            ]
        },
        {
            "title": "C Major Scale",
            "artist": "Exercise",
            "difficulty": "beginner",
            "category": "Ejercicios",
            "bpm": 80,
            "key_signature": "C major",
            "time_signature": "4/4",
            "description": "Escala básica de Do mayor para practicar.",
            "notes": [
                {"key": "C4", "start_time": 0, "duration": 750},
                {"key": "D4", "start_time": 750, "duration": 750},
                {"key": "E4", "start_time": 1500, "duration": 750},
                {"key": "F4", "start_time": 2250, "duration": 750},
                {"key": "G4", "start_time": 3000, "duration": 750},
                {"key": "A4", "start_time": 3750, "duration": 750},
                {"key": "B4", "start_time": 4500, "duration": 750},
                {"key": "C5", "start_time": 5250, "duration": 1500},
                
                # Descendente
                {"key": "B4", "start_time": 7500, "duration": 750},
                {"key": "A4", "start_time": 8250, "duration": 750},
                {"key": "G4", "start_time": 9000, "duration": 750},
                {"key": "F4", "start_time": 9750, "duration": 750},
                {"key": "E4", "start_time": 10500, "duration": 750},
                {"key": "D4", "start_time": 11250, "duration": 750},
                {"key": "C4", "start_time": 12000, "duration": 1500},
            ]
        }
    ]
    
    return songs

def main():
    """Función principal"""
    db = SessionLocal()
    song_service = SongService()
    
    try:
        print("🎵 Creando canciones de ejemplo...")
        
        sample_songs = create_sample_songs()
        created_count = 0
        
        for song_data in sample_songs:
            try:
                # Convertir a schema de Pydantic
                song_create = SongCreate(**song_data)
                
                # Crear la canción
                created_song = song_service.create_song(db, song_create)
                print(f"✅ Creada: {created_song.title} - {created_song.artist}")
                created_count += 1
                
            except Exception as e:
                print(f"❌ Error creando {song_data['title']}: {e}")
        
        print(f"\n🎉 ¡Proceso completado! Se crearon {created_count} canciones.")
        
    except Exception as e:
        print(f"❌ Error general: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    main()
