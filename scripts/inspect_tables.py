"""
Script para inspeccionar las tablas de la base de datos.
"""
import os
import sqlite3

# Definir ruta de la base de datos
db_path = os.path.join("data", "ismv3.db")

if not os.path.exists(db_path):
    print(f"ERROR: La base de datos no existe en {db_path}")
    exit(1)

print(f"Inspeccionando base de datos: {db_path}")
print(f"Tamaño: {os.path.getsize(db_path) / 1024:.2f} KB")

# Conectar a la base de datos
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Obtener lista de tablas
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()

if not tables:
    print("ERROR: No hay tablas en la base de datos.")
    exit(1)

print(f"\nTablas encontradas: {len(tables)}")

# Revisar cada tabla
for table_name in [table[0] for table in tables]:
    print(f"\n=== TABLA: {table_name} ===")
    
    # Estructura de la tabla
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    
    print(f"Columnas ({len(columns)}):")
    for col in columns:
        print(f"  - {col[1]} ({col[2]}){' PRIMARY KEY' if col[5] > 0 else ''}")
    
    # Contar registros
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    count = cursor.fetchone()[0]
    
    print(f"Registros: {count}")
    
    # Mostrar algunos datos de muestra
    if count > 0:
        cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
        rows = cursor.fetchall()
        
        print("Primeros registros:")
        for row in rows:
            print(f"  {row}")

conn.close()
print("\nInspección completada.")