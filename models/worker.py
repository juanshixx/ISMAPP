"""
Modelo de trabajador para ISMV3.
"""
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, Optional, List
from datetime import date


@dataclass
class Worker:
    """Clase que representa un trabajador en el sistema."""
    name: str
    document_id: str = ""  # DNI/NIE
    phone: str = ""
    address: str = ""
    active: bool = True
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    notes: str = ""
    payment_info: Dict[str, Any] = field(default_factory=dict)
    materials: List[str] = field(default_factory=list)
    id: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el objeto a un diccionario para almacenamiento."""
        data = asdict(self)
        # Convertir dates a string para almacenamiento
        if data['start_date'] is not None:
            data['start_date'] = data['start_date'].isoformat()
        if data['end_date'] is not None:
            data['end_date'] = data['end_date'].isoformat()
        
        # Eliminar ID si es None para permitir autoincremento en BD
        if data['id'] is None:
            del data['id']
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Worker':
        """Crea una instancia de Worker desde un diccionario."""
        # Copia del diccionario para no modificar el original
        worker_data = data.copy()
        
        # Convertir fechas de string a date si existen
        if 'start_date' in worker_data and worker_data['start_date']:
            if isinstance(worker_data['start_date'], str):
                worker_data['start_date'] = date.fromisoformat(worker_data['start_date'])
        
        if 'end_date' in worker_data and worker_data['end_date']:
            if isinstance(worker_data['end_date'], str):
                worker_data['end_date'] = date.fromisoformat(worker_data['end_date'])
        
        # Inicializar listas y diccionarios si no existen
        if 'payment_info' not in worker_data:
            worker_data['payment_info'] = {}
        
        if 'materials' not in worker_data:
            worker_data['materials'] = []
        
        # Filtrar solo las claves que corresponden a atributos de Worker
        valid_keys = cls.__dataclass_fields__.keys()
        filtered_data = {k: v for k, v in worker_data.items() if k in valid_keys}
        
        return cls(**filtered_data)