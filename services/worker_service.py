"""
Servicio para gestionar operaciones con trabajadores en ISMAPP.
"""
import logging
from models.worker import Worker, BankAccount

class WorkerService:
    """Servicio para operaciones relacionadas con trabajadores."""
    
    def __init__(self, data_manager):
        """
        Inicializa el servicio de trabajadores.
        
        Args:
            data_manager: Objeto DataManager para acceso a la base de datos
        """
        self.data_manager = data_manager
        self.logger = logging.getLogger(__name__)
    
    def get_all_workers(self):
        """
        Obtiene todos los trabajadores.
        
        Returns:
            list: Lista de objetos Worker
        """
        try:
            # Implementación simplificada que debe adaptarse a tu DataManager
            results = self.data_manager.execute_query("SELECT * FROM workers WHERE is_active = 1")
            
            workers = []
            for result in results:
                worker = self._create_worker_from_result(result)
                workers.append(worker)
                
            return workers
        except Exception as e:
            self.logger.error(f"Error al obtener trabajadores: {e}")
            return []
    
    def get_worker_by_id(self, worker_id):
        """
        Obtiene un trabajador por su ID.
        
        Args:
            worker_id: ID del trabajador
            
        Returns:
            Worker: Objeto trabajador o None si no se encuentra
        """
        try:
            results = self.data_manager.execute_query(
                "SELECT * FROM workers WHERE id = ? AND is_active = 1", 
                (worker_id,)
            )
            
            if results:
                return self._create_worker_from_result(results[0])
            return None
        except Exception as e:
            self.logger.error(f"Error al obtener trabajador #{worker_id}: {e}")
            return None
    
    def save_worker(self, worker):
        """
        Guarda o actualiza un trabajador.
        
        Args:
            worker: Objeto Worker a guardar
            
        Returns:
            bool: True si se guardó correctamente, False en caso contrario
        """
        try:
            if worker.id:
                # Actualizar trabajador existente
                query = """
                UPDATE workers SET 
                    name = ?, rut = ?, address = ?, phone = ?, email = ?,
                    position = ?, department = ?, contract_type = ?, hire_date = ?, salary = ?,
                    is_active = ?, notes = ?, bank_name = ?, account_type = ?,
                    account_number = ?, account_holder = ?, account_holder_rut = ?
                WHERE id = ?
                """
                self.data_manager.execute_query(
                    query,
                    (worker.name, worker.rut, worker.address, worker.phone, 
                     worker.email, worker.position, worker.department, worker.contract_type,
                     worker.hire_date, worker.salary, worker.is_active,
                     worker.notes, worker.bank_name, worker.account_type,
                     worker.account_number, worker.account_holder,
                     worker.account_holder_rut, worker.id)
                )
            else:
                # Insertar nuevo trabajador
                query = """
                INSERT INTO workers (
                    name, rut, address, phone, email, position, department,
                    contract_type, hire_date, salary, is_active, notes, bank_name, 
                    account_type, account_number, account_holder, account_holder_rut
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                result = self.data_manager.execute_query(
                    query,
                    (worker.name, worker.rut, worker.address, worker.phone, 
                     worker.email, worker.position, worker.department, worker.contract_type,
                     worker.hire_date, worker.salary, 1, worker.notes,
                     worker.bank_name, worker.account_type, worker.account_number,
                     worker.account_holder, worker.account_holder_rut),
                    get_last_id=True
                )
                
                # Obtener el ID asignado si la base de datos lo devuelve
                if isinstance(result, int):
                    worker.id = result
                
            return True
            
        except Exception as e:
            self.logger.error(f"Error al guardar trabajador: {e}")
            return False
    
    def delete_worker(self, worker_id):
        """
        Elimina un trabajador (marcándolo como inactivo).
        
        Args:
            worker_id: ID del trabajador a eliminar
            
        Returns:
            bool: True si se eliminó correctamente, False en caso contrario
        """
        try:
            # Marcar como inactivo en lugar de eliminar físicamente
            self.data_manager.execute_query(
                "UPDATE workers SET is_active = 0 WHERE id = ?",
                (worker_id,)
            )
            return True
            
        except Exception as e:
            self.logger.error(f"Error al eliminar trabajador #{worker_id}: {e}")
            return False
    
    def search_workers(self, search_term=None, department=None):
        """
        Busca trabajadores según criterios.
        
        Args:
            search_term: Término de búsqueda para nombre o RUT
            department: Filtrar por departamento
            
        Returns:
            list: Lista de trabajadores que coinciden con los criterios
        """
        try:
            query = "SELECT * FROM workers WHERE is_active = 1"
            params = []
            
            if search_term:
                query += " AND (name LIKE ? OR rut LIKE ? OR position LIKE ?)"
                term = f"%{search_term}%"
                params.extend([term, term, term])
                
            if department:
                query += " AND department = ?"
                params.append(department)
                
            results = self.data_manager.execute_query(query, tuple(params))
            
            workers = []
            for result in results:
                worker = self._create_worker_from_result(result)
                workers.append(worker)
                
            return workers
            
        except Exception as e:
            self.logger.error(f"Error al buscar trabajadores: {e}")
            return []
    
    def get_worker_bank_accounts(self, worker_id):
        """
        Obtiene las cuentas bancarias de un trabajador.
        
        Args:
            worker_id: ID del trabajador
            
        Returns:
            list: Lista de objetos BankAccount
        """
        try:
            results = self.data_manager.execute_query(
                "SELECT * FROM worker_bank_accounts WHERE worker_id = ?", 
                (worker_id,)
            )
            
            accounts = []
            for result in results:
                account = self._create_bank_account_from_result(result)
                accounts.append(account)
                
            return accounts
            
        except Exception as e:
            self.logger.error(f"Error al obtener cuentas bancarias del trabajador #{worker_id}: {e}")
            return []
    
    def save_bank_accounts(self, worker_id, accounts):
        """
        Guarda las cuentas bancarias de un trabajador.
        
        Args:
            worker_id: ID del trabajador
            accounts: Lista de objetos BankAccount
            
        Returns:
            bool: True si se guardó correctamente, False en caso contrario
        """
        try:
            # Eliminar cuentas existentes
            self.data_manager.execute_query(
                "DELETE FROM worker_bank_accounts WHERE worker_id = ?", 
                (worker_id,)
            )
            
            # Insertar nuevas cuentas
            for account in accounts:
                query = """
                INSERT INTO worker_bank_accounts (
                    worker_id, is_primary, bank_name, account_type,
                    account_number, account_holder, account_holder_rut
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """
                self.data_manager.execute_query(
                    query,
                    (worker_id, 1 if account.is_primary else 0, 
                     account.bank_name, account.account_type, account.account_number, 
                     account.account_holder, account.account_holder_rut)
                )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error al guardar cuentas bancarias del trabajador #{worker_id}: {e}")
            return False
    
    def _create_worker_from_result(self, result):
        """
        Crea un objeto Worker a partir de un resultado de consulta.
        
        Args:
            result: Resultado de la consulta (diccionario o tupla)
            
        Returns:
            Worker: Objeto trabajador
        """
        worker = Worker()
        
        # Si el resultado es un diccionario
        if isinstance(result, dict):
            for key, value in result.items():
                if hasattr(worker, key):
                    setattr(worker, key, value)
        # Si el resultado es una tupla/lista
        else:
            # Mapeo de índices de columnas (ajustar según estructura de la base de datos)
            columns = ['id', 'name', 'rut', 'address', 'phone', 'email', 
                      'position', 'department', 'contract_type', 'hire_date', 'salary', 
                      'is_active', 'notes', 'bank_name', 'account_type', 
                      'account_number', 'account_holder', 'account_holder_rut']
            
            for i, value in enumerate(result):
                if i < len(columns) and hasattr(worker, columns[i]):
                    setattr(worker, columns[i], value)
        
        return worker
    
    def _create_bank_account_from_result(self, result):
        """
        Crea un objeto BankAccount a partir de un resultado de consulta.
        
        Args:
            result: Resultado de la consulta (diccionario o tupla)
            
        Returns:
            BankAccount: Objeto cuenta bancaria
        """
        account = BankAccount()
        
        # Si el resultado es un diccionario
        if isinstance(result, dict):
            for key, value in result.items():
                if hasattr(account, key):
                    # Convertir is_primary de 0/1 a False/True
                    if key == 'is_primary':
                        setattr(account, key, bool(value))
                    else:
                        setattr(account, key, value)
        # Si el resultado es una tupla/lista
        else:
            # Mapeo de índices de columnas (ajustar según estructura de la base de datos)
            columns = ['id', 'worker_id', 'is_primary', 'bank_name', 'account_type',
                      'account_number', 'account_holder', 'account_holder_rut']
            
            for i, value in enumerate(result):
                if i < len(columns) and hasattr(account, columns[i]):
                    # Convertir is_primary de 0/1 a False/True
                    if columns[i] == 'is_primary':
                        setattr(account, columns[i], bool(value))
                    else:
                        setattr(account, columns[i], value)
        
        return account