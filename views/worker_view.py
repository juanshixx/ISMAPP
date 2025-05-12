"""
Vista para la gestión de trabajadores en ISMAPP.
"""
import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
from models.worker import Worker, BankAccount
from datetime import datetime, date

class WorkerView(ctk.CTkFrame):
    """Vista para la gestión de trabajadores."""
    
    def __init__(self, parent):
        """
        Inicializa la vista de trabajadores.
        
        Args:
            parent: Frame contenedor
        """
        super().__init__(parent)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Obtener referencias a servicios desde ventana principal
        main_window = self.winfo_toplevel()
        try:
            self.worker_service = main_window.services.get("WorkerService")
        except AttributeError:
            messagebox.showerror("Error", "No se pudo acceder a los servicios necesarios")
            return
        
        # Variables para control
        self.workers = []
        self.current_worker = None
        self.departments = ["Administración", "Operaciones", "Ventas", "Producción", "Logística", "Otro"]
        self.contract_types = ["Contrato Indefinido", "Contrato a Plazo Fijo", "Por Día", "Por Producción", "Honorarios", "Otro"]
        self.bank_accounts = []  # Lista para almacenar las cuentas bancarias del trabajador actual
        
        # Crear UI
        self._create_ui()
        
        # Cargar datos iniciales
        self._load_workers()
    
    def _create_ui(self):
        """Crea la interfaz de usuario."""
        # Usar ttk.PanedWindow para dividir la pantalla
        self.split_view = ttk.PanedWindow(self, orient="horizontal")
        self.split_view.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # Panel izquierdo (lista de trabajadores)
        self.left_panel = ctk.CTkFrame(self)
        self.left_panel.grid_rowconfigure(2, weight=1)
        self.left_panel.grid_columnconfigure(0, weight=1)
        
        # Panel derecho (detalle del trabajador)
        self.right_panel = ctk.CTkFrame(self)
        self.right_panel.grid_rowconfigure(0, weight=1)
        self.right_panel.grid_columnconfigure(0, weight=1)
        
        # Añadir paneles a PanedWindow
        self.split_view.add(self.left_panel, weight=1)
        self.split_view.add(self.right_panel, weight=2)
        
        # Crear componentes del panel izquierdo
        self._create_left_panel()
        
        # Crear componentes del panel derecho
        self._create_right_panel()
    
    def _create_left_panel(self):
        """Configura el panel izquierdo con la lista de trabajadores."""
        # Header con título y botón de nuevo trabajador
        header_frame = ctk.CTkFrame(self.left_panel, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        ctk.CTkLabel(
            header_frame,
            text="Trabajadores",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(side="left")
        
        # Botón para crear nuevo trabajador
        ctk.CTkButton(
            header_frame,
            text="+ Nuevo",
            command=self._create_worker,
            width=100
        ).pack(side="right")
        
        # Frame para filtros y búsqueda
        filter_frame = ctk.CTkFrame(self.left_panel)
        filter_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        filter_frame.grid_columnconfigure(1, weight=1)
        
        # Combobox para filtrar por departamento
        self.filter_var = tk.StringVar(value="Todos")
        department_filters = ["Todos"] + self.departments
        
        ctk.CTkLabel(filter_frame, text="Departamento:").grid(row=0, column=0, padx=5, pady=5)
        
        dept_filter = ctk.CTkComboBox(
            filter_frame,
            values=department_filters,
            variable=self.filter_var,
            state="readonly",
            width=150
        )
        dept_filter.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        dept_filter.bind("<<ComboboxSelected>>", self._apply_filter)
        
        # Campo de búsqueda
        search_frame = ctk.CTkFrame(filter_frame, fg_color="transparent")
        search_frame.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        search_frame.grid_columnconfigure(0, weight=1)
        
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self._apply_filter)
        
        search_entry = ctk.CTkEntry(
            search_frame, 
            placeholder_text="Buscar por nombre, RUT o cargo...",
            textvariable=self.search_var
        )
        search_entry.grid(row=0, column=0, sticky="ew")
        
        ctk.CTkButton(
            search_frame,
            text="🔍",
            width=30,
            command=self._apply_filter
        ).grid(row=0, column=1, padx=(5, 0))
        
        # Lista de trabajadores con scroll
        self.workers_frame = ctk.CTkScrollableFrame(self.left_panel)
        self.workers_frame.grid(row=2, column=0, sticky="nsew", pady=(10, 0))
    
    def _create_right_panel(self):
        """Configura el panel derecho con los detalles del trabajador."""
        # Crear notebook/pestañas
        self.tabs = ctk.CTkTabview(self.right_panel)
        self.tabs.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        # Añadir pestañas
        self.tabs.add("Información Personal")
        self.tabs.add("Datos Laborales")
        self.tabs.add("Cuentas Bancarias")
        
        # Configurar pestañas
        self._setup_personal_tab(self.tabs.tab("Información Personal"))
        self._setup_employment_tab(self.tabs.tab("Datos Laborales"))
        self._setup_banking_tab(self.tabs.tab("Cuentas Bancarias"))
    
    def _setup_personal_tab(self, parent):
        """Configura la pestaña de información personal."""
        # Panel con scroll
        personal_scroll = ctk.CTkScrollableFrame(parent)
        personal_scroll.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Contenedor del formulario
        form_frame = ctk.CTkFrame(personal_scroll, fg_color="transparent")
        form_frame.pack(fill="x", expand=True, pady=10)
        
        # Crear variables para el formulario
        self.form_vars = {
            "name": tk.StringVar(),
            "rut": tk.StringVar(),
            "address": tk.StringVar(),
            "phone": tk.StringVar(),
            "email": tk.StringVar(),
            "position": tk.StringVar(),
            "department": tk.StringVar(),
            "contract_type": tk.StringVar(),  # NUEVO: Variable para tipo de contrato
            "hire_date": tk.StringVar(),
            "salary": tk.StringVar(),
            "notes": tk.StringVar(),
        }
        
        # Nombre del trabajador
        ctk.CTkLabel(form_frame, text="Nombre completo:").grid(row=0, column=0, sticky="w", pady=(10, 0))
        self.name_entry = ctk.CTkEntry(form_frame, textvariable=self.form_vars["name"], width=300)
        self.name_entry.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        
        # RUT
        ctk.CTkLabel(form_frame, text="RUT:").grid(row=2, column=0, sticky="w", pady=(10, 0))
        ctk.CTkEntry(form_frame, textvariable=self.form_vars["rut"]).grid(row=3, column=0, sticky="ew", pady=(0, 10))
        
        # Dirección
        ctk.CTkLabel(form_frame, text="Dirección:").grid(row=4, column=0, sticky="w", pady=(10, 0))
        ctk.CTkEntry(form_frame, textvariable=self.form_vars["address"]).grid(row=5, column=0, sticky="ew", pady=(0, 10))
        
        # Teléfono
        ctk.CTkLabel(form_frame, text="Teléfono:").grid(row=6, column=0, sticky="w", pady=(10, 0))
        ctk.CTkEntry(form_frame, textvariable=self.form_vars["phone"]).grid(row=7, column=0, sticky="ew", pady=(0, 10))
        
        # Email
        ctk.CTkLabel(form_frame, text="Email:").grid(row=8, column=0, sticky="w", pady=(10, 0))
        ctk.CTkEntry(form_frame, textvariable=self.form_vars["email"]).grid(row=9, column=0, sticky="ew", pady=(0, 10))
        
        # Notas
        ctk.CTkLabel(form_frame, text="Notas personales:").grid(row=10, column=0, sticky="w", pady=(10, 0))
        ctk.CTkEntry(form_frame, textvariable=self.form_vars["notes"], height=60).grid(row=11, column=0, sticky="ew", pady=(0, 10))
        
        # Botones de acción
        btn_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        btn_frame.grid(row=12, column=0, sticky="ew", pady=20)
        
        self.save_btn = ctk.CTkButton(
            btn_frame,
            text="Guardar",
            command=self._save_worker,
            state="disabled",
            font=ctk.CTkFont(weight="bold")
        )
        self.save_btn.pack(side="right", padx=5)
        
        self.delete_btn = ctk.CTkButton(
            btn_frame,
            text="Eliminar",
            command=self._delete_worker,
            fg_color="#E76F51",
            state="disabled"
        )
        self.delete_btn.pack(side="right", padx=5)
        
        # Expandir columnas para llenar el espacio horizontal
        form_frame.columnconfigure(0, weight=1)
    
    def _setup_employment_tab(self, parent):
        """Configura la pestaña de datos laborales."""
        # Panel con scroll
        labor_scroll = ctk.CTkScrollableFrame(parent)
        labor_scroll.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Contenedor del formulario
        form_frame = ctk.CTkFrame(labor_scroll, fg_color="transparent")
        form_frame.pack(fill="x", expand=True, pady=10)
        
        # Cargo
        ctk.CTkLabel(form_frame, text="Cargo:").grid(row=0, column=0, sticky="w", pady=(10, 0))
        ctk.CTkEntry(form_frame, textvariable=self.form_vars["position"], width=300).grid(row=1, column=0, sticky="ew", pady=(0, 10))
        
        # Departamento
        ctk.CTkLabel(form_frame, text="Departamento:").grid(row=2, column=0, sticky="w", pady=(10, 0))
        dept_combobox = ctk.CTkComboBox(
            form_frame,
            values=self.departments,
            variable=self.form_vars["department"],
            width=300
        )
        dept_combobox.grid(row=3, column=0, sticky="ew", pady=(0, 10))
        
        # NUEVO: Tipo de contrato
        ctk.CTkLabel(form_frame, text="Tipo de Contrato:").grid(row=4, column=0, sticky="w", pady=(10, 0))
        contract_combobox = ctk.CTkComboBox(
            form_frame,
            values=self.contract_types,
            variable=self.form_vars["contract_type"],
            width=300
        )
        contract_combobox.grid(row=5, column=0, sticky="ew", pady=(0, 10))
        
        # Fecha de contratación
        ctk.CTkLabel(form_frame, text="Fecha de contratación (YYYY-MM-DD):").grid(row=6, column=0, sticky="w", pady=(10, 0))
        
        date_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        date_frame.grid(row=7, column=0, sticky="ew", pady=(0, 10))
        
        hire_date_entry = ctk.CTkEntry(date_frame, textvariable=self.form_vars["hire_date"], width=150)
        hire_date_entry.pack(side="left")
        
        # Botón para establecer fecha actual
        def set_current_date():
            self.form_vars["hire_date"].set(date.today().strftime("%Y-%m-%d"))
            
        ctk.CTkButton(
            date_frame, 
            text="Hoy",
            command=set_current_date,
            width=60
        ).pack(side="left", padx=(10, 0))
        
        # Salario
        ctk.CTkLabel(form_frame, text="Salario/Remuneración:").grid(row=8, column=0, sticky="w", pady=(10, 0))
        
        salary_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        salary_frame.grid(row=9, column=0, sticky="ew", pady=(0, 10))
        
        ctk.CTkLabel(salary_frame, text="$").pack(side="left")
        
        ctk.CTkEntry(
            salary_frame, 
            textvariable=self.form_vars["salary"], 
            width=150
        ).pack(side="left", padx=(5, 10))
        
        ctk.CTkLabel(salary_frame, text="CLP").pack(side="left")
        
        # Botones de acción para guardar datos laborales
        btn_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        btn_frame.grid(row=10, column=0, sticky="ew", pady=20)
        
        self.save_employment_btn = ctk.CTkButton(
            btn_frame,
            text="Guardar Datos Laborales",
            command=self._save_employment_data,
            state="disabled",
            font=ctk.CTkFont(weight="bold")
        )
        self.save_employment_btn.pack(side="right", padx=5)
        
        # Expandir columnas
        form_frame.columnconfigure(0, weight=1)
    
    def _setup_banking_tab(self, parent):
        """Configura la pestaña de cuentas bancarias."""
        # Panel de datos bancarios con scroll
        banking_scroll = ctk.CTkScrollableFrame(parent)
        banking_scroll.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Título y botón para añadir cuenta
        header_frame = ctk.CTkFrame(banking_scroll, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(
            header_frame,
            text="Cuentas Bancarias",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(side="left")
        
        # NUEVO: Botón para añadir nueva cuenta bancaria
        self.add_account_btn = ctk.CTkButton(
            header_frame,
            text="+ Añadir Cuenta",
            command=self._add_bank_account,
            state="disabled",
            width=120
        )
        self.add_account_btn.pack(side="right")
        
        # Frame para la lista de cuentas
        self.accounts_list_frame = ctk.CTkFrame(banking_scroll)
        self.accounts_list_frame.pack(fill="x", expand=True, pady=10)
        
        # Mensaje cuando no hay cuentas
        self.no_accounts_label = ctk.CTkLabel(
            self.accounts_list_frame,
            text="No hay cuentas bancarias registradas",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        self.no_accounts_label.pack(pady=30)
        
        # Nota informativa
        note_frame = ctk.CTkFrame(banking_scroll, fg_color=("gray90", "gray20"))
        note_frame.pack(fill="x", expand=True, pady=20)
        
        ctk.CTkLabel(
            note_frame,
            text="Importante: Los datos bancarios se utilizarán exclusivamente para el pago de remuneraciones y otros beneficios laborales.",
            font=ctk.CTkFont(size=12),
            wraplength=450,
            text_color=("gray40", "gray80")
        ).pack(padx=10, pady=10)
    
    def _load_workers(self):
        """Carga la lista de trabajadores desde la base de datos."""
        self.workers = self.worker_service.get_all_workers()
        self._update_workers_list()
    
    def _update_workers_list(self):
        """Actualiza la lista visual de trabajadores según filtros."""
        # Limpiar lista actual
        for widget in self.workers_frame.winfo_children():
            widget.destroy()
            
        # Obtener filtros
        search_term = self.search_var.get().lower()
        filter_dept = self.filter_var.get()
        if filter_dept == "Todos":
            filter_dept = None
            
        # Filtrar trabajadores
        filtered_workers = self.workers
        
        # Aplicar filtro de departamento si está seleccionado
        if filter_dept:
            filtered_workers = [w for w in filtered_workers if w.department == filter_dept]
            
        # Aplicar filtro de búsqueda
        if search_term:
            filtered_workers = [
                w for w in filtered_workers 
                if search_term in w.name.lower() or 
                   (w.rut and search_term in w.rut.lower()) or
                   (w.position and search_term in w.position.lower())
            ]
        
        # Mostrar mensaje si no hay trabajadores
        if not filtered_workers:
            no_results = ctk.CTkLabel(
                self.workers_frame,
                text="No se encontraron trabajadores",
                font=ctk.CTkFont(size=14),
                text_color="gray"
            )
            no_results.pack(pady=20)
            return
        
        # Crear elementos visuales para cada trabajador
        for i, worker in enumerate(filtered_workers):
            # Crear frame para el trabajador
            worker_frame = ctk.CTkFrame(self.workers_frame)
            worker_frame.pack(fill="x", pady=2)
            
            # Al hacer clic, seleccionar el trabajador
            worker_frame.bind("<Button-1>", lambda e, w=worker: self._select_worker(w))
            
            # Nombre del trabajador
            name_label = ctk.CTkLabel(
                worker_frame,
                text=worker.name,
                font=ctk.CTkFont(weight="bold")
            )
            name_label.bind("<Button-1>", lambda e, w=worker: self._select_worker(w))
            name_label.pack(anchor="w", pady=(5, 0), padx=10)
            
            # Cargo y departamento
            info_frame = ctk.CTkFrame(worker_frame, fg_color="transparent")
            info_frame.pack(fill="x", padx=10, pady=(0, 5))
            
            position_text = worker.position if worker.position else ""
            if worker.department:
                if position_text:
                    position_text += f" - {worker.department}"
                else:
                    position_text = worker.department
                    
            position_label = ctk.CTkLabel(
                info_frame,
                text=position_text,
                font=ctk.CTkFont(size=12)
            )
            position_label.bind("<Button-1>", lambda e, w=worker: self._select_worker(w))
            position_label.pack(side="left")
            
            # RUT
            rut_label = ctk.CTkLabel(
                info_frame,
                text=f"RUT: {worker.rut}" if worker.rut else "",
                font=ctk.CTkFont(size=12),
                text_color="gray50"
            )
            rut_label.bind("<Button-1>", lambda e, w=worker: self._select_worker(w))
            rut_label.pack(side="right")
    
    def _apply_filter(self, *args):
        """Aplica los filtros de búsqueda."""
        self._update_workers_list()
    
    def _select_worker(self, worker):
        """
        Selecciona un trabajador y muestra sus detalles.
        
        Args:
            worker: Objeto Worker a seleccionar
        """
        self.current_worker = worker
        
        # Rellenar formulario con datos del trabajador
        self.form_vars["name"].set(worker.name)
        self.form_vars["rut"].set(worker.rut or "")
        self.form_vars["address"].set(worker.address or "")
        self.form_vars["phone"].set(worker.phone or "")
        self.form_vars["email"].set(worker.email or "")
        self.form_vars["position"].set(worker.position or "")
        self.form_vars["department"].set(worker.department or "")
        self.form_vars["contract_type"].set(worker.contract_type or "")  # NUEVO: Cargar tipo de contrato
        self.form_vars["notes"].set(worker.notes or "")
        
        # Formatear fecha de contratación si existe
        if worker.hire_date:
            self.form_vars["hire_date"].set(worker.hire_date.strftime("%Y-%m-%d"))
        else:
            self.form_vars["hire_date"].set("")
        
        # Formatear salario si existe
        if worker.salary:
            self.form_vars["salary"].set(str(int(worker.salary)))
        else:
            self.form_vars["salary"].set("")
        
        # Cargar cuentas bancarias
        self._load_bank_accounts(worker)
        
        # Activar botones de guardar y eliminar
        self.save_btn.configure(state="normal")
        self.delete_btn.configure(state="normal")
        self.save_employment_btn.configure(state="normal")
        self.add_account_btn.configure(state="normal")
        
        # Cambiar a la pestaña de información personal
        self.tabs.set("Información Personal")
    
    def _create_worker(self):
        """Resetea el formulario para crear un nuevo trabajador."""
        self.current_worker = None
        
        # Limpiar formulario
        for var in self.form_vars.values():
            var.set("")
        
        # Limpiar cuentas bancarias
        self._load_bank_accounts(None)
        
        # Activar botón guardar y desactivar botón eliminar
        self.save_btn.configure(state="normal")
        self.delete_btn.configure(state="disabled")
        self.save_employment_btn.configure(state="disabled")
        self.add_account_btn.configure(state="disabled")
        
        # Cambiar a pestaña de información personal
        self.tabs.set("Información Personal")
        
        # Dar foco al campo de nombre
        self.name_entry.focus_set()
    
    def _save_worker(self):
        """Guarda los cambios del trabajador actual (información personal)."""
        # Validar campos requeridos
        if not self.form_vars["name"].get().strip():
            messagebox.showerror("Error", "El nombre es obligatorio")
            return
            
        if not self.form_vars["rut"].get().strip():
            messagebox.showerror("Error", "El RUT es obligatorio")
            return
        
        # Crear o actualizar el objeto trabajador
        if self.current_worker:
            # Actualizar trabajador existente
            worker = self.current_worker
        else:
            # Crear nuevo trabajador
            worker = Worker()
            
        # Actualizar propiedades básicas (información personal)
        worker.name = self.form_vars["name"].get().strip()
        worker.rut = self.form_vars["rut"].get().strip()
        worker.address = self.form_vars["address"].get().strip()
        worker.phone = self.form_vars["phone"].get().strip()
        worker.email = self.form_vars["email"].get().strip()
        worker.notes = self.form_vars["notes"].get().strip()
        worker.is_active = True
        
        # Mantener los datos existentes para otras pestañas
        if self.current_worker:
            worker.position = self.current_worker.position
            worker.department = self.current_worker.department
            worker.contract_type = self.current_worker.contract_type
            worker.hire_date = self.current_worker.hire_date
            worker.salary = self.current_worker.salary
            worker.bank_name = self.current_worker.bank_name
            worker.account_type = self.current_worker.account_type
            worker.account_number = self.current_worker.account_number
            worker.account_holder = self.current_worker.account_holder
            worker.account_holder_rut = self.current_worker.account_holder_rut
        
        # Guardar en base de datos
        success = self.worker_service.save_worker(worker)
        
        if success:
            action = "actualizado" if self.current_worker else "creado"
            messagebox.showinfo("Éxito", f"Trabajador {action} correctamente")
            
            # Actualizar trabajador actual
            self.current_worker = worker
            
            # Recargar lista de trabajadores
            self._load_workers()
            
            # Habilitar botones
            self.save_employment_btn.configure(state="normal")
            self.add_account_btn.configure(state="normal")
        else:
            messagebox.showerror("Error", "Error al guardar el trabajador")
    
    def _save_employment_data(self):
        """Guarda los datos laborales del trabajador actual."""
        if not self.current_worker:
            messagebox.showerror("Error", "No hay trabajador seleccionado")
            return
        
        # Validar fecha de contratación
        hire_date_str = self.form_vars["hire_date"].get().strip()
        if hire_date_str:
            try:
                hire_date = datetime.strptime(hire_date_str, "%Y-%m-%d").date()
            except ValueError:
                messagebox.showerror("Error", "Formato de fecha inválido. Use YYYY-MM-DD")
                return
        else:
            hire_date = None
        
        # Validar salario
        salary_str = self.form_vars["salary"].get().strip()
        if salary_str:
            try:
                salary = float(salary_str)
                if salary < 0:
                    messagebox.showerror("Error", "El salario no puede ser negativo")
                    return
            except ValueError:
                messagebox.showerror("Error", "El salario debe ser un número")
                return
        else:
            salary = None
        
        # Actualizar propiedades laborales
        self.current_worker.position = self.form_vars["position"].get().strip()
        self.current_worker.department = self.form_vars["department"].get().strip()
        self.current_worker.contract_type = self.form_vars["contract_type"].get().strip()  # NUEVO: Guardar tipo de contrato
        self.current_worker.hire_date = hire_date
        self.current_worker.salary = salary
        
        # Guardar en base de datos
        success = self.worker_service.save_worker(self.current_worker)
        
        if success:
            messagebox.showinfo("Éxito", "Datos laborales guardados correctamente")
            # Recargar lista de trabajadores por si ha cambiado el departamento (para los filtros)
            self._load_workers()
        else:
            messagebox.showerror("Error", "Error al guardar los datos laborales")
    
    def _load_bank_accounts(self, worker):
        """
        Carga las cuentas bancarias del trabajador.
        
        Args:
            worker: Objeto Worker o None para limpiar la lista
        """
        # Limpiar cuentas actuales del UI
        for widget in self.accounts_list_frame.winfo_children():
            widget.destroy()
        
        if not worker:
            # Mostrar mensaje de no cuentas
            self.no_accounts_label = ctk.CTkLabel(
                self.accounts_list_frame,
                text="No hay cuentas bancarias registradas",
                font=ctk.CTkFont(size=14),
                text_color="gray"
            )
            self.no_accounts_label.pack(pady=30)
            return
        
        # Obtener cuentas del trabajador
        self.bank_accounts = []
        
        # Intentar cargar las cuentas desde la base de datos
        try:
            # Si tienes un método en el servicio para obtener cuentas
            self.bank_accounts = self.worker_service.get_worker_bank_accounts(worker.id)
        except Exception:
            # Si el método no existe, usar las cuentas del objeto worker si están disponibles
            if hasattr(worker, "bank_accounts"):
                self.bank_accounts = worker.bank_accounts
        
        # Si no hay cuentas pero hay datos de cuenta "legado", crear una cuenta primaria
        if not self.bank_accounts and (worker.bank_name or worker.account_number):
            legacy_account = BankAccount(
                worker_id=worker.id,
                is_primary=True,
                bank_name=worker.bank_name,
                account_type=worker.account_type,
                account_number=worker.account_number,
                account_holder=worker.account_holder,
                account_holder_rut=worker.account_holder_rut
            )
            self.bank_accounts = [legacy_account]
        
        # Mostrar las cuentas o mensaje de no cuentas
        if not self.bank_accounts:
            self.no_accounts_label = ctk.CTkLabel(
                self.accounts_list_frame,
                text="No hay cuentas bancarias registradas",
                font=ctk.CTkFont(size=14),
                text_color="gray"
            )
            self.no_accounts_label.pack(pady=30)
        else:
            # Mostrar cada cuenta
            for i, account in enumerate(self.bank_accounts):
                self._create_account_item(account, i)
    
    def _create_account_item(self, account, index):
        """
        Crea un elemento UI para una cuenta bancaria.
        
        Args:
            account: Objeto BankAccount
            index: Índice en la lista
        """
        # Frame para esta cuenta
        account_frame = ctk.CTkFrame(self.accounts_list_frame, corner_radius=5)
        account_frame.pack(fill="x", pady=5, padx=5)
        
        # Frame para la cabecera (banco y tipo)
        header_frame = ctk.CTkFrame(account_frame, fg_color=("gray95", "gray25"))
        header_frame.pack(fill="x", padx=5, pady=5)
        
        # Banco y tipo
        bank_label = ctk.CTkLabel(
            header_frame,
            text=f"{account.bank_name or 'Banco no especificado'}",
            font=ctk.CTkFont(weight="bold"),
            text_color=("gray10", "gray90")
        )
        bank_label.pack(side="left", padx=10, pady=5)
        
        # Indicador de cuenta principal
        if account.is_primary:
            primary_label = ctk.CTkLabel(
                header_frame,
                text="Cuenta Principal",
                font=ctk.CTkFont(size=12),
                text_color="#43B0F1"
            )
            primary_label.pack(side="left", padx=10)
        
        # Tipo de cuenta
        type_label = ctk.CTkLabel(
            header_frame,
            text=f"{account.account_type or 'Tipo no especificado'}",
            font=ctk.CTkFont(size=12)
        )
        type_label.pack(side="right", padx=10, pady=5)
        
        # Frame para detalles
        details_frame = ctk.CTkFrame(account_frame, fg_color="transparent")
        details_frame.pack(fill="x", padx=10, pady=5)
        
        # Número de cuenta
        ctk.CTkLabel(
            details_frame,
            text=f"Número: {account.account_number or 'No especificado'}",
            font=ctk.CTkFont(size=12)
        ).pack(anchor="w", pady=2)
        
        # Titular
        ctk.CTkLabel(
            details_frame,
            text=f"Titular: {account.account_holder or 'No especificado'}",
            font=ctk.CTkFont(size=12)
        ).pack(anchor="w", pady=2)
        
        # RUT del titular
        ctk.CTkLabel(
            details_frame,
            text=f"RUT Titular: {account.account_holder_rut or 'No especificado'}",
            font=ctk.CTkFont(size=12)
        ).pack(anchor="w", pady=2)
        
        # Frame para botones
        btn_frame = ctk.CTkFrame(account_frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=10, pady=5)
        
        # Botón editar
        ctk.CTkButton(
            btn_frame,
            text="Editar",
            command=lambda: self._edit_bank_account(account, index),
            width=80,
            height=25
        ).pack(side="left", padx=5)
        
        # Botón establecer como principal
        if not account.is_primary:
            ctk.CTkButton(
                btn_frame,
                text="Definir como Principal",
                command=lambda: self._set_primary_account(index),
                width=140,
                height=25,
                fg_color="#43B0F1"
            ).pack(side="left", padx=5)
        
        # Botón eliminar
        ctk.CTkButton(
            btn_frame,
            text="Eliminar",
            command=lambda: self._delete_bank_account(index),
            width=80,
            height=25,
            fg_color="#E76F51"
        ).pack(side="right", padx=5)
    
    def _add_bank_account(self):
        """Muestra el diálogo para añadir una nueva cuenta bancaria."""
        if not self.current_worker:
            return
            
        self._show_bank_account_dialog()
    
    def _edit_bank_account(self, account, index):
        """
        Muestra el diálogo para editar una cuenta bancaria existente.
        
        Args:
            account: Objeto BankAccount a editar
            index: Índice en la lista de cuentas
        """
        self._show_bank_account_dialog(account, index)
    
    def _show_bank_account_dialog(self, account=None, index=None):
        """
        Muestra el diálogo para añadir/editar una cuenta bancaria.
        
        Args:
            account: Objeto BankAccount a editar o None para crear uno nuevo
            index: Índice en la lista si es edición
        """
        # Crear ventana de diálogo
        dialog = ctk.CTkToplevel(self)
        dialog.title("Cuenta Bancaria")
        dialog.geometry("500x450")
        
        # Centrar ventana
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f'{width}x{height}+{x}+{y}')
        
        # Frame principal con scroll
        main_frame = ctk.CTkScrollableFrame(dialog)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Título
        title_text = "Editar Cuenta Bancaria" if account else "Añadir Cuenta Bancaria"
        ctk.CTkLabel(
            main_frame,
            text=title_text,
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=(0, 20))
        
        # Variables para el formulario
        bank_var = tk.StringVar(value=account.bank_name if account else "")
        type_var = tk.StringVar(value=account.account_type if account else "")
        number_var = tk.StringVar(value=account.account_number if account else "")
        holder_var = tk.StringVar(value=account.account_holder if account else "")
        holder_rut_var = tk.StringVar(value=account.account_holder_rut if account else "")
        is_primary_var = tk.BooleanVar(value=account.is_primary if account else False)
        
        # Frame para el formulario
        form_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        form_frame.pack(fill="x", pady=10)
        
        # Campo para el banco
        ctk.CTkLabel(form_frame, text="Banco:").pack(anchor="w", pady=(10, 0))
        
        # Lista de bancos chilenos comunes
        banks = [
            "", 
            "Banco Estado", 
            "Banco Santander", 
            "Banco de Chile", 
            "Banco BCI", 
            "Banco Scotiabank", 
            "Banco Falabella",
            "Banco Itaú",
            "Banco Security",
            "Banco BICE",
            "Banco Internacional",
            "Otro"
        ]
        
        bank_combobox = ctk.CTkComboBox(
            form_frame,
            values=banks,
            variable=bank_var,
            width=400
        )
        bank_combobox.pack(fill="x", pady=(0, 10))
        
        # Campo para tipo de cuenta
        ctk.CTkLabel(form_frame, text="Tipo de cuenta:").pack(anchor="w", pady=(10, 0))
        
        account_types = [
            "",
            "Cuenta Corriente",
            "Cuenta Vista",
            "Cuenta RUT",
            "Cuenta de Ahorro",
            "Otra"
        ]
        
        type_combobox = ctk.CTkComboBox(
            form_frame,
            values=account_types,
            variable=type_var,
            width=400
        )
        type_combobox.pack(fill="x", pady=(0, 10))
        
        # Campo para número de cuenta
        ctk.CTkLabel(form_frame, text="Número de cuenta:").pack(anchor="w", pady=(10, 0))
        ctk.CTkEntry(form_frame, textvariable=number_var, width=400).pack(fill="x", pady=(0, 10))
        
        # Campo para titular
        ctk.CTkLabel(form_frame, text="Titular de la cuenta:").pack(anchor="w", pady=(10, 0))
        ctk.CTkEntry(form_frame, textvariable=holder_var, width=400).pack(fill="x", pady=(0, 10))
        
        # Campo para RUT del titular
        ctk.CTkLabel(form_frame, text="RUT del titular:").pack(anchor="w", pady=(10, 0))
        ctk.CTkEntry(form_frame, textvariable=holder_rut_var, width=400).pack(fill="x", pady=(0, 10))
        
        # Checkbox para cuenta principal
        primary_check = ctk.CTkCheckBox(
            form_frame,
            text="Esta es la cuenta principal para pagos",
            variable=is_primary_var
        )
        primary_check.pack(anchor="w", pady=(10, 0))
        
        # Deshabilitar la opción si ya es la cuenta principal y estamos editando
        if account and account.is_primary:
            primary_check.configure(state="disabled")
        
        # Mensaje de advertencia si estamos cambiando la cuenta principal
        if not account or not account.is_primary:
            ctk.CTkLabel(
                form_frame,
                text="Si marca esta como cuenta principal, se desmarcará cualquier otra cuenta principal existente.",
                font=ctk.CTkFont(size=10),
                text_color="gray50",
                wraplength=400
            ).pack(anchor="w", pady=(0, 10), padx=(25, 0))
        
        # Mensaje de error
        error_label = ctk.CTkLabel(main_frame, text="", text_color="red")
        error_label.pack(fill="x", pady=(10, 0))
        
        # Botones de acción
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=20)
        
        def on_cancel():
            dialog.destroy()
        
        def on_save():
            # Validar campo requerido
            if not number_var.get().strip():
                error_label.configure(text="El número de cuenta es obligatorio")
                return
                
            # Crear nuevo objeto o actualizar existente
            if account:
                # Actualizar cuenta existente
                account.bank_name = bank_var.get()
                account.account_type = type_var.get()
                account.account_number = number_var.get()
                account.account_holder = holder_var.get()
                account.account_holder_rut = holder_rut_var.get()
                
                # Si esta cuenta será principal, desmarcar las demás
                if is_primary_var.get() and not account.is_primary:
                    account.is_primary = True
                    for other_account in self.bank_accounts:
                        if other_account != account:
                            other_account.is_primary = False
            else:
                # Crear nueva cuenta
                new_account = BankAccount(
                    worker_id=self.current_worker.id,
                    bank_name=bank_var.get(),
                    account_type=type_var.get(),
                    account_number=number_var.get(),
                    account_holder=holder_var.get(),
                    account_holder_rut=holder_rut_var.get(),
                    is_primary=is_primary_var.get()
                )
                
                # Si esta cuenta será principal, desmarcar las demás
                if is_primary_var.get():
                    for other_account in self.bank_accounts:
                        other_account.is_primary = False
                
                # Si es la primera cuenta, marcarla como principal automáticamente
                if not self.bank_accounts:
                    new_account.is_primary = True
                    
                self.bank_accounts.append(new_account)
            
            # Guardar los cambios
            try:
                # Si tienes un método en el servicio para guardar cuentas
                success = self.worker_service.save_bank_accounts(self.current_worker.id, self.bank_accounts)
            except Exception:
                # Si el método no existe, solo actualiza la UI
                success = True
                
            if success:
                # Actualizar la interfaz
                self._load_bank_accounts(self.current_worker)
                dialog.destroy()
            else:
                error_label.configure(text="No se pudo guardar la cuenta bancaria")
                
        # Botón cancelar
        ctk.CTkButton(
            btn_frame,
            text="Cancelar",
            command=on_cancel,
            fg_color="gray50",
            width=100,
            height=32
        ).pack(side="left", padx=20)
        
        # Botón guardar
        ctk.CTkButton(
            btn_frame,
            text="Guardar",
            command=on_save,
            width=100,
            height=32,
            font=ctk.CTkFont(weight="bold")
        ).pack(side="right", padx=20)
        
        # Hacer modal
        dialog.transient(self)
        dialog.grab_set()
    
    def _set_primary_account(self, index):
        """
        Establece una cuenta como principal.
        
        Args:
            index: Índice de la cuenta en la lista
        """
        if 0 <= index < len(self.bank_accounts):
            # Desmarcar todas las cuentas
            for account in self.bank_accounts:
                account.is_primary = False
                
            # Marcar la cuenta seleccionada
            self.bank_accounts[index].is_primary = True
            
            # Guardar los cambios
            try:
                # Si tienes un método en el servicio para guardar cuentas
                success = self.worker_service.save_bank_accounts(self.current_worker.id, self.bank_accounts)
            except Exception:
                # Si el método no existe, solo actualiza la UI
                success = True
                
            if success:
                # Actualizar la interfaz
                self._load_bank_accounts(self.current_worker)
                messagebox.showinfo("Éxito", "Se ha establecido como cuenta principal")
            else:
                messagebox.showerror("Error", "No se pudo actualizar la cuenta bancaria")
    
    def _delete_bank_account(self, index):
        """
        Elimina una cuenta bancaria.
        
        Args:
            index: Índice de la cuenta en la lista
        """
        if 0 <= index < len(self.bank_accounts):
            account = self.bank_accounts[index]
            
            # Si es la cuenta principal, mostrar advertencia
            if account.is_primary:
                confirm = messagebox.askyesno(
                    "Confirmar eliminación",
                    "Está por eliminar la cuenta principal. Si continúa, deberá establecer otra cuenta como principal.\n\n¿Desea continuar?"
                )
                if not confirm:
                    return
            else:
                confirm = messagebox.askyesno(
                    "Confirmar eliminación",
                    "¿Está seguro de eliminar esta cuenta bancaria?"
                )
                if not confirm:
                    return
            
            # Eliminar la cuenta
            del self.bank_accounts[index]
            
            # Si era la principal y hay otras cuentas, establecer la primera como principal
            if account.is_primary and self.bank_accounts:
                self.bank_accounts[0].is_primary = True
            
            # Guardar los cambios
            try:
                # Si tienes un método en el servicio para guardar cuentas
                success = self.worker_service.save_bank_accounts(self.current_worker.id, self.bank_accounts)
            except Exception:
                # Si el método no existe, solo actualiza la UI
                success = True
                
            if success:
                # Actualizar la interfaz
                self._load_bank_accounts(self.current_worker)
                messagebox.showinfo("Éxito", "Cuenta bancaria eliminada")
            else:
                messagebox.showerror("Error", "No se pudo eliminar la cuenta bancaria")
    
    def _delete_worker(self):
        """Elimina el trabajador actual."""
        if not self.current_worker:
            return
            
        confirm = messagebox.askyesno(
            "Confirmar eliminación", 
            f"¿Está seguro de eliminar al trabajador {self.current_worker.name}?\n\n"
            f"Esta acción marcará al trabajador como inactivo."
        )
        
        if confirm:
            success = self.worker_service.delete_worker(self.current_worker.id)
            
            if success:
                messagebox.showinfo("Éxito", "Trabajador eliminado correctamente")
                
                # Recargar lista de trabajadores
                self._load_workers()
                
                # Limpiar formulario
                self._create_worker()
            else:
                messagebox.showerror("Error", "Error al eliminar el trabajador")