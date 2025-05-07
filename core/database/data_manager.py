"""
Gestor de acceso a la base de datos SQLite para ISMAPP.
"""
import os
import sqlite3
import threading

class DataManager:
    """Clase para gestionar operaciones de base de datos."""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """Implementación de patrón Singleton."""
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(DataManager, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance
    
    def __init__(self):
        """Inicializa el gestor de datos."""
        if self._initialized:
            return
            
        # Configurar ruta de la base de datos
        self.db_path = os.path.join("data", "ismv3.db")
        self._initialized = True
        
        # Verificar que existe la base de datos
        if not os.path.exists(self.db_path):
            # Crear directorio de datos si no existe
            data_dir = os.path.dirname(self.db_path)
            if not os.path.exists(data_dir):
                os.makedirs(data_dir, exist_ok=True)
                
            # Crear base de datos vacía
            try:
                connection = sqlite3.connect(self.db_path)
                connection.close()
                print(f"Base de datos creada en: {self.db_path}")
                
                # Crear el esquema básico
                self._create_schema()
            except Exception as e:
                print(f"Error al crear la base de datos: {e}")
    
    def _create_schema(self):
        """Crea el esquema inicial de la base de datos."""
        connection = None
        try:
            connection = sqlite3.connect(self.db_path)
            cursor = connection.cursor()
            
            # Tabla de usuarios (para autenticación)
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
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
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_username ON users (username)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_role ON users (role)")
            
            # Tabla de clientes
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS clients (
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
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_clients_name ON clients (name)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_clients_rut ON clients (rut)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_clients_type ON clients (client_type)")
            
            # Tabla de materiales
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS materials (
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
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_materials_name ON materials (name)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_materials_type ON materials (material_type)")
            
            # Tabla de relación cliente-material (con precios)
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS client_materials (
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
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_cm_client ON client_materials (client_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_cm_material ON client_materials (material_id)")
            
            # Tabla de trabajadores
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS workers (
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
            ''')
            
            # Crear índices para trabajadores
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_workers_name ON workers (name)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_workers_rut ON workers (rut)")
            
            # Insertar usuario admin por defecto
            cursor.execute('''
            INSERT OR IGNORE INTO users (username, password, name, role)
            VALUES (?, ?, ?, ?)
            ''', ('admin', 'admin123', 'Administrador', 'admin'))
            
            connection.commit()
            print("Esquema de base de datos creado correctamente!")
            
        except Exception as e:
            print(f"Error al crear el esquema: {e}")
            if connection:
                connection.rollback()
        finally:
            if connection:
                connection.close()
    
    def execute_query(self, query, params=()):
        """
        Ejecuta una consulta SQL y devuelve los resultados.
        
        Args:
            query (str): Consulta SQL a ejecutar
            params (tuple, optional): Parámetros para la consulta
            
        Returns:
            list/int/bool: Resultados de la consulta, ID de inserción o indicador de éxito
        """
        connection = None
        try:
            connection = sqlite3.connect(self.db_path)
            
            # Habilitar claves foráneas
            connection.execute("PRAGMA foreign_keys = ON")
            
            # Debug: mostrar consulta
            print(f"Ejecutando: {query}")
            print(f"Parámetros: {params}")
            
            # Para SELECT que involucre JOINs, utilizamos un enfoque alternativo
            if query.strip().upper().startswith("SELECT") and " JOIN " in query.upper():
                # Crear cursor directamente con row_factory
                connection.row_factory = sqlite3.Row
                cursor = connection.cursor()
                
                # Ejecutar la consulta
                cursor.execute(query, params)
                
                # Obtener los resultados
                rows = cursor.fetchall()
                
                # Para JOINs, creamos un diccionario por cada fila que incluye el prefijo de la tabla
                result = []
                for row in rows:
                    row_dict = {}
                    for key in row.keys():
                        row_dict[key] = row[key]  # Nombres de columnas estándar
                        
                    result.append(row_dict)
                    
                connection.close()
                return result
                
            # Para las consultas SELECT normales
            elif query.strip().upper().startswith("SELECT"):
                # Configurar para que las respuestas sean diccionarios
                connection.row_factory = sqlite3.Row
                cursor = connection.cursor()
                
                # Ejecutar consulta
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                # Convertir objetos Row a diccionarios
                results = []
                for row in rows:
                    results.append({key: row[key] for key in row.keys()})
                    
                connection.close()
                return results
            
            # Para INSERT, UPDATE, DELETE
            else:
                cursor = connection.cursor()
                cursor.execute(query, params)
                
                # Confirmar cambios
                connection.commit()
                
                # Para INSERT, intentar obtener el ID
                if query.strip().upper().startswith("INSERT"):
                    # Intentar obtener lastrowid
                    last_id = cursor.lastrowid
                    
                    # Si es None o 0, intentar obtenerlo explícitamente
                    if last_id is None or last_id == 0:
                        cursor.execute("SELECT last_insert_rowid()")
                        row = cursor.fetchone()
                        if row and row[0] is not None:
                            last_id = row[0]
                    
                    connection.close()
                    return last_id
                
                # Para UPDATE y DELETE, devolver True (éxito)
                connection.close()
                return True
                
        except Exception as e:
            print(f"Error en la consulta: {e}")
            if connection:
                connection.rollback()
            if connection:
                connection.close()
            # En lugar de propagar el error, devolvemos None para indicar un problema
            return None
    
    def get_all(self, table_name, condition=None):
        """
        Obtiene todos los registros de una tabla.
        
        Args:
            table_name (str): Nombre de la tabla
            condition (str, optional): Condición WHERE
            
        Returns:
            list: Lista de diccionarios con los datos
        """
        query = f"SELECT * FROM {table_name}"
        if condition:
            query += f" WHERE {condition}"
            
        return self.execute_query(query)
    
    def get_connection(self):
        """
        Obtiene una conexión a la base de datos.
        
        Returns:
            Connection: Objeto de conexión SQLite
        """
        try:
            connection = sqlite3.connect(self.db_path)
            connection.execute("PRAGMA foreign_keys = ON")
            return connection
        except Exception as e:
            print(f"Error al conectar a la base de datos: {e}")
            raise