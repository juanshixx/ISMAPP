"""
Controlador para gestionar trabajadores en ISMV3.
"""
from typing import List, Dict, Any, Optional
from datetime import date, datetime

from models.worker import Worker
from core.database.data_manager import DataManager


class WorkerController:
    """Controlador para la gestión de trabajadores."""
    
    def __init__(self):
        """Inicializa el controlador de trabajadores."""
        self.data_manager = DataManager()
        self.entity_type = 'workers'
    
    def get_all_workers(self) -> List[Worker]:
        """
        Obtiene todos los trabajadores.
        
        Returns:
            List[Worker]: Lista de trabajadores.
        """
        worker_dicts = self.data_manager.get_all(self.entity_type)
        return [Worker.from_dict(worker_dict) for worker_dict in worker_dicts]
    
    def get_active_workers(self) -> List[Worker]:
        """
        Obtiene todos los trabajadores activos.
        
        Returns:
            List[Worker]: Lista de trabajadores activos.
        """
        all_workers = self.get_all_workers()
        return [worker for worker in all_workers if worker.active]
    
    def get_inactive_workers(self) -> List[Worker]:
        """
        Obtiene todos los trabajadores inactivos.
        
        Returns:
            List[Worker]: Lista de trabajadores inactivos.
        """
        all_workers = self.get_all_workers()
        return [worker for worker in all_workers if not worker.active]
    
    def get_worker(self, worker_id: int) -> Optional[Worker]:
        """
        Obtiene un trabajador por su ID.
        
        Args:
            worker_id (int): ID del trabajador.
            
        Returns:
            Optional[Worker]: Trabajador encontrado o None si no existe.
        """
        worker_dict = self.data_manager.get_by_id(self.entity_type, worker_id)
        if worker_dict:
            return Worker.from_dict(worker_dict)
        return None
    
    def get_worker_by_document(self, document_id: str) -> Optional[Worker]:
        """
        Obtiene un trabajador por su documento de identidad.
        
        Args:
            document_id (str): Documento de identidad (DNI/NIE).
            
        Returns:
            Optional[Worker]: Trabajador encontrado o None si no existe.
        """
        all_workers = self.get_all_workers()
        for worker in all_workers:
            if worker.document_id.lower() == document_id.lower():
                return worker
        return None
    
    def save_worker(self, worker: Worker) -> Worker:
        """
        Guarda un trabajador nuevo o actualiza uno existente.
        
        Args:
            worker (Worker): Trabajador a guardar.
            
        Returns:
            Worker: Trabajador guardado con ID actualizado.
        """
        worker_dict = worker.to_dict()
        if worker.id is not None:
            worker_dict['id'] = worker.id
            
        saved_dict = self.data_manager.save(self.entity_type, worker_dict)
        return Worker.from_dict(saved_dict)
    
    def delete_worker(self, worker_id: int) -> bool:
        """
        Elimina un trabajador.
        
        Args:
            worker_id (int): ID del trabajador a eliminar.
            
        Returns:
            bool: True si se eliminó correctamente.
        """
        return self.data_manager.delete(self.entity_type, worker_id)
    
    def search_workers(self, search_term: str) -> List[Worker]:
        """
        Busca trabajadores que coincidan con el término de búsqueda.
        
        Args:
            search_term (str): Término de búsqueda (nombre, documento, teléfono).
            
        Returns:
            List[Worker]: Lista de trabajadores que coinciden.
        """
        all_workers = self.get_all_workers()
        search_term = search_term.lower()
        
        return [
            worker for worker in all_workers 
            if (search_term in worker.name.lower() or 
                search_term in worker.document_id.lower() or 
                search_term in worker.phone.lower())
        ]
    
    def toggle_worker_status(self, worker_id: int) -> Optional[Worker]:
        """
        Cambia el estado de activo/inactivo de un trabajador.
        
        Args:
            worker_id (int): ID del trabajador.
            
        Returns:
            Optional[Worker]: Trabajador actualizado o None si no existe.
        """
        worker = self.get_worker(worker_id)
        if not worker:
            return None
            
        worker.active = not worker.active
        if not worker.active and worker.end_date is None:
            worker.end_date = date.today()
        elif worker.active and worker.end_date is not None:
            worker.end_date = None
            
        return self.save_worker(worker)
    
    def get_workers_by_material(self, material: str) -> List[Worker]:
        """
        Obtiene trabajadores que trabajan con un material específico.
        
        Args:
            material (str): Material de trabajo.
            
        Returns:
            List[Worker]: Trabajadores que trabajan con el material.
        """
        all_workers = self.get_all_workers()
        material = material.lower()
        
        return [
            worker for worker in all_workers 
            if any(mat.lower() == material for mat in worker.materials)
        ]