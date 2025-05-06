"""
Vista para la gestión de trabajadores en ISMV3.
"""
import tkinter as tk
from tkinter import messagebox, ttk
import customtkinter as ctk
from typing import List, Optional, Dict, Any
from datetime import date

from models.worker import Worker
from controllers.worker_controller import WorkerController


class WorkerView(ctk.CTkFrame):
    """Vista para gestionar trabajadores."""
    
    def __init__(self, parent, **kwargs):
        """
        Inicializa la vista de trabajadores.
        
        Args:
            parent: Widget padre en la jerarquía de tkinter.
            **kwargs: Argumentos adicionales para el Frame.
        """
        super().__init__(parent, **kwargs)
        self.controller = WorkerController()
        self.selected_worker: Optional[Worker] = None
        
        self._init_ui()
        self._load_workers()
    
    def _init_ui(self):
        """Inicializa los elementos de la interfaz de usuario."""
        # Configuración de la cuadrícula principal
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=3)
        self.rowconfigure(0, weight=1)
        
        # Panel izquierdo - Lista de trabajadores
        left_panel = ctk.CTkFrame(self)
        left_panel.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # Filtros y búsqueda
        filter_frame = ctk.CTkFrame(left_panel)
        filter_frame.pack(fill="x", padx=5, pady=5)
        
        # Opciones de filtro
        self.filter_var = tk.StringVar(value="Todos")
        ctk.CTkLabel(filter_frame, text="Mostrar:").pack(side="left", padx=5)
        filter_menu = ctk.CTkOptionMenu(
            filter_frame, 
            values=["Todos", "Activos", "Inactivos"],
            variable=self.filter_var,
            command=self._on_filter_change
        )
        filter_menu.pack(side="left", padx=5)
        
        # Barra de búsqueda
        self.search_var = tk.StringVar()
        search_frame = ctk.CTkFrame(left_panel)
        search_frame.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(search_frame, text="Buscar:").pack(side="left", padx=5)
        search_entry = ctk.CTkEntry(search_frame, textvariable=self.search_var)
        search_entry.pack(side="left", fill="x", expand=True, padx=5)
        search_entry.bind("<KeyRelease>", self._on_search)
        
        # Lista de trabajadores
        list_frame = ctk.CTkFrame(left_panel)
        list_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.worker_listbox = tk.Listbox(list_frame, bg="#2b2b2b", fg="#ffffff",
                                         selectbackground="#1f538d")
        self.worker_listbox.pack(fill="both", expand=True)
        self.worker_listbox.bind("<<ListboxSelect>>", self._on_worker_select)
        
        # Botones de acción para la lista
        btn_frame = ctk.CTkFrame(left_panel)
        btn_frame.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkButton(btn_frame, text="Nuevo", command=self._on_new_worker).pack(
            side="left", padx=5, pady=5)
        ctk.CTkButton(btn_frame, text="Eliminar", command=self._on_delete_worker).pack(
            side="right", padx=5, pady=5)
        
        # Panel derecho - Detalles del trabajador
        right_panel = ctk.CTkFrame(self)
        right_panel.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        
        # Pestañas para los diferentes datos
        self.tab_view = ctk.CTkTabview(right_panel)
        self.tab_view.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Pestaña de información general
        info_tab = self.tab_view.add("Información")
        self._setup_info_tab(info_tab)
        
        # Pestaña de pagos
        payment_tab = self.tab_view.add("Pagos")
        self._setup_payment_tab(payment_tab)
        
        # Pestaña de materiales
        materials_tab = self.tab_view.add("Materiales")
        self._setup_materials_tab(materials_tab)
        
        # Botón guardar (común para todas las pestañas)
        save_btn = ctk.CTkButton(right_panel, text="Guardar", command=self._on_save_worker)
        save_btn.pack(pady=10)
    
    def _setup_info_tab(self, parent):
        """Configura la pestaña de información general."""
        # Variables para campos del formulario
        self.name_var = tk.StringVar()
        self.document_var = tk.StringVar()
        self.phone_var = tk.StringVar()
        self.address_var = tk.StringVar()
        self.active_var = tk.BooleanVar(value=True)
        self.start_date_var = tk.StringVar()
        self.end_date_var = tk.StringVar()
        
        # Formulario en grid
        form = ctk.CTkFrame(parent)
        form.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Campos obligatorios
        row = 0
        ctk.CTkLabel(form, text="Nombre:").grid(row=row, column=0, sticky="w", padx=5, pady=5)
        ctk.CTkEntry(form, textvariable=self.name_var, width=300).grid(
            row=row, column=1, sticky="ew", padx=5, pady=5)
        row += 1
        
        ctk.CTkLabel(form, text="DNI/NIE:").grid(row=row, column=0, sticky="w", padx=5, pady=5)
        ctk.CTkEntry(form, textvariable=self.document_var).grid(
            row=row, column=1, sticky="ew", padx=5, pady=5)
        row += 1
        
        # Campos opcionales
        ctk.CTkLabel(form, text="Teléfono:").grid(row=row, column=0, sticky="w", padx=5, pady=5)
        ctk.CTkEntry(form, textvariable=self.phone_var).grid(
            row=row, column=1, sticky="ew", padx=5, pady=5)
        row += 1
        
        ctk.CTkLabel(form, text="Dirección:").grid(row=row, column=0, sticky="w", padx=5, pady=5)
        ctk.CTkEntry(form, textvariable=self.address_var).grid(
            row=row, column=1, sticky="ew", padx=5, pady=5)
        row += 1
        
        # Estado
        status_frame = ctk.CTkFrame(form)
        status_frame.grid(row=row, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        
        ctk.CTkCheckBox(status_frame, text="Activo", variable=self.active_var, 
                     command=self._on_active_toggle).pack(side="left", padx=5)
        row += 1
        
        # Fechas
        dates_frame = ctk.CTkFrame(form)
        dates_frame.grid(row=row, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        
        ctk.CTkLabel(dates_frame, text="Fecha inicio:").pack(side="left", padx=5)
        ctk.CTkEntry(dates_frame, textvariable=self.start_date_var, width=100).pack(
            side="left", padx=5)
            
        ctk.CTkLabel(dates_frame, text="Fecha fin:").pack(side="left", padx=5)
        self.end_date_entry = ctk.CTkEntry(dates_frame, textvariable=self.end_date_var, width=100)
        self.end_date_entry.pack(side="left", padx=5)
        row += 1
        
        # Notas
        ctk.CTkLabel(form, text="Notas:").grid(row=row, column=0, sticky="nw", padx=5, pady=5)
        self.notes_text = ctk.CTkTextbox(form, height=100)
        self.notes_text.grid(row=row, column=1, sticky="ew", padx=5, pady=5)
        row += 1
        
        # Configurar para expansión
        form.columnconfigure(1, weight=1)
    
    def _setup_payment_tab(self, parent):
        """Configura la pestaña de información de pagos."""
        # Aquí irían los campos relacionados con la información de pagos
        # Por ahora, implementamos una versión básica
        
        payment_frame = ctk.CTkFrame(parent)
        payment_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Modo de pago
        self.payment_mode_var = tk.StringVar(value="efectivo")
        ctk.CTkLabel(payment_frame, text="Modo de pago:").pack(anchor="w", padx=5, pady=5)
        
        modes_frame = ctk.CTkFrame(payment_frame)
        modes_frame.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkRadioButton(modes_frame, text="Efectivo", variable=self.payment_mode_var, 
                        value="efectivo").pack(side="left", padx=10)
        ctk.CTkRadioButton(modes_frame, text="Transferencia", variable=self.payment_mode_var,
                        value="transferencia").pack(side="left", padx=10)
        
        # Cuenta bancaria (solo visible si el modo es transferencia)
        self.bank_frame = ctk.CTkFrame(payment_frame)
        self.bank_frame.pack(fill="x", padx=5, pady=5)
        
        self.bank_account_var = tk.StringVar()
        ctk.CTkLabel(self.bank_frame, text="Cuenta bancaria:").pack(side="left", padx=5)
        ctk.CTkEntry(self.bank_frame, textvariable=self.bank_account_var, width=200).pack(
            side="left", fill="x", expand=True, padx=5)
        
        # Mostrar/ocultar según el modo
        self.payment_mode_var.trace_add("write", self._on_payment_mode_change)
    
    def _setup_materials_tab(self, parent):
        """Configura la pestaña de materiales."""
        materials_frame = ctk.CTkFrame(parent)
        materials_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Lista de materiales disponibles
        material_options = ["Cartón", "Plástico", "Metal", "Vidrio", "Orgánico", "Otros"]
        
        # Checkboxes para los materiales
        self.material_vars = {}
        for material in material_options:
            var = tk.BooleanVar()
            self.material_vars[material] = var
            ctk.CTkCheckBox(materials_frame, text=material, variable=var).pack(
                anchor="w", padx=5, pady=5)
        
        # Campo para otros materiales
        other_frame = ctk.CTkFrame(materials_frame)
        other_frame.pack(fill="x", padx=5, pady=10)
        
        ctk.CTkLabel(other_frame, text="Otros materiales:").pack(side="left", padx=5)
        self.other_materials_var = tk.StringVar()
        ctk.CTkEntry(other_frame, textvariable=self.other_materials_var, width=200).pack(
            side="left", fill="x", expand=True, padx=5)
    
    def _load_workers(self, filter_option=None):
        """Carga la lista de trabajadores desde el controlador."""
        self.worker_listbox.delete(0, tk.END)
        
        if filter_option is None:
            filter_option = self.filter_var.get()
        
        # Obtener trabajadores según el filtro
        if filter_option == "Activos":
            workers = self.controller.get_active_workers()
        elif filter_option == "Inactivos":
            workers = self.controller.get_inactive_workers()
        else:  # "Todos"
            workers = self.controller.get_all_workers()
        
        # Ordenar por nombre
        workers.sort(key=lambda w: w.name)
        
        # Llenar la lista
        for worker in workers:
            display_text = f"{worker.name}"
            if worker.document_id:
                display_text += f" ({worker.document_id})"
            if not worker.active:
                display_text += " [Inactivo]"
                
            self.worker_listbox.insert(tk.END, display_text)
            # Almacenar ID como dato adicional
            self.worker_listbox.itemconfig(tk.END, {'worker_id': worker.id})
    
    def _on_filter_change(self, option):
        """Maneja el cambio en el filtro de trabajadores."""
        self._load_workers(option)
    
    def _on_search(self, event=None):
        """Maneja el evento de búsqueda en la lista."""
        search_term = self.search_var.get()
        if search_term:
            workers = self.controller.search_workers(search_term)
        else:
            # Si no hay término de búsqueda, usar el filtro actual
            self._load_workers()
            return
        
        # Actualizar la lista con los resultados
        self.worker_listbox.delete(0, tk.END)
        for worker in sorted(workers, key=lambda w: w.name):
            display_text = f"{worker.name}"
            if worker.document_id:
                display_text += f" ({worker.document_id})"
            if not worker.active:
                display_text += " [Inactivo]"
                
            self.worker_listbox.insert(tk.END, display_text)
            self.worker_listbox.itemconfig(tk.END, {'worker_id': worker.id})
    
    def _on_worker_select(self, event=None):
        """Maneja la selección de un trabajador en la lista."""
        selection = self.worker_listbox.curselection()
        if not selection:
            return
        
        index = selection[0]
        worker_id = self.worker_listbox.itemcget(index, 'worker_id')
        if not worker_id:
            return
        
        worker = self.controller.get_worker(int(worker_id))
        if worker:
            self.selected_worker = worker
            self._populate_form(worker)
    
    def _populate_form(self, worker: Worker):
        """Rellena el formulario con los datos del trabajador."""
        # Información general
        self.name_var.set(worker.name)
        self.document_var.set(worker.document_id)
        self.phone_var.set(worker.phone)
        self.address_var.set(worker.address)
        self.active_var.set(worker.active)
        
        # Fechas
        if worker.start_date:
            self.start_date_var.set(worker.start_date.strftime("%Y-%m-%d"))
        else:
            self.start_date_var.set("")
            
        if worker.end_date:
            self.end_date_var.set(worker.end_date.strftime("%Y-%m-%d"))
        else:
            self.end_date_var.set("")
        
        # Habilitar/deshabilitar campo de fecha fin según estado
        self._update_end_date_field()
        
        # Notas
        self.notes_text.delete("1.0", tk.END)
        if worker.notes:
            self.notes_text.insert("1.0", worker.notes)
        
        # Información de pago
        payment_info = worker.payment_info or {}
        self.payment_mode_var.set(payment_info.get('mode', 'efectivo'))
        self.bank_account_var.set(payment_info.get('bank_account', ''))
        self._on_payment_mode_change()
        
        # Materiales
        for material, var in self.material_vars.items():
            var.set(material.lower() in [m.lower() for m in worker.materials])
        
        # Otros materiales
        other_materials = [m for m in worker.materials 
                          if m.lower() not in [mat.lower() for mat in self.material_vars.keys()]]
        self.other_materials_var.set(", ".join(other_materials))
    
    def _on_active_toggle(self):
        """Actualiza la interfaz cuando cambia el estado activo/inactivo."""
        self._update_end_date_field()
    
    def _update_end_date_field(self):
        """Actualiza el campo de fecha fin según el estado activo/inactivo."""
        if self.active_var.get():
            self.end_date_entry.configure(state="disabled")
            self.end_date_var.set("")
        else:
            self.end_date_entry.configure(state="normal")
            # Si no hay fecha fin y está inactivo, poner fecha actual
            if not self.end_date_var.get():
                self.end_date_var.set(date.today().strftime("%Y-%m-%d"))
    
    def _on_payment_mode_change(self, *args):
        """Muestra u oculta campos según el modo de pago."""
        mode = self.payment_mode_var.get()
        if mode == "transferencia":
            self.bank_frame.pack(fill="x", padx=5, pady=5)
        else:
            self.bank_frame.pack_forget()
    
    def _on_new_worker(self):
        """Prepara el formulario para un nuevo trabajador."""
        self.selected_worker = None
        
        # Limpiar todos los campos
        self.name_var.set("")
        self.document_var.set("")
        self.phone_var.set("")
        self.address_var.set("")
        self.active_var.set(True)
        self.start_date_var.set(date.today().strftime("%Y-%m-%d"))
        self.end_date_var.set("")
        self.notes_text.delete("1.0", tk.END)
        
        # Pagos
        self.payment_mode_var.set("efectivo")
        self.bank_account_var.set("")
        self._on_payment_mode_change()
        
        # Materiales
        for var in self.material_vars.values():
            var.set(False)
        self.other_materials_var.set("")
        
        # Actualizar estado de campos
        self._update_end_date_field()
    
    def _on_save_worker(self):
        """Guarda los cambios del trabajador actual."""
        # Validar datos mínimos
        name = self.name_var.get().strip()
        document_id = self.document_var.get().strip()
        
        if not name:
            messagebox.showerror("Error", "El nombre es obligatorio")
            return
        
        # Validar fechas
        start_date = None
        end_date = None
        
        try:
            if self.start_date_var.get():
                start_date = date.fromisoformat(self.start_date_var.get())
        except ValueError:
            messagebox.showerror("Error", "Formato de fecha de inicio incorrecto. Usar YYYY-MM-DD")
            return
            
        try:
            if self.end_date_var.get():
                end_date = date.fromisoformat(self.end_date_var.get())
        except ValueError:
            messagebox.showerror("Error", "Formato de fecha de fin incorrecto. Usar YYYY-MM-DD")
            return
        
        # Recopilar materiales seleccionados
        materials = []
        for material, var in self.material_vars.items():
            if var.get():
                materials.append(material)
        
        # Añadir otros materiales
        if self.other_materials_var.get():
            other_materials = [m.strip() for m in self.other_materials_var.get().split(",") if m.strip()]
            materials.extend(other_materials)
        
        # Información de pago
        payment_info = {
            'mode': self.payment_mode_var.get()
        }
        
        if self.payment_mode_var.get() == "transferencia":
            payment_info['bank_account'] = self.bank_account_var.get()
        
        # Construir o actualizar objeto Worker
        if self.selected_worker:
            worker = self.selected_worker
            worker.name = name
            worker.document_id = document_id
            worker.phone = self.phone_var.get()
            worker.address = self.address_var.get()
            worker.active = self.active_var.get()
            worker.start_date = start_date
            worker.end_date = end_date
            worker.notes = self.notes_text.get("1.0", tk.END).strip()
            worker.payment_info = payment_info
            worker.materials = materials
        else:
            worker = Worker(
                name=name,
                document_id=document_id,
                phone=self.phone_var.get(),
                address=self.address_var.get(),
                active=self.active_var.get(),
                start_date=start_date,
                end_date=end_date,
                notes=self.notes_text.get("1.0", tk.END).strip(),
                payment_info=payment_info,
                materials=materials
            )
        
        # Guardar en base de datos
        saved_worker = self.controller.save_worker(worker)
        self.selected_worker = saved_worker
        
        # Actualizar lista
        self._load_workers()
        
        # Mostrar confirmación
        messagebox.showinfo("Éxito", f"Trabajador '{name}' guardado correctamente")
    
    def _on_delete_worker(self):
        """Elimina el trabajador seleccionado."""
        if not self.selected_worker:
            messagebox.showerror("Error", "No hay trabajador seleccionado")
            return
        
        if messagebox.askyesno("Confirmar", f"¿Está seguro de eliminar al trabajador '{self.selected_worker.name}'?"):
            if self.controller.delete_worker(self.selected_worker.id):
                messagebox.showinfo("Éxito", "Trabajador eliminado correctamente")
                self._load_workers()
                self._on_new_worker()  # Limpiar formulario
            else:
                messagebox.showerror("Error", "No se pudo eliminar al trabajador")