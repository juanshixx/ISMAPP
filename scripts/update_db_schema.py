"""
Script para actualizar el esquema de la base de datos y añadir la tabla de clientes.
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
    Actualiza el esquema de la base de datos para añadir la tabla de clientes.
    
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
        
        # Verificar si ya existe la tabla clients
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='clients'")
        if cursor.fetchone() is None:
            # Crear tabla clients
            cursor.execute('''
                CREATE TABLE clients (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    business_name TEXT NOT NULL,
                    rut TEXT NOT NULL,
                    address TEXT,
                    phone TEXT,
                    email TEXT,
                    contact_person TEXT,
                    notes TEXT,
                    is_active INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Crear índices para búsqueda rápida
            cursor.execute("CREATE INDEX idx_clients_name ON clients (name)")
            cursor.execute("CREATE INDEX idx_clients_business ON clients (business_name)")
            cursor.execute("CREATE INDEX idx_clients_rut ON clients (rut)")
            cursor.execute("CREATE INDEX idx_clients_active ON clients (is_active)")
            
            # Insertar datos de ejemplo
            sample_clients = [
                ("Comercial Recicla S.A.", "Comercial Recicla S.A.", "76.111.222-3", "Av. Las Industrias 1234, Santiago", 
                 "+56 2 2222 3333", "contacto@recicla.cl", "María González", "Cliente mayorista", 1),
                ("EcoRenova Ltda.", "Sociedad EcoRenova Limitada", "77.444.555-6", "Calle Los Recicladores 567, Concepción", 
                 "+56 41 222 3456", "info@ecorenova.cl", "Pedro Soto", "Especialista en plásticos", 1),
                ("Recuperaciones del Sur", "Recuperaciones del Sur SpA", "76.888.999-0", "Ruta 5 Sur Km 15, Temuco", 
                 "+56 45 268 7890", "contacto@recuperasur.cl", "Jorge Mendoza", "", 1),
                ("Metales Santiago", "Inversiones Metálicas S.A.", "96.333.444-5", "Camino a Melipilla 9876, Santiago", 
                 "+56 2 2777 8888", "ventas@metalesscl.cl", "Carolina Rojas", "Comprador de cobre y aluminio", 1),
                ("EcoPapel Chile", "Papelera Recicladora Chilena Ltda.", "77.123.456-7", "Los Alerces 456, Valparaíso", 
                 "+56 32 211 4567", "contacto@ecopapel.cl", "Roberto Fuentes", "", 1)
            ]
            
            cursor.executemany('''
                INSERT INTO clients (name, business_name, rut, address, phone, email, contact_person, notes, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', sample_clients)
            
            conn.commit()
            print("Tabla 'clients' creada correctamente con datos de ejemplo")
        else:
            print("La tabla 'clients' ya existe en la base de datos")
        
        conn.close()
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