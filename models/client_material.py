"""
Modelo de datos para la relación entre Cliente y Material.
"""

class ClientMaterial:
    """Representación de la relación entre un cliente y un material, incluyendo precio."""
    
    def __init__(self, id=None, client_id=None, material_id=None, price=0.0, 
                 includes_tax=False, notes=""):
        """
        Inicializa una nueva relación cliente-material.
        
        Args:
            id (int, optional): ID único de la relación
            client_id (int): ID del cliente
            material_id (int): ID del material
            price (float): Precio del material para este cliente
            includes_tax (bool): Si el precio incluye IVA
            notes (str): Notas adicionales
        """
        self.id = id
        self.client_id = client_id
        self.material_id = material_id
        self.price = price
        self.includes_tax = includes_tax
        self.notes = notes
    
    def to_dict(self):
        """Convierte la relación a un diccionario para almacenamiento."""
        return {
            'id': self.id,
            'client_id': self.client_id,
            'material_id': self.material_id,
            'price': self.price,
            'includes_tax': self.includes_tax,
            'notes': self.notes,
        }
    
    @classmethod
    def from_dict(cls, data):
        """
        Crea una instancia de ClientMaterial desde un diccionario.
        
        Args:
            data (dict): Diccionario con datos de la relación
            
        Returns:
            ClientMaterial: Nueva instancia de ClientMaterial
        """
        return cls(
            id=data.get('id'),
            client_id=data.get('client_id'),
            material_id=data.get('material_id'),
            price=float(data.get('price', 0.0)),
            includes_tax=bool(data.get('includes_tax', False)),
            notes=data.get('notes', '')
        )