"""
Servicio para la gestión de materiales y relaciones cliente-material.
"""
from models.material import Material
from models.client_material import ClientMaterial

class MaterialService:
    """Servicio para operaciones con materiales."""
    
    def __init__(self, data_manager):
        """
        Inicializa el servicio de materiales.
        
        Args:
            data_manager: Gestor de base de datos
        """
        self.db_manager = data_manager
    
    def get_all_materials(self):
        """
        Obtiene todos los materiales activos.
        
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
            material_id (int): ID del material
            
        Returns:
            Material: Objeto material o None si no se encuentra
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
                # CORREGIDO: Acepta IDs iguales a 0
                result = self._create_material(material)
                if result is not False and result is not None:
                    material.id = result if result is not True else None
                    return True
                return False
            else:
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
            int/bool: ID del material creado o False si hay error
        """
        query = """
        INSERT INTO materials (name, description, material_type, is_plastic_subtype,
                            plastic_subtype, plastic_state, custom_subtype, is_active)
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
            # CORREGIDO: Aceptar ID=0 como válido
            result = self.db_manager.execute_query(query, params)
            
            # Si el resultado es un número (incluyendo 0) o True, la operación fue exitosa
            if result is True or result is not None:
                return result
            return False
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
        query = """
        UPDATE materials
        SET is_active = 0, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        """
        
        try:
            self.db_manager.execute_query(query, (material_id,))
            return True
        except Exception as e:
            print(f"Error al eliminar material: {e}")
            return False
    
    def assign_material_to_client(self, client_id, material_id, price=0.0, includes_tax=False, notes=""):
        """
        Asigna un material a un cliente con su precio específico.
        
        Args:
            client_id (int): ID del cliente
            material_id (int): ID del material
            price (float): Precio acordado para el material
            includes_tax (bool): Indica si el precio incluye impuestos
            notes (str): Notas adicionales
            
        Returns:
            bool: True si la asignación fue exitosa
        """
        query = """
        INSERT INTO client_materials (client_id, material_id, price, includes_tax, notes)
        VALUES (?, ?, ?, ?, ?)
        """
        
        params = (client_id, material_id, price, includes_tax, notes)
        
        try:
            # CORREGIDO: Manejo mejorado del resultado
            result = self.db_manager.execute_query(query, params)
            
            # Aceptar cualquier valor numérico, incluyendo 0
            # También aceptar True como éxito en caso de que no se devuelva ID
            return result is not False and result is not None
        except Exception as e:
            print(f"Error al crear relación cliente-material: {e}")
            return False
    
    def get_client_materials(self, client_id):
        """
        Obtiene los materiales asociados a un cliente.
        
        Args:
            client_id (int): ID del cliente
            
        Returns:
            list: Lista de objetos ClientMaterial
        """
        query = """
        SELECT cm.*, m.* FROM client_materials cm
        JOIN materials m ON cm.material_id = m.id
        WHERE cm.client_id = ?
        ORDER BY m.name
        """
        
        try:
            results = self.db_manager.execute_query(query, (client_id,))
            
            # IMPORTANTE: Un resultado vacío (lista vacía) es diferente a un error
            # Si results es None, hubo un error; si es [], simplemente no hay materiales
            if results is None:
                print("La consulta devolvió None")
                return []
                
            client_materials = []
            
            # Mapeo correcto de columnas evitando conflictos con nombres duplicados
            for row in results:
                try:
                    # Crear objeto Material
                    material = Material(
                        id=row.get('material_id', None),  # Usar material_id de client_materials
                        name=row.get('name', ''),
                        description=row.get('description', ''),
                        material_type=row.get('material_type', ''),
                        is_plastic_subtype=row.get('is_plastic_subtype', 0),
                        plastic_subtype=row.get('plastic_subtype', ''),
                        plastic_state=row.get('plastic_state', ''),
                        custom_subtype=row.get('custom_subtype', ''),
                        is_active=row.get('is_active', 1)
                    )
                    
                    # Crear objeto ClientMaterial
                    client_material = ClientMaterial(
                        id=row.get('id', None),
                        client_id=row.get('client_id', client_id),
                        material_id=row.get('material_id', material.id),
                        price=row.get('price', 0.0),
                        includes_tax=bool(row.get('includes_tax', 0)),
                        notes=row.get('notes', '')
                    )
                    client_material.material = material
                    
                    client_materials.append(client_material)
                except Exception as e:
                    print(f"Error procesando fila: {e}")
                    # Continuamos con el siguiente material en vez de fallar completamente
                    continue
                
            return client_materials
        except Exception as e:
            print(f"Error al obtener materiales del cliente: {e}")
            return []
    
    def update_client_material(self, client_material):
        """
        Actualiza la relación entre cliente y material.
        
        Args:
            client_material (ClientMaterial): Objeto con los datos a actualizar
            
        Returns:
            bool: True si la actualización fue exitosa
        """
        query = """
        UPDATE client_materials 
        SET price = ?, includes_tax = ?, notes = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        """
        
        params = (
            client_material.price,
            client_material.includes_tax,
            client_material.notes,
            client_material.id
        )
        
        try:
            self.db_manager.execute_query(query, params)
            return True
        except Exception as e:
            print(f"Error al actualizar relación cliente-material: {e}")
            return False
    
    def remove_material_from_client(self, client_material_id):
        """
        Elimina la relación entre cliente y material.
        
        Args:
            client_material_id (int): ID de la relación a eliminar
            
        Returns:
            bool: True si se eliminó correctamente
        """
        query = "DELETE FROM client_materials WHERE id = ?"
        
        try:
            self.db_manager.execute_query(query, (client_material_id,))
            return True
        except Exception as e:
            print(f"Error al eliminar relación cliente-material: {e}")
            return False
    
    def get_available_materials_for_client(self, client_id):
        """
        Obtiene los materiales que no están asignados a un cliente.
        
        Args:
            client_id (int): ID del cliente
            
        Returns:
            list: Lista de objetos Material
        """
        # CORRECCIÓN: Consulta mejorada para garantizar resultados correctos
        query = """
        SELECT * FROM materials
        WHERE is_active = 1 AND id NOT IN (
            SELECT material_id FROM client_materials WHERE client_id = ?
        )
        ORDER BY name
        """
        
        try:
            results = self.db_manager.execute_query(query, (client_id,))
            
            # DEPURACIÓN: Verificar resultados crudos
            print(f"DEBUG - get_available_materials_for_client({client_id}) devuelve {len(results) if results else 0} materiales")
            
            materials = []
            
            # Si no hay resultados o es None, devolver lista vacía
            if not results:
                print("DEBUG - No hay materiales disponibles para este cliente")
                return []
                
            # Procesar resultados
            for row in results:
                try:
                    material = Material.from_dict(row)
                    materials.append(material)
                except Exception as e:
                    print(f"ERROR al procesar material: {e}")
                    continue
                    
            return materials
        except Exception as e:
            print(f"Error al obtener materiales disponibles: {e}")
            return []