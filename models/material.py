"""
Modelo de datos para la entidad Material.
"""
from typing import List, Optional

class MaterialType:
    """Constantes para tipos de materiales"""
    PLASTIC = "plastic"
    CUSTOM = "custom"  # Tipo para materiales definidos por el usuario
    
    @classmethod
    def get_all_types(cls) -> List[str]:
        """Retorna todos los tipos de materiales disponibles"""
        return [cls.PLASTIC, cls.CUSTOM]
    
    @classmethod
    def get_display_name(cls, type_code: str) -> str:
        """Retorna el nombre para mostrar de un tipo de material"""
        display_names = {
            cls.PLASTIC: "Plástico",
            cls.CUSTOM: "Otro (Personalizado)"
        }
        return display_names.get(type_code, "Desconocido")

class PlasticSubtype:
    """Constantes para subtipos de plásticos"""
    CANDY = "candy"
    GUM = "gum"
    OTHER = "other"
    
    @classmethod
    def get_all_subtypes(cls) -> List[str]:
        """Retorna todos los subtipos de plásticos disponibles"""
        return [cls.CANDY, cls.GUM, cls.OTHER]
    
    @classmethod
    def get_display_name(cls, subtype_code: str) -> str:
        """Retorna el nombre para mostrar de un subtipo de plástico"""
        display_names = {
            cls.CANDY: "Caramelo",
            cls.GUM: "Chicle",
            cls.OTHER: "Otro"
        }
        return display_names.get(subtype_code, "Desconocido")

class Material:
    """Representación de un material en el sistema."""
    
    def __init__(self, id=None, name="", description="", material_type="", 
                 is_plastic_subtype=False, plastic_subtype="", 
                 plastic_state="", custom_subtype="", is_active=True):
        """
        Inicializa un nuevo material.
        
        Args:
            id (int, optional): ID único del material
            name (str): Nombre del material
            description (str): Descripción del material
            material_type (str): Tipo del material (de MaterialType)
            is_plastic_subtype (bool): Si es un subtipo de plástico
            plastic_subtype (str): Subtipo de plástico (de PlasticSubtype)
            plastic_state (str): Estado del plástico ('clean' o 'dirty')
            custom_subtype (str): Nombre personalizado si el subtipo es "other" o tipo es "custom"
            is_active (bool): Estado del material (activo/inactivo)
        """
        self.id = id
        self.name = name
        self.description = description
        self.material_type = material_type
        self.is_plastic_subtype = is_plastic_subtype
        self.plastic_subtype = plastic_subtype
        self.plastic_state = plastic_state  # 'clean' o 'dirty'
        self.custom_subtype = custom_subtype
        self.is_active = is_active
    
    def to_dict(self):
        """Convierte el material a un diccionario para almacenamiento."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'material_type': self.material_type,
            'is_plastic_subtype': self.is_plastic_subtype,
            'plastic_subtype': self.plastic_subtype,
            'plastic_state': self.plastic_state,
            'custom_subtype': self.custom_subtype,
            'is_active': self.is_active,
        }
    
    @classmethod
    def from_dict(cls, data):
        """
        Crea una instancia de Material desde un diccionario.
        
        Args:
            data (dict): Diccionario con datos del material
            
        Returns:
            Material: Nueva instancia de Material
        """
        return cls(
            id=data.get('id'),
            name=data.get('name', ''),
            description=data.get('description', ''),
            material_type=data.get('material_type', ''),
            is_plastic_subtype=bool(data.get('is_plastic_subtype', False)),
            plastic_subtype=data.get('plastic_subtype', ''),
            plastic_state=data.get('plastic_state', ''),
            custom_subtype=data.get('custom_subtype', ''),
            is_active=bool(data.get('is_active', True))
        )

    def get_full_name(self) -> str:
        """Retorna el nombre completo del material incluyendo subtipo y estado"""
        name = self.name
        
        if self.material_type == MaterialType.CUSTOM:
            return name  # Para materiales personalizados, solo mostrar el nombre
        
        if self.is_plastic_subtype:
            subtype_name = self.custom_subtype if self.plastic_subtype == PlasticSubtype.OTHER else PlasticSubtype.get_display_name(self.plastic_subtype)
            state = "Limpio" if self.plastic_state == "clean" else "Sucio"
            name = f"{name} ({subtype_name}, {state})"
        
        return name