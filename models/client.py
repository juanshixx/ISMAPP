"""
Modelo de datos para la entidad Cliente.
"""

class Client:
    """Representación de un cliente en el sistema."""
    
    def __init__(self, id=None, name="", business_name="", rut="", address="", 
                 phone="", email="", contact_person="", notes="", is_active=True):
        """
        Inicializa un nuevo cliente.
        
        Args:
            id (int, optional): ID único del cliente
            name (str): Nombre del cliente
            business_name (str): Razón social
            rut (str): RUT o identificación fiscal
            address (str): Dirección
            phone (str): Teléfono de contacto
            email (str): Correo electrónico
            contact_person (str): Persona de contacto
            notes (str): Notas adicionales
            is_active (bool): Estado del cliente (activo/inactivo)
        """
        self.id = id
        self.name = name
        self.business_name = business_name
        self.rut = rut
        self.address = address
        self.phone = phone
        self.email = email
        self.contact_person = contact_person
        self.notes = notes
        self.is_active = is_active
    
    def to_dict(self):
        """Convierte el cliente a un diccionario para almacenamiento."""
        return {
            'id': self.id,
            'name': self.name,
            'business_name': self.business_name,
            'rut': self.rut,
            'address': self.address,
            'phone': self.phone,
            'email': self.email,
            'contact_person': self.contact_person,
            'notes': self.notes,
            'is_active': self.is_active,
        }
    
    @classmethod
    def from_dict(cls, data):
        """
        Crea una instancia de Cliente desde un diccionario.
        
        Args:
            data (dict): Diccionario con datos del cliente
            
        Returns:
            Client: Nueva instancia de Cliente
        """
        return cls(
            id=data.get('id'),
            name=data.get('name', ''),
            business_name=data.get('business_name', ''),
            rut=data.get('rut', ''),
            address=data.get('address', ''),
            phone=data.get('phone', ''),
            email=data.get('email', ''),
            contact_person=data.get('contact_person', ''),
            notes=data.get('notes', ''),
            is_active=data.get('is_active', True)
        )