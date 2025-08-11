#!/usr/bin/env python3
"""
Script de inicialización completa de la base de datos.
Crea tablas, índices y datos iniciales si es necesario.
"""

import sys
import os
from typing import Optional

# Agregar el directorio raíz del proyecto al PYTHONPATH
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import inspect, text
from sqlalchemy.orm import Session
from app.core.database import Base, engine, SessionLocal
from app.core.config import settings

# Importar todos los modelos
from app.models.user import User
from app.models.composition import Composition
from app.models.key_mapping import KeyMapping
from app.models.song import Song, Recording, MidiFile


def check_database_connection() -> bool:
    """Verifica si la conexión a la base de datos funciona."""
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        print("✅ Conexión a la base de datos exitosa")
        return True
    except Exception as e:
        print(f"❌ Error de conexión a la base de datos: {e}")
        return False


def check_existing_tables() -> list:
    """Verifica qué tablas ya existen en la base de datos."""
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    return existing_tables


def create_tables_with_verification() -> None:
    """Crea las tablas con verificación detallada."""
    try:
        print(f"🚀 Inicializando base de datos para La Bandina")
        print(f"📍 Base de datos: {settings.POSTGRES_DB}")
        print(f"🏠 Servidor: {settings.POSTGRES_SERVER}:{settings.POSTGRES_PORT}")
        print("=" * 50)
        
        # Verificar conexión
        if not check_database_connection():
            return False
            
        # Verificar tablas existentes
        existing_tables = check_existing_tables()
        if existing_tables:
            print(f"📊 Tablas existentes: {', '.join(existing_tables)}")
        else:
            print("📊 No hay tablas existentes")
            
        print("🔧 Creando/verificando tablas...")
        
        # Crear todas las tablas
        Base.metadata.create_all(bind=engine)
        
        # Verificar tablas después de la creación
        new_tables = check_existing_tables()
        created_tables = set(new_tables) - set(existing_tables)
        
        if created_tables:
            print(f"✅ Tablas creadas: {', '.join(created_tables)}")
        
        print(f"📊 Total de tablas: {len(new_tables)}")
        print("✅ Inicialización de base de datos completada!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error durante la inicialización: {e}")
        return False


def create_initial_data() -> None:
    """Crea datos iniciales si es necesario."""
    db = SessionLocal()
    try:
        # Verificar si ya hay usuarios
        user_count = db.query(User).count()
        if user_count == 0:
            print("👤 Creando usuario administrador por defecto...")
            # Aquí podrías crear un usuario admin por defecto si lo necesitas
            # admin_user = User(...)
            # db.add(admin_user)
            # db.commit()
            print("ℹ️  Para crear usuarios, usa la API de registro")
        else:
            print(f"👥 Ya existen {user_count} usuarios en la base de datos")
            
    except Exception as e:
        print(f"❌ Error al crear datos iniciales: {e}")
    finally:
        db.close()


def show_database_info() -> None:
    """Muestra información útil sobre la base de datos."""
    db = SessionLocal()
    try:
        print("\n" + "=" * 50)
        print("📈 INFORMACIÓN DE LA BASE DE DATOS")
        print("=" * 50)
        
        # Contar registros en cada tabla
        tables_info = [
            ("👥 Usuarios", User, db.query(User).count()),
            ("🎵 Canciones", Song, db.query(Song).count()),
            ("🎤 Grabaciones", Recording, db.query(Recording).count()),
            ("🎼 Composiciones", Composition, db.query(Composition).count()),
            ("⌨️  Mapeos de teclas", KeyMapping, db.query(KeyMapping).count()),
            ("🎹 Archivos MIDI", MidiFile, db.query(MidiFile).count()),
        ]
        
        for name, model, count in tables_info:
            print(f"{name}: {count}")
            
        print("=" * 50)
        
    except Exception as e:
        print(f"❌ Error al obtener información: {e}")
    finally:
        db.close()


def main():
    """Función principal del script"""
    success = create_tables_with_verification()
    
    if success:
        create_initial_data()
        show_database_info()
        
        print("\n🎉 ¡Base de datos lista para usar!")
        print("🚀 Puedes iniciar el servidor con: uvicorn main:app --reload")
    else:
        print("❌ Falló la inicialización de la base de datos")
        sys.exit(1)


if __name__ == "__main__":
    main()
