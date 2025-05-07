"""
Vista para la administración de usuarios en ISMAPP.
"""
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk

class UserAdminView(ctk.CTkFrame):
    """Vista para la administración de usuarios del sistema."""
    
    def __init__(self, parent):
        """
        Inicializa la vista de administración de usuarios.
        
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
        except AttributeError:
            messagebox.showerror("Error", "No se pudo acceder al gestor de datos")
            return
        
        # Variables para almacenar datos
        self.users = []
        self.current_user = None
        
        # Crear UI
        self._create_ui()
        
        # Cargar datos iniciales
        self._load_users()
    
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
            text="Administración de Usuarios",
            font=ctk.CTkFont(size=22, weight="bold")
        ).pack(side="left")
        
        # Botón para crear nuevo usuario
        self.add_button = ctk.CTkButton(
            header_frame,
            text="+ Nuevo Usuario",
            command=self._show_edit_dialog,
            width=130
        )
        self.add_button.pack(side="right", padx=10)
        
        # Frame para búsqueda
        search_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        search_frame.pack(fill="x", pady=(0, 15))
        
        # Barra de búsqueda
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *args: self._filter_users())
        
        search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Buscar usuario...",
            width=300,
            textvariable=self.search_var
        )
        search_entry.pack(side="left", fill="x", expand=True)
        
        # Frame para la tabla de usuarios
        table_container = ctk.CTkFrame(self.main_container)
        table_container.pack(fill="both", expand=True)
        
        # Cabecera de la tabla
        columns = ["Usuario", "Nombre", "Rol", "Estado", "Acciones"]
        header_frame = ctk.CTkFrame(table_container, fg_color=("#DDDDDD", "#2B2B2B"))
        header_frame.pack(fill="x")
        
        # Configurar ancho de columnas
        widths = [0.2, 0.3, 0.15, 0.15, 0.2]  # Proporciones
        for i, col in enumerate(columns):
            col_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
            col_frame.pack(side="left", fill="both", expand=True, padx=2, pady=5)
            col_frame.configure(width=int(700 * widths[i]))  # Ancho proporcional
                
            ctk.CTkLabel(
                col_frame, 
                text=col,
                font=ctk.CTkFont(weight="bold")
            ).pack()
        
        # Contenedor para filas de usuarios
        self.users_rows_frame = ctk.CTkScrollableFrame(table_container, fg_color="transparent")
        self.users_rows_frame.pack(fill="both", expand=True)
    
    def _load_users(self):
        """Carga la lista de usuarios desde la base de datos."""
        query = """
        SELECT id, username, name, role, is_active 
        FROM users 
        ORDER BY username
        """
        
        try:
            self.users = self.data_manager.execute_query(query)
            self._update_users_table()
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar usuarios: {e}")
    
    def _filter_users(self):
        """Filtra la lista de usuarios según búsqueda."""
        self._update_users_table()
    
    def _update_users_table(self):
        """Actualiza la tabla de usuarios en la UI."""
        # Limpiar tabla actual
        for widget in self.users_rows_frame.winfo_children():
            widget.destroy()
        
        # Obtener término de búsqueda
        search_term = self.search_var.get().lower().strip()
        
        # Filtrar usuarios
        filtered_users = self.users
        if search_term:
            filtered_users = [
                user for user in self.users
                if (search_term in user['username'].lower() or
                    search_term in (user['name'] or '').lower() or
                    search_term in (user['role'] or '').lower())
            ]
        
        # Verificar si hay usuarios para mostrar
        if not filtered_users:
            no_data_label = ctk.CTkLabel(
                self.users_rows_frame,
                text="No se encontraron usuarios",
                font=ctk.CTkFont(size=14),
                text_color="gray60"
            )
            no_data_label.pack(pady=30)
            return
        
        # Crear filas para cada usuario
        for i, user in enumerate(filtered_users):
            row_color = ("#F5F5F5", "#2D2D2D") if i % 2 == 0 else ("#FFFFFF", "#333333")
            row_frame = ctk.CTkFrame(self.users_rows_frame, fg_color=row_color, corner_radius=0)
            row_frame.pack(fill="x", pady=1)
            
            # Username
            username_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
            username_frame.pack(side="left", fill="both", expand=True, padx=2, pady=8)
            ctk.CTkLabel(username_frame, text=user['username']).pack(anchor="w", padx=5)
            
            # Nombre
            name_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
            name_frame.pack(side="left", fill="both", expand=True, padx=2, pady=8)
            ctk.CTkLabel(name_frame, text=user['name'] or "").pack(anchor="w", padx=5)
            
            # Rol
            role_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
            role_frame.pack(side="left", fill="both", expand=True, padx=2, pady=8)
            
            role_text = user['role']
            role_color = "#4CAF50" if role_text == "admin" else "#2196F3"
            
            ctk.CTkLabel(
                role_frame, 
                text=role_text,
                text_color=role_color,
                font=ctk.CTkFont(size=12, weight="bold")
            ).pack(anchor="w", padx=5)
            
            # Estado
            status_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
            status_frame.pack(side="left", fill="both", expand=True, padx=2, pady=8)
            
            is_active = user['is_active'] == 1
            status_text = "Activo" if is_active else "Inactivo"
            status_color = "#4CAF50" if is_active else "#F44336"
            
            ctk.CTkLabel(
                status_frame, 
                text=status_text,
                text_color=status_color
            ).pack(anchor="w", padx=5)
            
            # Acciones
            actions_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
            actions_frame.pack(side="left", fill="both", padx=2, pady=3)
            
            # Botón editar
            edit_btn = ctk.CTkButton(
                actions_frame,
                text="✏️",
                width=30,
                command=lambda u=user: self._show_edit_dialog(u),
                fg_color=("#6E9075", "#2D6A6A")
            )
            edit_btn.pack(side="left", padx=2)
            
            # Botón eliminar/restaurar
            icon = "🔄" if not is_active else "❌"
            color = ("#BC7777", "#AA5555") if is_active else ("#6E9075", "#2D6A6A")
            
            toggle_btn = ctk.CTkButton(
                actions_frame,
                text=icon,
                width=30,
                command=lambda u=user: self._toggle_user_status(u),
                fg_color=color
            )
            toggle_btn.pack(side="left", padx=2)
            
            # Botón resetear contraseña
            reset_btn = ctk.CTkButton(
                actions_frame,
                text="🔑",
                width=30,
                command=lambda u=user: self._reset_password(u),
                fg_color=("#5D87B4", "#2D6A9A")
            )
            reset_btn.pack(side="left", padx=2)
    
    def _show_edit_dialog(self, user=None):
        """
        Muestra el diálogo para crear o editar un usuario.
        
        Args:
            user (dict, optional): Usuario a editar, None para crear nuevo
        """
        self.current_user = user or {}
        
        # Crear ventana de diálogo
        dialog = ctk.CTkToplevel(self)
        dialog.title("Nuevo Usuario" if not user else "Editar Usuario")
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
            text="Datos del Usuario",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=(0, 20), anchor="w")
        
        # Form fields
        form_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        form_frame.pack(fill="x", pady=10)
        
        # Variables para campos
        username_var = tk.StringVar(value=self.current_user.get('username', ''))
        name_var = tk.StringVar(value=self.current_user.get('name', ''))
        role_var = tk.StringVar(value=self.current_user.get('role', 'user'))
        active_var = tk.BooleanVar(value=self.current_user.get('is_active', 1) == 1)
        password_var = tk.StringVar()
        confirm_var = tk.StringVar()
        
        # Username
        ctk.CTkLabel(form_frame, text="Nombre de usuario*").pack(anchor="w", pady=(10, 0))
        username_entry = ctk.CTkEntry(form_frame, textvariable=username_var)
        username_entry.pack(fill="x", pady=(0, 10))
        
        # Nombre completo
        ctk.CTkLabel(form_frame, text="Nombre completo").pack(anchor="w", pady=(10, 0))
        ctk.CTkEntry(form_frame, textvariable=name_var).pack(fill="x", pady=(0, 10))
        
        # Rol
        ctk.CTkLabel(form_frame, text="Rol*").pack(anchor="w", pady=(10, 0))
        
        role_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        role_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkRadioButton(
            role_frame, 
            text="Usuario", 
            variable=role_var, 
            value="user"
        ).pack(side="left", padx=10)
        
        ctk.CTkRadioButton(
            role_frame, 
            text="Administrador", 
            variable=role_var, 
            value="admin"
        ).pack(side="left", padx=10)
        
        # Contraseña (solo para nuevos usuarios)
        if not user:
            ctk.CTkLabel(form_frame, text="Contraseña*").pack(anchor="w", pady=(10, 0))
            ctk.CTkEntry(form_frame, textvariable=password_var, show="•").pack(fill="x", pady=(0, 10))
            
            ctk.CTkLabel(form_frame, text="Confirmar contraseña*").pack(anchor="w", pady=(10, 0))
            ctk.CTkEntry(form_frame, textvariable=confirm_var, show="•").pack(fill="x", pady=(0, 10))
        
        # Estado
        active_switch = ctk.CTkSwitch(
            form_frame, 
            text="Usuario Activo",
            variable=active_var,
            onvalue=True,
            offvalue=False
        )
        active_switch.pack(anchor="w", pady=(10, 0))
        
        # Mensaje de error
        error_label = ctk.CTkLabel(main_frame, text="", text_color="red")
        error_label.pack(fill="x", pady=(10, 0))
        
        # Botones
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=20)
        
        # Función para guardar usuario
        def save_user():
            # Validar campos
            if not username_var.get().strip():
                error_label.configure(text="El nombre de usuario es obligatorio")
                return
            
            if not user and not password_var.get():
                error_label.configure(text="La contraseña es obligatoria")
                return
                
            if not user and password_var.get() != confirm_var.get():
                error_label.configure(text="Las contraseñas no coinciden")
                return
            
            # Preparar datos
            user_data = {
                'username': username_var.get().strip(),
                'name': name_var.get().strip(),
                'role': role_var.get(),
                'is_active': 1 if active_var.get() else 0
            }
            
            try:
                if user:
                    # Actualizar usuario existente
                    query = """
                    UPDATE users 
                    SET username = ?, name = ?, role = ?, is_active = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                    """
                    self.data_manager.execute_query(
                        query, 
                        (user_data['username'], user_data['name'], 
                         user_data['role'], user_data['is_active'], 
                         user['id'])
                    )
                    messagebox.showinfo("Éxito", "Usuario actualizado correctamente")
                else:
                    # Crear nuevo usuario
                    query = """
                    INSERT INTO users (username, password, name, role, is_active)
                    VALUES (?, ?, ?, ?, ?)
                    """
                    self.data_manager.execute_query(
                        query, 
                        (user_data['username'], password_var.get(), 
                         user_data['name'], user_data['role'], 
                         user_data['is_active'])
                    )
                    messagebox.showinfo("Éxito", "Usuario creado correctamente")
                
                dialog.destroy()
                self._load_users()
            except Exception as e:
                error_label.configure(text=f"Error: {e}")
        
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
            command=save_user,
            width=100
        ).pack(side="right", padx=20)
        
        # Bloquear ventana principal
        dialog.transient(self)
        dialog.grab_set()
        
        # Enfocar primer campo
        username_entry.focus_set()
    
    def _toggle_user_status(self, user):
        """
        Cambia el estado de un usuario (activo/inactivo).
        
        Args:
            user (dict): Usuario a modificar
        """
        new_status = 0 if user['is_active'] == 1 else 1
        status_text = "activar" if new_status == 1 else "desactivar"
        
        # No permitir desactivar al último administrador activo
        if new_status == 0 and user['role'] == 'admin':
            # Verificar si hay otros administradores activos
            query = "SELECT COUNT(*) as count FROM users WHERE role = 'admin' AND is_active = 1"
            result = self.data_manager.execute_query(query)
            
            if result[0]['count'] <= 1:
                messagebox.showerror("Error", "No se puede desactivar al último administrador activo")
                return
        
        if messagebox.askyesno(
            "Confirmar acción", 
            f"¿Está seguro que desea {status_text} al usuario '{user['username']}'?"
        ):
            try:
                query = "UPDATE users SET is_active = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
                self.data_manager.execute_query(query, (new_status, user['id']))
                
                messagebox.showinfo("Éxito", f"Usuario {status_text}do correctamente")
                self._load_users()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo {status_text} el usuario: {e}")
    
    def _reset_password(self, user):
        """
        Permite resetear la contraseña de un usuario.
        
        Args:
            user (dict): Usuario a modificar
        """
        dialog = ctk.CTkToplevel(self)
        dialog.title(f"Resetear Contraseña - {user['username']}")
        dialog.geometry("400x250")
        dialog.resizable(False, False)
        
        # Centrar ventana
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f'+{x}+{y}')
        
        # Frame principal
        main_frame = ctk.CTkFrame(dialog)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Título
        ctk.CTkLabel(
            main_frame,
            text=f"Resetear Contraseña para {user['username']}",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(0, 20))
        
        # Variables
        new_pass_var = tk.StringVar()
        confirm_pass_var = tk.StringVar()
        
        # Formulario
        form_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        form_frame.pack(fill="x", pady=10)
        
        # Nueva contraseña
        ctk.CTkLabel(form_frame, text="Nueva contraseña:").pack(anchor="w")
        new_pass_entry = ctk.CTkEntry(form_frame, textvariable=new_pass_var, show="•")
        new_pass_entry.pack(fill="x", pady=(0, 10))
        
        # Confirmar contraseña
        ctk.CTkLabel(form_frame, text="Confirmar contraseña:").pack(anchor="w")
        ctk.CTkEntry(form_frame, textvariable=confirm_pass_var, show="•").pack(fill="x")
        
        # Mensaje de error
        error_label = ctk.CTkLabel(form_frame, text="", text_color="red")
        error_label.pack(fill="x", pady=(10, 0))
        
        # Botones
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=20)
        
        def reset_password():
            # Validar campos
            if not new_pass_var.get():
                error_label.configure(text="La contraseña no puede estar vacía")
                return
            
            if new_pass_var.get() != confirm_pass_var.get():
                error_label.configure(text="Las contraseñas no coinciden")
                return
            
            try:
                # Actualizar contraseña
                query = "UPDATE users SET password = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
                self.data_manager.execute_query(query, (new_pass_var.get(), user['id']))
                
                messagebox.showinfo("Éxito", "Contraseña actualizada correctamente")
                dialog.destroy()
            except Exception as e:
                error_label.configure(text=f"Error: {e}")
        
        # Botón cancelar
        ctk.CTkButton(
            btn_frame,
            text="Cancelar",
            command=dialog.destroy,
            fg_color="gray50",
            width=100
        ).pack(side="left", padx=10)
        
        # Botón restablecer
        ctk.CTkButton(
            btn_frame,
            text="Restablecer",
            command=reset_password,
            width=100,
            fg_color="#E76F51"
        ).pack(side="right", padx=10)
        
        # Bloquear ventana principal
        dialog.transient(self)
        dialog.grab_set()
        
        # Enfocar primer campo
        new_pass_entry.focus_set()