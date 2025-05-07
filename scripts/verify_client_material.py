"""
Verifica si existe una relación entre cliente y material específicos.
"""
import sqlite3
import os

# Conectar a la base de datos
db_path = os.path.join("data", "ismv3.db")
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Parámetros del último intento
client_id = 4
material_id = 12

# Verificar si existe la relación
cursor.execute("""
    SELECT * FROM client_materials 
    WHERE client_id = ? AND material_id = ?
""", (client_id, material_id))

row = cursor.fetchone()

if row:
    print("¡Relación encontrada! La inserción SÍ fue exitosa:")
    print(f"ID: {row['id']}")
    print(f"Cliente ID: {row['client_id']}")
    print(f"Material ID: {row['material_id']}")
    print(f"Precio: {row['price']}")
    print(f"Incluye impuestos: {'Sí' if row['includes_tax'] else 'No'}")
    print(f"Notas: {row['notes']}")
else:
    print(f"No se encontró relación entre cliente ID={client_id} y material ID={material_id}")

conn.close()