"""
Script para verificar la conexión de cliente-material y diagnosticar problemas.
"""
import os
import sqlite3
import sys

# Ruta de la base de datos
DB_PATH = os.path.join("data", "ismv3.db")

def check_client_materials(client_id):
    """Verifica los materiales de un cliente específico."""
    conn = None
    try:
        # Conectar a la base de datos
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Verificar si el cliente existe
        cursor.execute("SELECT * FROM clients WHERE id = ?", (client_id,))
        client = cursor.fetchone()
        
        if not client:
            print(f"Error: No se encontró ningún cliente con ID {client_id}")
            return
            
        print(f"Cliente encontrado: {client['name']} (ID: {client_id})")
        
        # Verificar materiales del cliente usando una consulta simple
        cursor.execute("""
            SELECT cm.id, cm.material_id, cm.price, cm.includes_tax, m.name, m.material_type
            FROM client_materials cm
            JOIN materials m ON cm.material_id = m.id
            WHERE cm.client_id = ?
        """, (client_id,))
        
        materials = cursor.fetchall()
        
        if not materials:
            print("Este cliente no tiene materiales asignados.")
            return
            
        print(f"\nMateriales del cliente (encontrados {len(materials)}):")
        for material in materials:
            print(f"  • {material['name']} (ID: {material['material_id']})")
            print(f"    - Tipo: {material['material_type']}")
            print(f"    - Precio: ${material['price']}")
            print(f"    - Incluye impuesto: {'Sí' if material['includes_tax'] else 'No'}")
            print("    ------------------------")
        
        # Todo correcto
        print("\n✓ La conexión entre cliente y materiales funciona correctamente")
        
    except Exception as e:
        print(f"Error al verificar los materiales del cliente: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    # Verificar cliente con ID=4 (el del error en tu mensaje)
    client_id = 4
    
    # Si se proporciona un ID como argumento, usarlo
    if len(sys.argv) > 1:
        try:
            client_id = int(sys.argv[1])
        except ValueError:
            print(f"Error: El ID proporcionado '{sys.argv[1]}' no es un número válido.")
            sys.exit(1)
            
    check_client_materials(client_id)