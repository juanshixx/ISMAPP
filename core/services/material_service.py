"""
Servicio para la gestión de materiales.
"""
from models.material import Material

class MaterialService:
    """Servicio para operaciones CRUD de materiales."""
    
    def __init__(self, data_manager):
        """
        Inicializa el servicio de materiales.
        
        Args:
            data_manager: Gestor de base de datos
        """
        self.db_manager = data_manager
    
    def get_all_materials(self):
        """
        Obtiene todos los materiales.
        
        Returns:
            list: Lista de objetos Material
        """
        query = "SELECT * FROM materials WHERE is_active = 1 ORDER BY name"
        
        try:
            results = self.db_manager.execute_query(query)
            materials = []
            
            for row in results:
                material = Material.from_dict(row)
                materials.append(material)
                
            return materials
        except Exception as e:
            print(f"Error al obtener materiales: {e}")
            return []
    
    def get_material_by_id(self, material_id):
        """
        Obtiene un material por su ID.
        
        Args:
            material_id (int): ID del material a buscar
            
        Returns:
            Material: Objeto material si se encuentra, None en otro caso
        """
        query = "SELECT * FROM materials WHERE id = ?"
        
        try:
            results = self.db_manager.execute_query(query, (material_id,))
            
            if results:
                return Material.from_dict(results[0])
            return None
        except Exception as e:
            print(f"Error al obtener material por ID: {e}")
            return None
    
    def save_material(self, material):
        """
        Guarda un material (nuevo o existente).
        
        Args:
            material (Material): Material a guardar
            
        Returns:
            bool: True si se guardó correctamente
        """
        try:
            if material.id is None:
                # Crear nuevo material
                return self._create_material(material)
            else:
                # Actualizar material existente
                return self._update_material(material)
        except Exception as e:
            print(f"Error al guardar material: {e}")
            return False
    
    def _create_material(self, material):
        """
        Crea un nuevo material en la base de datos.
        
        Args:
            material (Material): Material a crear
            
        Returns:
            bool: True si se creó correctamente
        """
        query = """
        INSERT INTO materials (name, description, material_type, 
                              is_plastic_subtype, plastic_subtype, 
                              plastic_state, custom_subtype, is_active)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        params = (
            material.name, 
            material.description, 
            material.material_type,
            material.is_plastic_subtype, 
            material.plastic_subtype, 
            material.plastic_state, 
            material.custom_subtype,
            material.is_active
        )
        
        try:
            result = self.db_manager.execute_query(query, params)
            material.id = result
            return True
        except Exception as e:
            print(f"Error al crear material: {e}")
            return False
    
    def _update_material(self, material):
        """
        Actualiza un material existente.
        
        Args:
            material (Material): Material a actualizar
            
        Returns:
            bool: True si se actualizó correctamente
        """
        query = """
        UPDATE materials 
        SET name = ?, 
            description = ?, 
            material_type = ?, 
            is_plastic_subtype = ?, 
            plastic_subtype = ?, 
            plastic_state = ?, 
            custom_subtype = ?, 
            is_active = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        """
        
        params = (
            material.name, 
            material.description, 
            material.material_type,
            material.is_plastic_subtype, 
            material.plastic_subtype, 
            material.plastic_state, 
            material.custom_subtype,
            material.is_active,
            material.id
        )
        
        try:
            self.db_manager.execute_query(query, params)
            return True
        except Exception as e:
            print(f"Error al actualizar material: {e}")
            return False
    
    def delete_material(self, material_id):
        """
        Elimina un material de forma lógica.
        
        Args:
            material_id (int): ID del material a eliminar
            
        Returns:
            bool: True si se eliminó correctamente
        """
        # Verificar si el material está siendo usado en alguna relación
        check_query = "SELECT COUNT(*) as count FROM client_materials WHERE material_id = ?"
        
        try:
            result = self.db_manager.execute_query(check_query, (material_id,))
            if result and result[0]["count"] > 0:
                # Material está en uso, marcarlo como inactivo en lugar de eliminarlo
                update_query = "UPDATE materials SET is_active = 0, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
                self.db_manager.execute_query(update_query, (material_id,))
            else:
                # Material no está en uso, eliminarlo físicamente
                delete_query = "DELETE FROM materials WHERE id = ?"
                self.db_manager.execute_query(delete_query, (material_id,))
                
            return True
        except Exception as e:
            print(f"Error al eliminar material: {e}")
            return False