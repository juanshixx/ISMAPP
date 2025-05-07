"""
Servicio para la gestión de clientes en la base de datos.
"""
import sqlite3
from models.client import Client, ClientType

class ClientService:
    """Servicio para operaciones CRUD de clientes."""
    
    def __init__(self, db_manager):
        """
        Inicializa el servicio con una conexión a la base de datos.
        
        Args:
            db_manager: Instancia de DataManager para acceder a la base de datos
        """
        self.db_manager = db_manager
        
    def get_all_clients(self, include_inactive=False):
        """
        Obtiene todos los clientes de la base de datos.
        
        Args:
            include_inactive (bool): Si se incluyen clientes inactivos
            
        Returns:
            list: Lista de objetos Client
        """
        query = "SELECT * FROM clients"
        if not include_inactive:
            query += " WHERE is_active = 1"
        query += " ORDER BY name"
        
        try:
            results = self.db_manager.execute_query(query)
            return [Client.from_dict(result) for result in results]
        except Exception as e:
            print(f"Error al obtener clientes: {e}")
            return []
    
    def search_clients(self, search_term, client_type=None):
        """
        Busca clientes que coincidan con el término de búsqueda.
        
        Args:
            search_term (str): Término para buscar
            client_type (str, optional): Tipo de cliente a filtrar (comprador/proveedor)
            
        Returns:
            list: Lista de objetos Client que coinciden
        """
        # Limpiamos y preparamos el término de búsqueda
        search = f"%{search_term.strip()}%"
        
        query = """
        SELECT * FROM clients 
        WHERE (name LIKE ? OR business_name LIKE ? OR rut LIKE ? OR contact_person LIKE ?)
        AND is_active = 1 
        """
        
        # Añadir filtro por tipo de cliente si se especifica
        params = [search, search, search, search]
        if client_type:
            if client_type == ClientType.BUYER:
                query += "AND (client_type = ? OR client_type = ?) "
                params.extend([ClientType.BUYER, ClientType.BOTH])
            elif client_type == ClientType.SUPPLIER:
                query += "AND (client_type = ? OR client_type = ?) "
                params.extend([ClientType.SUPPLIER, ClientType.BOTH])
        
        query += "ORDER BY name"
        
        try:
            results = self.db_manager.execute_query(query, tuple(params))
            return [Client.from_dict(result) for result in results]
        except Exception as e:
            print(f"Error al buscar clientes: {e}")
            return []
    
    def get_client_by_id(self, client_id):
        """
        Obtiene un cliente por su ID.
        
        Args:
            client_id (int): ID del cliente
            
        Returns:
            Client: Cliente encontrado o None
        """
        query = "SELECT * FROM clients WHERE id = ?"
        
        try:
            results = self.db_manager.execute_query(query, (client_id,))
            return Client.from_dict(results[0]) if results else None
        except Exception as e:
            print(f"Error al obtener cliente por ID: {e}")
            return None
    
    def save_client(self, client):
        """
        Guarda un cliente en la base de datos (nuevo o actualización).
        
        Args:
            client (Client): Cliente a guardar
            
        Returns:
            bool: True si se guardó correctamente, False en caso contrario
        """
        if client.id is None:
            return self._create_client(client)
        else:
            return self._update_client(client)
    
    def _create_client(self, client):
        """Crea un nuevo cliente en la base de datos."""
        query = """
        INSERT INTO clients (name, business_name, rut, address, phone, email, 
                           contact_person, notes, is_active, client_type)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        params = (
            client.name, client.business_name, client.rut, client.address, 
            client.phone, client.email, client.contact_person, client.notes, 
            client.is_active, client.client_type
        )
        
        try:
            # Usar execute_query en lugar de execute_insert
            self.db_manager.execute_query(query, params)
            result = self.db_manager.execute_query("SELECT last_insert_rowid()")
            client.id = result[0][0] if result else None
            return True
        except Exception as e:
            print(f"Error al crear cliente: {e}")
            return False
    
    def _update_client(self, client):
        """Actualiza un cliente existente en la base de datos."""
        query = """
        UPDATE clients 
        SET name = ?, business_name = ?, rut = ?, address = ?, phone = ?, 
            email = ?, contact_person = ?, notes = ?, is_active = ?, client_type = ?
        WHERE id = ?
        """
        
        params = (
            client.name, client.business_name, client.rut, client.address, 
            client.phone, client.email, client.contact_person, client.notes, 
            client.is_active, client.client_type, client.id
        )
        
        try:
            # Usar execute_query en lugar de execute_update
            self.db_manager.execute_query(query, params)
            return True
        except Exception as e:
            print(f"Error al actualizar cliente: {e}")
            return False
    
    def delete_client(self, client_id):
        """
        Elimina un cliente (marcándolo como inactivo).
        
        Args:
            client_id (int): ID del cliente a eliminar
            
        Returns:
            bool: True si se eliminó correctamente, False en caso contrario
        """
        # Soft delete (marcar como inactivo)
        query = "UPDATE clients SET is_active = 0 WHERE id = ?"
        
        try:
            # Usar execute_query en lugar de execute_update
            self.db_manager.execute_query(query, (client_id,))
            return True
        except Exception as e:
            print(f"Error al eliminar cliente: {e}")
            return False