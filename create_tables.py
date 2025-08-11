#!/usr/bin/env python3
"""
Script para crear las tablas de la base de datos automáticamente.
Este script importa todos los modelos y usa SQLAlchemy para crear las tablas.
"""

import sys
import os

# Agregar el directorio raíz del proyecto al PYTHONPATH
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import Base, engine
from app.core.config import settings

# Importar todos los modelos para que estén registrados en el metadata
from app.models.user import User
from app.models.composition import Composition
from app.models.key_mapping import KeyMapping
from app.models.song import Song, Recording, MidiFile


def create_tables() -> None:
    """
    Crea todas las tablas definidas en los modelos si no existen.
    """
    try:
        print(f"🚀 Conectando a la base de datos: {settings.POSTGRES_DB}")
        print(f"📍 Servidor: {settings.POSTGRES_SERVER}:{settings.POSTGRES_PORT}")
        print("🔧 Creando tablas...")
        
        # Crear todas las tablas
        Base.metadata.create_all(bind=engine)
        
        print("✅ Tablas creadas exitosamente!")
        
        # Mostrar las tablas que fueron creadas/verificadas
        tables = Base.metadata.tables.keys()
        print(f"📊 Tablas disponibles: {', '.join(tables)}")
        
    except Exception as e:
        print(f"❌ Error al crear las tablas: {e}")
        sys.exit(1)


def drop_tables() -> None:
    """
    Elimina todas las tablas (útil para desarrollo).
    ¡CUIDADO! Esto eliminará todos los datos.
    """
    try:
        print("⚠️  ADVERTENCIA: Esto eliminará TODAS las tablas y datos!")
        confirm = input("¿Estás seguro? Escribe 'YES' para continuar: ")
        
        if confirm == "YES":
            print("🗑️  Eliminando tablas...")
            Base.metadata.drop_all(bind=engine)
            print("✅ Tablas eliminadas exitosamente!")
        else:
            print("❌ Operación cancelada.")
            
    except Exception as e:
        print(f"❌ Error al eliminar las tablas: {e}")
        sys.exit(1)


def main():
    """Función principal del script"""
    if len(sys.argv) > 1:
        if sys.argv[1] == "drop":
            drop_tables()
        elif sys.argv[1] == "create":
            create_tables()
        else:
            print("❌ Comando no reconocido. Usa 'create' o 'drop'")
    else:
        create_tables()


if __name__ == "__main__":
    main()
