"""
Servicio para la gestión de la relación entre clientes y materiales.
"""
from models.client_material import ClientMaterial
from models.material import Material

class ClientMaterialService:
    """Servicio para operaciones de precios de materiales por cliente."""
    
    def __init__(self, db_manager):
        """
        Inicializa el servicio con una conexión a la base de datos.
        
        Args:
            db_manager: Instancia de DataManager para acceder a la base de datos
        """
        self.db_manager = db_manager
    
    def get_client_materials(self, client_id):
        """
        Obtiene todos los materiales asociados a un cliente.
        
        Args:
            client_id (int): ID del cliente
            
        Returns:
            list: Lista de tuplas (ClientMaterial, Material)
        """
        query = """
        SELECT cm.*, m.* FROM client_materials cm
        JOIN materials m ON cm.material_id = m.id
        WHERE cm.client_id = ?
        ORDER BY m.name
        """
        
        try:
            results = self.db_manager.execute_query(query, (client_id,))
            client_materials = []
            
            for row in results:
                # Dividir el resultado en dos partes: datos de la relación y datos del material
                cm_data = {
                    'id': row[0],
                    'client_id': row[1],
                    'material_id': row[2],
                    'price': row[3],
                    'includes_tax': row[4],
                    'notes': row[5]
                }
                
                m_data = {
                    'id': row[6],
                    'name': row[7],
                    'description': row[8],
                    'material_type': row[9],
                    'is_plastic_subtype': row[10],
                    'plastic_subtype': row[11],
                    'plastic_state': row[12],
                    'custom_subtype': row[13],
                    'is_active': row[14]
                }
                
                client_material = ClientMaterial.from_dict(cm_data)
                material = Material.from_dict(m_data)
                
                client_materials.append((client_material, material))
            
            return client_materials
        except Exception as e:
            print(f"Error al obtener materiales del cliente: {e}")
            return []
    
    def get_available_materials(self, client_id):
        """
        Obtiene materiales disponibles que aún no están asociados al cliente.
        
        Args:
            client_id (int): ID del cliente
            
        Returns:
            list: Lista de objetos Material disponibles
        """
        query = """
        SELECT * FROM materials 
        WHERE is_active = 1 AND id NOT IN (
            SELECT material_id FROM client_materials WHERE client_id = ?
        )
        ORDER BY name
        """
        
        try:
            results = self.db_manager.execute_query(query, (client_id,))
            return [Material.from_dict(row) for row in results]
        except Exception as e:
            print(f"Error al obtener materiales disponibles: {e}")
            return []
    
    def save_client_material(self, client_material):
        """
        Guarda la relación entre un cliente y un material.
        
        Args:
            client_material (ClientMaterial): Relación a guardar
            
        Returns:
            bool: True si se guardó correctamente
        """
        if client_material.id is None:
            return self._create_client_material(client_material)
        else:
            return self._update_client_material(client_material)
    
    def _create_client_material(self, client_material):
        """Crea una nueva relación cliente-material."""
        query = """
        INSERT INTO client_materials (client_id, material_id, price, includes_tax, notes)
        VALUES (?, ?, ?, ?, ?)
        """
        
        params = (
            client_material.client_id, client_material.material_id,
            client_material.price, client_material.includes_tax, client_material.notes
        )
        
        try:
            self.db_manager.execute_query(query, params)
            result = self.db_manager.execute_query("SELECT last_insert_rowid()")
            client_material.id = result[0][0] if result else None
            return True
        except Exception as e:
            print(f"Error al crear relación cliente-material: {e}")
            return False
    
    def _update_client_material(self, client_material):
        """Actualiza una relación cliente-material existente."""
        query = """
        UPDATE client_materials 
        SET price = ?, includes_tax = ?, notes = ?
        WHERE id = ?
        """
        
        params = (
            client_material.price, client_material.includes_tax, 
            client_material.notes, client_material.id
        )
        
        try:
            self.db_manager.execute_query(query, params)
            return True
        except Exception as e:
            print(f"Error al actualizar relación cliente-material: {e}")
            return False
    
    def delete_client_material(self, relation_id):
        """
        Elimina una relación cliente-material.
        
        Args:
            relation_id (int): ID de la relación a eliminar
            
        Returns:
            bool: True si se eliminó correctamente
        """
        query = "DELETE FROM client_materials WHERE id = ?"
        
        try:
            self.db_manager.execute_query(query, (relation_id,))
            return True
        except Exception as e:
            print(f"Error al eliminar relación cliente-material: {e}")
            return False