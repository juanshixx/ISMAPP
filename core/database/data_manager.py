"""
Gestor de datos que utiliza SQLite directamente.
"""
import os
from typing import Dict, List, Any, Optional
import json
import sqlite3
from datetime import datetime

class DataManager:
    """
    Gestor de datos que proporciona acceso a la base de datos SQLite.
    """
    
    _instance = None  # Para implementar patrón Singleton
    
    def __new__(cls, *args, **kwargs):
        """Implementa patrón Singleton para una única instancia de acceso a datos"""
        if cls._instance is None:
            cls._instance = super(DataManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, db_path: str = "data/ismv3.db"):
        """
        Inicializa el gestor de datos.
        
        Args:
            db_path (str): Ruta al archivo de base de datos SQLite.
        """
        # Evitar reinicializar si ya existe
        if hasattr(self, 'initialized'):
            return
            
        self.db_path = db_path
        self.connection = None
        self.cursor = None
        
        # Marcar como inicializado
        self.initialized = True
        
        # Asegurarse de que existe el directorio
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Conectar inmediatamente
        self.connect()
    
    def __del__(self):
        """Desconectar al finalizar"""
        self.disconnect()
    
    def connect(self) -> bool:
        """Establecer conexión con la base de datos"""
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row  # Para obtener resultados como diccionarios
            self.cursor = self.connection.cursor()
            return True
        except Exception as e:
            print(f"Error al conectar con la base de datos: {str(e)}")
            return False
    
    def disconnect(self) -> bool:
        """Cerrar conexión con la base de datos"""
        try:
            if self.connection:
                self.connection.close()
                self.connection = None
                self.cursor = None
            return True
        except Exception as e:
            print(f"Error al desconectar de la base de datos: {str(e)}")
            return False
    
    def _ensure_table_exists(self, entity_type: str):
        """Asegura que existe la tabla para el tipo de entidad"""
        self.cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS {entity_type} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data JSON NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        self.connection.commit()
    
    def get_all(self, entity_type: str) -> List[Dict[str, Any]]:
        """
        Obtiene todos los registros de una entidad.
        
        Args:
            entity_type (str): Tipo de entidad.
            
        Returns:
            List[Dict[str, Any]]: Lista de diccionarios con los datos.
        """
        if not self.connection and not self.connect():
            return []
        
        try:
            self._ensure_table_exists(entity_type)
            self.cursor.execute(f"SELECT id, data FROM {entity_type}")
            rows = self.cursor.fetchall()
            
            result = []
            for row in rows:
                # Combinar ID con datos JSON
                data = json.loads(row['data'])
                data['id'] = row['id']  # Asegurar que el ID está incluido
                result.append(data)
            
            return result
        except Exception as e:
            print(f"Error al obtener datos de {entity_type}: {str(e)}")
            return []
    
    def get_by_id(self, entity_type: str, entity_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene un registro por su ID.
        
        Args:
            entity_type (str): Tipo de entidad.
            entity_id (int): ID de la entidad.
            
        Returns:
            Optional[Dict[str, Any]]: Diccionario con los datos o None si no se encuentra.
        """
        if not self.connection and not self.connect():
            return None
        
        try:
            self._ensure_table_exists(entity_type)
            self.cursor.execute(f"SELECT id, data FROM {entity_type} WHERE id = ?", (entity_id,))
            row = self.cursor.fetchone()
            
            if row:
                data = json.loads(row['data'])
                data['id'] = row['id']  # Asegurar que el ID está incluido
                return data
            return None
        except Exception as e:
            print(f"Error al obtener entidad {entity_type} con ID {entity_id}: {str(e)}")
            return None
    
    def save(self, entity_type: str, entity_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Guarda un registro nuevo o actualiza uno existente.
        
        Args:
            entity_type (str): Tipo de entidad.
            entity_data (Dict[str, Any]): Datos de la entidad.
            
        Returns:
            Dict[str, Any]: Datos de la entidad guardada.
        """
        if not self.connection and not self.connect():
            return entity_data
        
        try:
            self._ensure_table_exists(entity_type)
            
            entity_id = entity_data.pop('id', None)  # Extraer ID si existe
            now = datetime.now().isoformat()
            
            if entity_id:
                # Actualizar registro existente
                self.cursor.execute(
                    f"UPDATE {entity_type} SET data = ?, updated_at = ? WHERE id = ?",
                    (json.dumps(entity_data), now, entity_id)
                )
                if self.cursor.rowcount == 0:
                    # Si no se actualizó ninguna fila, insertar como nuevo
                    self.cursor.execute(
                        f"INSERT INTO {entity_type} (id, data, created_at, updated_at) VALUES (?, ?, ?, ?)",
                        (entity_id, json.dumps(entity_data), now, now)
                    )
            else:
                # Insertar nuevo registro
                self.cursor.execute(
                    f"INSERT INTO {entity_type} (data, created_at, updated_at) VALUES (?, ?, ?)",
                    (json.dumps(entity_data), now, now)
                )
                entity_id = self.cursor.lastrowid
            
            self.connection.commit()
            
            # Devolver datos con ID
            entity_data['id'] = entity_id
            return entity_data
        except Exception as e:
            print(f"Error al guardar datos en {entity_type}: {str(e)}")
            self.connection.rollback()
            return entity_data
    
    def delete(self, entity_type: str, entity_id: int) -> bool:
        """
        Elimina un registro por su ID.
        
        Args:
            entity_type (str): Tipo de entidad.
            entity_id (int): ID de la entidad a eliminar.
            
        Returns:
            bool: True si se eliminó correctamente.
        """
        if not self.connection and not self.connect():
            return False
        
        try:
            self._ensure_table_exists(entity_type)
            self.cursor.execute(f"DELETE FROM {entity_type} WHERE id = ?", (entity_id,))
            self.connection.commit()
            return self.cursor.rowcount > 0
        except Exception as e:
            print(f"Error al eliminar registro de {entity_type}: {str(e)}")
            self.connection.rollback()
            return False