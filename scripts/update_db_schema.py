"""
Script para actualizar el esquema de la base de datos.
"""
import sqlite3
import os
import sys

# Añadir directorio raíz al path de Python
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

def update_db_schema(db_path):
    """
    Actualiza el esquema de la base de datos.
    
    Args:
        db_path (str): Ruta al archivo de base de datos
    """
    # Verificar si existe la base de datos
    if not os.path.exists(db_path):
        print(f"Error: No se encontró la base de datos en {db_path}")
        return False
    
    # Conexión a la base de datos
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 1. Actualizar la tabla de clientes si ya existe
        cursor.execute("PRAGMA table_info(clients)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Añadir columna client_type si no existe
        if 'client_type' not in columns:
            cursor.execute("ALTER TABLE clients ADD COLUMN client_type TEXT DEFAULT 'both'")
        
        # 2. Crear tabla de materiales si no existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='materials'")
        if cursor.fetchone() is None:
            cursor.execute('''
                CREATE TABLE materials (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT,
                    material_type TEXT NOT NULL,
                    is_plastic_subtype INTEGER DEFAULT 0,
                    plastic_subtype TEXT,
                    plastic_state TEXT,
                    custom_subtype TEXT,
                    is_active INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Crear índices para la tabla de materiales
            cursor.execute("CREATE INDEX idx_materials_name ON materials (name)")
            cursor.execute("CREATE INDEX idx_materials_type ON materials (material_type)")
            cursor.execute("CREATE INDEX idx_materials_active ON materials (is_active)")
            
            # Insertar materiales de ejemplo
            sample_materials = [
                ("PET", "Polietileno tereftalato", "plastic", 1, "candy", "clean", "", 1),
                ("HDPE", "Polietileno de alta densidad", "plastic", 1, "gum", "clean", "", 1),
                ("PP", "Polipropileno", "plastic", 1, "other", "clean", "Flexible", 1),
                ("PVC", "Policloruro de vinilo", "plastic", 1, "other", "dirty", "Rígido", 1),
                ("Cobre", "Cobre para reciclaje", "metal", 0, "", "", "", 1),
                ("Aluminio", "Latas y perfiles", "metal", 0, "", "", "", 1),
                ("Chatarra Ferrosa", "Hierro y acero", "metal", 0, "", "", "", 1),
                ("Cartón", "Cajas y embalajes", "paper", 0, "", "", "", 1),
                ("Papel Blanco", "Papel de oficina", "paper", 0, "", "", "", 1),
                ("Vidrio Transparente", "Botellas y frascos", "glass", 0, "", "", "", 1)
            ]
            
            cursor.executemany('''
                INSERT INTO materials (name, description, material_type, is_plastic_subtype,
                                    plastic_subtype, plastic_state, custom_subtype, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', sample_materials)
        
        # 3. Crear tabla de relación cliente-material si no existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='client_materials'")
        if cursor.fetchone() is None:
            cursor.execute('''
                CREATE TABLE client_materials (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    client_id INTEGER NOT NULL,
                    material_id INTEGER NOT NULL,
                    price REAL DEFAULT 0.0,
                    includes_tax INTEGER DEFAULT 0,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (client_id) REFERENCES clients(id),
                    FOREIGN KEY (material_id) REFERENCES materials(id),
                    UNIQUE(client_id, material_id)
                )
            ''')
            
            # Crear índices para la tabla de relación
            cursor.execute("CREATE INDEX idx_cm_client ON client_materials (client_id)")
            cursor.execute("CREATE INDEX idx_cm_material ON client_materials (material_id)")
        
        conn.commit()
        conn.close()
        print("Esquema de base de datos actualizado correctamente")
        return True
        
    except sqlite3.Error as e:
        print(f"Error de SQLite: {e}")
        return False
    except Exception as e:
        print(f"Error inesperado: {e}")
        return False

if __name__ == "__main__":
    # Ruta a la base de datos
    db_path = os.path.join(parent_dir, "data", "ismv3.db")
    
    print(f"Actualizando base de datos en: {db_path}")
    if update_db_schema(db_path):
        print("Actualización completada con éxito")
    else:
        print("Error al actualizar la base de datos")