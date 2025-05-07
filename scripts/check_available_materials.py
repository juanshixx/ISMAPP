"""
Script para verificar materiales disponibles para un cliente específico.
"""
import os
import sqlite3
import sys

# Ruta de la base de datos
DB_PATH = os.path.join("data", "ismv3.db")

def check_available_materials(client_id):
    """Verifica los materiales disponibles para un cliente."""
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
        
        # Verificar materiales ya asignados al cliente
        cursor.execute("""
            SELECT cm.material_id, m.name, m.material_type
            FROM client_materials cm
            JOIN materials m ON cm.material_id = m.id
            WHERE cm.client_id = ?
        """, (client_id,))
        
        assigned = cursor.fetchall()
        
        print(f"\nMateriales ya asignados a este cliente ({len(assigned)}):")
        if assigned:
            for mat in assigned:
                print(f"  • {mat['name']} (ID: {mat['material_id']}, Tipo: {mat['material_type']})")
        else:
            print("  (Ninguno)")
        
        # Verificar materiales disponibles (no asignados) al cliente
        cursor.execute("""
            SELECT * FROM materials
            WHERE is_active = 1 AND id NOT IN (
                SELECT material_id FROM client_materials WHERE client_id = ?
            )
            ORDER BY name
        """, (client_id,))
        
        available = cursor.fetchall()
        
        print(f"\nMateriales DISPONIBLES para asignar ({len(available)}):")
        if available:
            for mat in available:
                print(f"  • {mat['name']} (ID: {mat['id']}, Tipo: {mat['material_type']})")
        else:
            print("  (Ninguno - Todos los materiales ya están asignados a este cliente)")
        
        # Verificar si hay materiales en la base de datos
        cursor.execute("SELECT COUNT(*) as count FROM materials WHERE is_active = 1")
        total = cursor.fetchone()['count']
        
        print(f"\nTotal de materiales activos en la base de datos: {total}")
        
        if total == 0:
            print("\n*** PROBLEMA DETECTADO: No hay materiales en la base de datos ***")
            print("Solución: Añada al menos un material desde el módulo de Materiales")
        
        if len(assigned) == total and total > 0:
            print("\n*** INFORMACIÓN: Todos los materiales ya están asignados a este cliente ***")
            print("Para añadir más materiales, primero debe crearlos en el módulo de Materiales")
        
    except Exception as e:
        print(f"Error al verificar materiales disponibles: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    # Si se proporciona un ID como argumento, usarlo
    client_id = 4  # ID predeterminado
    
    if len(sys.argv) > 1:
        try:
            client_id = int(sys.argv[1])
        except ValueError:
            print(f"Error: El ID proporcionado '{sys.argv[1]}' no es un número válido.")
            sys.exit(1)
    
    print(f"Verificando materiales disponibles para el cliente ID: {client_id}\n")
    check_available_materials(client_id)