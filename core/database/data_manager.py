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
            print(f"ADVERTENCIA: La base de datos no existe en {self.db_path}")
            print("Por favor ejecuta el script 'scripts/recreate_db.py' primero")
    
    def execute_query(self, query, params=()):
        """
        Ejecuta una consulta SQL y devuelve los resultados.
        
        Args:
            query (str): Consulta SQL a ejecutar
            params (tuple, optional): Parámetros para la consulta
            
        Returns:
            list/int: Resultados de la consulta o ID de la última inserción
        """
        connection = None
        try:
            connection = sqlite3.connect(self.db_path)
            
            # Habilitar claves foráneas
            connection.execute("PRAGMA foreign_keys = ON")
            
            # Configurar para que las respuestas sean diccionarios
            connection.row_factory = sqlite3.Row
            cursor = connection.cursor()
            
            # Debug: mostrar consulta
            print(f"Ejecutando: {query}")
            print(f"Parámetros: {params}")
            
            # Ejecutar consulta
            cursor.execute(query, params)
            
            # Para SELECT, devolver resultados
            if query.strip().upper().startswith("SELECT"):
                rows = cursor.fetchall()
                # Convertir objetos Row a diccionarios
                results = []
                for row in rows:
                    results.append({key: row[key] for key in row.keys()})
                return results
            
            # Para INSERT, UPDATE, DELETE
            else:
                connection.commit()
                last_id = cursor.lastrowid
                return last_id
                
        except Exception as e:
            print(f"Error en la consulta: {e}")
            if connection:
                connection.rollback()
            raise
        finally:
            if connection:
                connection.close()
    
    # Método de compatibilidad para WorkerView
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