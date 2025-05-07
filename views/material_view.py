"""
Vista para la gestión de materiales.
"""
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from models.material import Material, MaterialType, PlasticSubtype
from core.services.material_service import MaterialService

class MaterialView(ctk.CTkFrame):
    """Vista para la gestión de materiales."""
    
    def __init__(self, parent):
        """
        Inicializa la vista de materiales.
        
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
            self.material_service = MaterialService(self.data_manager)
        except AttributeError:
            messagebox.showerror("Error", "No se pudo acceder al gestor de datos")
            return
        
        # Variables para almacenar datos
        self.materials = []
        self.current_material = None
        self.filtered_materials = []
        
        # Crear UI
        self._create_ui()
        
        # Cargar datos iniciales
        self._load_materials()
    
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
            text="Gestión de Materiales",
            font=ctk.CTkFont(size=22, weight="bold")
        ).pack(side="left")
        
        # Botón para crear nuevo material
        self.add_button = ctk.CTkButton(
            header_frame,
            text="+ Nuevo Material",
            command=self._show_edit_dialog,
            width=150
        )
        self.add_button.pack(side="right", padx=10)
        
        # Frame para búsqueda y filtros
        search_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        search_frame.pack(fill="x", pady=(0, 15))
        
        # Barra de búsqueda
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *args: self._filter_materials())
        
        search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Buscar material...",
            width=300,
            textvariable=self.search_var
        )
        search_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        # Filtro de tipo de material
        filter_frame = ctk.CTkFrame(search_frame, fg_color="transparent")
        filter_frame.pack(side="right")
        
        ctk.CTkLabel(filter_frame, text="Mostrar:").pack(side="left", padx=(0, 5))
        
        self.filter_var = tk.StringVar(value="all")
        
        # Opciones de filtro
        filter_options = {
            "all": "Todos",
            MaterialType.PLASTIC: "Plásticos",
            MaterialType.CUSTOM: "Personalizados"
        }
        
        filter_menu = ctk.CTkOptionMenu(
            filter_frame,
            values=list(filter_options.values()),
            command=lambda choice: self._set_filter(
                next(key for key, value in filter_options.items() if value == choice)
            )
        )
        filter_menu.pack(side="left")
        
        # Frame para la tabla de materiales
        table_container = ctk.CTkFrame(self.main_container)
        table_container.pack(fill="both", expand=True)
        
        # Cabecera de la tabla
        columns = ["Nombre", "Tipo", "Subtipo", "Estado", "Acciones"]
        header_frame = ctk.CTkFrame(table_container, fg_color=("#DDDDDD", "#2B2B2B"))
        header_frame.pack(fill="x")
        
        # Configurar ancho de columnas
        widths = [0.3, 0.2, 0.2, 0.15, 0.15]  # Proporciones
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
        
        # Contenedor para filas de materiales
        self.material_rows_frame = ctk.CTkScrollableFrame(table_container, fg_color="transparent")
        self.material_rows_frame.pack(fill="both", expand=True)
    
    def _set_filter(self, filter_type):
        """
        Establece el filtro por tipo de material.
        
        Args:
            filter_type (str): Tipo de filtro a aplicar
        """
        self.filter_var.set(filter_type)
        self._filter_materials()
    
    def _load_materials(self):
        """Carga la lista de materiales desde la base de datos."""
        # Cargar materiales
        self.materials = self.material_service.get_all_materials()
        self._filter_materials()
    
    def _filter_materials(self):
        """Filtra la lista de materiales según búsqueda y filtros."""
        search_term = self.search_var.get().lower().strip()
        filter_type = self.filter_var.get()
        
        if filter_type == "all":
            # Filtrar solo por término de búsqueda
            if not search_term:
                self.filtered_materials = self.materials.copy()
            else:
                self.filtered_materials = [
                    material for material in self.materials
                    if (search_term in material.name.lower() or
                        search_term in material.description.lower() or
                        search_term in material.custom_subtype.lower())
                ]
        else:
            # Filtrar por tipo y término de búsqueda
            if not search_term:
                self.filtered_materials = [
                    material for material in self.materials
                    if material.material_type == filter_type
                ]
            else:
                self.filtered_materials = [
                    material for material in self.materials
                    if material.material_type == filter_type and
                       (search_term in material.name.lower() or
                        search_term in material.description.lower() or
                        search_term in material.custom_subtype.lower())
                ]
        
        self._update_material_table()
    
    def _update_material_table(self):
        """Actualiza la tabla de materiales en la UI."""
        # Limpiar tabla actual
        for widget in self.material_rows_frame.winfo_children():
            widget.destroy()
        
        # Verificar si hay materiales para mostrar
        if not self.filtered_materials:
            no_data_label = ctk.CTkLabel(
                self.material_rows_frame,
                text="No se encontraron materiales",
                font=ctk.CTkFont(size=14),
                text_color="gray60"
            )
            no_data_label.pack(pady=30)
            return
        
        # Crear filas para cada material
        for i, material in enumerate(self.filtered_materials):
            row_color = ("#F5F5F5", "#2D2D2D") if i % 2 == 0 else ("#FFFFFF", "#333333")
            row_frame = ctk.CTkFrame(self.material_rows_frame, fg_color=row_color, corner_radius=0)
            row_frame.pack(fill="x", pady=1)
            
            # Nombre
            name_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
            name_frame.pack(side="left", fill="both", expand=True, padx=2, pady=8)
            ctk.CTkLabel(name_frame, text=material.name).pack(anchor="w", padx=5)
            
            # Tipo
            type_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
            type_frame.pack(side="left", fill="both", expand=True, padx=2, pady=8)
            
            type_text = MaterialType.get_display_name(material.material_type)
            type_color = {
                MaterialType.PLASTIC: "#4CAF50",
                MaterialType.CUSTOM: "#FF9800"
            }.get(material.material_type, "gray60")
            
            ctk.CTkLabel(
                type_frame, 
                text=type_text,
                text_color=type_color,
                font=ctk.CTkFont(size=12, weight="bold")
            ).pack(anchor="w", padx=5)
            
            # Subtipo
            subtype_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
            subtype_frame.pack(side="left", fill="both", expand=True, padx=2, pady=8)
            
            subtype_text = ""
            if material.material_type == MaterialType.PLASTIC:
                if material.plastic_subtype == PlasticSubtype.OTHER:
                    subtype_text = material.custom_subtype
                else:
                    subtype_text = PlasticSubtype.get_display_name(material.plastic_subtype)
            else:
                subtype_text = material.custom_subtype if material.custom_subtype else "-"
                
            ctk.CTkLabel(subtype_frame, text=subtype_text).pack(anchor="w", padx=5)
            
            # Estado
            state_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
            state_frame.pack(side="left", fill="both", expand=True, padx=2, pady=8)
            
            if material.material_type == MaterialType.PLASTIC and material.is_plastic_subtype:
                state_text = "Limpio" if material.plastic_state == "clean" else "Sucio"
            else:
                state_text = "-"
                
            ctk.CTkLabel(state_frame, text=state_text).pack(anchor="w", padx=5)
            
            # Acciones
            actions_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
            actions_frame.pack(side="left", fill="both", padx=2, pady=3)
            
            # Botón editar
            edit_btn = ctk.CTkButton(
                actions_frame,
                text="✏️",
                width=30,
                command=lambda m=material: self._show_edit_dialog(m),
                fg_color=("#6E9075", "#2D6A6A")
            )
            edit_btn.pack(side="left", padx=2)
            
            # Botón eliminar
            delete_btn = ctk.CTkButton(
                actions_frame,
                text="🗑️",
                width=30,
                command=lambda m=material: self._confirm_delete(m),
                fg_color=("#BC7777", "#AA5555")
            )
            delete_btn.pack(side="left", padx=2)
    
    def _show_edit_dialog(self, material=None):
        """
        Muestra el diálogo para crear o editar un material.
        
        Args:
            material (Material, optional): Material a editar, None para crear nuevo
        """
        self.current_material = material or Material()
        
        # Crear ventana de diálogo
        dialog = ctk.CTkToplevel(self)
        dialog.title("Nuevo Material" if material is None else "Editar Material")
        dialog.geometry("600x650")
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
            text="Datos del Material",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=(0, 20), anchor="w")
        
        # Form fields
        form_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        form_frame.pack(fill="x", pady=10)
        
        # Variables para campos
        name_var = tk.StringVar(value=self.current_material.name)
        description_var = tk.StringVar(value=self.current_material.description)
        material_type_var = tk.StringVar(value=self.current_material.material_type)
        is_plastic_var = tk.BooleanVar(value=self.current_material.is_plastic_subtype)
        plastic_subtype_var = tk.StringVar(value=self.current_material.plastic_subtype)
        plastic_state_var = tk.StringVar(value=self.current_material.plastic_state or "clean")
        custom_subtype_var = tk.StringVar(value=self.current_material.custom_subtype)
        active_var = tk.BooleanVar(value=self.current_material.is_active)
        
        # Función para actualizar visibilidad de campos
        def update_fields(*args):
            material_type = material_type_var.get()
            
            # Mostrar/ocultar campos según el tipo de material
            if material_type == MaterialType.PLASTIC:
                plastic_fields_frame.grid()
                custom_subtype_label.grid_remove()
                custom_subtype_entry.grid_remove()
                
                # Actualizar campos de subtipo plástico
                is_plastic = is_plastic_var.get()
                subtype = plastic_subtype_var.get()
                
                if is_plastic:
                    plastic_subtype_label.grid()
                    plastic_subtype_menu.grid()
                    plastic_state_label.grid()
                    plastic_state_frame.grid()
                    
                    # Mostrar/ocultar campo de subtipo personalizado
                    if subtype == PlasticSubtype.OTHER:
                        custom_plastic_label.grid()
                        custom_plastic_entry.grid()
                    else:
                        custom_plastic_label.grid_remove()
                        custom_plastic_entry.grid_remove()
                else:
                    plastic_subtype_label.grid_remove()
                    plastic_subtype_menu.grid_remove()
                    plastic_state_label.grid_remove()
                    plastic_state_frame.grid_remove()
                    custom_plastic_label.grid_remove()
                    custom_plastic_entry.grid_remove()
            else:  # MaterialType.CUSTOM
                plastic_fields_frame.grid_remove()
                custom_subtype_label.grid()
                custom_subtype_entry.grid()
        
        # Nombre (requerido)
        ctk.CTkLabel(form_frame, text="Nombre*").grid(row=0, column=0, sticky="w", padx=5, pady=(10, 0))
        name_entry = ctk.CTkEntry(form_frame, textvariable=name_var)
        name_entry.grid(row=1, column=0, sticky="ew", padx=5, pady=(0, 10))
        name_entry.focus_set()  # Auto-focus
        
        # Descripción
        ctk.CTkLabel(form_frame, text="Descripción").grid(row=2, column=0, sticky="w", padx=5, pady=(10, 0))
        description_entry = ctk.CTkTextbox(form_frame, height=60)
        description_entry.grid(row=3, column=0, sticky="ew", padx=5, pady=(0, 10))
        description_entry.insert("1.0", self.current_material.description)
        
        # Tipo de material (requerido)
        ctk.CTkLabel(form_frame, text="Tipo de Material*").grid(row=4, column=0, sticky="w", padx=5, pady=(10, 0))
        
        type_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        type_frame.grid(row=5, column=0, sticky="ew", padx=5, pady=(0, 10))
        
        # Opciones para tipo de material (solo plástico y personalizado)
        plastic_rb = ctk.CTkRadioButton(
            type_frame, 
            text="Plástico", 
            variable=material_type_var, 
            value=MaterialType.PLASTIC,
            command=update_fields
        )
        plastic_rb.pack(side="left", padx=10)
        
        custom_rb = ctk.CTkRadioButton(
            type_frame, 
            text="Otro (Personalizado)", 
            variable=material_type_var, 
            value=MaterialType.CUSTOM,
            command=update_fields
        )
        custom_rb.pack(side="left", padx=10)
        
        # Frame para campos de materiales personalizados
        custom_subtype_label = ctk.CTkLabel(form_frame, text="Nombre del Material")
        custom_subtype_label.grid(row=6, column=0, sticky="w", padx=5, pady=(10, 0))
        
        custom_subtype_entry = ctk.CTkEntry(form_frame, textvariable=custom_subtype_var)
        custom_subtype_entry.grid(row=7, column=0, sticky="ew", padx=5, pady=(0, 10))
        
        # Frame para campos específicos de plásticos
        plastic_fields_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        plastic_fields_frame.grid(row=8, column=0, sticky="ew", padx=5, pady=(10, 0))
        
        # Checkbox para subtipo de plástico
        plastic_checkbox = ctk.CTkCheckBox(
            plastic_fields_frame,
            text="Es un subtipo específico de plástico",
            variable=is_plastic_var,
            command=update_fields
        )
        plastic_checkbox.pack(anchor="w", pady=(0, 10))
        
        # Subtipo de plástico (Caramelo, Chicle, Otro)
        plastic_subtype_label = ctk.CTkLabel(plastic_fields_frame, text="Subtipo de Plástico")
        plastic_subtype_label.pack(anchor="w", pady=(10, 0))
        
        plastic_subtypes = {
            PlasticSubtype.CANDY: "Caramelo",
            PlasticSubtype.GUM: "Chicle",
            PlasticSubtype.OTHER: "Otro"
        }
        
        plastic_subtype_menu = ctk.CTkOptionMenu(
            plastic_fields_frame,
            values=list(plastic_subtypes.values()),
            variable=plastic_subtype_var,
            command=lambda choice: plastic_subtype_var.set(
                next(key for key, value in plastic_subtypes.items() if value == choice)
            )
        )
        plastic_subtype_menu.pack(fill="x", pady=(0, 10))
        
        # Subtipo personalizado para "Otro"
        custom_plastic_label = ctk.CTkLabel(plastic_fields_frame, text="Especificar Subtipo")
        custom_plastic_label.pack(anchor="w", pady=(10, 0))
        
        custom_plastic_entry = ctk.CTkEntry(plastic_fields_frame, textvariable=custom_subtype_var)
        custom_plastic_entry.pack(fill="x", pady=(0, 10))
        
        # Estado del plástico (limpio/sucio)
        plastic_state_label = ctk.CTkLabel(plastic_fields_frame, text="Estado del Plástico")
        plastic_state_label.pack(anchor="w", pady=(10, 0))
        
        plastic_state_frame = ctk.CTkFrame(plastic_fields_frame, fg_color="transparent")
        plastic_state_frame.pack(fill="x", pady=(0, 10))
        
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
        
        # Estado (activo/inactivo)
        active_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        active_frame.grid(row=9, column=0, sticky="w", padx=5, pady=10)
        
        active_switch = ctk.CTkSwitch(
            active_frame, 
            text="Material Activo",
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
        
        # Establecer valores iniciales en los widgets
        if not material_type_var.get():
            material_type_var.set(MaterialType.PLASTIC)
        
        # Ajustar el valor inicial para el menú de subtipo
        if plastic_subtype_var.get() and plastic_subtype_var.get() in plastic_subtypes:
            plastic_subtype_menu.set(plastic_subtypes[plastic_subtype_var.get()])
        else:
            plastic_subtype_var.set(PlasticSubtype.CANDY)
            plastic_subtype_menu.set(plastic_subtypes[PlasticSubtype.CANDY])
        
        # Actualizar campos según los valores iniciales
        update_fields()
        
        # Función para guardar material
        def save_material():
            # Validar campos requeridos
            if not name_var.get().strip():
                error_label.configure(text="El nombre es obligatorio")
                name_entry.focus_set()
                return
                
            if not material_type_var.get():
                error_label.configure(text="Debe seleccionar un tipo de material")
                return
            
            # Validar campos específicos según el tipo
            if material_type_var.get() == MaterialType.CUSTOM:
                if not custom_subtype_var.get().strip():
                    error_label.configure(text="Debe especificar el nombre del material personalizado")
                    custom_subtype_entry.focus_set()
                    return
            elif material_type_var.get() == MaterialType.PLASTIC:
                if is_plastic_var.get() and plastic_subtype_var.get() == PlasticSubtype.OTHER:
                    if not custom_subtype_var.get().strip():
                        error_label.configure(text="Debe especificar el subtipo personalizado")
                        custom_plastic_entry.focus_set()
                        return
            
            # Actualizar objeto material
            self.current_material.name = name_var.get().strip()
            self.current_material.description = description_entry.get("1.0", "end-1c").strip()
            self.current_material.material_type = material_type_var.get()
            self.current_material.is_active = active_var.get()
            
            if material_type_var.get() == MaterialType.PLASTIC:
                self.current_material.is_plastic_subtype = is_plastic_var.get()
                if is_plastic_var.get():
                    self.current_material.plastic_subtype = plastic_subtype_var.get()
                    self.current_material.plastic_state = plastic_state_var.get()
                    if plastic_subtype_var.get() == PlasticSubtype.OTHER:
                        self.current_material.custom_subtype = custom_subtype_var.get().strip()
                    else:
                        self.current_material.custom_subtype = ""
                else:
                    self.current_material.plastic_subtype = ""
                    self.current_material.plastic_state = ""
                    self.current_material.custom_subtype = ""
            else:  # MaterialType.CUSTOM
                self.current_material.is_plastic_subtype = False
                self.current_material.plastic_subtype = ""
                self.current_material.plastic_state = ""
                self.current_material.custom_subtype = custom_subtype_var.get().strip()
            
            # Guardar en la base de datos
            if self.material_service.save_material(self.current_material):
                messagebox.showinfo("Éxito", "Material guardado correctamente")
                dialog.destroy()
                self._load_materials()  # Recargar datos
            else:
                error_label.configure(text="Error al guardar el material")
        
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
        
        # Bloquear ventana principal
        dialog.transient(self)
        dialog.grab_set()
    
    def _confirm_delete(self, material):
        """
        Confirma y elimina un material.
        
        Args:
            material (Material): Material a eliminar
        """
        if messagebox.askyesno(
            "Eliminar Material", 
            f"¿Está seguro que desea eliminar el material '{material.name}'?\n\n"
            "Esta acción no se puede deshacer."
        ):
            if self.material_service.delete_material(material.id):
                messagebox.showinfo("Éxito", "Material eliminado correctamente")
                self._load_materials()  # Recargar datos
            else:
                messagebox.showerror("Error", "No se pudo eliminar el material")