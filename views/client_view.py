"""
Vista para la gestión de clientes en ISMAPP.
"""
import tkinter as tk
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
        # Crear panel dividido (split view)
        self.split_view = ctk.CTkPanedWindow(self, orientation="horizontal")
        self.split_view.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # Panel izquierdo (lista de clientes)
        self.left_panel = ctk.CTkFrame(self.split_view)
        self.left_panel.grid_rowconfigure(1, weight=1)
        self.left_panel.grid_columnconfigure(0, weight=1)
        
        # Panel derecho (detalle del cliente)
        self.right_panel = ctk.CTkFrame(self.split_view)
        self.right_panel.grid_rowconfigure(0, weight=1)
        self.right_panel.grid_columnconfigure(0, weight=1)
        
        self.split_view.add(self.left_panel)
        self.split_view.add(self.right_panel)
        
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
        self.tabs.add("Materiales")
        
        # Configurar pestaña de detalles
        self._setup_details_tab(self.tabs.tab("Detalles"))
        
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
            
        # Mostrar los materiales en la lista
        for i, client_material in enumerate(self.client_materials):
            material = client_material.material
            
            # Crear frame para el material
            material_frame = ctk.CTkFrame(self.materials_list)
            material_frame.pack(fill="x", pady=5)
            
            # Nombre y tipo de material
            header_frame = ctk.CTkFrame(material_frame, fg_color="transparent")
            header_frame.pack(fill="x", padx=10, pady=(5, 0))
            
            ctk.CTkLabel(
                header_frame,
                text=material.name,
                font=ctk.CTkFont(weight="bold")
            ).pack(side="left")
            
            ctk.CTkLabel(
                header_frame,
                text=material.material_type,
                font=ctk.CTkFont(size=12),
                text_color="gray50"
            ).pack(side="right")
            
            # Precio y detalles
            details_frame = ctk.CTkFrame(material_frame, fg_color="transparent")
            details_frame.pack(fill="x", padx=10, pady=(0, 5))
            
            # Precio
            price_text = f"Precio: ${client_material.price:.2f} / kg"
            if client_material.includes_tax:
                price_text += " (incluye impuestos)"
                
            ctk.CTkLabel(
                details_frame,
                text=price_text,
                font=ctk.CTkFont(size=12)
            ).pack(side="left")
            
            # Botones de acción
            actions_frame = ctk.CTkFrame(material_frame, fg_color="transparent")
            actions_frame.pack(fill="x", padx=10, pady=(0, 5))
            
            # Botón editar
            ctk.CTkButton(
                actions_frame,
                text="Editar",
                command=lambda cm=client_material: self._show_edit_material_dialog(cm),
                width=80,
                height=25,
                fg_color="#2D6A6A"
            ).pack(side="left", padx=(0, 5))
            
            # Botón eliminar
            ctk.CTkButton(
                actions_frame,
                text="Eliminar",
                command=lambda cm=client_material: self._remove_client_material(cm),
                width=80,
                height=25,
                fg_color="#E76F51"
            ).pack(side="left")
    
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
        
        # DEPURACIÓN: Verificar materiales disponibles
        print(f"DEBUG: Materiales disponibles para cliente #{self.current_client.id}:")
        for m in available_materials:
            print(f"- ID: {m.id}, Nombre: {m.name}")
        
        # Crear ventana de diálogo
        dialog = ctk.CTkToplevel(self)
        dialog.title(f"Añadir Material a {self.current_client.name}")
        dialog.geometry("500x500")
        
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
        price_var = tk.StringVar(value="0.0")
        tax_var = tk.BooleanVar(value=False)
        notes_var = tk.StringVar()
        
        # Material (desplegable)
        ctk.CTkLabel(main_frame, text="Material:").pack(anchor="w", pady=(10, 0))
        
        # Crear diccionario para mapear nombres a objetos material
        material_map = {f"{m.name} ({m.material_type})": m for m in available_materials}
        material_options = list(material_map.keys())
        
        # Verificar si hay opciones antes de crear el ComboBox
        if material_options:
            material_dropdown = ctk.CTkComboBox(
                main_frame,
                values=material_options,
                variable=material_var,
                width=300,
                state="readonly"
            )
            material_dropdown.pack(fill="x", pady=(0, 10))
            
            # Seleccionar el primer material por defecto
            material_var.set(material_options[0])
        else:
            # En caso de que la lista esté vacía por alguna razón (no debería pasar, pero por seguridad)
            ctk.CTkLabel(
                main_frame, 
                text="No hay materiales disponibles", 
                text_color="red"
            ).pack(pady=10)
            
            # Añadir un botón para cerrar el diálogo
            ctk.CTkButton(
                main_frame,
                text="Cerrar",
                command=dialog.destroy
            ).pack(pady=20)
            return
        
        # Precio
        ctk.CTkLabel(main_frame, text="Precio:").pack(anchor="w", pady=(10, 0))
        
        price_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        price_frame.pack(fill="x", pady=(0, 10))
        
        price_entry = ctk.CTkEntry(price_frame, textvariable=price_var)
        price_entry.pack(side="left", fill="x", expand=True)
        
        ctk.CTkLabel(price_frame, text="$ / kg").pack(side="right", padx=5)
        
        # Incluye impuesto
        tax_check = ctk.CTkCheckBox(
            main_frame,
            text="El precio incluye impuestos",
            variable=tax_var,
            onvalue=True,
            offvalue=False
        )
        tax_check.pack(anchor="w", pady=10)
        
        # Notas
        ctk.CTkLabel(main_frame, text="Notas:").pack(anchor="w", pady=(10, 0))
        notes_entry = ctk.CTkEntry(main_frame, textvariable=notes_var)
        notes_entry.pack(fill="x", pady=(0, 20))
        
        # Mensaje de error
        error_label = ctk.CTkLabel(main_frame, text="", text_color="red")
        error_label.pack(fill="x", pady=(10, 0))
        
        # Botones
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=20)
        
        def on_add_material():
            if not material_var.get():
                error_label.configure(text="Debe seleccionar un material")
                return
            
            try:
                price = float(price_var.get().replace(",", "."))
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
                messagebox.showinfo("Éxito", f"Material '{selected_material.name}' añadido")
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
            width=100
        ).pack(side="left", padx=20)
        
        # Botón guardar
        ctk.CTkButton(
            btn_frame,
            text="Añadir",
            command=on_add_material,
            width=100
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
        # Crear ventana de diálogo
        dialog = ctk.CTkToplevel(self)
        dialog.title(f"Editar Material - {client_material.material.name}")
        dialog.geometry("450x400")
        
        # Contenedor principal con scroll
        main_frame = ctk.CTkScrollableFrame(dialog)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Título
        ctk.CTkLabel(
            main_frame,
            text=f"Editar {client_material.material.name}",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=(0, 20), anchor="w")
        
        # Variables
        price_var = tk.StringVar(value=str(client_material.price))
        tax_var = tk.BooleanVar(value=client_material.includes_tax)
        notes_var = tk.StringVar(value=client_material.notes or "")
        
        # Información del material
        info_frame = ctk.CTkFrame(main_frame, fg_color=("#EDF6F9", "#202835"))
        info_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            info_frame,
            text=f"Tipo: {client_material.material.material_type}",
            font=ctk.CTkFont(size=12)
        ).pack(anchor="w", padx=10, pady=(10, 0))
        
        if client_material.material.description:
            ctk.CTkLabel(
                info_frame,
                text=f"Descripción: {client_material.material.description}",
                font=ctk.CTkFont(size=12),
                wraplength=380
            ).pack(anchor="w", padx=10, pady=(5, 10))
        
        # Formulario
        form_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        form_frame.pack(fill="x", pady=10)
        
        # Precio
        ctk.CTkLabel(form_frame, text="Precio:").pack(anchor="w", pady=(10, 0))
        
        price_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        price_frame.pack(fill="x", pady=(0, 10))
        
        price_entry = ctk.CTkEntry(price_frame, textvariable=price_var)
        price_entry.pack(side="left", fill="x", expand=True)
        
        ctk.CTkLabel(price_frame, text="$ / kg").pack(side="right", padx=5)
        
        # Incluye impuesto
        tax_check = ctk.CTkCheckBox(
            form_frame,
            text="El precio incluye impuestos",
            variable=tax_var,
            onvalue=True,
            offvalue=False
        )
        tax_check.pack(anchor="w", pady=10)
        
        # Notas
        ctk.CTkLabel(form_frame, text="Notas:").pack(anchor="w", pady=(10, 0))
        notes_entry = ctk.CTkEntry(form_frame, textvariable=notes_var, height=50)
        notes_entry.pack(fill="x", pady=(0, 10))
        
        # Mensaje de error
        error_label = ctk.CTkLabel(main_frame, text="", text_color="red")
        error_label.pack(fill="x", pady=(10, 0))
        
        # Botones
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=20)
        
        def on_edit_material():
            try:
                price = float(price_var.get().replace(",", "."))
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
            width=100
        ).pack(side="left", padx=10)
        
        # Botón actualizar
        ctk.CTkButton(
            btn_frame,
            text="Actualizar",
            command=on_edit_material,
            width=100
        ).pack(side="right", padx=10)
        
        # Centrar la ventana
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f'+{x}+{y}')
        
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
            f"¿Está seguro de eliminar el material '{client_material.material.name}' de este cliente?"
        )
        
        if confirm:
            success = self.material_service.remove_material_from_client(client_material.id)
            
            if success:
                messagebox.showinfo("Éxito", "Material eliminado correctamente")
                # Actualizar lista de materiales
                self._load_client_materials()
            else:
                messagebox.showerror("Error", "No se pudo eliminar el material")