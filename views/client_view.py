"""
Vista para la gestión de clientes en ISMAPP.
"""
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from models.client import Client, ClientType
from models.material import Material, MaterialType, PlasticSubtype
from models.client_material import ClientMaterial
from core.services.client_service import ClientService
from core.services.material_service import MaterialService
from core.services.client_material_service import ClientMaterialService

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
        main_window = self.winfo_toplevel()
        try:
            self.data_manager = main_window.data_manager
            # Inicializar servicios
            self.client_service = ClientService(self.data_manager)
            self.material_service = MaterialService(self.data_manager)
            self.client_material_service = ClientMaterialService(self.data_manager)
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
        
        # Frame para búsqueda y filtros
        search_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        search_frame.pack(fill="x", pady=(0, 15))
        
        # Barra de búsqueda
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *args: self._filter_clients())
        
        search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Buscar cliente...",
            width=300,
            textvariable=self.search_var
        )
        search_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        # Filtro de tipo de cliente
        filter_frame = ctk.CTkFrame(search_frame, fg_color="transparent")
        filter_frame.pack(side="right")
        
        ctk.CTkLabel(filter_frame, text="Filtrar por:").pack(side="left", padx=(0, 5))
        
        self.filter_var = tk.StringVar(value="all")
        
        # Opciones de filtro
        filter_options = {
            "all": "Todos",
            ClientType.BUYER: "Compradores",
            ClientType.SUPPLIER: "Proveedores"
        }
        
        filter_menu = ctk.CTkOptionMenu(
            filter_frame,
            values=list(filter_options.values()),
            command=lambda choice: self._set_filter(
                next(key for key, value in filter_options.items() if value == choice)
            )
        )
        filter_menu.pack(side="left")
        
        # Frame para la tabla de clientes
        table_container = ctk.CTkFrame(self.main_container)
        table_container.pack(fill="both", expand=True)
        
        # Cabecera de la tabla
        columns = ["Nombre", "Razón Social", "RUT", "Tipo", "Teléfono", "Acciones"]
        header_frame = ctk.CTkFrame(table_container, fg_color=("#DDDDDD", "#2B2B2B"))
        header_frame.pack(fill="x")
        
        # Configurar ancho de columnas
        widths = [0.22, 0.22, 0.15, 0.13, 0.1, 0.18]  # Proporciones
        for i, col in enumerate(columns):
            col_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
            col_frame.pack(side="left", fill="both", expand=True, padx=2, pady=5)
            if i == len(columns) - 1:  # Si es la última columna (Acciones)
                col_frame.configure(width=150)  # Ancho fijo para acciones
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
    
    def _set_filter(self, filter_type):
        """
        Establece el filtro por tipo de cliente.
        
        Args:
            filter_type (str): Tipo de filtro a aplicar
        """
        self.filter_var.set(filter_type)
        self._filter_clients()
    
    def _load_clients(self):
        """Carga la lista de clientes desde la base de datos."""
        # Limpiar lista actual
        self.clients = self.client_service.get_all_clients()
        self._filter_clients()
    
    def _filter_clients(self):
        """Filtra la lista de clientes según búsqueda y filtros."""
        search_term = self.search_var.get().lower().strip()
        filter_type = self.filter_var.get()
        
        if filter_type == "all":
            # Filtrar solo por término de búsqueda
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
        else:
            # Filtrar por tipo y término de búsqueda
            if not search_term:
                self.filtered_clients = [
                    client for client in self.clients
                    if (filter_type == ClientType.BUYER and client.is_buyer()) or
                       (filter_type == ClientType.SUPPLIER and client.is_supplier())
                ]
            else:
                self.filtered_clients = [
                    client for client in self.clients
                    if ((filter_type == ClientType.BUYER and client.is_buyer()) or
                        (filter_type == ClientType.SUPPLIER and client.is_supplier())) and
                       (search_term in client.name.lower() or
                        search_term in client.business_name.lower() or
                        search_term in client.rut.lower() or
                        search_term in client.contact_person.lower())
                ]
        
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
            name_frame = ctk.CTkFrame(row_frame, fg_color="transparent", width=150)
            name_frame.pack(side="left", fill="both", expand=True, padx=2, pady=8)
            ctk.CTkLabel(name_frame, text=client.name).pack(anchor="w", padx=5)
            
            # Razón Social
            business_frame = ctk.CTkFrame(row_frame, fg_color="transparent", width=150)
            business_frame.pack(side="left", fill="both", expand=True, padx=2, pady=8)
            ctk.CTkLabel(business_frame, text=client.business_name).pack(anchor="w", padx=5)
            
            # RUT
            rut_frame = ctk.CTkFrame(row_frame, fg_color="transparent", width=100)
            rut_frame.pack(side="left", fill="both", expand=True, padx=2, pady=8)
            ctk.CTkLabel(rut_frame, text=client.rut).pack(anchor="w", padx=5)
            
            # Tipo de cliente
            type_frame = ctk.CTkFrame(row_frame, fg_color="transparent", width=90)
            type_frame.pack(side="left", fill="both", expand=True, padx=2, pady=8)
            
            type_text = ClientType.get_display_name(client.client_type)
            type_color = {
                ClientType.BUYER: "#4CAF50",
                ClientType.SUPPLIER: "#2196F3",
                ClientType.BOTH: "#9C27B0"
            }.get(client.client_type, "gray60")
            
            ctk.CTkLabel(
                type_frame, 
                text=type_text,
                text_color=type_color,
                font=ctk.CTkFont(size=12, weight="bold")
            ).pack(anchor="w", padx=5)
            
            # Teléfono
            phone_frame = ctk.CTkFrame(row_frame, fg_color="transparent", width=70)
            phone_frame.pack(side="left", fill="both", expand=True, padx=2, pady=8)
            ctk.CTkLabel(phone_frame, text=client.phone).pack(anchor="w", padx=5)
            
            # Acciones
            actions_frame = ctk.CTkFrame(row_frame, fg_color="transparent", width=120)
            actions_frame.pack(side="left", fill="both", padx=2, pady=3)
            
            # Botón materiales
            materials_btn = ctk.CTkButton(
                actions_frame,
                text="📦",
                width=30,
                command=lambda c=client: self._show_materials_dialog(c),
                fg_color=("#5D87B4", "#2D6A9A")
            )
            materials_btn.pack(side="left", padx=2)
            
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
        dialog.geometry("600x750")
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
        client_type_var = tk.StringVar(value=self.current_client.client_type)
        
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
        
        # Tipo de cliente (requerido)
        ctk.CTkLabel(form_frame, text="Tipo de Cliente*").grid(row=12, column=0, sticky="w", padx=5, pady=(10, 0))
        
        type_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        type_frame.grid(row=13, column=0, sticky="ew", padx=5, pady=(0, 10))
        
        # Opciones para tipo de cliente
        buyer_rb = ctk.CTkRadioButton(
            type_frame, 
            text="Comprador", 
            variable=client_type_var, 
            value=ClientType.BUYER
        )
        buyer_rb.pack(side="left", padx=10)
        
        supplier_rb = ctk.CTkRadioButton(
            type_frame, 
            text="Proveedor", 
            variable=client_type_var, 
            value=ClientType.SUPPLIER
        )
        supplier_rb.pack(side="left", padx=10)
        
        both_rb = ctk.CTkRadioButton(
            type_frame, 
            text="Ambos", 
            variable=client_type_var, 
            value=ClientType.BOTH
        )
        both_rb.pack(side="left", padx=10)
        
        # Dirección
        ctk.CTkLabel(form_frame, text="Dirección").grid(row=14, column=0, sticky="w", padx=5, pady=(10, 0))
        address_entry = ctk.CTkTextbox(form_frame, height=60)
        address_entry.grid(row=15, column=0, sticky="ew", padx=5, pady=(0, 10))
        address_entry.insert("1.0", self.current_client.address)
        
        # Notas
        ctk.CTkLabel(form_frame, text="Notas").grid(row=16, column=0, sticky="w", padx=5, pady=(10, 0))
        notes_entry = ctk.CTkTextbox(form_frame, height=60)
        notes_entry.grid(row=17, column=0, sticky="ew", padx=5, pady=(0, 10))
        notes_entry.insert("1.0", self.current_client.notes)
        
        # Estado (activo/inactivo)
        active_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        active_frame.grid(row=18, column=0, sticky="w", padx=5, pady=10)
        
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
                
            if not client_type_var.get():
                error_label.configure(text="Debe seleccionar un tipo de cliente")
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
            self.current_client.client_type = client_type_var.get()
            
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
    
    def _show_materials_dialog(self, client):
        """
        Muestra el diálogo para gestionar materiales y precios del cliente.
        
        Args:
            client (Client): Cliente para gestionar materiales
        """
        # Crear ventana de diálogo
        dialog = ctk.CTkToplevel(self)
        dialog.title(f"Materiales y Precios - {client.name}")
        dialog.geometry("800x600")
        dialog.resizable(True, True)
        
        # Centrar ventana
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f'+{x}+{y}')
        
        # Configurar grid
        dialog.grid_rowconfigure(0, weight=1)
        dialog.grid_columnconfigure(0, weight=1)
        
        # Contenedor principal con scroll
        main_frame = ctk.CTkScrollableFrame(dialog)
        main_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        
        # Título
        header_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(
            header_frame,
            text=f"Materiales y Precios para {client.name}",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(side="left")
        
        # Botón para agregar material
        add_btn = ctk.CTkButton(
            header_frame,
            text="+ Agregar Material",
            command=lambda: self._show_add_material_dialog(dialog, client),
            width=150
        )
        add_btn.pack(side="right")
        
        # Frame para la lista de materiales
        materials_frame = ctk.CTkFrame(main_frame)
        materials_frame.pack(fill="both", expand=True, pady=10)
        
        # Cargar materiales del cliente
        self._load_client_materials(client, materials_frame)
        
        # Bloquear ventana principal
        dialog.transient(self)
        dialog.grab_set()
    
    def _load_client_materials(self, client, container):
        """
        Carga y muestra los materiales asociados al cliente.
        
        Args:
            client (Client): Cliente del que mostrar materiales
            container (CTkFrame): Contenedor donde mostrar los materiales
        """
        # Limpiar contenedor
        for widget in container.winfo_children():
            widget.destroy()
        
        # Obtener materiales asociados al cliente
        client_materials = self.client_material_service.get_client_materials(client.id)
        
        # Verificar si hay materiales para mostrar
        if not client_materials:
            ctk.CTkLabel(
                container,
                text="No hay materiales asociados a este cliente",
                font=ctk.CTkFont(size=14),
                text_color="gray60"
            ).pack(pady=30)
            return
        
        # Cabecera
        header_frame = ctk.CTkFrame(container, fg_color=("#DDDDDD", "#2B2B2B"))
        header_frame.pack(fill="x")
        
        # Columnas
        columns = ["Material", "Tipo", "Precio", "Incluye IVA", "Acciones"]
        widths = [0.35, 0.18, 0.17, 0.15, 0.15]  # Proporciones
        
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
        
        # Contenedor para las filas de materiales
        materials_list = ctk.CTkScrollableFrame(container, fg_color="transparent")
        materials_list.pack(fill="both", expand=True, pady=5)
        
        # Crear filas para cada material
        for i, (client_material, material) in enumerate(client_materials):
            row_color = ("#F5F5F5", "#2D2D2D") if i % 2 == 0 else ("#FFFFFF", "#333333")
            row_frame = ctk.CTkFrame(materials_list, fg_color=row_color, corner_radius=0)
            row_frame.pack(fill="x", pady=1)
            
            # Material
            name_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
            name_frame.pack(side="left", fill="both", expand=True, padx=2, pady=8)
            
            material_name = material.get_full_name()
            ctk.CTkLabel(name_frame, text=material_name).pack(anchor="w", padx=5)
            
            # Tipo
            type_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
            type_frame.pack(side="left", fill="both", expand=True, padx=2, pady=8)
            
            material_type = MaterialType.get_display_name(material.material_type)
            ctk.CTkLabel(type_frame, text=material_type).pack(anchor="w", padx=5)
            
            # Precio
            price_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
            price_frame.pack(side="left", fill="both", expand=True, padx=2, pady=8)
            
            price_text = f"${client_material.price:,.2f}"
            ctk.CTkLabel(price_frame, text=price_text).pack(anchor="w", padx=5)
            
            # Incluye IVA
            tax_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
            tax_frame.pack(side="left", fill="both", expand=True, padx=2, pady=8)
            
            tax_text = "Sí" if client_material.includes_tax else "No"
            ctk.CTkLabel(tax_frame, text=tax_text).pack(anchor="w", padx=5)
            
            # Acciones
            actions_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
            actions_frame.pack(side="left", fill="both", padx=2, pady=3)
            
            # Botón editar
            edit_btn = ctk.CTkButton(
                actions_frame,
                text="✏️",
                width=30,
                command=lambda c=client, cm=client_material, m=material: 
                         self._show_edit_price_dialog(container.master, c, cm, m),
                fg_color=("#6E9075", "#2D6A6A")
            )
            edit_btn.pack(side="left", padx=2)
            
            # Botón eliminar
            delete_btn = ctk.CTkButton(
                actions_frame,
                text="🗑️",
                width=30,
                command=lambda cm=client_material, m=material: 
                         self._confirm_delete_material(container.master, client, cm, m),
                fg_color=("#BC7777", "#AA5555")
            )
            delete_btn.pack(side="left", padx=2)
    
    def _show_add_material_dialog(self, parent_dialog, client):
        """
        Muestra el diálogo para agregar un material al cliente.
        
        Args:
            parent_dialog: Diálogo padre
            client (Client): Cliente al que agregar el material
        """
        # Crear ventana de diálogo
        dialog = ctk.CTkToplevel(parent_dialog)
        dialog.title("Agregar Material")
        dialog.geometry("550x550")
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
            text="Agregar Material al Cliente",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(0, 20))
        
        # Variables para campos
        material_type_var = tk.StringVar(value="existing")  # existing o custom
        existing_material_var = tk.StringVar()
        custom_material_var = tk.StringVar()
        is_plastic_var = tk.BooleanVar(value=True)
        plastic_subtype_var = tk.StringVar(value=PlasticSubtype.CANDY)
        plastic_state_var = tk.StringVar(value="clean")
        custom_subtype_var = tk.StringVar()
        price_var = tk.StringVar(value="0.00")
        tax_var = tk.BooleanVar(value=False)
        
        # Función para actualizar visibilidad de campos
        def update_fields(*args):
            material_choice = material_type_var.get()
            
            if material_choice == "existing":
                existing_frame.pack(fill="x", pady=10)
                custom_frame.pack_forget()
            else:  # custom
                existing_frame.pack_forget()
                custom_frame.pack(fill="x", pady=10)
                
                # Actualizar campos de subtipo plástico
                is_plastic = is_plastic_var.get()
                subtype = plastic_subtype_var.get()
                
                if is_plastic:
                    plastic_subtype_label.pack(anchor="w", pady=(10, 0))
                    plastic_subtype_menu.pack(fill="x", pady=(0, 10))
                    plastic_state_label.pack(anchor="w", pady=(10, 0))
                    plastic_state_frame.pack(fill="x", pady=(0, 10))
                    
                    # Mostrar/ocultar campo de subtipo personalizado
                    if subtype == PlasticSubtype.OTHER:
                        custom_plastic_label.pack(anchor="w", pady=(10, 0))
                        custom_plastic_entry.pack(fill="x", pady=(0, 10))
                    else:
                        custom_plastic_label.pack_forget()
                        custom_plastic_entry.pack_forget()
                else:
                    plastic_subtype_label.pack_forget()
                    plastic_subtype_menu.pack_forget()
                    plastic_state_label.pack_forget()
                    plastic_state_frame.pack_forget()
                    custom_plastic_label.pack_forget()
                    custom_plastic_entry.pack_forget()
        
        # Form
        form_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        form_frame.pack(fill="x", pady=10)
        
        # Opciones de material (existente o personalizado)
        options_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        options_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(options_frame, text="Tipo de Material:").pack(anchor="w", pady=(0, 5))
        
        options_radio_frame = ctk.CTkFrame(options_frame, fg_color="transparent")
        options_radio_frame.pack(fill="x")
        
        existing_rb = ctk.CTkRadioButton(
            options_radio_frame,
            text="Seleccionar Material Existente",
            variable=material_type_var,
            value="existing",
            command=update_fields
        )
        existing_rb.pack(side="left", padx=10)
        
        custom_rb = ctk.CTkRadioButton(
            options_radio_frame,
            text="Definir Material Manualmente",
            variable=material_type_var,
            value="custom",
            command=update_fields
        )
        custom_rb.pack(side="left", padx=10)
        
        # Frame para material existente
        existing_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        existing_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(existing_frame, text="Material:").pack(anchor="w", pady=(0, 5))
        
        # Obtener materiales disponibles (priorizando plásticos)
        available_materials = self.client_material_service.get_available_materials(client.id)
        plastic_materials = [m for m in available_materials if m.material_type == MaterialType.PLASTIC]
        other_materials = [m for m in available_materials if m.material_type != MaterialType.PLASTIC]
        
        material_options = []
        if plastic_materials:
            material_options.append(("-- Plásticos --", None))  # Encabezado
            material_options.extend([(m.get_full_name(), m.id) for m in plastic_materials])
        
        if other_materials:
            if material_options:  # Si ya hay plásticos, añadir separador
                material_options.append(("------------------", None))
            material_options.append(("-- Otros Materiales --", None))  # Encabezado
            material_options.extend([(m.get_full_name(), m.id) for m in other_materials])
        
        if not material_options:
            material_options = [("No hay materiales disponibles", None)]
        
        material_names = [m[0] for m in material_options]
        
        # OptionMenu para seleccionar material
        material_menu = ctk.CTkOptionMenu(
            existing_frame, 
            values=material_names,
            variable=existing_material_var,
            dynamic_resizing=False,
            width=300
        )
        material_menu.pack(fill="x", pady=(0, 15))
        
        if material_names:
            # Seleccionar primer material válido (no encabezado)
            for i, (name, id) in enumerate(material_options):
                if id is not None:
                    material_menu.set(name)
                    break
        
        # Frame para material personalizado
        custom_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        
        # Nombre del material personalizado
        ctk.CTkLabel(custom_frame, text="Nombre del Material:").pack(anchor="w", pady=(0, 5))
        
        custom_name_entry = ctk.CTkEntry(custom_frame, textvariable=custom_material_var)
        custom_name_entry.pack(fill="x", pady=(0, 10))
        
        # Checkbox para subtipo de plástico
        plastic_checkbox = ctk.CTkCheckBox(
            custom_frame,
            text="Es un plástico",
            variable=is_plastic_var,
            command=update_fields
        )
        plastic_checkbox.pack(anchor="w", pady=(10, 5))
        
        # Subtipo de plástico (Caramelo, Chicle, Otro)
        plastic_subtype_label = ctk.CTkLabel(custom_frame, text="Subtipo de Plástico")
        
        plastic_subtypes = {
            PlasticSubtype.CANDY: "Caramelo",
            PlasticSubtype.GUM: "Chicle",
            PlasticSubtype.OTHER: "Otro"
        }
        
        plastic_subtype_menu = ctk.CTkOptionMenu(
            custom_frame,
            values=list(plastic_subtypes.values()),
            command=lambda choice: plastic_subtype_var.set(
                next(key for key, value in plastic_subtypes.items() if value == choice)
            )
        )
        plastic_subtype_menu.set(plastic_subtypes[PlasticSubtype.CANDY])
        
        # Subtipo personalizado para "Otro"
        custom_plastic_label = ctk.CTkLabel(custom_frame, text="Especificar Subtipo")
        
        custom_plastic_entry = ctk.CTkEntry(custom_frame, textvariable=custom_subtype_var)
        
        # Estado del plástico (limpio/sucio)
        plastic_state_label = ctk.CTkLabel(custom_frame, text="Estado del Plástico")
        
        plastic_state_frame = ctk.CTkFrame(custom_frame, fg_color="transparent")
        
        clean_rb = ctk.CTkRadioButton(
            plastic_state_frame,
            text="Limpio",
            variable=plastic_state_var,
            value="clean"
        )
        clean_rb.pack(side="left", padx=10)
        
        dirty_rb = ctk.CTkRadioButton(
            plastic_state_frame,
            text="Sucio",
            variable=plastic_state_var,
            value="dirty"
        )
        dirty_rb.pack(side="left", padx=10)
        
        # Sección de precios (común para ambos tipos)
        price_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        price_frame.pack(fill="x", pady=15)
        
        # Precio
        ctk.CTkLabel(price_frame, text="Precio:").pack(anchor="w", pady=(0, 5))
        
        price_entry = ctk.CTkEntry(price_frame, textvariable=price_var)
        price_entry.pack(fill="x", pady=(0, 15))
        
        # Incluye IVA
        tax_switch = ctk.CTkSwitch(
            price_frame, 
            text="Incluye IVA",
            variable=tax_var,
            onvalue=True,
            offvalue=False
        )
        tax_switch.pack(anchor="w", pady=(0, 15))
        
        # Notas
        ctk.CTkLabel(price_frame, text="Notas:").pack(anchor="w", pady=(0, 5))
        
        notes_entry = ctk.CTkTextbox(price_frame, height=80)
        notes_entry.pack(fill="x", pady=(0, 15))
        
        # Mensaje de error
        error_label = ctk.CTkLabel(main_frame, text="", text_color="red")
        error_label.pack(fill="x", pady=(5, 0))
        
        # Botones
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=15)
        
        # Actualizar campos según valores iniciales
        update_fields()
        
        def save_material():
            try:
                # Convertir precio a float
                try:
                    price = float(price_var.get().replace(',', '.'))
                except ValueError:
                    error_label.configure(text="El precio debe ser un número válido")
                    return
                
                material_id = None
                
                # Determinar si estamos usando un material existente o creando uno nuevo
                if material_type_var.get() == "existing":
                    # Validar selección de material
                    selected_name = existing_material_var.get()
                    
                    # Verificar si se ha seleccionado un encabezado
                    if selected_name in ["-- Plásticos --", "-- Otros Materiales --", "------------------", "No hay materiales disponibles"]:
                        error_label.configure(text="Debe seleccionar un material válido")
                        return
                        
                    # Obtener el ID del material seleccionado
                    material_id = next((id for name, id in material_options if name == selected_name), None)
                    
                    if not material_id:
                        error_label.configure(text="El material seleccionado no es válido")
                        return
                else:  # custom
                    # Validar campos del material personalizado
                    if not custom_material_var.get().strip():
                        error_label.configure(text="Debe especificar un nombre para el material")
                        custom_name_entry.focus_set()
                        return
                    
                    if is_plastic_var.get() and plastic_subtype_var.get() == PlasticSubtype.OTHER:
                        if not custom_subtype_var.get().strip():
                            error_label.configure(text="Debe especificar el subtipo de plástico personalizado")
                            custom_plastic_entry.focus_set()
                            return
                    
                    # Crear el nuevo material
                    new_material = Material(
                        name=custom_material_var.get().strip(),
                        description="",
                        material_type=MaterialType.PLASTIC if is_plastic_var.get() else MaterialType.CUSTOM,
                        is_plastic_subtype=is_plastic_var.get(),
                        plastic_subtype=plastic_subtype_var.get() if is_plastic_var.get() else "",
                        plastic_state=plastic_state_var.get() if is_plastic_var.get() else "",
                        custom_subtype=custom_subtype_var.get().strip() if is_plastic_var.get() and plastic_subtype_var.get() == PlasticSubtype.OTHER else custom_material_var.get().strip() if not is_plastic_var.get() else "",
                        is_active=True
                    )
                    
                    # Guardar el material en la base de datos
                    if self.material_service.save_material(new_material):
                        material_id = new_material.id
                    else:
                        error_label.configure(text="Error al crear el nuevo material")
                        return
                
                # Crear relación cliente-material
                client_material = ClientMaterial(
                    client_id=client.id,
                    material_id=material_id,
                    price=price,
                    includes_tax=tax_var.get(),
                    notes=notes_entry.get("1.0", "end-1c").strip()
                )
                
                # Guardar en la base de datos
                if self.client_material_service.save_client_material(client_material):
                    messagebox.showinfo("Éxito", "Material agregado correctamente")
                    dialog.destroy()
                    
                    # Recargar la vista de materiales
                    materials_frame = next(
                        w for w in parent_dialog.winfo_children()
                        if isinstance(w, ctk.CTkScrollableFrame)
                    )
                    materials_container = next(
                        w for w in materials_frame.winfo_children()
                        if isinstance(w, ctk.CTkFrame) and w.winfo_children() and not "transparent" in str(w.cget("fg_color"))
                    )
                    self._load_client_materials(client, materials_container)
                else:
                    error_label.configure(text="Error al guardar la relación")
                    
            except Exception as e:
                error_label.configure(text=f"Error: {str(e)}")
        
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
            command=save_material,
            width=100
        ).pack(side="right", padx=20)
        
        # Bloquear ventana padre
        dialog.transient(parent_dialog)
        dialog.grab_set()
    
    def _show_edit_price_dialog(self, parent_dialog, client, client_material, material):
        """
        Muestra diálogo para editar el precio de un material.
        
        Args:
            parent_dialog: Diálogo padre
            client (Client): Cliente propietario
            client_material (ClientMaterial): Relación cliente-material a editar
            material (Material): Material asociado
        """
        # Crear ventana de diálogo
        dialog = ctk.CTkToplevel(parent_dialog)
        dialog.title("Editar Precio")
        dialog.geometry("500x400")
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
            text=f"Editar Precio - {material.get_full_name()}",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(0, 20))
        
        # Form
        form_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        form_frame.pack(fill="x", pady=10)
        
        # Precio
        ctk.CTkLabel(form_frame, text="Precio:").pack(anchor="w", pady=(0, 5))
        
        price_var = tk.StringVar(value=str(client_material.price))
        price_entry = ctk.CTkEntry(form_frame, textvariable=price_var)
        price_entry.pack(fill="x", pady=(0, 15))
        
        # Incluye IVA
        tax_var = tk.BooleanVar(value=client_material.includes_tax)
        tax_switch = ctk.CTkSwitch(
            form_frame, 
            text="Incluye IVA",
            variable=tax_var,
            onvalue=True,
            offvalue=False
        )
        tax_switch.pack(anchor="w", pady=(0, 15))
        
        # Notas
        ctk.CTkLabel(form_frame, text="Notas:").pack(anchor="w", pady=(0, 5))
        
        notes_entry = ctk.CTkTextbox(form_frame, height=80)
        notes_entry.pack(fill="x", pady=(0, 15))
        notes_entry.insert("1.0", client_material.notes)
        
        # Mensaje de error
        error_label = ctk.CTkLabel(main_frame, text="", text_color="red")
        error_label.pack(fill="x", pady=(5, 0))
        
        # Botones
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=15)
        
        def save_price():
            try:
                # Convertir precio a float
                try:
                    price = float(price_var.get().replace(',', '.'))
                except ValueError:
                    error_label.configure(text="El precio debe ser un número válido")
                    return
                
                # Actualizar objeto
                client_material.price = price
                client_material.includes_tax = tax_var.get()
                client_material.notes = notes_entry.get("1.0", "end-1c").strip()
                
                # Guardar en la base de datos
                if self.client_material_service.save_client_material(client_material):
                    messagebox.showinfo("Éxito", "Precio actualizado correctamente")
                    dialog.destroy()
                    
                    # Recargar la vista de materiales
                    materials_frame = next(
                        w for w in parent_dialog.winfo_children()
                        if isinstance(w, ctk.CTkScrollableFrame)
                    )
                    materials_container = next(
                        w for w in materials_frame.winfo_children()
                        if isinstance(w, ctk.CTkFrame) and w.winfo_children() and not "transparent" in str(w.cget("fg_color"))
                    )
                    self._load_client_materials(client, materials_container)
                else:
                    error_label.configure(text="Error al actualizar el precio")
                    
            except Exception as e:
                error_label.configure(text=f"Error: {str(e)}")
        
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
            command=save_price,
            width=100
        ).pack(side="right", padx=20)
        
        # Bloquear ventana padre
        dialog.transient(parent_dialog)
        dialog.grab_set()
    
    def _confirm_delete_material(self, parent_dialog, client, client_material, material):
        """
        Confirma y elimina una relación cliente-material.
        
        Args:
            parent_dialog: Diálogo padre
            client (Client): Cliente propietario
            client_material (ClientMaterial): Relación cliente-material a eliminar
            material (Material): Material asociado
        """
        if messagebox.askyesno(
            "Eliminar Material", 
            f"¿Está seguro que desea eliminar el material '{material.get_full_name()}' de este cliente?\n\n"
            "Esta acción no se puede deshacer."
        ):
            if self.client_material_service.delete_client_material(client_material.id):
                messagebox.showinfo("Éxito", "Material eliminado correctamente")
                
                # Recargar la vista de materiales
                materials_frame = next(
                    w for w in parent_dialog.winfo_children()
                    if isinstance(w, ctk.CTkScrollableFrame)
                )
                materials_container = next(
                    w for w in materials_frame.winfo_children()
                    if isinstance(w, ctk.CTkFrame) and w.winfo_children() and not "transparent" in str(w.cget("fg_color"))
                )
                self._load_client_materials(client, materials_container)
            else:
                messagebox.showerror("Error", "No se pudo eliminar el material")
    
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