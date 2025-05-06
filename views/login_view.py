"""
Vista de login para ISMV3.
Proporciona autenticación de usuarios antes de acceder a la aplicación.
"""
import os
import json
import hashlib
import tkinter as tk
import customtkinter as ctk
from typing import Callable, Dict, Any, Optional


class LoginView(ctk.CTkToplevel):
    """
    Ventana de login para autenticación de usuarios.
    """
    
    def __init__(self, master, on_login_success: Callable = None):
        """
        Inicializa la ventana de login.
        
        Args:
            master: Widget padre.
            on_login_success: Función a ejecutar cuando el login sea exitoso.
        """
        super().__init__(master)
        self.master = master
        self.on_login_success = on_login_success
        self.users_file = os.path.join("data", "users.json")
        
        # Configurar ventana
        self.title("ISMV3 - Iniciar Sesión")
        self.geometry("400x500")
        self.resizable(False, False)
        
        # Centrar en pantalla
        self.center_window()
        
        # Bloquear ventana principal hasta que esta se cierre
        self.transient(master)
        self.grab_set()
        
        # Inicializar UI
        self._init_ui()
        
        # Asegurar que existe el archivo de usuarios
        self._ensure_users_file()
    
    def center_window(self):
        """Centra la ventana en la pantalla."""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
    
    def _init_ui(self):
        """Inicializa la interfaz de usuario del login con diseño mejorado."""
        # Frame principal con fondo
        main_frame = ctk.CTkFrame(self, fg_color=("#F5F5F5", "#1E293B"))
        main_frame.pack(fill="both", expand=True)
        
        # Panel de login (a la derecha)
        login_panel = ctk.CTkFrame(main_frame, fg_color=("#FFFFFF", "#111827"), corner_radius=15)
        login_panel.pack(fill="both", expand=True, padx=40, pady=40)
        
        # Logo o imagen
        logo_frame = ctk.CTkFrame(login_panel, fg_color="transparent")
        logo_frame.pack(pady=(40, 0))
        
        logo_label = ctk.CTkLabel(
            logo_frame, 
            text="ISMV3", 
            font=ctk.CTkFont(family="Arial", size=42, weight="bold"),
            text_color=("#1E3D58", "#43B0F1")
        )
        logo_label.pack()
        
        # Subtítulo
        subtitle = ctk.CTkLabel(
            login_panel, 
            text="Sistema de Gestión para Empresas de Reciclaje",
            font=ctk.CTkFont(size=14),
            text_color=("gray50", "gray70")
        )
        subtitle.pack(pady=(5, 40))
        
        # Frame para formulario
        form_frame = ctk.CTkFrame(login_panel, fg_color="transparent")
        form_frame.pack(fill="x", padx=50, pady=10)
        
        # Username
        username_label = ctk.CTkLabel(form_frame, text="Usuario")
        username_label.pack(anchor="w", pady=(10, 0))
        
        self.username_var = tk.StringVar()
        username_entry = ctk.CTkEntry(
            form_frame, 
            textvariable=self.username_var, 
            width=300,
            height=40,
            placeholder_text="Ingrese su nombre de usuario"
        )
        username_entry.pack(fill="x", pady=(5, 15))
        
        # Password
        password_label = ctk.CTkLabel(form_frame, text="Contraseña")
        password_label.pack(anchor="w", pady=(10, 0))
        
        self.password_var = tk.StringVar()
        password_entry = ctk.CTkEntry(
            form_frame, 
            textvariable=self.password_var, 
            show="•", 
            width=300,
            height=40,
            placeholder_text="Ingrese su contraseña"
        )
        password_entry.pack(fill="x", pady=(5, 15))
        
        # Recordar usuario
        options_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        options_frame.pack(fill="x", pady=10)
        
        self.remember_var = tk.BooleanVar(value=False)
        remember_check = ctk.CTkCheckBox(
            options_frame, 
            text="Recordar usuario", 
            variable=self.remember_var,
            border_color=("#43B0F1", "#43B0F1"),
            fg_color=("#43B0F1", "#43B0F1"),
            hover_color=("#2D98D6", "#2D98D6")
        )
        remember_check.pack(anchor="w")
        
        # Mensaje de error (inicialmente oculto)
        self.error_label = ctk.CTkLabel(
            form_frame, 
            text="", 
            text_color="#E74C3C"
        )
        self.error_label.pack(fill="x", pady=10)
        
        # Botón de login
        login_button = ctk.CTkButton(
            form_frame, 
            text="Iniciar Sesión", 
            command=self._on_login,
            fg_color=("#2D98D6", "#2D98D6"),
            hover_color=("#1E77A8", "#1E77A8"),
            height=45,
            font=ctk.CTkFont(size=15, weight="bold"),
            corner_radius=8
        )
        login_button.pack(fill="x", pady=15)
        
        # Footer
        footer_text = ctk.CTkLabel(
            login_panel, 
            text="© 2023 ISMV3 - Todos los derechos reservados",
            font=ctk.CTkFont(size=10),
            text_color=("gray50", "gray70")
        )
        footer_text.pack(side="bottom", pady=15)
        
        # Vinculación de Enter para login
        self.bind("<Return>", lambda event: self._on_login())
        
        # Cargar usuario recordado si existe
        self._load_remembered_user()
        
        # Enfocar campo de usuario o contraseña
        if self.username_var.get():
            password_entry.focus_set()
        else:
            username_entry.focus_set()
    
    def _ensure_users_file(self):
        """
        Asegura que existe el archivo de usuarios con al menos un admin.
        """
        os.makedirs(os.path.dirname(self.users_file), exist_ok=True)
        
        if not os.path.exists(self.users_file):
            # Crear archivo con usuario admin por defecto
            default_users = {
                "admin": {
                    "password": self._hash_password("admin"),  # Contraseña: admin
                    "name": "Administrador",
                    "role": "admin",
                    "is_active": True
                }
            }
            
            with open(self.users_file, 'w') as f:
                json.dump(default_users, f, indent=2)
    
    def _hash_password(self, password: str) -> str:
        """
        Aplica hash a la contraseña para almacenamiento seguro.
        
        Args:
            password: Contraseña en texto plano.
            
        Returns:
            str: Hash de la contraseña.
        """
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _on_login(self):
        """Maneja el evento de inicio de sesión."""
        username = self.username_var.get().strip()
        password = self.password_var.get()
        
        if not username or not password:
            self.error_label.configure(text="Por favor, ingrese usuario y contraseña")
            return
        
        user = self._authenticate(username, password)
        if user:
            # Guardar preferencia de recordar usuario
            if self.remember_var.get():
                self._save_remembered_user(username)
            else:
                self._clear_remembered_user()
            
            # Notificar login exitoso y cerrar ventana
            if self.on_login_success:
                self.on_login_success(user)
            self.destroy()
        else:
            self.error_label.configure(text="Usuario o contraseña incorrectos")
    
    def _authenticate(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Autentica al usuario con sus credenciales.
        
        Args:
            username: Nombre de usuario.
            password: Contraseña.
            
        Returns:
            Optional[Dict[str, Any]]: Datos del usuario o None si la autenticación falla.
        """
        try:
            with open(self.users_file, 'r') as f:
                users = json.load(f)
                
            if username in users:
                user_data = users[username]
                hashed_password = self._hash_password(password)
                
                if user_data.get('is_active', True) and user_data['password'] == hashed_password:
                    # Añadir username al diccionario para referencia
                    user_data['username'] = username
                    return user_data
        except Exception as e:
            print(f"Error durante la autenticación: {e}")
        
        return None
    
    def _save_remembered_user(self, username: str):
        """Guarda el nombre de usuario para recordarlo."""
        try:
            with open(os.path.join("data", "remembered_user.txt"), 'w') as f:
                f.write(username)
        except Exception as e:
            print(f"Error al guardar usuario recordado: {e}")
    
    def _clear_remembered_user(self):
        """Elimina el usuario recordado."""
        try:
            remembered_file = os.path.join("data", "remembered_user.txt")
            if os.path.exists(remembered_file):
                os.remove(remembered_file)
        except Exception as e:
            print(f"Error al borrar usuario recordado: {e}")
    
    def _load_remembered_user(self):
        """Carga el usuario recordado si existe."""
        try:
            remembered_file = os.path.join("data", "remembered_user.txt")
            if os.path.exists(remembered_file):
                with open(remembered_file, 'r') as f:
                    username = f.read().strip()
                    if username:
                        self.username_var.set(username)
                        self.remember_var.set(True)
        except Exception as e:
            print(f"Error al cargar usuario recordado: {e}")