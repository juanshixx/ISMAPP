"""
Modelo de datos para la entidad Cliente.
"""

class ClientType:
    """Constantes para tipos de clientes"""
    BUYER = "buyer"
    SUPPLIER = "supplier"
    BOTH = "both"
    
    @classmethod
    def get_all_types(cls):
        """Retorna todos los tipos de clientes disponibles"""
        return [cls.BUYER, cls.SUPPLIER, cls.BOTH]
    
    @classmethod
    def get_display_name(cls, type_code):
        """Retorna el nombre para mostrar de un tipo de cliente"""
        display_names = {
            cls.BUYER: "Comprador",
            cls.SUPPLIER: "Proveedor",
            cls.BOTH: "Comprador y Proveedor"
        }
        return display_names.get(type_code, "Desconocido")

class Client:
    """Representación de un cliente en el sistema."""
    
    def __init__(self, id=None, name="", business_name="", rut="", address="", 
                 phone="", email="", contact_person="", notes="", is_active=True,
                 client_type=ClientType.BOTH):
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
            client_type (str): Tipo de cliente (comprador/proveedor/ambos)
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
        self.client_type = client_type
    
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
            'client_type': self.client_type,
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
            is_active=data.get('is_active', True),
            client_type=data.get('client_type', ClientType.BOTH)
        )

    def is_buyer(self):
        """Verifica si el cliente es comprador"""
        return self.client_type in [ClientType.BUYER, ClientType.BOTH]
        
    def is_supplier(self):
        """Verifica si el cliente es proveedor"""
        return self.client_type in [ClientType.SUPPLIER, ClientType.BOTH]