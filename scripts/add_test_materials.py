"""
Script para añadir materiales de prueba a la base de datos.
"""
import os
import sqlite3
import sys
from datetime import datetime

# Ruta de la base de datos
DB_PATH = os.path.join("data", "ismv3.db")

# Materiales de prueba a añadir
TEST_MATERIALS = [
    {
        "name": "Cartón corrugado",
        "description": "Cartón utilizado principalmente en cajas y empaques",
        "material_type": "Cartón",
        "is_plastic_subtype": 0,
        "is_active": 1
    },
    {
        "name": "Papel blanco",
        "description": "Papel de oficina, impresión y escritura",
        "material_type": "Papel",
        "is_plastic_subtype": 0,
        "is_active": 1
    },
    {
        "name": "PET transparente",
        "description": "Botellas de bebidas y envases transparentes",
        "material_type": "Plástico",
        "is_plastic_subtype": 1,
        "plastic_subtype": "PET",
        "plastic_state": "Limpio",
        "is_active": 1
    },
    {
        "name": "HDPE color",
        "description": "Envases de detergentes, shampoo, etc.",
        "material_type": "Plástico",
        "is_plastic_subtype": 1,
        "plastic_subtype": "HDPE",
        "plastic_state": "Mixto",
        "is_active": 1
    },
    {
        "name": "Aluminio",
        "description": "Latas de bebidas y otros envases de aluminio",
        "material_type": "Metal",
        "is_plastic_subtype": 0,
        "is_active": 1
    }
]

def add_test_materials():
    """Añade materiales de prueba a la base de datos."""
    conn = None
    try:
        # Conectar a la base de datos
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Verificar los materiales existentes
        cursor.execute("SELECT name FROM materials")
        existing_materials = {row[0] for row in cursor.fetchall()}
        
        # Añadir materiales que no existen
        added = 0
        skipped = 0
        
        for material in TEST_MATERIALS:
            if material["name"] not in existing_materials:
                cursor.execute("""
                    INSERT INTO materials (
                        name, description, material_type, is_plastic_subtype,
                        plastic_subtype, plastic_state, is_active,
                        created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    material["name"],
                    material.get("description", ""),
                    material["material_type"],
                    material.get("is_plastic_subtype", 0),
                    material.get("plastic_subtype", ""),
                    material.get("plastic_state", ""),
                    material.get("is_active", 1),
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                ))
                added += 1
            else:
                skipped += 1
        
        conn.commit()
        print(f"Materiales añadidos: {added}")
        print(f"Materiales saltados (ya existían): {skipped}")
        
        # Mostrar todos los materiales en la base de datos
        cursor.execute("SELECT id, name, material_type FROM materials")
        all_materials = cursor.fetchall()
        
        print("\nMateriales en la base de datos:")
        for mat in all_materials:
            print(f"  • ID: {mat[0]} - {mat[1]} ({mat[2]})")
        
    except Exception as e:
        print(f"Error al añadir materiales: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    add_test_materials()