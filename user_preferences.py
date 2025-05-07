"""
Módulo para gestionar las preferencias personales de cada usuario.
Almacena configuraciones como el orden del menú y el tema de la aplicación.
"""
import os
import json
from pathlib import Path

class UserPreferences:
    def __init__(self, username):
        """
        Inicializa el gestor de preferencias para un usuario específico.
        
        Args:
            username (str): Nombre de usuario para el que se gestionan las preferencias
        """
        self.username = username
        
        # Asegurarse de que existe el directorio
        self.prefs_dir = Path("data/preferences")
        self.prefs_dir.mkdir(parents=True, exist_ok=True)
        
        # Ruta al archivo de preferencias
        self.prefs_file = self.prefs_dir / f"{username}_prefs.json"
        
        # Menú por defecto (coincide con la estructura actual del sidebar)
        self.default_menu = {
            "GENERAL": [
                {"id": "dashboard", "text": "📊  Dashboard"},
            ],
            "OPERACIONES": [
                {"id": "weighing", "text": "⚖️  Pesajes"},
                {"id": "transactions", "text": "💰  Transacciones"},
            ],
            "ENTIDADES": [
                {"id": "workers", "text": "👷  Trabajadores"},
                {"id": "clients", "text": "🏢  Clientes"},
                {"id": "materials", "text": "📦  Materiales"},
            ],
            "ADMINISTRACIÓN": [
                {"id": "users", "text": "👥  Usuarios"},
                {"id": "settings", "text": "⚙️  Configuración"},
            ]
        }
        
        # Preferencias por defecto
        self.default_preferences = {
            "theme": "dark",   # tema oscuro por defecto, como se indica en el código original
            "menu_order": self.default_menu,
        }
        
        # Cargar preferencias
        self._load_preferences()
    
    def _load_preferences(self):
        """Carga las preferencias del usuario desde el archivo."""
        try:
            if self.prefs_file.exists():
                with open(self.prefs_file, 'r', encoding='utf-8') as f:
                    self.preferences = json.load(f)
            else:
                # Si no existe el archivo, usar preferencias por defecto
                self.preferences = self.default_preferences.copy()
                self._save_preferences()
        except Exception as e:
            print(f"Error al cargar preferencias: {e}")
            self.preferences = self.default_preferences.copy()
    
    def _save_preferences(self):
        """Guarda las preferencias del usuario en el archivo."""
        try:
            with open(self.prefs_file, 'w', encoding='utf-8') as f:
                json.dump(self.preferences, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error al guardar preferencias: {e}")
    
    def get_theme(self):
        """
        Obtiene el tema preferido por el usuario.
        
        Returns:
            str: "dark" o "light"
        """
        return self.preferences.get("theme", "dark")
    
    def set_theme(self, theme):
        """
        Establece el tema preferido por el usuario.
        
        Args:
            theme (str): "dark" o "light"
        """
        if theme in ["dark", "light"]:
            self.preferences["theme"] = theme
            self._save_preferences()
    
    def toggle_theme(self):
        """
        Alterna entre tema claro y oscuro.
        
        Returns:
            str: El nuevo tema ("dark" o "light")
        """
        current = self.get_theme()
        new_theme = "light" if current == "dark" else "dark"
        self.set_theme(new_theme)
        return new_theme
    
    def get_menu_order(self):
        """
        Obtiene el orden del menú establecido por el usuario.
        
        Returns:
            dict: Diccionario con la estructura del menú
        """
        return self.preferences.get("menu_order", self.default_menu)
    
    def set_menu_order(self, menu_order):
        """
        Establece un nuevo orden del menú para el usuario.
        
        Args:
            menu_order (dict): Nueva estructura del menú
        """
        self.preferences["menu_order"] = menu_order
        self._save_preferences()
    
    def reset_preferences(self):
        """Restablece todas las preferencias a los valores por defecto."""
        self.preferences = self.default_preferences.copy()
        self._save_preferences()