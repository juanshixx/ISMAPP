"""
Script para verificar materiales en la base de datos.
"""
import os
import sqlite3
import sys

# Añadir directorio raíz al path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# Verificar materiales
def check_materials():
    """Verifica los materiales en la base de datos."""
    db_path = os.path.join(parent_dir, "data", "ismv3.db")
    
    if not os.path.exists(db_path):
        print(f"Error: La base de datos no existe en {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row  # Para acceso por nombre de columna
        cursor = conn.cursor()
        
        # Verificar si la tabla existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='materials'")
        if not cursor.fetchone():
            print("Error: La tabla 'materials' no existe en la base de datos")
            return
        
        # Ver la estructura de la tabla
        cursor.execute("PRAGMA table_info(materials)")
        columns = cursor.fetchall()
        print("Estructura de la tabla 'materials':")
        for col in columns:
            print(f"  - {col['name']} ({col['type']})")
        
        # Contar materiales
        cursor.execute("SELECT COUNT(*) as count FROM materials")
        count = cursor.fetchone()['count']
        print(f"\nTotal de materiales: {count}")
        
        # Obtener lista de materiales
        cursor.execute("SELECT * FROM materials ORDER BY material_type, name")
        materials = cursor.fetchall()
        
        if not materials:
            print("No se encontraron materiales en la base de datos.")
            return
        
        print("\nLista de Materiales:")
        print("=" * 80)
        print(f"{'ID':<4} {'Nombre':<20} {'Tipo':<12} {'Plástico':<8} {'Subtipo':<15} {'Estado':<10} {'Personalizado':<15} {'Activo':<8}")
        print("-" * 80)
        
        for mat in materials:
            is_plastic = "Sí" if mat['is_plastic_subtype'] == 1 else "No"
            is_active = "Sí" if mat['is_active'] == 1 else "No"
            print(f"{mat['id']:<4} {mat['name']:<20} {mat['material_type']:<12} {is_plastic:<8} {mat['plastic_subtype']:<15} {mat['plastic_state']:<10} {mat['custom_subtype']:<15} {is_active:<8}")
        
    except Exception as e:
        print(f"Error al verificar materiales: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    check_materials()