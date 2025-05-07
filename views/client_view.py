"""
Vista para la gestión de clientes en ISMAPP.
"""
import tkinter as tk
from tkinter import ttk  # Importamos ttk para usar PanedWindow
from tkinter import messagebox
import customtkinter as ctk
from models.client import Client

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
        
        # Obtener referencias a servicios desde ventana principal
        main_window = self.winfo_toplevel()
        try:
            self.client_service = main_window.services.get("ClientService")
            self.material_service = main_window.services.get("MaterialService")
        except AttributeError:
            messagebox.showerror("Error", "No se pudo acceder a los servicios necesarios")
            return
        
        # Variables para control
        self.clients = []
        self.current_client = None
        self.client_materials = []
        
        # Crear UI
        self._create_ui()
        
        # Cargar datos iniciales
        self._load_clients()
    
    def _create_ui(self):
        """Crea la interfaz de usuario."""
        # MODIFICADO: Usar ttk.PanedWindow en lugar de CTkPanedWindow
        self.split_view = ttk.PanedWindow(self, orient="horizontal")
        self.split_view.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # Panel izquierdo (lista de clientes)
        self.left_panel = ctk.CTkFrame(self)  # No pasar self.split_view como parent
        self.left_panel.grid_rowconfigure(1, weight=1)
        self.left_panel.grid_columnconfigure(0, weight=1)
        
        # Panel derecho (detalle del cliente)
        self.right_panel = ctk.CTkFrame(self)  # No pasar self.split_view como parent
        self.right_panel.grid_rowconfigure(0, weight=1)
        self.right_panel.grid_columnconfigure(0, weight=1)
        
        # Añadir paneles a PanedWindow
        self.split_view.add(self.left_panel, weight=1)
        self.split_view.add(self.right_panel, weight=2)
        
        # Crear componentes del panel izquierdo (lista de clientes)
        self._create_left_panel()
        
        # Crear componentes del panel derecho (detalle y materiales)
        self._create_right_panel()
    
    def _create_left_panel(self):
        """Configura el panel izquierdo con la lista de clientes."""
        # Header con título y botón de nuevo cliente
        header_frame = ctk.CTkFrame(self.left_panel, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        ctk.CTkLabel(
            header_frame,
            text="Clientes",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(side="left")
        
        # Botón para crear nuevo cliente
        ctk.CTkButton(
            header_frame,
            text="+ Nuevo",
            command=self._create_client,
            width=100
        ).pack(side="right")
        
        # Frame para filtros y búsqueda
        filter_frame = ctk.CTkFrame(self.left_panel)
        filter_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        
        # Combobox para filtrar por tipo de cliente
        self.filter_var = tk.StringVar(value="Todos")
        type_filter = ctk.CTkComboBox(
            filter_frame,
            values=["Todos", "Compradores", "Proveedores", "Ambos"],
            variable=self.filter_var,
            state="readonly",
            width=120
        )
        type_filter.grid(row=0, column=0, padx=5, pady=5)
        type_filter.bind("<<ComboboxSelected>>", self._apply_filter)
        
        # Campo de búsqueda
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self._apply_filter)
        
        search_entry = ctk.CTkEntry(
            filter_frame, 
            placeholder_text="Buscar...",
            textvariable=self.search_var
        )
        search_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        filter_frame.columnconfigure(1, weight=1)
        
        # Lista de clientes con scroll
        self.clients_frame = ctk.CTkScrollableFrame(self.left_panel)
        self.clients_frame.grid(row=2, column=0, sticky="nsew", pady=10)
        self.left_panel.rowconfigure(2, weight=1)
    
    def _create_right_panel(self):
        """Configura el panel derecho con los detalles del cliente."""
        # Crear notebook/pestañas
        self.tabs = ctk.CTkTabview(self.right_panel)
        self.tabs.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        # Añadir pestañas
        self.tabs.add("Detalles")
        self.tabs.add("Datos Bancarios")
        self.tabs.add("Materiales")
        
        # Configurar pestaña de detalles
        self._setup_details_tab(self.tabs.tab("Detalles"))
        
        # Configurar pestaña de datos bancarios
        self._setup_banking_tab(self.tabs.tab("Datos Bancarios"))
        
        # Configurar pestaña de materiales
        self._setup_materials_tab(self.tabs.tab("Materiales"))
    
    def _setup_details_tab(self, parent):
        """Configura la pestaña de detalles del cliente."""
        # Panel de detalles con scroll
        details_scroll = ctk.CTkScrollableFrame(parent)
        details_scroll.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Contenedor del formulario
        form_frame = ctk.CTkFrame(details_scroll, fg_color="transparent")
        form_frame.pack(fill="x", expand=True, pady=10)
        
        # Crear variables para el formulario
        self.form_vars = {
            "name": tk.StringVar(),
            "business_name": tk.StringVar(),
            "rut": tk.StringVar(),
            "address": tk.StringVar(),
            "phone": tk.StringVar(),
            "email": tk.StringVar(),
            "contact_person": tk.StringVar(),
            "notes": tk.StringVar(),
            "client_type": tk.StringVar(value="both"),
            # Variables para datos bancarios
            "bank_name": tk.StringVar(),
            "account_type": tk.StringVar(),
            "account_number": tk.StringVar(),
            "account_holder": tk.StringVar(),
        }
        
        # Nombre del cliente
        ctk.CTkLabel(form_frame, text="Nombre:").grid(row=0, column=0, sticky="w", pady=(10, 0))
        self.name_entry = ctk.CTkEntry(form_frame, textvariable=self.form_vars["name"], width=300)
        self.name_entry.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        
        # Razón social
        ctk.CTkLabel(form_frame, text="Razón Social:").grid(row=2, column=0, sticky="w", pady=(10, 0))
        ctk.CTkEntry(form_frame, textvariable=self.form_vars["business_name"]).grid(row=3, column=0, sticky="ew", pady=(0, 10))
        
        # RUT
        ctk.CTkLabel(form_frame, text="RUT:").grid(row=4, column=0, sticky="w", pady=(10, 0))
        ctk.CTkEntry(form_frame, textvariable=self.form_vars["rut"]).grid(row=5, column=0, sticky="ew", pady=(0, 10))
        
        # Dirección
        ctk.CTkLabel(form_frame, text="Dirección:").grid(row=6, column=0, sticky="w", pady=(10, 0))
        ctk.CTkEntry(form_frame, textvariable=self.form_vars["address"]).grid(row=7, column=0, sticky="ew", pady=(0, 10))
        
        # Teléfono
        ctk.CTkLabel(form_frame, text="Teléfono:").grid(row=8, column=0, sticky="w", pady=(10, 0))
        ctk.CTkEntry(form_frame, textvariable=self.form_vars["phone"]).grid(row=9, column=0, sticky="ew", pady=(0, 10))
        
        # Email
        ctk.CTkLabel(form_frame, text="Email:").grid(row=10, column=0, sticky="w", pady=(10, 0))
        ctk.CTkEntry(form_frame, textvariable=self.form_vars["email"]).grid(row=11, column=0, sticky="ew", pady=(0, 10))
        
        # Persona de contacto
        ctk.CTkLabel(form_frame, text="Persona de contacto:").grid(row=12, column=0, sticky="w", pady=(10, 0))
        ctk.CTkEntry(form_frame, textvariable=self.form_vars["contact_person"]).grid(row=13, column=0, sticky="ew", pady=(0, 10))
        
        # Notas
        ctk.CTkLabel(form_frame, text="Notas:").grid(row=14, column=0, sticky="w", pady=(10, 0))
        ctk.CTkEntry(form_frame, textvariable=self.form_vars["notes"], height=50).grid(row=15, column=0, sticky="ew", pady=(0, 10))
        
        # Tipo de cliente
        ctk.CTkLabel(form_frame, text="Tipo de cliente:").grid(row=16, column=0, sticky="w", pady=(10, 0))
        
        type_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        type_frame.grid(row=17, column=0, sticky="ew", pady=(0, 20))
        
        # Radio buttons para tipo de cliente
        ctk.CTkRadioButton(
            type_frame, 
            text="Comprador", 
            variable=self.form_vars["client_type"],
            value="buyer"
        ).grid(row=0, column=0, padx=(0, 10))
        
        ctk.CTkRadioButton(
            type_frame, 
            text="Proveedor", 
            variable=self.form_vars["client_type"],
            value="supplier"
        ).grid(row=0, column=1, padx=10)
        
        ctk.CTkRadioButton(
            type_frame, 
            text="Ambos", 
            variable=self.form_vars["client_type"],
            value="both"
        ).grid(row=0, column=2, padx=10)
        
        # Botones de acción
        btn_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        btn_frame.grid(row=18, column=0, sticky="ew", pady=20)
        
        self.save_btn = ctk.CTkButton(
            btn_frame,
            text="Guardar",
            command=self._save_client,
            state="disabled"
        )
        self.save_btn.pack(side="right", padx=5)
        
        self.delete_btn = ctk.CTkButton(
            btn_frame,
            text="Eliminar",
            command=self._delete_client,
            fg_color="#E76F51",
            state="disabled"
        )
        self.delete_btn.pack(side="right", padx=5)
        
        # Expandir columnas para llenar el espacio horizontal
        form_frame.columnconfigure(0, weight=1)
    
    def _setup_banking_tab(self, parent):
        """Configura la pestaña de datos bancarios del cliente."""
        # Panel de datos bancarios con scroll
        banking_scroll = ctk.CTkScrollableFrame(parent)
        banking_scroll.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Contenedor del formulario bancario
        form_frame = ctk.CTkFrame(banking_scroll, fg_color="transparent")
        form_frame.pack(fill="x", expand=True, pady=10)
        
        # Banco
        ctk.CTkLabel(form_frame, text="Banco:").grid(row=0, column=0, sticky="w", pady=(10, 0))
        
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
            variable=self.form_vars["bank_name"],
            width=300
        )
        bank_combobox.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        
        # Tipo de cuenta
        ctk.CTkLabel(form_frame, text="Tipo de cuenta:").grid(row=2, column=0, sticky="w", pady=(10, 0))
        
        account_types = [
            "",
            "Cuenta Corriente",
            "Cuenta Vista",
            "Cuenta RUT",
            "Cuenta de Ahorro",
            "Otra"
        ]
        
        account_type_combobox = ctk.CTkComboBox(
            form_frame,
            values=account_types,
            variable=self.form_vars["account_type"],
            width=300
        )
        account_type_combobox.grid(row=3, column=0, sticky="ew", pady=(0, 10))
        
        # Número de cuenta
        ctk.CTkLabel(form_frame, text="Número de cuenta:").grid(row=4, column=0, sticky="w", pady=(10, 0))
        ctk.CTkEntry(form_frame, textvariable=self.form_vars["account_number"]).grid(row=5, column=0, sticky="ew", pady=(0, 10))
        
        # Titular de la cuenta
        ctk.CTkLabel(form_frame, text="Titular de la cuenta:").grid(row=6, column=0, sticky="w", pady=(10, 0))
        ctk.CTkEntry(form_frame, textvariable=self.form_vars["account_holder"]).grid(row=7, column=0, sticky="ew", pady=(0, 10))
        
        # Expandir columnas para llenar el espacio horizontal
        form_frame.columnconfigure(0, weight=1)
        
        # Nota informativa
        note_frame = ctk.CTkFrame(banking_scroll, fg_color=("gray90", "gray20"))
        note_frame.pack(fill="x", expand=True, pady=20)
        
        ctk.CTkLabel(
            note_frame,
            text="Importante: Los datos bancarios se utilizarán exclusivamente para transacciones relacionadas con la compra/venta de materiales.",
            font=ctk.CTkFont(size=12),
            wraplength=450,
            text_color=("gray40", "gray80")
        ).pack(padx=10, pady=10)
    
    def _setup_materials_tab(self, parent):
        """Configura la pestaña de materiales del cliente."""
        # Frame para la lista de materiales
        materials_frame = ctk.CTkFrame(parent)
        materials_frame.pack(fill="both", expand=True, padx=5, pady=5)
        materials_frame.grid_rowconfigure(1, weight=1)
        materials_frame.grid_columnconfigure(0, weight=1)
        
        # Encabezado con botón para añadir material
        header_frame = ctk.CTkFrame(materials_frame, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        ctk.CTkLabel(
            header_frame, 
            text="Materiales asociados", 
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(side="left")
        
        self.add_material_btn = ctk.CTkButton(
            header_frame,
            text="+ Añadir Material",
            command=self._show_add_material_dialog,
            width=130,
            state="disabled"
        )
        self.add_material_btn.pack(side="right")
        
        # Tabla/lista de materiales con scroll
        self.materials_list = ctk.CTkScrollableFrame(materials_frame)
        self.materials_list.grid(row=1, column=0, sticky="nsew", pady=5)
    
    def _load_clients(self):
        """Carga la lista de clientes desde la base de datos."""
        self.clients = self.client_service.get_all_clients()
        self._update_clients_list()
    
    def _update_clients_list(self):
        """Actualiza la lista visual de clientes según filtros."""
        # Limpiar lista actual
        for widget in self.clients_frame.winfo_children():
            widget.destroy()
            
        # Obtener filtros
        search_term = self.search_var.get().lower()
        filter_type = self.filter_var.get()
        
        # Mapear el filtro a los valores de la base de datos
        type_mapping = {
            "Todos": None,
            "Compradores": "buyer",
            "Proveedores": "supplier",
            "Ambos": "both"
        }
        selected_type = type_mapping.get(filter_type)
        
        # Filtrar clientes
        filtered_clients = self.clients
        
        # Filtrar por tipo
        if selected_type:
            filtered_clients = [c for c in filtered_clients if c.client_type == selected_type]
            
        # Filtrar por término de búsqueda
        if search_term:
            filtered_clients = [
                c for c in filtered_clients 
                if search_term in c.name.lower() or 
                   search_term in c.business_name.lower() or
                   search_term in (c.rut.lower() if c.rut else "") or
                   search_term in (c.contact_person.lower() if c.contact_person else "")
            ]
        
        # Mostrar mensaje si no hay clientes
        if not filtered_clients:
            no_results = ctk.CTkLabel(
                self.clients_frame,
                text="No se encontraron clientes",
                font=ctk.CTkFont(size=14),
                text_color="gray"
            )
            no_results.pack(pady=20)
            return
        
        # Crear elementos visuales para cada cliente
        for i, client in enumerate(filtered_clients):
            # Alternar colores para mejor visualización
            bg_color = "#F0F0F0" if i % 2 == 0 else "#FFFFFF"
            
            client_frame = ctk.CTkFrame(self.clients_frame)
            client_frame.pack(fill="x", pady=2)
            
            # Al hacer clic, seleccionar el cliente
            client_frame.bind("<Button-1>", lambda e, c=client: self._select_client(c))
            
            # Nombre del cliente
            name_label = ctk.CTkLabel(
                client_frame,
                text=client.name,
                font=ctk.CTkFont(weight="bold")
            )
            name_label.bind("<Button-1>", lambda e, c=client: self._select_client(c))
            name_label.pack(anchor="w", pady=(5, 0), padx=10)
            
            # RUT
            info_frame = ctk.CTkFrame(client_frame, fg_color="transparent")
            info_frame.pack(fill="x", padx=10, pady=(0, 5))
            
            rut_label = ctk.CTkLabel(
                info_frame,
                text=f"RUT: {client.rut}" if client.rut else "",
                font=ctk.CTkFont(size=12)
            )
            rut_label.bind("<Button-1>", lambda e, c=client: self._select_client(c))
            rut_label.pack(side="left")
            
            # Tipo
            type_mapping = {
                "buyer": "Comprador",
                "supplier": "Proveedor",
                "both": "Ambos"
            }
            
            type_label = ctk.CTkLabel(
                info_frame,
                text=type_mapping.get(client.client_type, ""),
                font=ctk.CTkFont(size=12),
                text_color="gray50"
            )
            type_label.bind("<Button-1>", lambda e, c=client: self._select_client(c))
            type_label.pack(side="right")
    
    def _apply_filter(self, *args):
        """Aplica los filtros de búsqueda."""
        self._update_clients_list()
    
    def _select_client(self, client):
        """
        Selecciona un cliente y muestra sus detalles.
        
        Args:
            client: Objeto Cliente a seleccionar
        """
        self.current_client = client
        
        # Rellenar formulario con datos del cliente
        self.form_vars["name"].set(client.name)
        self.form_vars["business_name"].set(client.business_name)
        self.form_vars["rut"].set(client.rut)
        self.form_vars["address"].set(client.address or "")
        self.form_vars["phone"].set(client.phone or "")
        self.form_vars["email"].set(client.email or "")
        self.form_vars["contact_person"].set(client.contact_person or "")
        self.form_vars["notes"].set(client.notes or "")
        self.form_vars["client_type"].set(client.client_type)
        
        # Cargar datos bancarios
        self.form_vars["bank_name"].set(client.bank_name if hasattr(client, 'bank_name') else "")
        self.form_vars["account_type"].set(client.account_type if hasattr(client, 'account_type') else "")
        self.form_vars["account_number"].set(client.account_number if hasattr(client, 'account_number') else "")
        self.form_vars["account_holder"].set(client.account_holder if hasattr(client, 'account_holder') else "")
        
        # Activar botones de guardar y eliminar
        self.save_btn.configure(state="normal")
        self.delete_btn.configure(state="normal")
        
        # Activar botón de añadir material
        self.add_material_btn.configure(state="normal")
        
        # Cambiar a la pestaña de detalles
        self.tabs.set("Detalles")
        
        # Cargar materiales del cliente
        self._load_client_materials()
    
    def _load_client_materials(self):
        """Carga los materiales asociados al cliente actual."""
        if not self.current_client:
            return
            
        # Obtener materiales del cliente
        self.client_materials = self.material_service.get_client_materials(self.current_client.id)
        
        # Limpiar lista actual
        for widget in self.materials_list.winfo_children():
            widget.destroy()
            
        # Si no hay materiales, mostrar mensaje
        if not self.client_materials:
            no_materials = ctk.CTkLabel(
                self.materials_list,
                text="Este cliente no tiene materiales asociados",
                font=ctk.CTkFont(size=14),
                text_color="gray"
            )
            no_materials.pack(pady=20)
            return
            
        # MEJORADO: Mostrar los materiales en la lista con más detalles
        for i, client_material in enumerate(self.client_materials):
            material = client_material.material
            
            # Crear frame para el material con borde
            material_frame = ctk.CTkFrame(self.materials_list, border_width=1, border_color=("gray70", "gray30"))
            material_frame.pack(fill="x", pady=5, padx=5)
            
            # Usar grid para mejor organización de la información
            material_frame.columnconfigure(0, weight=1)
            material_frame.columnconfigure(1, weight=0)
            
            # Nombre y color de estado según limpio/sucio
            header_frame = ctk.CTkFrame(material_frame, fg_color="transparent")
            header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=(10, 5))
            
            # Título con nombre del material
            material_title = ctk.CTkLabel(
                header_frame,
                text=material.name,
                font=ctk.CTkFont(size=16, weight="bold")
            )
            material_title.pack(side="left")
            
            # Etiqueta de estado con color
            is_clean = getattr(material, 'is_clean', None)
            if is_clean is not None:
                state_text = "LIMPIO" if is_clean else "SUCIO"
                state_color = ("#4CAF50", "#2E7D32") if is_clean else ("#F44336", "#C62828")
                
                state_label = ctk.CTkLabel(
                    header_frame,
                    text=state_text,
                    font=ctk.CTkFont(size=12, weight="bold"),
                    text_color=state_color,
                    corner_radius=5,
                    padx=8,
                    pady=2
                )
                state_label.pack(side="right")
            
            # Línea separadora
            separator = ctk.CTkFrame(material_frame, height=1, fg_color=("gray70", "gray30"))
            separator.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 5))
            
            # Detalles principales - columna izquierda
            details_frame = ctk.CTkFrame(material_frame, fg_color="transparent")
            details_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=5)
            
            # Información de Tipo
            type_frame = ctk.CTkFrame(details_frame, fg_color="transparent")
            type_frame.pack(fill="x", pady=2)
            
            ctk.CTkLabel(
                type_frame,
                text="Tipo:",
                font=ctk.CTkFont(size=12, weight="bold"),
                width=70,
                anchor="w"
            ).pack(side="left")
            
            ctk.CTkLabel(
                type_frame,
                text=material.material_type,
                font=ctk.CTkFont(size=12)
            ).pack(side="left")
            
            # Categoría si está disponible
            if hasattr(material, 'category') and material.category:
                category_frame = ctk.CTkFrame(details_frame, fg_color="transparent")
                category_frame.pack(fill="x", pady=2)
                
                ctk.CTkLabel(
                    category_frame,
                    text="Categoría:",
                    font=ctk.CTkFont(size=12, weight="bold"),
                    width=70,
                    anchor="w"
                ).pack(side="left")
                
                ctk.CTkLabel(
                    category_frame,
                    text=material.category,
                    font=ctk.CTkFont(size=12)
                ).pack(side="left")
            
            # Código si está disponible
            if hasattr(material, 'code') and material.code:
                code_frame = ctk.CTkFrame(details_frame, fg_color="transparent")
                code_frame.pack(fill="x", pady=2)
                
                ctk.CTkLabel(
                    code_frame,
                    text="Código:",
                    font=ctk.CTkFont(size=12, weight="bold"),
                    width=70,
                    anchor="w"
                ).pack(side="left")
                
                ctk.CTkLabel(
                    code_frame,
                    text=material.code,
                    font=ctk.CTkFont(size=12)
                ).pack(side="left")
            
            # Precio y configuración - columna derecha
            price_frame = ctk.CTkFrame(material_frame, fg_color="transparent")
            price_frame.grid(row=2, column=1, sticky="nsew", padx=10, pady=5)
            
            # Precio con formato
            price_label = ctk.CTkLabel(
                price_frame,
                text=f"${client_material.price:,.0f} CLP/kg",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color=("#2196F3", "#42A5F5")
            )
            price_label.pack(anchor="e")
            
            # Indicador de impuestos
            if client_material.includes_tax:
                tax_label = ctk.CTkLabel(
                    price_frame,
                    text="Incluye impuestos",
                    font=ctk.CTkFont(size=10),
                    text_color="gray50"
                )
                tax_label.pack(anchor="e")
            
            # Descripción si está disponible
            if hasattr(material, 'description') and material.description:
                desc_frame = ctk.CTkFrame(material_frame, fg_color=("gray95", "gray20"))
                desc_frame.grid(row=3, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 5))
                
                ctk.CTkLabel(
                    desc_frame,
                    text="Descripción:",
                    font=ctk.CTkFont(size=12, weight="bold"),
                    anchor="w"
                ).pack(fill="x", padx=5, pady=(5, 0))
                
                ctk.CTkLabel(
                    desc_frame,
                    text=material.description,
                    font=ctk.CTkFont(size=12),
                    wraplength=400,
                    justify="left",
                    anchor="w"
                ).pack(fill="x", padx=5, pady=(0, 5))
            
            # Notas del cliente sobre este material
            if client_material.notes:
                notes_frame = ctk.CTkFrame(material_frame, fg_color=("gray95", "gray20"))
                notes_frame.grid(row=4, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 5))
                
                ctk.CTkLabel(
                    notes_frame,
                    text="Notas:",
                    font=ctk.CTkFont(size=12, weight="bold"),
                    anchor="w"
                ).pack(fill="x", padx=5, pady=(5, 0))
                
                ctk.CTkLabel(
                    notes_frame,
                    text=client_material.notes,
                    font=ctk.CTkFont(size=12),
                    wraplength=400,
                    justify="left",
                    anchor="w"
                ).pack(fill="x", padx=5, pady=(0, 5))
            
            # Botones de acción
            actions_frame = ctk.CTkFrame(material_frame, fg_color="transparent")
            actions_frame.grid(row=5, column=0, columnspan=2, sticky="ew", padx=10, pady=(5, 10))
            
            # Botón para ver detalles completos
            ctk.CTkButton(
                actions_frame,
                text="Ver Detalles",
                command=lambda cm=client_material: self._show_material_details(cm),
                width=100,
                height=30,
                fg_color=("#1E88E5", "#1565C0")
            ).pack(side="left", padx=(0, 5))
            
            # Botón editar
            ctk.CTkButton(
                actions_frame,
                text="Editar",
                command=lambda cm=client_material: self._show_edit_material_dialog(cm),
                width=80,
                height=30,
                fg_color="#2D6A6A"
            ).pack(side="left", padx=5)
            
            # Botón eliminar
            ctk.CTkButton(
                actions_frame,
                text="Eliminar",
                command=lambda cm=client_material: self._remove_client_material(cm),
                width=80,
                height=30,
                fg_color="#E76F51"
            ).pack(side="left", padx=5)
    
    # NUEVO: Método para mostrar detalles completos del material
    def _show_material_details(self, client_material):
        """
        Muestra una ventana con todos los detalles del material.
        
        Args:
            client_material: Objeto ClientMaterial a mostrar
        """
        material = client_material.material
        
        # Crear ventana de detalles
        detail_window = ctk.CTkToplevel(self)
        detail_window.title(f"Detalles del Material - {material.name}")
        detail_window.geometry("600x500")
        detail_window.resizable(True, True)
        
        # Centrar ventana
        detail_window.update_idletasks()
        width = detail_window.winfo_width()
        height = detail_window.winfo_height()
        x = (detail_window.winfo_screenwidth() // 2) - (width // 2)
        y = (detail_window.winfo_screenheight() // 2) - (height // 2)
        detail_window.geometry(f'+{x}+{y}')
        
        # Frame principal con scroll para todos los detalles
        main_frame = ctk.CTkScrollableFrame(detail_window)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Encabezado con nombre y estado
        header_frame = ctk.CTkFrame(main_frame, fg_color=("gray95", "gray15"), corner_radius=10)
        header_frame.pack(fill="x", pady=(0, 15))
        
        # Nombre del material (título grande)
        title_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_frame.pack(fill="x", padx=15, pady=(15, 5))
        
        ctk.CTkLabel(
            title_frame,
            text=material.name,
            font=ctk.CTkFont(size=24, weight="bold")
        ).pack(side="left")
        
        # Estado (Limpio/Sucio) con color
        is_clean = getattr(material, 'is_clean', None)
        if is_clean is not None:
            state_text = "LIMPIO" if is_clean else "SUCIO"
            state_color = ("#4CAF50", "#2E7D32") if is_clean else ("#F44336", "#C62828")
            
            state_frame = ctk.CTkFrame(header_frame, fg_color=state_color, corner_radius=5)
            state_frame.pack(side="right", padx=15, pady=15)
            
            ctk.CTkLabel(
                state_frame,
                text=state_text,
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color="white"
            ).pack(padx=10, pady=5)
        
        # Tipo y categoría
        type_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        type_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        type_text = material.material_type
        if hasattr(material, 'category') and material.category:
            type_text += f" - {material.category}"
        
        ctk.CTkLabel(
            type_frame,
            text=type_text,
            font=ctk.CTkFont(size=16),
            text_color="gray50"
        ).pack(side="left")
        
        # Sección de precios con estilo destacado
        price_section = ctk.CTkFrame(main_frame, fg_color=("#E3F2FD", "#0D47A1"), corner_radius=10)
        price_section.pack(fill="x", pady=15)
        
        # Título de la sección
        ctk.CTkLabel(
            price_section,
            text="Información de Precio",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=("black", "white")
        ).pack(anchor="w", padx=15, pady=(15, 10))
        
        # Precio con formato
        price_info = ctk.CTkFrame(price_section, fg_color="transparent")
        price_info.pack(fill="x", padx=15, pady=(0, 5))
        
        ctk.CTkLabel(
            price_info,
            text="Precio por kg:",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=("black", "white"),
            width=120,
            anchor="w"
        ).pack(side="left")
        
        ctk.CTkLabel(
            price_info,
            text=f"${client_material.price:,.0f} CLP",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=("black", "white")
        ).pack(side="left", padx=10)
        
        # Impuestos
        tax_info = ctk.CTkFrame(price_section, fg_color="transparent")
        tax_info.pack(fill="x", padx=15, pady=(0, 15))
        
        ctk.CTkLabel(
            tax_info,
            text="Impuestos:",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=("black", "white"),
            width=120,
            anchor="w"
        ).pack(side="left")
        
        tax_status = "Incluidos en el precio" if client_material.includes_tax else "No incluidos"
        ctk.CTkLabel(
            tax_info,
            text=tax_status,
            font=ctk.CTkFont(size=14),
            text_color=("black", "white")
        ).pack(side="left", padx=10)
        
        # Sección de detalles del material
        details_section = ctk.CTkFrame(main_frame, corner_radius=10)
        details_section.pack(fill="x", pady=15)
        
        # Título de la sección
        ctk.CTkLabel(
            details_section,
            text="Propiedades del Material",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=15, pady=(15, 10))
        
        # Tabla de propiedades
        property_table = ctk.CTkFrame(details_section, fg_color="transparent")
        property_table.pack(fill="x", padx=15, pady=(0, 15))
        
        # Función para añadir una fila de propiedad
        def add_property_row(label, value, row, highlight=False):
            if value is None or value == "":
                return row  # No añadir filas vacías
                
            bg_color = ("gray90", "gray25") if highlight else "transparent"
            
            prop_frame = ctk.CTkFrame(property_table, fg_color=bg_color)
            prop_frame.grid(row=row, column=0, sticky="ew", pady=1)
            prop_frame.columnconfigure(1, weight=1)
            
            ctk.CTkLabel(
                prop_frame,
                text=f"{label}:",
                font=ctk.CTkFont(size=13, weight="bold"),
                width=150,
                anchor="w"
            ).grid(row=0, column=0, padx=5, pady=5, sticky="w")
            
            ctk.CTkLabel(
                prop_frame,
                text=str(value),
                font=ctk.CTkFont(size=13),
                anchor="w",
                wraplength=350,
                justify="left"
            ).grid(row=0, column=1, padx=5, pady=5, sticky="w")
            
            return row + 1
        
        # Añadir todas las propiedades disponibles del material
        row_index = 0
        row_index = add_property_row("ID", getattr(material, 'id', ""), row_index)
        row_index = add_property_row("Tipo", material.material_type, row_index, True)
        row_index = add_property_row("Categoría", getattr(material, 'category', ""), row_index)
        row_index = add_property_row("Código", getattr(material, 'code', ""), row_index)
        row_index = add_property_row("Estado", "Limpio" if getattr(material, 'is_clean', None) else "Sucio" if getattr(material, 'is_clean', None) is not None else "No especificado", row_index, True)
        row_index = add_property_row("Densidad", getattr(material, 'density', ""), row_index)
        row_index = add_property_row("Unidad", getattr(material, 'unit', ""), row_index)
        
        # Iterar dinámicamente sobre todos los atributos para no perder ninguno
        for attr_name in dir(material):
            # Ignorar atributos privados y métodos
            if attr_name.startswith('_') or callable(getattr(material, attr_name)):
                continue
                
            # Ignorar atributos ya mostrados
            if attr_name in ['id', 'name', 'material_type', 'category', 'code', 'is_clean', 'density', 'unit', 'description']:
                continue
                
            attr_value = getattr(material, attr_name)
            if attr_value is not None and attr_value != "":
                # Convertir nombre de atributo de snake_case a formato título
                display_name = " ".join(word.capitalize() for word in attr_name.split('_'))
                row_index = add_property_row(display_name, attr_value, row_index)
        
        # Sección de descripción si existe
        if hasattr(material, 'description') and material.description:
            desc_section = ctk.CTkFrame(main_frame, corner_radius=10)
            desc_section.pack(fill="x", pady=15)
            
            ctk.CTkLabel(
                desc_section,
                text="Descripción",
                font=ctk.CTkFont(size=16, weight="bold")
            ).pack(anchor="w", padx=15, pady=(15, 5))
            
            ctk.CTkLabel(
                desc_section,
                text=material.description,
                font=ctk.CTkFont(size=13),
                wraplength=520,
                justify="left"
            ).pack(fill="x", padx=15, pady=(0, 15))
        
        # Sección de notas del cliente si existen
        if client_material.notes:
            notes_section = ctk.CTkFrame(main_frame, corner_radius=10)
            notes_section.pack(fill="x", pady=15)
            
            ctk.CTkLabel(
                notes_section,
                text="Notas específicas para este cliente",
                font=ctk.CTkFont(size=16, weight="bold")
            ).pack(anchor="w", padx=15, pady=(15, 5))
            
            ctk.CTkLabel(
                notes_section,
                text=client_material.notes,
                font=ctk.CTkFont(size=13),
                wraplength=520,
                justify="left"
            ).pack(fill="x", padx=15, pady=(0, 15))
        
        # Botón para cerrar
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=15)
        
        ctk.CTkButton(
            btn_frame,
            text="Cerrar",
            command=detail_window.destroy,
            width=100
        ).pack(side="right", padx=5)
        
        # Botón para editar
        ctk.CTkButton(
            btn_frame,
            text="Editar",
            command=lambda: [detail_window.destroy(), self._show_edit_material_dialog(client_material)],
            width=100,
            fg_color="#2D6A6A"
        ).pack(side="right", padx=5)
        
        # Hacer modal
        detail_window.transient(self)
        detail_window.grab_set()
    
    def _create_client(self):
        """Resetea el formulario para crear un nuevo cliente."""
        self.current_client = None
        
        # Limpiar formulario
        for var in self.form_vars.values():
            var.set("")
        self.form_vars["client_type"].set("both")
        
        # Activar botón guardar y desactivar botón eliminar
        self.save_btn.configure(state="normal")
        self.delete_btn.configure(state="disabled")
        
        # Desactivar botón de añadir material
        self.add_material_btn.configure(state="disabled")
        
        # Cambiar a pestaña de detalles
        self.tabs.set("Detalles")
        
        # Limpiar lista de materiales
        for widget in self.materials_list.winfo_children():
            widget.destroy()
            
        # Dar foco al campo de nombre
        self.name_entry.focus_set()
    
    def _save_client(self):
        """Guarda los cambios del cliente actual."""
        # Validar campos requeridos
        if not self.form_vars["name"].get().strip():
            messagebox.showerror("Error", "El nombre es obligatorio")
            return
            
        if not self.form_vars["business_name"].get().strip():
            messagebox.showerror("Error", "La razón social es obligatoria")
            return
            
        if not self.form_vars["rut"].get().strip():
            messagebox.showerror("Error", "El RUT es obligatorio")
            return
        
        # Crear o actualizar el objeto cliente
        if self.current_client:
            # Actualizar cliente existente
            client = self.current_client
        else:
            # Crear nuevo cliente
            client = Client()
            
        # Actualizar propiedades
        client.name = self.form_vars["name"].get().strip()
        client.business_name = self.form_vars["business_name"].get().strip()
        client.rut = self.form_vars["rut"].get().strip()
        client.address = self.form_vars["address"].get().strip()
        client.phone = self.form_vars["phone"].get().strip()
        client.email = self.form_vars["email"].get().strip()
        client.contact_person = self.form_vars["contact_person"].get().strip()
        client.notes = self.form_vars["notes"].get().strip()
        client.client_type = self.form_vars["client_type"].get()
        client.is_active = True
        
        # Guardar datos bancarios
        client.bank_name = self.form_vars["bank_name"].get().strip()
        client.account_type = self.form_vars["account_type"].get().strip()
        client.account_number = self.form_vars["account_number"].get().strip()
        client.account_holder = self.form_vars["account_holder"].get().strip()
        
        # Guardar en base de datos
        success = self.client_service.save_client(client)
        
        if success:
            action = "actualizado" if self.current_client else "creado"
            messagebox.showinfo("Éxito", f"Cliente {action} correctamente")
            
            # Actualizar cliente actual
            self.current_client = client
            
            # Recargar lista de clientes
            self._load_clients()
            
            # Habilitar botón de añadir material si es un cliente existente
            self.add_material_btn.configure(state="normal")
        else:
            messagebox.showerror("Error", "Error al guardar el cliente")
    
    def _delete_client(self):
        """Elimina el cliente actual."""
        if not self.current_client:
            return
            
        confirm = messagebox.askyesno(
            "Confirmar eliminación", 
            f"¿Está seguro de eliminar el cliente {self.current_client.name}?"
        )
        
        if confirm:
            success = self.client_service.delete_client(self.current_client.id)
            
            if success:
                messagebox.showinfo("Éxito", "Cliente eliminado correctamente")
                
                # Recargar lista de clientes
                self._load_clients()
                
                # Limpiar formulario
                self._create_client()
            else:
                messagebox.showerror("Error", "Error al eliminar el cliente")
    
    def _show_add_material_dialog(self):
        """Muestra el diálogo para añadir un material al cliente."""
        if not self.current_client:
            messagebox.showerror("Error", "Debe seleccionar un cliente primero")
            return
        
        # Obtener lista de materiales disponibles para este cliente
        available_materials = self.material_service.get_available_materials_for_client(
            self.current_client.id)
        
        if not available_materials:
            messagebox.showinfo("Información", 
                             f"No hay materiales disponibles para asignar a {self.current_client.name}")
            return
        
        # Crear ventana de diálogo
        dialog = ctk.CTkToplevel(self)
        dialog.title(f"Añadir Material a {self.current_client.name}")
        dialog.geometry("600x600")
        
        # Frame contenedor principal con scroll
        main_frame = ctk.CTkScrollableFrame(dialog)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Título
        ctk.CTkLabel(
            main_frame,
            text="Seleccione Material",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=(0, 20), anchor="w")
        
        # Variables
        material_var = tk.StringVar()
        price_var = tk.StringVar(value="0")
        tax_var = tk.BooleanVar(value=False)
        notes_var = tk.StringVar()
        
        # MEJORADO: Crear diccionario para mapear nombres a objetos material con detalles
        material_map = {}
        material_options = []
        
        for m in available_materials:
            # Crear texto para mostrar en el combo
            display_text = f"{m.name} ({m.material_type}"
            if hasattr(m, 'is_clean'):
                state = "Limpio" if m.is_clean else "Sucio"
                display_text += f" - {state}"
            display_text += ")"
            
            # Guardar mapping
            material_map[display_text] = m
            material_options.append(display_text)
        
        # Marco de selección de material
        selection_frame = ctk.CTkFrame(main_frame, corner_radius=8)
        selection_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            selection_frame,
            text="Material:",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", padx=15, pady=(15, 5))
        
        # Combobox para seleccionar material
        if material_options:
            material_dropdown = ctk.CTkComboBox(
                selection_frame,
                values=material_options,
                variable=material_var,
                width=500,
                state="readonly"
            )
            material_dropdown.pack(padx=15, pady=(0, 15), fill="x")
            
            # Seleccionar el primer material por defecto
            material_var.set(material_options[0])
        else:
            ctk.CTkLabel(
                selection_frame, 
                text="No hay materiales disponibles", 
                text_color="red"
            ).pack(pady=10)
            
            # Botón para cerrar
            ctk.CTkButton(
                selection_frame,
                text="Cerrar",
                command=dialog.destroy
            ).pack(pady=20)
            return
        
        # NUEVO: Frame para mostrar los detalles del material seleccionado
        self.preview_frame = ctk.CTkFrame(main_frame)
        self.preview_frame.pack(fill="x", pady=10)
        
        # Función para actualizar los detalles del material seleccionado
        def update_material_preview(*args):
            # Limpiar frame de vista previa
            for widget in self.preview_frame.winfo_children():
                widget.destroy()
                
            selected_material = material_map.get(material_var.get())
            
            if not selected_material:
                return
                
            # Título de sección
            ctk.CTkLabel(
                self.preview_frame,
                text="Detalles del Material",
                font=ctk.CTkFont(size=16, weight="bold")
            ).pack(anchor="w", padx=15, pady=(15, 10))
            
            # Tabla de propiedades
            details_table = ctk.CTkFrame(self.preview_frame, fg_color="transparent")
            details_table.pack(fill="x", padx=15, pady=(0, 15))
            
            # Propiedades básicas
            row = 0
            
            # Tipo y estado
            type_text = selected_material.material_type
            if hasattr(selected_material, 'is_clean'):
                state = "Limpio" if selected_material.is_clean else "Sucio"
                type_text += f" - {state}"
                
            # Mostrar propiedades en filas
            properties = [
                ("Tipo", type_text),
            ]
            
            # Añadir categoría si existe
            if hasattr(selected_material, 'category') and selected_material.category:
                properties.append(("Categoría", selected_material.category))
            
            # Añadir código si existe
            if hasattr(selected_material, 'code') and selected_material.code:
                properties.append(("Código", selected_material.code))
                
            # Mostrar descripción si existe
            if hasattr(selected_material, 'description') and selected_material.description:
                properties.append(("Descripción", selected_material.description))
            
            # Crear filas de propiedades
            for i, (prop_name, prop_value) in enumerate(properties):
                # Alternar colores
                bg_color = "transparent" if i % 2 == 0 else ("gray95", "gray25")
                
                prop_row = ctk.CTkFrame(details_table, fg_color=bg_color)
                prop_row.pack(fill="x", pady=1)
                prop_row.columnconfigure(1, weight=1)
                
                # Nombre de la propiedad
                ctk.CTkLabel(
                    prop_row,
                    text=f"{prop_name}:",
                    font=ctk.CTkFont(size=13, weight="bold"),
                    width=100,
                    anchor="w"
                ).grid(row=0, column=0, padx=10, pady=5, sticky="w")
                
                # Valor de la propiedad
                ctk.CTkLabel(
                    prop_row,
                    text=str(prop_value),
                    font=ctk.CTkFont(size=13),
                    anchor="w",
                    wraplength=400,
                    justify="left"
                ).grid(row=0, column=1, padx=10, pady=5, sticky="w")
        
        # Vincular cambio de selección con la actualización de vista previa
        material_var.trace_add("write", update_material_preview)
        # Actualizar vista previa inicial
        update_material_preview()
        
        # Frame para configuración de precio
        price_config_frame = ctk.CTkFrame(main_frame, corner_radius=8)
        price_config_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            price_config_frame,
            text="Configuración de Precio",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=15, pady=(15, 10))
        
        # Precio con formato CLP
        price_frame = ctk.CTkFrame(price_config_frame, fg_color="transparent")
        price_frame.pack(fill="x", padx=15, pady=(0, 10))
        
        ctk.CTkLabel(
            price_frame,
            text="Precio por kilogramo:",
            font=ctk.CTkFont(size=14),
            anchor="w",
            width=150
        ).pack(side="left")
        
        # Campo de precio con símbolo CLP
        price_entry_frame = ctk.CTkFrame(price_frame, fg_color="transparent")
        price_entry_frame.pack(side="left", fill="x", expand=True)
        
        ctk.CTkLabel(
            price_entry_frame,
            text="$",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="left", padx=(0, 5))
        
        price_entry = ctk.CTkEntry(price_entry_frame, textvariable=price_var, width=120)
        price_entry.pack(side="left")
        
        ctk.CTkLabel(
            price_entry_frame,
            text="CLP / kg",
            font=ctk.CTkFont(size=14)
        ).pack(side="left", padx=5)
        
        # Incluye impuesto
        tax_frame = ctk.CTkFrame(price_config_frame, fg_color="transparent")
        tax_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        tax_check = ctk.CTkCheckBox(
            tax_frame,
            text="El precio incluye impuestos",
            variable=tax_var,
            onvalue=True,
            offvalue=False,
            font=ctk.CTkFont(size=14)
        )
        tax_check.pack(anchor="w")
        
        # Notas específicas para este cliente
        notes_frame = ctk.CTkFrame(main_frame, corner_radius=8)
        notes_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            notes_frame,
            text="Notas",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=15, pady=(15, 5))
        
        ctk.CTkLabel(
            notes_frame,
            text="Observaciones específicas sobre este material para este cliente:",
            font=ctk.CTkFont(size=12)
        ).pack(anchor="w", padx=15, pady=(0, 5))
        
        notes_entry = ctk.CTkEntry(notes_frame, textvariable=notes_var, height=60)
        notes_entry.pack(fill="x", padx=15, pady=(0, 15))
        
        # Mensaje de error
        error_label = ctk.CTkLabel(main_frame, text="", text_color="red")
        error_label.pack(fill="x", pady=(10, 0))
        
        # Botones de acción
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=20)
        
        def on_add_material():
            if not material_var.get():
                error_label.configure(text="Debe seleccionar un material")
                return
            
            try:
                price = float(price_var.get().replace(",", ".").replace("$", ""))
                if price < 0:
                    error_label.configure(text="El precio no puede ser negativo")
                    return
            except ValueError:
                error_label.configure(text="El precio debe ser un número válido")
                return
                
            selected_material = material_map.get(material_var.get())
            if not selected_material:
                error_label.configure(text="Material no válido")
                return
                
            # Añadir material al cliente
            success = self.material_service.assign_material_to_client(
                client_id=self.current_client.id,
                material_id=selected_material.id,
                price=price,
                includes_tax=tax_var.get(),
                notes=notes_var.get()
            )
            
            if success:
                messagebox.showinfo("Éxito", f"Material '{selected_material.name}' añadido correctamente")
                dialog.destroy()
                # Actualizar la lista de materiales del cliente
                self._load_client_materials()
            else:
                error_label.configure(text="No se pudo añadir el material")
        
        # Botón cancelar
        ctk.CTkButton(
            btn_frame,
            text="Cancelar",
            command=dialog.destroy,
            fg_color="gray50",
            width=100,
            height=32
        ).pack(side="left", padx=20)
        
        # Botón guardar
        ctk.CTkButton(
            btn_frame,
            text="Añadir Material",
            command=on_add_material,
            width=120,
            height=32,
            font=ctk.CTkFont(weight="bold")
        ).pack(side="right", padx=20)
        
        # Centrar la ventana
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f'{width}x{height}+{x}+{y}')
        
        # Hacer modal
        dialog.transient(self)
        dialog.grab_set()
    
    def _show_edit_material_dialog(self, client_material):
        """
        Muestra el diálogo para editar un material del cliente.
        
        Args:
            client_material: Objeto ClientMaterial a editar
        """
        material = client_material.material
        
        # Crear ventana de diálogo
        dialog = ctk.CTkToplevel(self)
        dialog.title(f"Editar Material - {material.name}")
        dialog.geometry("600x600")
        
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
        title_frame = ctk.CTkFrame(main_frame, fg_color=("gray95", "gray15"), corner_radius=10)
        title_frame.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(
            title_frame, 
            text=f"Editar {material.name}",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=(15, 5), padx=15)
        
        # Subtítulo con información del material
        subtitle_text = f"Tipo: {material.material_type}"
        
        # Añadir estado si está disponible
        if hasattr(material, 'is_clean'):
            state = "Limpio" if material.is_clean else "Sucio"
            subtitle_text += f" - {state}"
        
        ctk.CTkLabel(
            title_frame,
            text=subtitle_text,
            font=ctk.CTkFont(size=14),
            text_color="gray50"
        ).pack(pady=(0, 15), padx=15)
        
        # Variables
        price_var = tk.StringVar(value=str(client_material.price))
        tax_var = tk.BooleanVar(value=client_material.includes_tax)
        notes_var = tk.StringVar(value=client_material.notes or "")
        
        # Información del material
        info_frame = ctk.CTkFrame(main_frame, corner_radius=8)
        info_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            info_frame,
            text="Información del Material",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=15, pady=(15, 10))
        
        # Tabla de propiedades
        properties_table = ctk.CTkFrame(info_frame, fg_color="transparent")
        properties_table.pack(fill="x", padx=15, pady=(0, 15))
        
        # Añadir propiedades relevantes
        properties = []
        
        # Tipo de material
        properties.append(("Tipo", material.material_type))
        
        # Categoría si existe
        if hasattr(material, 'category') and material.category:
            properties.append(("Categoría", material.category))
        
        # Estado limpio/sucio si existe
        if hasattr(material, 'is_clean'):
            state = "Limpio" if material.is_clean else "Sucio"
            properties.append(("Estado", state))
        
        # Código si existe
        if hasattr(material, 'code') and material.code:
            properties.append(("Código", material.code))
            
        # Descripción si existe
        if hasattr(material, 'description') and material.description:
            properties.append(("Descripción", material.description))
        
        # Crear tabla de propiedades
        for i, (prop_name, prop_value) in enumerate(properties):
            # Alternar colores
            bg_color = "transparent" if i % 2 == 0 else ("gray95", "gray25")
            
            prop_row = ctk.CTkFrame(properties_table, fg_color=bg_color)
            prop_row.pack(fill="x", pady=1)
            prop_row.columnconfigure(1, weight=1)
            
            # Nombre de la propiedad
            ctk.CTkLabel(
                prop_row,
                text=f"{prop_name}:",
                font=ctk.CTkFont(size=13, weight="bold"),
                width=100,
                anchor="w"
            ).grid(row=0, column=0, padx=10, pady=5, sticky="w")
            
            # Valor de la propiedad
            ctk.CTkLabel(
                prop_row,
                text=str(prop_value),
                font=ctk.CTkFont(size=13),
                anchor="w",
                wraplength=400
            ).grid(row=0, column=1, padx=10, pady=5, sticky="w")
        
        # Sección para editar el precio
        price_frame = ctk.CTkFrame(main_frame, corner_radius=8)
        price_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            price_frame,
            text="Configuración de Precio",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=15, pady=(15, 10))
        
        # Campo de precio
        price_input_frame = ctk.CTkFrame(price_frame, fg_color="transparent")
        price_input_frame.pack(fill="x", padx=15, pady=(0, 10))
        
        ctk.CTkLabel(
            price_input_frame,
            text="Precio por kilogramo:",
            font=ctk.CTkFont(size=14),
            width=150,
            anchor="w"
        ).pack(side="left")
        
        # Crear frame especial para el input del precio con símbolo
        price_entry_frame = ctk.CTkFrame(price_input_frame, fg_color="transparent")
        price_entry_frame.pack(side="left")
        
        # Símbolo de peso
        ctk.CTkLabel(
            price_entry_frame,
            text="$",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="left", padx=(0, 5))
        
        # Entrada para el precio
        price_entry = ctk.CTkEntry(price_entry_frame, textvariable=price_var, width=120)
        price_entry.pack(side="left")
        
        # Unidad monetaria
        ctk.CTkLabel(
            price_entry_frame,
            text="CLP / kg",
            font=ctk.CTkFont(size=14)
        ).pack(side="left", padx=5)
        
        # Incluye impuesto
        tax_frame = ctk.CTkFrame(price_frame, fg_color="transparent")
        tax_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        tax_check = ctk.CTkCheckBox(
            tax_frame,
            text="El precio incluye impuestos",
            variable=tax_var,
            onvalue=True,
            offvalue=False,
            font=ctk.CTkFont(size=14)
        )
        tax_check.pack(anchor="w")
        
        # Notas específicas para este cliente
        notes_frame = ctk.CTkFrame(main_frame, corner_radius=8)
        notes_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            notes_frame,
            text="Notas",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=15, pady=(15, 5))
        
        ctk.CTkLabel(
            notes_frame,
            text="Observaciones específicas sobre este material para este cliente:",
            font=ctk.CTkFont(size=12)
        ).pack(anchor="w", padx=15, pady=(0, 5))
        
        notes_entry = ctk.CTkEntry(notes_frame, textvariable=notes_var, height=60)
        notes_entry.pack(fill="x", padx=15, pady=(0, 15))
        
        # Mensaje de error
        error_label = ctk.CTkLabel(main_frame, text="", text_color="red")
        error_label.pack(fill="x", pady=(10, 0))
        
        # Botones
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=20)
        
        def on_edit_material():
            try:
                price = float(price_var.get().replace(",", ".").replace("$", ""))
                if price < 0:
                    error_label.configure(text="El precio no puede ser negativo")
                    return
            except ValueError:
                error_label.configure(text="El precio debe ser un número válido")
                return
                
            # Actualizar objeto
            client_material.price = price
            client_material.includes_tax = tax_var.get()
            client_material.notes = notes_var.get()
            
            # Guardar cambios
            success = self.material_service.update_client_material(client_material)
            
            if success:
                messagebox.showinfo("Éxito", "Material actualizado correctamente")
                dialog.destroy()
                # Actualizar lista de materiales
                self._load_client_materials()
            else:
                error_label.configure(text="No se pudo actualizar el material")
        
        # Botón cancelar
        ctk.CTkButton(
            btn_frame,
            text="Cancelar",
            command=dialog.destroy,
            fg_color="gray50",
            width=100,
            height=32
        ).pack(side="left", padx=20)
        
        # Botón actualizar
        ctk.CTkButton(
            btn_frame,
            text="Guardar Cambios",
            command=on_edit_material,
            width=140,
            height=32,
            font=ctk.CTkFont(weight="bold")
        ).pack(side="right", padx=20)
        
        # Hacer modal
        dialog.transient(self)
        dialog.grab_set()
    
    def _remove_client_material(self, client_material):
        """
        Elimina un material del cliente.
        
        Args:
            client_material: Objeto ClientMaterial a eliminar
        """
        confirm = messagebox.askyesno(
            "Confirmar eliminación", 
            f"¿Está seguro de eliminar el material '{client_material.material.name}' de este cliente?\n\n"
            f"Esta acción no se puede deshacer."
        )
        
        if confirm:
            success = self.material_service.remove_material_from_client(client_material.id)
            
            if success:
                messagebox.showinfo("Éxito", "Material eliminado correctamente")
                # Actualizar lista de materiales
                self._load_client_materials()
            else:
                messagebox.showerror("Error", "No se pudo eliminar el material")