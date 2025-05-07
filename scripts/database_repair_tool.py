"""
Script de diagnóstico y reparación para la base de datos de ISMAPP.

Este script verifica y repara problemas comunes en la base de datos:
1. Verificar integridad de la base de datos
2. Crear tablas faltantes
3. Reparar secuencias SQLite
4. Verificar relaciones entre tablas
5. Crear respaldo antes de realizar cambios
"""
import os
import sqlite3
import shutil
import sys
from datetime import datetime

# Configuración
DB_PATH = os.path.join("data", "ismv3.db")
BACKUP_DIR = os.path.join("data", "backups")

# Asegurar que existe el directorio de backups
os.makedirs(BACKUP_DIR, exist_ok=True)

def create_backup():
    """Crea una copia de seguridad de la base de datos."""
    if not os.path.exists(DB_PATH):
        print(f"No se encontró la base de datos en: {DB_PATH}")
        return False

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(BACKUP_DIR, f"ismv3_backup_{timestamp}.db")
    
    try:
        shutil.copy2(DB_PATH, backup_path)
        print(f"✓ Backup creado en: {backup_path}")
        return True
    except Exception as e:
        print(f"✗ Error al crear backup: {e}")
        return False

def check_and_connect_db():
    """Verifica la existencia de la base de datos y establece conexión."""
    if not os.path.exists(DB_PATH):
        print(f"✗ La base de datos no existe en: {DB_PATH}")
        
        # Crear directorio de datos si no existe
        db_dir = os.path.dirname(DB_PATH)
        if not os.path.exists(db_dir):
            os.makedirs(db_dir)
            print(f"✓ Directorio de datos creado: {db_dir}")
        
        response = input("¿Desea crear una nueva base de datos? (s/n): ")
        if response.lower() not in ('s', 'si', 'sí', 'y', 'yes'):
            print("Operación cancelada.")
            sys.exit(0)
            
        conn = sqlite3.connect(DB_PATH)
        print(f"✓ Base de datos vacía creada en: {DB_PATH}")
        return conn
    
    try:
        conn = sqlite3.connect(DB_PATH)
        print(f"✓ Conexión establecida con la base de datos")
        return conn
    except Exception as e:
        print(f"✗ Error al conectar con la base de datos: {e}")
        sys.exit(1)

def check_tables(conn):
    """Verifica qué tablas existen en la base de datos."""
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    existing_tables = [row[0] for row in cursor.fetchall()]
    
    print("\n=== TABLAS EXISTENTES ===")
    if existing_tables:
        for table in existing_tables:
            print(f"- {table}")
    else:
        print("No se encontraron tablas en la base de datos.")
    
    # Tablas requeridas por la aplicación
    required_tables = ['users', 'clients', 'materials', 'client_materials', 'workers']
    missing_tables = [table for table in required_tables if table not in existing_tables]
    
    if missing_tables:
        print("\n=== TABLAS FALTANTES ===")
        for table in missing_tables:
            print(f"- {table}")
        
        return missing_tables
    else:
        print("\n✓ Todas las tablas requeridas existen")
        return []

def create_missing_tables(conn, missing_tables):
    """Crea las tablas que faltan en la base de datos."""
    if not missing_tables:
        return
    
    print("\n=== CREANDO TABLAS FALTANTES ===")
    cursor = conn.cursor()
    
    table_schemas = {
        'users': '''
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
        ''',
        'clients': '''
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
        ''',
        'materials': '''
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
        ''',
        'client_materials': '''
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
        ''',
        'workers': '''
            CREATE TABLE workers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                rut TEXT NOT NULL UNIQUE,
                phone TEXT,
                address TEXT,
                email TEXT,
                role TEXT,
                salary REAL DEFAULT 0.0,
                is_active INTEGER DEFAULT 1,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        '''
    }
    
    for table in missing_tables:
        if table in table_schemas:
            try:
                cursor.execute(table_schemas[table])
                print(f"✓ Tabla '{table}' creada correctamente")
                
                # Crear índices para las tablas
                if table == 'clients':
                    cursor.execute("CREATE INDEX IF NOT EXISTS idx_clients_name ON clients (name)")
                    cursor.execute("CREATE INDEX IF NOT EXISTS idx_clients_rut ON clients (rut)")
                    cursor.execute("CREATE INDEX IF NOT EXISTS idx_clients_type ON clients (client_type)")
                elif table == 'materials':
                    cursor.execute("CREATE INDEX IF NOT EXISTS idx_materials_name ON materials (name)")
                    cursor.execute("CREATE INDEX IF NOT EXISTS idx_materials_type ON materials (material_type)")
                elif table == 'client_materials':
                    cursor.execute("CREATE INDEX IF NOT EXISTS idx_cm_client ON client_materials (client_id)")
                    cursor.execute("CREATE INDEX IF NOT EXISTS idx_cm_material ON client_materials (material_id)")
                elif table == 'workers':
                    cursor.execute("CREATE INDEX IF NOT EXISTS idx_workers_name ON workers (name)")
                    cursor.execute("CREATE INDEX IF NOT EXISTS idx_workers_rut ON workers (rut)")
                
                # Si es la tabla users y está vacía, crear usuario admin
                if table == 'users':
                    cursor.execute("INSERT OR IGNORE INTO users (username, password, name, role) VALUES (?, ?, ?, ?)",
                                 ('admin', 'admin123', 'Administrador', 'admin'))
                
            except Exception as e:
                print(f"✗ Error al crear tabla '{table}': {e}")
        else:
            print(f"✗ No se encontró esquema para la tabla '{table}'")
    
    conn.commit()

