"""
Servicio para la gestión de clientes.
"""
from models.client import Client

class ClientService:
    """Servicio para operaciones CRUD de clientes."""
    
    def __init__(self, data_manager):
        """
        Inicializa el servicio de clientes.
        
        Args:
            data_manager: Gestor de base de datos
        """
        self.db_manager = data_manager
    
    def get_all_clients(self):
        """
        Obtiene todos los clientes activos.
        
        Returns:
            list: Lista de objetos Client
        """
        query = "SELECT * FROM clients WHERE is_active = 1 ORDER BY name"
        
        try:
            results = self.db_manager.execute_query(query)
            clients = []
            
            for row in results:
                client = Client.from_dict(row)
                clients.append(client)
                
            return clients
        except Exception as e:
            print(f"Error al obtener clientes: {e}")
            return []
    
    def get_client_by_id(self, client_id):
        """
        Obtiene un cliente por su ID.
        
        Args:
            client_id (int): ID del cliente a buscar
            
        Returns:
            Client: Objeto cliente si se encuentra, None en otro caso
        """
        query = "SELECT * FROM clients WHERE id = ?"
        
        try:
            results = self.db_manager.execute_query(query, (client_id,))
            
            if results:
                return Client.from_dict(results[0])
            return None
        except Exception as e:
            print(f"Error al obtener cliente por ID: {e}")
            return None
    
    def save_client(self, client):
        """
        Guarda un cliente (nuevo o existente).
        
        Args:
            client (Client): Cliente a guardar
            
        Returns:
            bool: True si se guardó correctamente
        """
        try:
            if client.id is None:
                # CORREGIDO: Acepta IDs igual a 0
                result = self._create_client(client)
                if result is not False and result is not None:
                    client.id = result if result is not True else None
                    return True
                return False
            else:
                return self._update_client(client)
        except Exception as e:
            print(f"Error al guardar cliente: {e}")
            return False
    
    def _create_client(self, client):
        """
        Crea un nuevo cliente en la base de datos.
        
        Args:
            client (Client): Cliente a crear
            
        Returns:
            int/bool: ID del cliente creado o False si hay error
        """
        query = """
        INSERT INTO clients (name, business_name, rut, address, phone, email, 
                           contact_person, notes, is_active, client_type)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        params = (
            client.name, 
            client.business_name, 
            client.rut,
            client.address, 
            client.phone, 
            client.email, 
            client.contact_person,
            client.notes,
            client.is_active,
            client.client_type
        )
        
        try:
            # CORREGIDO: Aceptar ID=0 como válido
            result = self.db_manager.execute_query(query, params)
            
            # Si el resultado es un número (incluyendo 0) o True, la operación fue exitosa
            if result is True or result is not None:
                return result
            return False
        except Exception as e:
            print(f"Error al crear cliente: {e}")
            return False
    
    def _update_client(self, client):
        """
        Actualiza un cliente existente.
        
        Args:
            client (Client): Cliente a actualizar
            
        Returns:
            bool: True si se actualizó correctamente
        """
        query = """
        UPDATE clients 
        SET name = ?, 
            business_name = ?, 
            rut = ?, 
            address = ?, 
            phone = ?, 
            email = ?, 
            contact_person = ?, 
            notes = ?,
            is_active = ?,
            client_type = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        """
        
        params = (
            client.name, 
            client.business_name, 
            client.rut,
            client.address, 
            client.phone, 
            client.email, 
            client.contact_person,
            client.notes,
            client.is_active,
            client.client_type,
            client.id
        )
        
        try:
            self.db_manager.execute_query(query, params)
            return True
        except Exception as e:
            print(f"Error al actualizar cliente: {e}")
            return False
    
    def delete_client(self, client_id):
        """
        Elimina un cliente de forma lógica.
        
        Args:
            client_id (int): ID del cliente a eliminar
            
        Returns:
            bool: True si se eliminó correctamente
        """
        # En lugar de eliminar, marcamos como inactivo
        query = """
        UPDATE clients SET is_active = 0, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        """
        
        try:
            self.db_manager.execute_query(query, (client_id,))
            return True
        except Exception as e:
            print(f"Error al eliminar cliente: {e}")
            return False
    
    def search_clients(self, search_term):
        """
        Busca clientes que coincidan con el término de búsqueda.
        
        Args:
            search_term (str): Término de búsqueda
            
        Returns:
            list: Lista de objetos Client que coinciden
        """
        search_pattern = f"%{search_term}%"
        
        query = """
        SELECT * FROM clients
        WHERE is_active = 1 AND (
            name LIKE ? OR 
            business_name LIKE ? OR 
            rut LIKE ? OR
            contact_person LIKE ?
        )
        ORDER BY name
        """
        
        try:
            params = (search_pattern, search_pattern, search_pattern, search_pattern)
            results = self.db_manager.execute_query(query, params)
            
            clients = []
            for row in results:
                client = Client.from_dict(row)
                clients.append(client)
                
            return clients
        except Exception as e:
            print(f"Error al buscar clientes: {e}")
            return []
    
    def get_clients_by_type(self, client_type):
        """
        Obtiene clientes filtrados por tipo.
        
        Args:
            client_type (str): Tipo de cliente a filtrar ('supplier', 'buyer', 'both')
            
        Returns:
            list: Lista de objetos Client
        """
        query = "SELECT * FROM clients WHERE is_active = 1 AND client_type = ? ORDER BY name"
        
        try:
            results = self.db_manager.execute_query(query, (client_type,))
            
            clients = []
            for row in results:
                client = Client.from_dict(row)
                clients.append(client)
                
            return clients
        except Exception as e:
            print(f"Error al obtener clientes por tipo: {e}")
            return []