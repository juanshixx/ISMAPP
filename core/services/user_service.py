"""
Servicio para la gestión de usuarios del sistema.
"""
from models.user import User

class UserService:
    """Servicio para operaciones con usuarios."""
    
    def __init__(self, data_manager):
        """
        Inicializa el servicio de usuarios.
        
        Args:
            data_manager: Gestor de base de datos
        """
        self.db_manager = data_manager
    
    def authenticate(self, username, password):
        """
        Autentica al usuario.
        
        Args:
            username (str): Nombre de usuario
            password (str): Contraseña
            
        Returns:
            dict: Datos del usuario si la autenticación es exitosa, None en caso contrario
        """
        query = "SELECT * FROM users WHERE username = ? AND password = ? AND is_active = 1"
        
        try:
            results = self.db_manager.execute_query(query, (username, password))
            
            if results and len(results) > 0:
                return results[0]
            return None
        except Exception as e:
            print(f"Error de autenticación: {e}")
            return None
    
    def get_all_users(self):
        """
        Obtiene todos los usuarios.
        
        Returns:
            list: Lista de objetos User
        """
        query = "SELECT * FROM users ORDER BY username"
        
        try:
            results = self.db_manager.execute_query(query)
            users = []
            
            for row in results:
                user = User(
                    username=row.get('username', ''),
                    name=row.get('name', ''),
                    role=row.get('role', 'user'),
                    is_active=bool(row.get('is_active', 1))
                )
                # Asignar ID después para evitar errores de validación
                user.id = row.get('id')
                users.append(user)
                
            return users
        except Exception as e:
            print(f"Error al obtener usuarios: {e}")
            return []
    
    def get_user_by_id(self, user_id):
        """
        Obtiene un usuario por su ID.
        
        Args:
            user_id (int): ID del usuario
            
        Returns:
            User: Objeto usuario o None si no se encuentra
        """
        query = "SELECT * FROM users WHERE id = ?"
        
        try:
            results = self.db_manager.execute_query(query, (user_id,))
            if results:
                row = results[0]
                user = User(
                    username=row.get('username', ''),
                    name=row.get('name', ''),
                    role=row.get('role', 'user'),
                    is_active=bool(row.get('is_active', 1))
                )
                user.id = row.get('id')
                return user
            return None
        except Exception as e:
            print(f"Error al obtener usuario por ID: {e}")
            return None
    
    def save_user(self, user):
        """
        Guarda un usuario (nuevo o existente).
        
        Args:
            user (User): Usuario a guardar
            
        Returns:
            bool: True si se guardó correctamente
        """
        if user.id is None:
            return self._create_user(user)
        else:
            return self._update_user(user)
    
    def _create_user(self, user):
        """
        Crea un nuevo usuario.
        
        Args:
            user (User): Usuario a crear
            
        Returns:
            bool: True si se creó correctamente
        """
        query = """
        INSERT INTO users (username, password, name, role, is_active)
        VALUES (?, ?, ?, ?, ?)
        """
        
        # En un sistema real, la contraseña debería estar encriptada
        # Por simplicidad usamos una contraseña temporal
        default_password = "changeme"
        
        params = (
            user.username,
            default_password,
            user.name,
            user.role,
            user.is_active
        )
        
        try:
            result = self.db_manager.execute_query(query, params)
            if result is not False and result is not None:
                user.id = result if result is not True else None
                return True
            return False
        except Exception as e:
            print(f"Error al crear usuario: {e}")
            return False
    
    def _update_user(self, user):
        """
        Actualiza un usuario existente.
        
        Args:
            user (User): Usuario a actualizar
            
        Returns:
            bool: True si se actualizó correctamente
        """
        query = """
        UPDATE users 
        SET name = ?, role = ?, is_active = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        """
        
        params = (
            user.name,
            user.role,
            user.is_active,
            user.id
        )
        
        try:
            self.db_manager.execute_query(query, params)
            return True
        except Exception as e:
            print(f"Error al actualizar usuario: {e}")
            return False
    
    def change_password(self, user_id, new_password):
        """
        Cambia la contraseña de un usuario.
        
        Args:
            user_id (int): ID del usuario
            new_password (str): Nueva contraseña
            
        Returns:
            bool: True si se cambió correctamente
        """
        query = "UPDATE users SET password = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
        
        # En un sistema real, la contraseña debería estar encriptada
        
        try:
            self.db_manager.execute_query(query, (new_password, user_id))
            return True
        except Exception as e:
            print(f"Error al cambiar contraseña: {e}")
            return False
    
    def delete_user(self, user_id):
        """
        Elimina un usuario de forma lógica.
        
        Args:
            user_id (int): ID del usuario a eliminar
            
        Returns:
            bool: True si se eliminó correctamente
        """
        query = "UPDATE users SET is_active = 0, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
        
        try:
            self.db_manager.execute_query(query, (user_id,))
            return True
        except Exception as e:
            print(f"Error al eliminar usuario: {e}")
            return False