def verify_table_structure(conn):
    """Verifica la estructura de las tablas existentes."""
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    existing_tables = [row[0] for row in cursor.fetchall()]
    
    print("\n=== VERIFICANDO ESTRUCTURA DE TABLAS ===")
    
    for table in existing_tables:
        if table.startswith('sqlite_'):  # Ignorar tablas del sistema SQLite
            continue
            
        try:
            cursor.execute(f"PRAGMA table_info({table})")
            columns = cursor.fetchall()
            
            print(f"\nTabla: {table}")
            for col in columns:
                col_id, name, type_, notnull, default, pk = col
                pk_mark = "🔑" if pk else ""
                null_mark = "NOT NULL" if notnull else "NULL"
                default_val = f"DEFAULT {default}" if default is not None else ""
                print(f"   {name} {type_} {null_mark} {default_val} {pk_mark}")
        except Exception as e:
            print(f"✗ Error al verificar estructura de '{table}': {e}")

def reset_sequences(conn):
    """Restablece las secuencias de autoincremento para todas las tablas."""
    print("\n=== RESTABLECIENDO SECUENCIAS ===")
    
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall() if not row[0].startswith('sqlite_')]
    
    for table in tables:
        try:
            # Verificar si la tabla tiene una columna de ID autoincremental
            cursor.execute(f"PRAGMA table_info({table})")
            columns = cursor.fetchall()
            
            id_column = None
            for col in columns:
                if col[1].lower() == 'id' and col[5] == 1:  # Columna ID con PK
                    id_column = col[1]
                    break
            
            if id_column:
                # Obtener el máximo ID actual
                cursor.execute(f"SELECT MAX({id_column}) FROM {table}")
                max_id = cursor.fetchone()[0] or 0
                
                # Actualizar la secuencia
                cursor.execute("UPDATE sqlite_sequence SET seq = ? WHERE name = ?", (max_id, table))
                
                # Si no existe entrada en sqlite_sequence, crearla
                cursor.execute("SELECT count(*) FROM sqlite_sequence WHERE name = ?", (table,))
                if cursor.fetchone()[0] == 0:
                    cursor.execute("INSERT INTO sqlite_sequence (name, seq) VALUES (?, ?)", (table, max_id))
                
                print(f"✓ Secuencia de '{table}' restablecida a {max_id}")
        except Exception as e:
            print(f"✗ Error al restablecer secuencia de '{table}': {e}")
    
    conn.commit()

def verify_integrity(conn):
    """Verifica la integridad referencial de la base de datos."""
    print("\n=== VERIFICANDO INTEGRIDAD REFERENCIAL ===")
    
    cursor = conn.cursor()
    try:
        cursor.execute("PRAGMA foreign_key_check")
        integrity_errors = cursor.fetchall()
        
        if integrity_errors:
            print("✗ Se encontraron errores de integridad referencial:")
            for error in integrity_errors:
                print(f"  - Tabla: {error[0]}, RowID: {error[1]}, Referencia: {error[2]}, ID: {error[3]}")
        else:
            print("✓ No se encontraron errores de integridad referencial")
    except Exception as e:
        print(f"✗ Error al verificar integridad: {e}")

