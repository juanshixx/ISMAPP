"""
Vista para la administración de usuarios en ISMV3.
"""
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from typing import Optional, List, Dict, Any

from models.user import User
from controllers.user_controller import UserController


class UserAdminView(ctk.CTkFrame):
    """Vista para administrar usuarios del sistema."""
    
    def __init__(self, parent, **kwargs):
        """
        Inicializa la vista de administración de usuarios.
        
        Args:
            parent: Widget padre en la jerarquía de tkinter.
            **kwargs: Argumentos adicionales para el Frame.
        """
        super().__init__(parent, **kwargs)
        self.controller = UserController()
        self.selected_user: Optional[User] = None
        
        self._init_ui()
        self._load_users()
    
    def _init_ui(self):
        """Inicializa los elementos de la interfaz de usuario."""
        # Configuración de la cuadrícula principal
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=3)
        self.rowconfigure(0, weight=1)
        
        # Panel izquierdo - Lista de usuarios
        left_panel = ctk.CTkFrame(self)
        left_panel.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # Lista de usuarios
        list_frame = ctk.CTkFrame(left_panel)
        list_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.user_listbox = tk.Listbox(list_frame, bg="#2b2b2b", fg="#ffffff",
                                     selectbackground="#1f538d")
        self.user_listbox.pack(fill="both", expand=True)
        self.user_listbox.bind("<<ListboxSelect>>", self._on_user_select)
        
        # Botones de acción para la lista
        btn_frame = ctk.CTkFrame(left_panel)
        btn_frame.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkButton(btn_frame, text="Nuevo", command=self._on_new_user).pack(
            side="left", padx=5, pady=5)
        ctk.CTkButton(btn_frame, text="Eliminar", command=self._on_delete_user).pack(
            side="right", padx=5, pady=5)
        
        # Panel derecho - Detalles del usuario
        right_panel = ctk.CTkFrame(self)
        right_panel.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        
        # Formulario de detalles
        form_frame = ctk.CTkFrame(right_panel)
        form_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Variables para campos del formulario
        self.username_var = tk.StringVar()
        self.name_var = tk.StringVar()
        self.role_var = tk.StringVar(value="user")
        self.active_var = tk.BooleanVar(value=True)
        self.password_var = tk.StringVar()
        self.confirm_password_var = tk.StringVar()
        
        # Campos del formulario
        row = 0
        
        # Username
        ctk.CTkLabel(form_frame, text="Usuario:").grid(
            row=row, column=0, sticky="w", padx=5, pady=5)
        self.username_entry = ctk.CTkEntry(form_frame, textvariable=self.username_var, width=300)
        self.username_entry.grid(row=row, column=1, sticky="ew", padx=5, pady=5)
        row += 1
        
        # Nombre completo
        ctk.CTkLabel(form_frame, text="Nombre:").grid(
            row=row, column=0, sticky="w", padx=5, pady=5)
        ctk.CTkEntry(form_frame, textvariable=self.name_var, width=300).grid(
            row=row, column=1, sticky="ew", padx=5, pady=5)
        row += 1
        
        # Role
        ctk.CTkLabel(form_frame, text="Rol:").grid(
            row=row, column=0, sticky="w", padx=5, pady=5)
        
        roles_frame = ctk.CTkFrame(form_frame)
        roles_frame.grid(row=row, column=1, sticky="ew", padx=5, pady=5)
        
        ctk.CTkRadioButton(roles_frame, text="Usuario", variable=self.role_var, 
                        value="user").pack(side="left", padx=10)
        ctk.CTkRadioButton(roles_frame, text="Administrador", variable=self.role_var,
                        value="admin").pack(side="left", padx=10)
        row += 1
        
        # Estado activo
        ctk.CTkLabel(form_frame, text="Estado:").grid(
            row=row, column=0, sticky="w", padx=5, pady=5)
        ctk.CTkCheckBox(roles_frame, text="Activo", variable=self.active_var).pack(
            side="left", padx=50)
        row += 1
        
        # Separador para contraseña
        separator = ctk.CTkFrame(form_frame, height=2, fg_color="gray50")
        separator.grid(row=row, column=0, columnspan=2, sticky="ew", padx=5, pady=10)
        row += 1
        
        # Contraseña
        ctk.CTkLabel(form_frame, text="Contraseña:").grid(
            row=row, column=0, sticky="w", padx=5, pady=5)
        ctk.CTkEntry(form_frame, textvariable=self.password_var, show="•", width=300).grid(
            row=row, column=1, sticky="ew", padx=5, pady=5)
        row += 1
        
        # Confirmar contraseña
        ctk.CTkLabel(form_frame, text="Confirmar contraseña:").grid(
            row=row, column=0, sticky="w", padx=5, pady=5)
        ctk.CTkEntry(form_frame, textvariable=self.confirm_password_var, show="•", width=300).grid(
            row=row, column=1, sticky="ew", padx=5, pady=5)
        row += 1
        
        # Nota sobre contraseña
        self.password_note = ctk.CTkLabel(
            form_frame, 
            text="Dejar en blanco para mantener la contraseña actual",
            text_color="gray70",
            font=ctk.CTkFont(size=10, slant="italic")
        )
        self.password_note.grid(row=row, column=0, columnspan=2, sticky="w", padx=5)
        row += 1
        
        # Mensajes de error
        self.error_label = ctk.CTkLabel(form_frame, text="", text_color="red")
        self.error_label.grid(row=row, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        row += 1
        
        # Botón guardar
        ctk.CTkButton(form_frame, text="Guardar", command=self._on_save_user).grid(
            row=row, column=0, columnspan=2, padx=5, pady=10)
        
        # Configuración de expansión en el formulario
        form_frame.columnconfigure(1, weight=1)
    
    def _load_users(self):
        """Carga la lista de usuarios desde el controlador."""
        self.user_listbox.delete(0, tk.END)
        users = self.controller.get_all_users()
        
        for user in sorted(users, key=lambda u: u.username):
            status = "✓" if user.is_active else "✗"
            role = "Admin" if user.role == "admin" else "Usuario"
            self.user_listbox.insert(tk.END, f"{status} {user.username} ({role})")
            # Almacenamos el username como datos adicionales del item
            self.user_listbox.itemconfig(tk.END, {'username': user.username})
    
    def _on_user_select(self, event=None):
        """Maneja la selección de un usuario en la lista."""
        selection = self.user_listbox.curselection()
        if not selection:
            return
        
        index = selection[0]
        username = self.user_listbox.itemcget(index, 'username')
        if not username:
            return
        
        user = self.controller.get_user(username)
        if user:
            self.selected_user = user
            self._populate_form(user)
    
    def _populate_form(self, user: User):
        """Rellena el formulario con los datos del usuario."""
        self.username_var.set(user.username)
        self.name_var.set(user.name)
        self.role_var.set(user.role)
        self.active_var.set(user.is_active)
        
        # Limpiar campos de contraseña
        self.password_var.set("")
        self.confirm_password_var.set("")
        
        # Mostrar nota de contraseña
        self.password_note.grid()
        
        # Deshabilitar cambio de username para usuarios existentes
        self.username_entry.configure(state="disabled")
        
        # Limpiar mensaje de error
        self.error_label.configure(text="")
    
    def _on_new_user(self):
        """Prepara el formulario para un nuevo usuario."""
        self.selected_user = None
        
        # Limpiar campos
        self.username_var.set("")
        self.name_var.set("")
        self.role_var.set("user")
        self.active_var.set(True)
        self.password_var.set("")
        self.confirm_password_var.set("")
        
        # Habilitar campo de username
        self.username_entry.configure(state="normal")
        
        # Ocultar nota de contraseña
        self.password_note.grid_remove()
        
        # Limpiar mensaje de error
        self.error_label.configure(text="")
    
    def _on_save_user(self):
        """Guarda los cambios del usuario actual."""
        # Validar datos
        username = self.username_var.get().strip()
        name = self.name_var.get().strip()
        role = self.role_var.get()
        is_active = self.active_var.get()
        password = self.password_var.get()
        confirm_password = self.confirm_password_var.get()
        
        if not username:
            self.error_label.configure(text="El nombre de usuario es obligatorio")
            return
        
        if not name:
            self.error_label.configure(text="El nombre es obligatorio")
            return
        
        # Validar contraseñas
        if self.selected_user is None:  # Nuevo usuario
            if not password:
                self.error_label.configure(text="La contraseña es obligatoria para nuevos usuarios")
                return
        
        if password and password != confirm_password:
            self.error_label.configure(text="Las contraseñas no coinciden")
            return
        
        # Construir objeto User
        if self.selected_user:
            # Actualizar usuario existente
            user = self.selected_user
            user.name = name
            user.role = role
            user.is_active = is_active
        else:
            # Crear nuevo usuario
            user = User(
                username=username,
                name=name,
                role=role,
                is_active=is_active
            )
        
        # Guardar usuario
        if self.controller.save_user(user, password if password else None):
            messagebox.showinfo("Éxito", f"Usuario '{username}' guardado correctamente")
            self._load_users()
            
            # Si era un nuevo usuario, seleccionarlo
            if not self.selected_user:
                self.selected_user = self.controller.get_user(username)
                self._populate_form(self.selected_user)
        else:
            self.error_label.configure(text="Error al guardar el usuario")
    
    def _on_delete_user(self):
        """Elimina el usuario seleccionado."""
        if not self.selected_user:
            messagebox.showerror("Error", "No hay usuario seleccionado")
            return
        
        # No permitir eliminar el admin
        if self.selected_user.username == "admin":
            messagebox.showerror("Error", "No se puede eliminar el usuario administrador")
            return
        
        if messagebox.askyesno("Confirmar", f"¿Está seguro de eliminar el usuario '{self.selected_user.username}'?"):
            if self.controller.delete_user(self.selected_user.username):
                messagebox.showinfo("Éxito", "Usuario eliminado correctamente")
                self._load_users()
                self._on_new_user()  # Limpiar formulario
            else:
                messagebox.showerror("Error", "No se pudo eliminar el usuario")