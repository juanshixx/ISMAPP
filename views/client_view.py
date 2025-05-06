"""
Vista para la gestión de clientes en ISMAPP.
"""
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from models.client import Client
from core.services.client_service import ClientService

class ClientView(ctk.CTkFrame):
    """Vista para la gestión de clientes."""
    
    def __init__(self, parent):
        """
        Inicializa la vista de clientes.
        
        Args:
            parent: Frame contenedor
        """
        super().__init__(parent)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Obtener referencia al data_manager desde la ventana principal
        # Asumimos que la ventana principal tiene una instancia de data_manager
        main_window = self.winfo_toplevel()
        try:
            self.data_manager = main_window.data_manager
            # Inicializar el servicio de clientes
            self.client_service = ClientService(self.data_manager)
        except AttributeError:
            messagebox.showerror("Error", "No se pudo acceder al gestor de datos")
            return
        
        # Variables para almacenar datos
        self.clients = []
        self.current_client = None
        self.filtered_clients = []
        
        # Crear UI
        self._create_ui()
        
        # Cargar datos iniciales
        self._load_clients()
    
    def _create_ui(self):
        """Crea la interfaz de usuario del módulo."""
        # Frame contenedor principal (scrollable)
        self.main_container = ctk.CTkScrollableFrame(self)
        self.main_container.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # Título del módulo
        header_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(
            header_frame,
            text="Gestión de Clientes",
            font=ctk.CTkFont(size=22, weight="bold")
        ).pack(side="left")
        
        # Botón para crear nuevo cliente
        self.add_button = ctk.CTkButton(
            header_frame,
            text="+ Nuevo Cliente",
            command=self._show_edit_dialog,
            width=130
        )
        self.add_button.pack(side="right", padx=10)
        
        # Barra de búsqueda
        search_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        search_frame.pack(fill="x", pady=(0, 15))
        
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *args: self._filter_clients())
        
        search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Buscar cliente...",
            width=300,
            textvariable=self.search_var
        )
        search_entry.pack(side="left", fill="x", expand=True)
        
        # Frame para la tabla de clientes
        table_container = ctk.CTkFrame(self.main_container)
        table_container.pack(fill="both", expand=True)
        
        # Cabecera de la tabla
        columns = ["Nombre", "Razón Social", "RUT", "Teléfono", "Contacto", "Acciones"]
        header_frame = ctk.CTkFrame(table_container, fg_color=("#DDDDDD", "#2B2B2B"))
        header_frame.pack(fill="x")
        
        # Configurar ancho de columnas
        widths = [0.25, 0.25, 0.15, 0.1, 0.15, 0.1]  # Proporciones
        for i, col in enumerate(columns):
            col_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
            col_frame.pack(side="left", fill="both", expand=True, padx=2, pady=5)
            if i == len(columns) - 1:  # Si es la última columna (Acciones)
                col_frame.configure(width=100)  # Ancho fijo para acciones
            else:
                col_frame.configure(width=int(700 * widths[i]))  # Ancho proporcional
                
            ctk.CTkLabel(
                col_frame, 
                text=col,
                font=ctk.CTkFont(weight="bold")
            ).pack()
        
        # Contenedor para filas de clientes
        self.client_rows_frame = ctk.CTkScrollableFrame(table_container, fg_color="transparent")
        self.client_rows_frame.pack(fill="both", expand=True)
    
    def _load_clients(self):
        """Carga la lista de clientes desde la base de datos."""
        # Limpiar lista actual
        self.clients = self.client_service.get_all_clients()
        self.filtered_clients = self.clients.copy()
        
        # Actualizar UI
        self._update_client_table()
    
    def _update_client_table(self):
        """Actualiza la tabla de clientes en la UI."""
        # Limpiar tabla actual
        for widget in self.client_rows_frame.winfo_children():
            widget.destroy()
        
        # Verificar si hay clientes para mostrar
        if not self.filtered_clients:
            no_data_label = ctk.CTkLabel(
                self.client_rows_frame,
                text="No se encontraron clientes",
                font=ctk.CTkFont(size=14),
                text_color="gray60"
            )
            no_data_label.pack(pady=30)
            return
        
        # Crear filas para cada cliente
        for i, client in enumerate(self.filtered_clients):
            row_color = ("#F5F5F5", "#2D2D2D") if i % 2 == 0 else ("#FFFFFF", "#333333")
            row_frame = ctk.CTkFrame(self.client_rows_frame, fg_color=row_color, corner_radius=0)
            row_frame.pack(fill="x", pady=1)
            
            # Nombre
            name_frame = ctk.CTkFrame(row_frame, fg_color="transparent", width=200)
            name_frame.pack(side="left", fill="both", expand=True, padx=2, pady=8)
            ctk.CTkLabel(name_frame, text=client.name).pack(anchor="w", padx=5)
            
            # Razón Social
            business_frame = ctk.CTkFrame(row_frame, fg_color="transparent", width=200)
            business_frame.pack(side="left", fill="both", expand=True, padx=2, pady=8)
            ctk.CTkLabel(business_frame, text=client.business_name).pack(anchor="w", padx=5)
            
            # RUT
            rut_frame = ctk.CTkFrame(row_frame, fg_color="transparent", width=120)
            rut_frame.pack(side="left", fill="both", expand=True, padx=2, pady=8)
            ctk.CTkLabel(rut_frame, text=client.rut).pack(anchor="w", padx=5)
            
            # Teléfono
            phone_frame = ctk.CTkFrame(row_frame, fg_color="transparent", width=80)
            phone_frame.pack(side="left", fill="both", expand=True, padx=2, pady=8)
            ctk.CTkLabel(phone_frame, text=client.phone).pack(anchor="w", padx=5)
            
            # Contacto
            contact_frame = ctk.CTkFrame(row_frame, fg_color="transparent", width=120)
            contact_frame.pack(side="left", fill="both", expand=True, padx=2, pady=8)
            ctk.CTkLabel(contact_frame, text=client.contact_person).pack(anchor="w", padx=5)
            
            # Acciones
            actions_frame = ctk.CTkFrame(row_frame, fg_color="transparent", width=100)
            actions_frame.pack(side="left", fill="both", padx=2, pady=3)
            
            # Botón editar
            edit_btn = ctk.CTkButton(
                actions_frame,
                text="✏️",
                width=30,
                command=lambda c=client: self._show_edit_dialog(c),
                fg_color=("#6E9075", "#2D6A6A")
            )
            edit_btn.pack(side="left", padx=2)
            
            # Botón eliminar
            delete_btn = ctk.CTkButton(
                actions_frame,
                text="🗑️",
                width=30,
                command=lambda c=client: self._confirm_delete(c),
                fg_color=("#BC7777", "#AA5555")
            )
            delete_btn.pack(side="left", padx=2)
    
    def _filter_clients(self):
        """Filtra la lista de clientes según el término de búsqueda."""
        search_term = self.search_var.get().lower().strip()
        
        if not search_term:
            self.filtered_clients = self.clients.copy()
        else:
            self.filtered_clients = [
                client for client in self.clients
                if (search_term in client.name.lower() or
                    search_term in client.business_name.lower() or
                    search_term in client.rut.lower() or
                    search_term in client.contact_person.lower())
            ]
        
        self._update_client_table()
    
    def _show_edit_dialog(self, client=None):
        """
        Muestra el diálogo para crear o editar un cliente.
        
        Args:
            client (Client, optional): Cliente a editar, None para crear nuevo
        """
        self.current_client = client or Client()
        
        # Crear ventana de diálogo
        dialog = ctk.CTkToplevel(self)
        dialog.title("Nuevo Cliente" if client is None else "Editar Cliente")
        dialog.geometry("600x700")
        dialog.resizable(False, False)
        
        # Centrar ventana
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f'+{x}+{y}')
        
        # Contenedor principal con scroll
        main_frame = ctk.CTkScrollableFrame(dialog)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Título
        ctk.CTkLabel(
            main_frame,
            text="Datos del Cliente",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=(0, 20), anchor="w")
        
        # Form fields
        form_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        form_frame.pack(fill="x", pady=10)
        
        # Variables para campos
        name_var = tk.StringVar(value=self.current_client.name)
        business_var = tk.StringVar(value=self.current_client.business_name)
        rut_var = tk.StringVar(value=self.current_client.rut)
        address_var = tk.StringVar(value=self.current_client.address)
        phone_var = tk.StringVar(value=self.current_client.phone)
        email_var = tk.StringVar(value=self.current_client.email)
        contact_var = tk.StringVar(value=self.current_client.contact_person)
        notes_var = tk.StringVar(value=self.current_client.notes)
        active_var = tk.BooleanVar(value=self.current_client.is_active)
        
        # Función para crear campos con label
        def create_field(parent, label_text, variable, row, is_required=False):
            # Label
            label_text = f"{label_text}{'*' if is_required else ''}"
            ctk.CTkLabel(parent, text=label_text).grid(row=row, column=0, sticky="w", padx=5, pady=(10, 0))
            
            # Entry
            entry = ctk.CTkEntry(parent, textvariable=variable)
            entry.grid(row=row+1, column=0, sticky="ew", padx=5, pady=(0, 10))
            return entry
        
        # Nombre (requerido)
        name_entry = create_field(form_frame, "Nombre", name_var, 0, True)
        name_entry.focus_set()  # Auto-focus
        
        # Razón Social (requerido)
        business_entry = create_field(form_frame, "Razón Social", business_var, 2, True)
        
        # RUT (requerido)
        rut_entry = create_field(form_frame, "RUT", rut_var, 4, True)
        
        # Teléfono
        phone_entry = create_field(form_frame, "Teléfono", phone_var, 6)
        
        # Email
        email_entry = create_field(form_frame, "Email", email_var, 8)
        
        # Persona de Contacto
        contact_entry = create_field(form_frame, "Persona de Contacto", contact_var, 10)
        
        # Dirección
        ctk.CTkLabel(form_frame, text="Dirección").grid(row=12, column=0, sticky="w", padx=5, pady=(10, 0))
        address_entry = ctk.CTkTextbox(form_frame, height=60)
        address_entry.grid(row=13, column=0, sticky="ew", padx=5, pady=(0, 10))
        address_entry.insert("1.0", self.current_client.address)
        
        # Notas
        ctk.CTkLabel(form_frame, text="Notas").grid(row=14, column=0, sticky="w", padx=5, pady=(10, 0))
        notes_entry = ctk.CTkTextbox(form_frame, height=60)
        notes_entry.grid(row=15, column=0, sticky="ew", padx=5, pady=(0, 10))
        notes_entry.insert("1.0", self.current_client.notes)
        
        # Estado (activo/inactivo)
        active_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        active_frame.grid(row=16, column=0, sticky="w", padx=5, pady=10)
        
        active_switch = ctk.CTkSwitch(
            active_frame, 
            text="Cliente Activo",
            variable=active_var,
            onvalue=True,
            offvalue=False
        )
        active_switch.pack(side="left")
        
        # Mensaje de error
        error_label = ctk.CTkLabel(main_frame, text="", text_color="red")
        error_label.pack(fill="x", pady=(10, 0))
        
        # Botones
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=20)
        
        # Función para guardar cliente
        def save_client():
            # Validar campos requeridos
            if not name_var.get().strip():
                error_label.configure(text="El nombre es obligatorio")
                name_entry.focus_set()
                return
                
            if not business_var.get().strip():
                error_label.configure(text="La razón social es obligatoria")
                business_entry.focus_set()
                return
                
            if not rut_var.get().strip():
                error_label.configure(text="El RUT es obligatorio")
                rut_entry.focus_set()
                return
            
            # Actualizar objeto cliente
            self.current_client.name = name_var.get().strip()
            self.current_client.business_name = business_var.get().strip()
            self.current_client.rut = rut_var.get().strip()
            self.current_client.address = address_entry.get("1.0", "end-1c").strip()
            self.current_client.phone = phone_var.get().strip()
            self.current_client.email = email_var.get().strip()
            self.current_client.contact_person = contact_var.get().strip()
            self.current_client.notes = notes_entry.get("1.0", "end-1c").strip()
            self.current_client.is_active = active_var.get()
            
            # Guardar en la base de datos
            if self.client_service.save_client(self.current_client):
                messagebox.showinfo("Éxito", "Cliente guardado correctamente")
                dialog.destroy()
                self._load_clients()  # Recargar datos
            else:
                error_label.configure(text="Error al guardar el cliente")
        
        # Botón cancelar
        ctk.CTkButton(
            btn_frame,
            text="Cancelar",
            command=dialog.destroy,
            fg_color="gray50",
            width=100
        ).pack(side="left", padx=20)
        
        # Botón guardar
        ctk.CTkButton(
            btn_frame,
            text="Guardar",
            command=save_client,
            width=100
        ).pack(side="right", padx=20)
        
        # Bloquear ventana principal
        dialog.transient(self)
        dialog.grab_set()
        
    def _confirm_delete(self, client):
        """
        Confirma y elimina un cliente.
        
        Args:
            client (Client): Cliente a eliminar
        """
        if messagebox.askyesno(
            "Eliminar Cliente", 
            f"¿Está seguro que desea eliminar al cliente '{client.name}'?\n\n"
            "Esta acción no se puede deshacer."
        ):
            if self.client_service.delete_client(client.id):
                messagebox.showinfo("Éxito", "Cliente eliminado correctamente")
                self._load_clients()  # Recargar datos
            else:
                messagebox.showerror("Error", "No se pudo eliminar el cliente")