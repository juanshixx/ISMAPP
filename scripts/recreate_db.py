"""
Script para recrear la base de datos desde cero.
"""
import os
import sqlite3
import shutil

# Definir ruta de la base de datos
data_dir = "data"
db_path = os.path.join(data_dir, "ismv3.db")

# Eliminar base de datos si existe
if os.path.exists(db_path):
    print(f"Eliminando base de datos existente: {db_path}")
    try:
        os.remove(db_path)
    except PermissionError:
        print("No se pudo eliminar la base de datos. Asegúrate de que no esté en uso.")
        exit(1)

# Crear directorio de datos si no existe
os.makedirs(data_dir, exist_ok=True)

# Crear nueva base de datos
print(f"Creando nueva base de datos en: {db_path}")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Habilitar claves foráneas
cursor.execute("PRAGMA foreign_keys = ON")

print("Creando tablas...")

# Tabla de usuarios (para autenticación)
cursor.execute('''
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    name TEXT,
    role TEXT DEFAULT 'user',
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

# Crear índices para usuarios
cursor.execute("CREATE INDEX idx_users_username ON users (username)")
cursor.execute("CREATE INDEX idx_users_role ON users (role)")

# Tabla de clientes
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
    client_type TEXT DEFAULT 'both',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

# Crear índices para clientes
cursor.execute("CREATE INDEX idx_clients_name ON clients (name)")
cursor.execute("CREATE INDEX idx_clients_rut ON clients (rut)")
cursor.execute("CREATE INDEX idx_clients_type ON clients (client_type)")

# Tabla de materiales
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

# Crear índices para materiales
cursor.execute("CREATE INDEX idx_materials_name ON materials (name)")
cursor.execute("CREATE INDEX idx_materials_type ON materials (material_type)")

# Tabla de relación cliente-material (con precios)
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

# Crear índices para relación
cursor.execute("CREATE INDEX idx_cm_client ON client_materials (client_id)")
cursor.execute("CREATE INDEX idx_cm_material ON client_materials (material_id)")

print("Insertando datos iniciales...")

# Insertar usuario admin por defecto
cursor.execute('''
INSERT INTO users (username, password, name, role)
VALUES (?, ?, ?, ?)
''', ('admin', 'admin123', 'Administrador', 'admin'))

# Insertar datos de ejemplo para materiales
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

# Insertar datos de ejemplo para clientes
sample_clients = [
    ("Comercial Recicla S.A.", "Comercial Recicla S.A.", "76.111.222-3", "Av. Las Industrias 1234, Santiago", 
    "+56 2 2222 3333", "contacto@recicla.cl", "María González", "Cliente mayorista", 1, "buyer"),
    ("EcoRenova Ltda.", "Sociedad EcoRenova Limitada", "77.444.555-6", "Calle Los Recicladores 567, Concepción", 
    "+56 41 222 3456", "info@ecorenova.cl", "Pedro Soto", "Especialista en plásticos", 1, "supplier"),
    ("Recuperaciones del Sur", "Recuperaciones del Sur SpA", "76.888.999-0", "Ruta 5 Sur Km 15, Temuco", 
    "+56 45 268 7890", "contacto@recuperasur.cl", "Jorge Mendoza", "", 1, "both")
]

cursor.executemany('''
    INSERT INTO clients (name, business_name, rut, address, phone, email, 
                       contact_person, notes, is_active, client_type)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
''', sample_clients)

# Confirmar cambios
conn.commit()

# Verificar la creación de tablas
print("\nVerificando tablas creadas:")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
for table in tables:
    print(f"- {table[0]}")
    cursor.execute(f"PRAGMA table_info({table[0]})")
    columns = cursor.fetchall()
    print(f"  Columnas: {len(columns)}")
    print(f"  Nombres: {', '.join(col[1] for col in columns)}")

conn.close()

print("\n¡Base de datos recreada exitosamente!")
print(f"Tamaño del archivo: {os.path.getsize(db_path) / 1024:.2f} KB")