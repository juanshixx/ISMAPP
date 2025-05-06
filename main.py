"""
Punto de entrada principal para la aplicación ISMV3.
Sistema de gestión para empresas de reciclaje.
"""
import os
import sys
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from datetime import datetime
from typing import Dict, Any, Optional

# Añadir directorio raíz al path de Python para resolver problemas de importación
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Importaciones de la aplicación
try:
    from core.database.data_manager import DataManager
    from views.login_view import LoginView
    from views.worker_view import WorkerView
    from views.user_admin_view import UserAdminView
    from views.dashboard_view import DashboardView
    from models.user import User
except ImportError as e:
    print(f"Error de importación: {e}")
    # Crear directorios necesarios si no existen
    for path in ['core/database', 'views', 'models']:
        os.makedirs(path, exist_ok=True)
    print("Se han creado los directorios necesarios. Por favor, asegúrate de tener todos los archivos requeridos.")
    sys.exit(1)


class ISMV3App(ctk.CTk):
    """Aplicación principal de ISMV3."""
    
    def __init__(self):
        super().__init__()
        
        # Estado de la aplicación
        self.current_user: Optional[User] = None
        
        # Cargar tema personalizado
        self._load_custom_theme()
        
        # Configuración inicial
        self.title("ISMV3 - Sistema de Gestión")
        self.geometry("1200x700")
        self.minsize(800, 600)
        
        # Configurar tema
        ctk.set_appearance_mode("dark")  # Modos: "system" (por defecto), "dark", "light"
        ctk.set_default_color_theme("blue")  # Temas: "blue" (por defecto), "green", "dark-blue"
        
        # Asegurar que existe la base de datos
        self._setup_database()
        
        # Inicializar gestor de datos (singleton)
        try:
            self.data_manager = DataManager()
        except Exception as e:
            print(f"Error al inicializar DataManager: {e}")
        
        # Mostrar login antes de la interfaz principal
        self.withdraw()  # Ocultar ventana principal primero
        self._show_login()
    
    def _load_custom_theme(self):
        """Carga el tema personalizado si existe."""
        theme_path = os.path.join("assets", "styles", "custom_theme.json")
        if os.path.exists(theme_path):
            try:
                ctk.set_default_color_theme(theme_path)
            except Exception as e:
                print(f"Error al cargar tema personalizado: {e}")
    
    def _setup_database(self):
        """Asegura que la base de datos existe."""
        db_path = os.path.join("data", "ismv3.db")
        data_dir = os.path.dirname(db_path)
        if not os.path.exists(data_dir):
            os.makedirs(data_dir, exist_ok=True)
            
        if not os.path.exists(db_path):
            # Crear base de datos
            try:
                from setup_database import setup_sqlite_database
                setup_sqlite_database(db_path)
                print("Base de datos creada")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo crear la base de datos: {e}")
    
    def _show_login(self):
        """Muestra la ventana de login."""
        try:
            login_window = LoginView(self, self._on_login_success)
        except Exception as e:
            self.deiconify()  # Mostrar ventana principal si hay error
            messagebox.showerror("Error", f"Error al iniciar sesión: {e}")
    
    def _on_login_success(self, user_data: Dict[str, Any]):
        """
        Maneja el inicio de sesión exitoso.
        
        Args:
            user_data: Datos del usuario autenticado.
        """
        # Crear objeto User
        self.current_user = User(
            username=user_data['username'],
            name=user_data.get('name', 'Usuario'),
            role=user_data.get('role', 'user'),
            is_active=user_data.get('is_active', True)
        )
        
        # Mostrar ventana principal
        self.deiconify()
        
        # Configurar interfaz para el usuario actual
        self._init_ui()
        
        # Actualizar título con nombre de usuario
        self.title(f"ISMV3 - {self.current_user.name} [{self.current_user.role}]")
    
    def _init_ui(self):
        """Inicializa la interfaz de usuario principal."""
        # Configuración del contenedor principal
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        
        # Barra superior (menú y usuario)
        self._create_top_bar()
        
        # Menú lateral
        self._create_sidebar()
        
        # Contenedor principal para los frames
        self.main_view = ctk.CTkFrame(self)
        self.main_view.grid(row=1, column=1, sticky="nsew", padx=20, pady=(0, 20))
        
        # Estado e información (barra inferior)
        self._create_status_bar()
        
        # Inicializar frames de contenido
        self._setup_content_frames()
        
        # Mostrar el frame inicial
        self.current_frame = None
        self.show_frame("dashboard")  # Iniciar con dashboard
    
    def _create_top_bar(self):
        """Crea la barra superior con menú y usuario."""
        top_bar = ctk.CTkFrame(self, height=40, fg_color=("gray85", "gray20"))
        top_bar.grid(row=0, column=0, columnspan=2, sticky="ew")
        top_bar.grid_propagate(False)
        
        # Configurar la cuadrícula de la barra superior
        top_bar.columnconfigure(1, weight=1)
        
        # Logo pequeño
        ctk.CTkLabel(top_bar, text="ISMV3", 
                   font=ctk.CTkFont(size=14, weight="bold")).grid(
                       row=0, column=0, padx=10, pady=5, sticky="w")
        
        # Versión
        ctk.CTkLabel(top_bar, text="v1.0", 
                   font=ctk.CTkFont(size=10)).grid(
                       row=0, column=0, padx=(60, 0), pady=5, sticky="w")
        
        # Widget de usuario activo (derecha)
        user_frame = ctk.CTkFrame(top_bar, fg_color=("gray80", "gray25"))
        user_frame.grid(row=0, column=2, padx=10, pady=5, sticky="e")
        
        if self.current_user:
            # Nombre de usuario
            ctk.CTkLabel(user_frame, text=f"{self.current_user.name}", 
                       font=ctk.CTkFont(size=12, weight="bold")).pack(
                           side="left", padx=5, pady=2)
            
            # Botón de opciones de usuario
            user_menu_btn = ctk.CTkButton(user_frame, text="≡", width=30, height=30,
                                       command=self._show_user_menu)
            user_menu_btn.pack(side="left", padx=5, pady=2)
    
    def _create_sidebar(self):
        """Crea el menú lateral con mejoras visuales."""
        # Frame base con gradiente
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0, fg_color=("#1E3D58", "#1E3D58"))
        self.sidebar.grid(row=1, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)  # Mantener ancho fijo
        
        # Logo de la app
        logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        logo_frame.pack(fill="x", pady=(25, 20))
        
        # Logo text con estilo
        ctk.CTkLabel(
            logo_frame, 
            text="ISMV3",
            font=ctk.CTkFont(family="Arial", size=28, weight="bold"),
            text_color="#E8E8E8"
        ).pack(pady=10)
        
        ctk.CTkLabel(
            logo_frame,
            text="Sistema de Gestión de Reciclaje",
            font=ctk.CTkFont(size=10),
            text_color="#43B0F1"
        ).pack(pady=(0, 15))
        
        # Separador
        ctk.CTkFrame(self.sidebar, height=1, fg_color="#43B0F1").pack(fill="x", padx=20)
        
        # Sección 1: General
        self._add_menu_section("GENERAL", "#E8E8E8")
        self._add_menu_button("dashboard", "📊  Dashboard", lambda: self.show_frame("dashboard"))
        
        # Sección 2: Operaciones
        self._add_menu_section("OPERACIONES", "#E8E8E8")
        self._add_menu_button("weighing", "⚖️  Pesajes", lambda: self.show_frame("weighing"))
        self._add_menu_button("transactions", "💰  Transacciones", lambda: self.show_frame("transactions"))
        
        # Sección 3: Entidades
        self._add_menu_section("ENTIDADES", "#E8E8E8")
        self._add_menu_button("workers", "👷  Trabajadores", lambda: self.show_frame("workers"))
        self._add_menu_button("clients", "🏢  Clientes", lambda: self.show_frame("clients"))
        self._add_menu_button("materials", "📦  Materiales", lambda: self.show_frame("materials"))
        
        # Sección 4: Administración (solo para admin)
        if self.current_user and self.current_user.role == "admin":
            self._add_menu_section("ADMINISTRACIÓN", "#E8E8E8")
            self._add_menu_button("users", "👥  Usuarios", lambda: self.show_frame("users"))
            self._add_menu_button("settings", "⚙️  Configuración", lambda: self.show_frame("settings"))
        
        # Botón de cierre de sesión al final
        logout_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        logout_frame.pack(side="bottom", fill="x", pady=20)
        
        logout_btn = ctk.CTkButton(
            logout_frame, 
            text="Cerrar sesión", 
            command=self._logout,
            fg_color="#E76F51",
            hover_color="#F4A261",
            font=ctk.CTkFont(weight="bold")
        )
        logout_btn.pack(padx=20, pady=10)

    def _create_status_bar(self):
        """Crea la barra de estado inferior."""
        status_bar = ctk.CTkFrame(self, height=25, fg_color=("gray80", "#1E3D58"))
        status_bar.grid(row=2, column=0, columnspan=2, sticky="ew")
        
        # Fecha actual
        date_label = ctk.CTkLabel(status_bar, text=datetime.now().strftime("%Y-%m-%d"),
                               font=ctk.CTkFont(size=10))
        date_label.pack(side="right", padx=10)
        
        # Mensaje de estado
        self.status_msg = ctk.CTkLabel(status_bar, text="Listo", 
                                    font=ctk.CTkFont(size=10))
        self.status_msg.pack(side="left", padx=10)
    
    def _add_menu_section(self, title, text_color="#FFFFFF"):
        """Añade una sección al menú lateral con mejor estilo."""
        section_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        section_frame.pack(fill="x", padx=10, pady=(15, 5))
        
        section_label = ctk.CTkLabel(
            section_frame, 
            text=title, 
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=text_color
        )
        section_label.pack(fill="x", padx=10, pady=(0, 5), anchor="w")
    
    def _add_menu_button(self, frame_name, text, command):
        """Añade un botón al menú lateral con mejor estilo."""
        btn = ctk.CTkButton(
            self.sidebar, 
            text=text, 
            command=command,
            fg_color="transparent", 
            text_color="#E8E8E8",
            hover_color=("#43B0F1", "#43B0F1"),
            anchor="w",
            height=35,
            corner_radius=5,
            font=ctk.CTkFont(size=13)
        )
        btn.pack(fill="x", padx=10, pady=3)
        
        # Guardar referencia al botón para resaltar el activo
        if not hasattr(self, 'menu_buttons'):
            self.menu_buttons = {}
        self.menu_buttons[frame_name] = btn
    
    def _setup_content_frames(self):
        """Inicializa los frames de contenido de la aplicación."""
        # Diccionario para almacenar frames
        self.frames = {}
        
        # Frame Dashboard - Usando la nueva vista mejorada
        try:
            self.frames["dashboard"] = DashboardView(self.main_view)
        except Exception as e:
            print(f"Error al cargar DashboardView: {e}")
            # Fallback a un dashboard simple si falla
            self.frames["dashboard"] = ctk.CTkFrame(self.main_view)
            ctk.CTkLabel(self.frames["dashboard"], 
                       text="Dashboard - Bienvenido a ISMV3", 
                       font=ctk.CTkFont(size=20, weight="bold")).pack(pady=20)
        
        # Frame Trabajadores
        try:
            self.frames["workers"] = WorkerView(self.main_view)
        except Exception as e:
            print(f"Error al cargar WorkerView: {e}")
            self.frames["workers"] = ctk.CTkFrame(self.main_view)
            ctk.CTkLabel(self.frames["workers"], 
                       text=f"Error al cargar módulo de Trabajadores: {str(e)}", 
                       text_color="red").pack(pady=20)
        
        # Frame Clientes (placeholder)
        self.frames["clients"] = ctk.CTkFrame(self.main_view)
        ctk.CTkLabel(self.frames["clients"], 
                   text="Módulo de Clientes", 
                   font=ctk.CTkFont(size=20, weight="bold")).pack(pady=20)
        
        # Frame Pesajes (placeholder)
        self.frames["weighing"] = ctk.CTkFrame(self.main_view)
        ctk.CTkLabel(self.frames["weighing"], 
                   text="Módulo de Pesajes", 
                   font=ctk.CTkFont(size=20, weight="bold")).pack(pady=20)
        
        # Frame Transacciones (placeholder)
        self.frames["transactions"] = ctk.CTkFrame(self.main_view)
        ctk.CTkLabel(self.frames["transactions"], 
                   text="Módulo de Transacciones", 
                   font=ctk.CTkFont(size=20, weight="bold")).pack(pady=20)
        
        # Frame Materiales (placeholder)
        self.frames["materials"] = ctk.CTkFrame(self.main_view)
        ctk.CTkLabel(self.frames["materials"], 
                   text="Módulo de Materiales", 
                   font=ctk.CTkFont(size=20, weight="bold")).pack(pady=20)
        
        # Solo para administradores
        if self.current_user and self.current_user.role == "admin":
            try:
                # Frame Usuarios
                self.frames["users"] = UserAdminView(self.main_view)
            except Exception as e:
                print(f"Error al cargar UserAdminView: {e}")
                self.frames["users"] = ctk.CTkFrame(self.main_view)
                ctk.CTkLabel(self.frames["users"], 
                           text=f"Error al cargar módulo de Usuarios: {str(e)}", 
                           text_color="red").pack(pady=20)
            
            # Frame Configuración (placeholder)
            self.frames["settings"] = ctk.CTkFrame(self.main_view)
            ctk.CTkLabel(self.frames["settings"], 
                       text="Configuración del Sistema", 
                       font=ctk.CTkFont(size=20, weight="bold")).pack(pady=20)
    
    def show_frame(self, frame_name):
        """
        Muestra el frame especificado y oculta los demás.
        
        Args:
            frame_name (str): Nombre del frame a mostrar.
        """
        # Verificar permisos para frames de administración
        if frame_name in ["users", "settings"] and (
                not self.current_user or self.current_user.role != "admin"):
            messagebox.showwarning("Acceso denegado", 
                                "No tiene permisos para acceder a esta funcionalidad.")
            return
        
        # Verificar que el frame existe
        if frame_name not in self.frames:
            messagebox.showerror("Error", f"El módulo '{frame_name}' no está disponible")
            return
        
        # Ocultar frame actual
        if self.current_frame and self.current_frame in self.frames:
            self.frames[self.current_frame].pack_forget()
        
        # Mostrar nuevo frame
        self.frames[frame_name].pack(fill="both", expand=True)
        self.current_frame = frame_name
        
        # Actualizar estado
        self.status_msg.configure(text=f"Módulo: {frame_name.capitalize()}")
        
        # Resaltar botón activo en el menú
        self._highlight_active_menu(frame_name)
    
    def _highlight_active_menu(self, active_frame):
        """Resalta el botón del menú activo."""
        if hasattr(self, 'menu_buttons'):
            for frame_name, btn in self.menu_buttons.items():
                if frame_name == active_frame:
                    btn.configure(fg_color=("#43B0F1", "#2D98D6"))
                else:
                    btn.configure(fg_color="transparent")
    
    def _show_user_menu(self):
        """Muestra el menú del usuario."""
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label=f"Usuario: {self.current_user.username}")
        menu.add_separator()
        menu.add_command(label="Cambiar contraseña", command=self._change_password)
        menu.add_separator()
        menu.add_command(label="Cerrar sesión", command=self._logout)
        
        # Mostrar menú en la posición del cursor
        try:
            menu.tk_popup(self.winfo_pointerx(), self.winfo_pointery())
        finally:
            menu.grab_release()
    
    def _change_password(self):
        """Muestra diálogo para cambiar contraseña."""
        # Implementar diálogo de cambio de contraseña
        change_window = ctk.CTkToplevel(self)
        change_window.title("Cambiar contraseña")
        change_window.geometry("400x300")
        change_window.resizable(False, False)
        
        # Centrar ventana
        change_window.update_idletasks()
        width = change_window.winfo_width()
        height = change_window.winfo_height()
        x = (change_window.winfo_screenwidth() // 2) - (width // 2)
        y = (change_window.winfo_screenheight() // 2) - (height // 2)
        change_window.geometry(f'{width}x{height}+{x}+{y}')
        
        # Frame principal
        main_frame = ctk.CTkFrame(change_window)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Título
        title = ctk.CTkLabel(
            main_frame, 
            text="Cambiar Contraseña",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title.pack(pady=(20, 30))
        
        # Variables
        old_pass_var = tk.StringVar()
        new_pass_var = tk.StringVar()
        confirm_pass_var = tk.StringVar()
        
        # Formulario
        form_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        form_frame.pack(fill="x", padx=20, pady=10)
        
        # Contraseña actual
        ctk.CTkLabel(form_frame, text="Contraseña actual:").pack(anchor="w")
        ctk.CTkEntry(form_frame, textvariable=old_pass_var, show="•").pack(fill="x", pady=(5, 15))
        
        # Nueva contraseña
        ctk.CTkLabel(form_frame, text="Nueva contraseña:").pack(anchor="w")
        ctk.CTkEntry(form_frame, textvariable=new_pass_var, show="•").pack(fill="x", pady=(5, 15))
        
        # Confirmar contraseña
        ctk.CTkLabel(form_frame, text="Confirmar nueva contraseña:").pack(anchor="w")
        ctk.CTkEntry(form_frame, textvariable=confirm_pass_var, show="•").pack(fill="x", pady=(5, 15))
        
        # Mensaje de error
        error_label = ctk.CTkLabel(form_frame, text="", text_color="red")
        error_label.pack(fill="x", pady=5)
        
        # Botones
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=20)
        
        def on_cancel():
            change_window.destroy()
        
        def on_change():
            # Aquí iría la lógica para cambiar la contraseña
            # Por ahora mostraremos solo un mensaje
            if not old_pass_var.get() or not new_pass_var.get() or not confirm_pass_var.get():
                error_label.configure(text="Por favor complete todos los campos")
                return
                
            if new_pass_var.get() != confirm_pass_var.get():
                error_label.configure(text="Las nuevas contraseñas no coinciden")
                return
                
            # Simulamos éxito (aquí se conectaría con el controlador de usuarios)
            messagebox.showinfo("Éxito", "Contraseña cambiada correctamente")
            change_window.destroy()
        
        ctk.CTkButton(
            btn_frame, 
            text="Cancelar", 
            command=on_cancel,
            fg_color="gray50",
            width=100
        ).pack(side="left", padx=20)
        
        ctk.CTkButton(
            btn_frame, 
            text="Cambiar", 
            command=on_change,
            width=100
        ).pack(side="right", padx=20)
        
        # Bloquear ventana principal
        change_window.transient(self)
        change_window.grab_set()
    
    def _logout(self):
        """Cierra la sesión actual."""
        if messagebox.askyesno("Cerrar sesión", 
                             "¿Está seguro que desea cerrar la sesión?"):
            # Destruir la ventana actual y mostrar login
            self.withdraw()
            self.current_user = None
            self._show_login()


if __name__ == "__main__":
    try:
        # Asegurar que existen las carpetas necesarias
        for dir_path in ["data", "assets/styles", "assets/images"]:
            os.makedirs(dir_path, exist_ok=True)
        
        app = ISMV3App()
        app.mainloop()
    except Exception as e:
        print(f"Error al iniciar la aplicación: {e}")
        # Mostrar diálogo de error
        root = tk.Tk()
        root.withdraw()
        tk.messagebox.showerror("Error", f"Error al iniciar la aplicación: {e}")