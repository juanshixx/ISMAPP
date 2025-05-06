"""
Controlador para gestionar usuarios en ISMV3.
"""
import os
import json
import hashlib
from typing import List, Dict, Any, Optional

from models.user import User


class UserController:
    """Controlador para la gestión de usuarios."""
    
    def __init__(self):
        """Inicializa el controlador de usuarios."""
        self.users_file = os.path.join("data", "users.json")
        self._ensure_users_file()
    
    def _ensure_users_file(self):
        """Asegura que existe el archivo de usuarios con un admin por defecto."""
        os.makedirs(os.path.dirname(self.users_file), exist_ok=True)
        
        if not os.path.exists(self.users_file):
            # Crear archivo con usuario admin por defecto
            default_users = {
                "admin": {
                    "password": self._hash_password("admin"),  # Contraseña: admin
                    "name": "Administrador",
                    "role": "admin",
                    "is_active": True
                }
            }
            
            with open(self.users_file, 'w') as f:
                json.dump(default_users, f, indent=2)
    
    def _hash_password(self, password: str) -> str:
        """Aplica hash a una contraseña."""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def get_all_users(self) -> List[User]:
        """
        Obtiene todos los usuarios.
        
        Returns:
            List[User]: Lista de usuarios.
        """
        try:
            with open(self.users_file, 'r') as f:
                users_data = json.load(f)
            
            users = []
            for username, data in users_data.items():
                # Añadir username al diccionario
                user_data = data.copy()
                user_data['username'] = username
                # No incluir la contraseña en el objeto User
                if 'password' in user_data:
                    del user_data['password']
                users.append(User.from_dict(user_data))
            
            return users
        except Exception as e:
            print(f"Error al obtener usuarios: {e}")
            return []
    
    def get_user(self, username: str) -> Optional[User]:
        """
        Obtiene un usuario por su nombre de usuario.
        
        Args:
            username (str): Nombre de usuario.
            
        Returns:
            Optional[User]: Usuario encontrado o None si no existe.
        """
        try:
            with open(self.users_file, 'r') as f:
                users_data = json.load(f)
            
            if username in users_data:
                user_data = users_data[username].copy()
                user_data['username'] = username
                # No incluir la contraseña en el objeto User
                if 'password' in user_data:
                    del user_data['password']
                return User.from_dict(user_data)
            
            return None
        except Exception as e:
            print(f"Error al obtener usuario: {e}")
            return None
    
    def save_user(self, user: User, password: Optional[str] = None) -> bool:
        """
        Guarda un usuario nuevo o actualiza uno existente.
        
        Args:
            user (User): Usuario a guardar.
            password (Optional[str]): Contraseña en texto plano (solo para nuevos usuarios o cambios).
            
        Returns:
            bool: True si se guardó correctamente.
        """
        try:
            with open(self.users_file, 'r') as f:
                users_data = json.load(f)
            
            # Datos a guardar (sin incluir el nombre de usuario en el diccionario)
            user_dict = user.to_dict()
            username = user_dict.pop('username')
            
            if username in users_data:
                # Actualizar usuario existente
                # No sobrescribir la contraseña a menos que se proporcione una nueva
                if password is not None:
                    user_dict['password'] = self._hash_password(password)
                else:
                    # Mantener contraseña existente
                    user_dict['password'] = users_data[username]['password']
                
                users_data[username].update(user_dict)
            else:
                # Nuevo usuario
                if password is None:
                    # Contraseña requerida para nuevos usuarios
                    return False
                
                user_dict['password'] = self._hash_password(password)
                users_data[username] = user_dict
            
            # Guardar cambios
            with open(self.users_file, 'w') as f:
                json.dump(users_data, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error al guardar usuario: {e}")
            return False
    
    def delete_user(self, username: str) -> bool:
        """
        Elimina un usuario.
        
        Args:
            username (str): Nombre de usuario a eliminar.
            
        Returns:
            bool: True si se eliminó correctamente.
        """
        try:
            # No permitir eliminar el usuario admin
            if username == "admin":
                return False
            
            with open(self.users_file, 'r') as f:
                users_data = json.load(f)
            
            if username in users_data:
                del users_data[username]
                
                with open(self.users_file, 'w') as f:
                    json.dump(users_data, f, indent=2)
                
                return True
            
            return False
        except Exception as e:
            print(f"Error al eliminar usuario: {e}")
            return False
    
    def change_password(self, username: str, old_password: str, new_password: str) -> bool:
        """
        Cambia la contraseña de un usuario.
        
        Args:
            username (str): Nombre de usuario.
            old_password (str): Contraseña actual.
            new_password (str): Nueva contraseña.
            
        Returns:
            bool: True si se cambió correctamente.
        """
        try:
            with open(self.users_file, 'r') as f:
                users_data = json.load(f)
            
            if username in users_data:
                user_data = users_data[username]
                
                # Verificar contraseña actual
                if user_data['password'] == self._hash_password(old_password):
                    user_data['password'] = self._hash_password(new_password)
                    
                    with open(self.users_file, 'w') as f:
                        json.dump(users_data, f, indent=2)
                    
                    return True
            
            return False
        except Exception as e:
            print(f"Error al cambiar contraseña: {e}")
            return False
    
    def authenticate(self, username: str, password: str) -> Optional[User]:
        """
        Autentica un usuario con sus credenciales.
        
        Args:
            username (str): Nombre de usuario.
            password (str): Contraseña.
            
        Returns:
            Optional[User]: Usuario autenticado o None si falló.
        """
        try:
            with open(self.users_file, 'r') as f:
                users_data = json.load(f)
            
            if username in users_data:
                user_data = users_data[username]
                
                if (user_data.get('is_active', True) and 
                    user_data['password'] == self._hash_password(password)):
                    
                    # Crear objeto User (sin contraseña)
                    user_dict = user_data.copy()
                    user_dict['username'] = username
                    if 'password' in user_dict:
                        del user_dict['password']
                    
                    return User.from_dict(user_dict)
            
            return None
        except Exception as e:
            print(f"Error al autenticar usuario: {e}")
            return None