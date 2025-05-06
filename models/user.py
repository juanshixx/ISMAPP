"""
Modelo de usuario para ISMV3.
"""
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, Optional, List


@dataclass
class User:
    """Clase que representa un usuario en el sistema."""
    username: str
    name: str
    role: str = "user"  # Roles: admin, user
    permissions: List[str] = field(default_factory=list)
    is_active: bool = True
    id: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el objeto a un diccionario para almacenamiento."""
        data = asdict(self)
        # Eliminar ID si es None para permitir autoincremento en BD
        if data['id'] is None:
            del data['id']
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """Crea una instancia de User desde un diccionario."""
        # Filtrar solo las claves que corresponden a atributos de User
        valid_keys = cls.__dataclass_fields__.keys()
        filtered_data = {k: v for k, v in data.items() if k in valid_keys}
        return cls(**filtered_data)
    
    def has_permission(self, permission: str) -> bool:
        """
        Verifica si el usuario tiene un permiso específico.
        
        Args:
            permission: Permiso a verificar.
            
        Returns:
            bool: True si el usuario tiene el permiso.
        """
        # Los admin tienen todos los permisos
        if self.role == "admin":
            return True
        
        return permission in self.permissions