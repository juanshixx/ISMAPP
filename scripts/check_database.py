"""
Script para verificar la base de datos.
"""
import os
import sys
import sqlite3

# Añadir directorio raíz al path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

def check_database():
    """Verifica el estado de la base de datos."""
    db_path = os.path.join(parent_dir, "data", "ismv3.db")
    
    # Verificar si el archivo existe
    if not os.path.exists(db_path):
        print(f"ERROR: La base de datos no existe en {db_path}")
        return False
        
    print(f"Base de datos encontrada en: {db_path}")
    print(f"Tamaño: {os.path.getsize(db_path) / 1024:.2f} KB")
    
    # Conectarse a la base de datos
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar tablas existentes
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        print("\nTablas en la base de datos:")
        if not tables:
            print("  ¡No hay tablas definidas!")
            return False
            
        for table in tables:
            table_name = table[0]
            print(f"- {table_name}")
            
            # Obtener estructura de la tabla
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            print(f"  Columnas: {len(columns)}")
            
            # Contar registros en la tabla
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"  Registros: {count}")
            
        conn.close()
        print("\n✅ Base de datos verificada correctamente.")
        return True
        
    except sqlite3.Error as e:
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    check_database()