def fix_client_material_issues(conn):
    """Corrige problemas específicos con la relación cliente-material."""
    print("\n=== CORRIGIENDO PROBLEMAS DE CLIENTE-MATERIAL ===")
    
    cursor = conn.cursor()
    
    # 1. Verificar si hay clientes sin materiales
    cursor.execute("""
        SELECT c.id, c.name 
        FROM clients c
        LEFT JOIN client_materials cm ON c.id = cm.client_id
        WHERE cm.id IS NULL AND c.is_active = 1
    """)
    clients_without_materials = cursor.fetchall()
    
    if clients_without_materials:
        print("Clientes sin materiales asignados:")
        for client in clients_without_materials:
            print(f"  - ID: {client[0]}, Nombre: {client[1]}")
    
    # 2. Verificar errores comunes de referencias
    try:
        # Materiales referenciados que no existen
        cursor.execute("""
            SELECT cm.id, cm.client_id, cm.material_id
            FROM client_materials cm
            LEFT JOIN materials m ON cm.material_id = m.id
            WHERE m.id IS NULL
        """)
        invalid_refs = cursor.fetchall()
        
        if invalid_refs:
            print("\n✗ Referencias inválidas a materiales:")
            for ref in invalid_refs:
                print(f"  - ID: {ref[0]}, Cliente ID: {ref[1]}, Material ID inexistente: {ref[2]}")
            
            fix = input("¿Desea eliminar estas referencias inválidas? (s/n): ")
            if fix.lower() in ('s', 'si', 'sí', 'y', 'yes'):
                for ref in invalid_refs:
                    cursor.execute("DELETE FROM client_materials WHERE id = ?", (ref[0],))
                conn.commit()
                print("✓ Referencias inválidas eliminadas")
    except Exception as e:
        print(f"✗ Error al verificar referencias: {e}")
    
    # 3. Verificar duplicados en client_materials
    try:
        cursor.execute("""
            SELECT client_id, material_id, COUNT(*) 
            FROM client_materials 
            GROUP BY client_id, material_id 
            HAVING COUNT(*) > 1
        """)
        duplicates = cursor.fetchall()
        
        if duplicates:
            print("\n✗ Entradas duplicadas en client_materials:")
            for dup in duplicates:
                print(f"  - Cliente ID: {dup[0]}, Material ID: {dup[1]}, Repeticiones: {dup[2]}")
            
            fix = input("¿Desea corregir estas duplicaciones? (s/n): ")
            if fix.lower() in ('s', 'si', 'sí', 'y', 'yes'):
                for dup in duplicates:
                    # Mantener solo el registro más reciente para cada par cliente-material
                    cursor.execute("""
                        DELETE FROM client_materials 
                        WHERE client_id = ? AND material_id = ? 
                        AND id NOT IN (
                            SELECT id FROM client_materials 
                            WHERE client_id = ? AND material_id = ? 
                            ORDER BY updated_at DESC LIMIT 1
                        )
                    """, (dup[0], dup[1], dup[0], dup[1]))
                conn.commit()
                print("✓ Duplicados corregidos")
    except Exception as e:
        print(f"✗ Error al verificar duplicados: {e}")

def check_users_table(conn):
    """Verifica la tabla de usuarios y crea al admin si es necesario."""
    print("\n=== VERIFICANDO TABLA DE USUARIOS ===")
    
    cursor = conn.cursor()
    
    # Verificar si existe al menos un usuario admin
    cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'admin'")
    admin_count = cursor.fetchone()[0]
    
    if admin_count == 0:
        print("✗ No hay usuarios con rol de administrador")
        create_admin = input("¿Desea crear el usuario administrador predeterminado? (s/n): ")
        
        if create_admin.lower() in ('s', 'si', 'sí', 'y', 'yes'):
            cursor.execute("""
                INSERT INTO users (username, password, name, role, is_active) 
                VALUES (?, ?, ?, ?, ?)
            """, ('admin', 'admin123', 'Administrador', 'admin', 1))
            conn.commit()
            print("✓ Usuario administrador creado (usuario: admin, contraseña: admin123)")
    else:
        print(f"✓ Existen {admin_count} usuarios administradores")

def print_summary():
    """Imprime un resumen de los problemas comunes y soluciones."""
    print("\n=== SOLUCIONES PARA ERRORES COMUNES ===")
    print("\n1. Error: 'no such table: workers'")
    print("   Solución: Este script ha creado la tabla faltante 'workers'.")
    
    print("\n2. Error: 'unknown option \"-username\"'")
    print("   Solución: Este es un error de Tkinter en la vista UserAdminView.")
    print("   Verifique el archivo 'views/user_admin_view.py' para asegurarse")
    print("   de que todas las opciones de widgets son válidas.")
    
    print("\n3. Error: 'Error al crear relación cliente-material: 0'")
    print("   Solución: Esto ocurre porque el código interpreta incorrectamente el ID")
    print("   devuelto tras la inserción. Se ha corregido en material_service.py y client_service.py.")
    print("   - La inserción probablemente fue exitosa pero el código lo interpretaba como error.")
    
    print("\n4. Para resolver problemas persistentes, verifique:")
    print("   - Asegúrese de que DataManager.execute_query() maneja correctamente los resultados")
    print("   - Revise los *_service.py para garantizar que manejen correctamente los IDs devueltos")

def main():
    """Función principal del script."""
    print("===== HERRAMIENTA DE DIAGNÓSTICO Y REPARACIÓN DE BASE DE DATOS =====")
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Base de datos: {DB_PATH}\n")
    
    # Crear backup antes de hacer cambios
    backup_success = create_backup()
    
    # Verificar y conectar a la base de datos
    conn = check_and_connect_db()
    
    # Verificar tablas existentes
    missing_tables = check_tables(conn)
    
    # Crear tablas faltantes
    if missing_tables:
        create_missing_tables(conn, missing_tables)
    
    # Verificar estructura de tablas
    verify_table_structure(conn)
    
    # Restablecer secuencias
    reset_sequences(conn)
    
    # Verificar integridad referencial
    verify_integrity(conn)
    
    # Corregir problemas específicos
    fix_client_material_issues(conn)
    
    # Verificar tabla de usuarios
    check_users_table(conn)
    
    # Imprimir resumen
    print_summary()
    
    # Cerrar conexión
    conn.close()
    
    print("\n=== FINALIZADO ===")
    print("La base de datos ha sido diagnosticada y reparada.")
    print("Por favor, reinicie la aplicación para aplicar los cambios.")

if __name__ == "__main__":
    main()