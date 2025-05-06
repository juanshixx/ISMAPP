"""
Vista del dashboard principal con elementos visuales mejorados.
"""
import tkinter as tk
import customtkinter as ctk
from PIL import Image, ImageTk
import os
from datetime import datetime
import random  # Solo para datos de ejemplo

class DashboardView(ctk.CTkFrame):
    """Dashboard mejorado con elementos visuales atractivos"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        # Configuración de la cuadrícula
        self.columnconfigure((0, 1, 2), weight=1, uniform="equal")
        self.rowconfigure(0, weight=0)  # Espacio para encabezado
        self.rowconfigure(1, weight=1)  # Espacio para widgets principales
        self.rowconfigure(2, weight=1)  # Espacio para gráficos
        
        # Título con estilo
        header = ctk.CTkFrame(self, fg_color=("gray80", "#1E3D58"), corner_radius=10)
        header.grid(row=0, column=0, columnspan=3, sticky="ew", padx=20, pady=(20, 10))
        
        title_label = ctk.CTkLabel(
            header, 
            text="Panel de Control", 
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=("gray20", "white")
        )
        title_label.pack(pady=15)
        
        # Cargar imágenes si están disponibles
        self.icons = self._load_icons()
        
        # Tarjetas informativas
        self._create_info_cards()
        
        # Sección de gráficos y estadísticas
        self._create_charts()
        
        # Sección de actividades recientes
        self._create_recent_activities()
        
    def _load_icons(self):
        """Carga iconos para la interfaz"""
        icons = {}
        icons_path = os.path.join("assets", "images", "icons")
        
        # Crear directorio si no existe
        os.makedirs(icons_path, exist_ok=True)
        
        # Devolver diccionario vacío si no hay iconos
        return icons
    
    def _create_info_cards(self):
        """Crea tarjetas informativas con estadísticas clave"""
        # Frame contenedor
        cards_frame = ctk.CTkFrame(self, fg_color="transparent")
        cards_frame.grid(row=1, column=0, columnspan=3, sticky="nsew", padx=20, pady=10)
        cards_frame.columnconfigure((0, 1, 2), weight=1, uniform="equal")
        
        # Datos de ejemplo
        card_data = [
            {
                "title": "Pesajes del Mes",
                "value": f"{random.randint(50, 200)}",
                "color": "#43B0F1"  # Azul
            },
            {
                "title": "Material Reciclado",
                "value": f"{random.randint(1000, 5000)} kg",
                "color": "#26C485"  # Verde
            },
            {
                "title": "Ingresos Estimados",
                "value": f"{random.randint(500, 2000)}€",
                "color": "#E8A249"  # Ámbar
            }
        ]
        
        # Crear tarjetas
        for i, data in enumerate(card_data):
            card = ctk.CTkFrame(cards_frame, fg_color=data["color"], corner_radius=15)
            card.grid(row=0, column=i, padx=10, pady=10, sticky="nsew")
            
            # Contenido de la tarjeta
            title = ctk.CTkLabel(
                card, 
                text=data["title"],
                font=ctk.CTkFont(size=14),
                text_color="white"
            )
            title.pack(pady=(15, 5))
            
            value = ctk.CTkLabel(
                card, 
                text=data["value"],
                font=ctk.CTkFont(size=24, weight="bold"),
                text_color="white"
            )
            value.pack(pady=(5, 15))
    
    def _create_charts(self):
        """Crea visualizaciones gráficas simuladas"""
        charts_frame = ctk.CTkFrame(self)
        charts_frame.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=(20, 10), pady=10)
        
        # Encabezado del gráfico
        chart_header = ctk.CTkLabel(
            charts_frame,
            text="Estadísticas de Reciclaje por Material",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        chart_header.pack(pady=(15, 10))
        
        # Simulación de gráfico con barras de colores
        chart_content = ctk.CTkFrame(charts_frame, fg_color="transparent")
        chart_content.pack(fill="both", expand=True, padx=20, pady=10)
        
        materials = ["Cartón", "Plástico", "Metal", "Vidrio", "Otros"]
        colors = ["#E76F51", "#F4A261", "#E9C46A", "#2A9D8F", "#264653"]
        
        for i, (material, color) in enumerate(zip(materials, colors)):
            # Etiqueta de material
            ctk.CTkLabel(chart_content, text=material, width=80).grid(
                row=i, column=0, sticky="w", pady=5)
            
            # Barra de valor
            value = random.randint(10, 100)
            bar_frame = ctk.CTkFrame(chart_content, height=20, fg_color=color, corner_radius=5)
            bar_frame.grid(row=i, column=1, sticky="ew", pady=5)
            
            # Valor numérico
            ctk.CTkLabel(chart_content, text=f"{value}%").grid(
                row=i, column=2, padx=10)
            
        # Expandir las barras
        chart_content.columnconfigure(1, weight=1)
    
    def _create_recent_activities(self):
        """Crea panel de actividades recientes"""
        activity_frame = ctk.CTkFrame(self)
        activity_frame.grid(row=2, column=2, sticky="nsew", padx=(10, 20), pady=10)
        
        # Encabezado
        ctk.CTkLabel(
            activity_frame,
            text="Actividad Reciente",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(15, 10))
        
        # Lista de actividades
        activities = [
            {"text": "Pesaje completado", "time": "Hace 10 min", "user": "Carlos"},
            {"text": "Nuevo cliente registrado", "time": "Hace 2 horas", "user": "Ana"},
            {"text": "Informe mensual generado", "time": "Hoy, 09:45", "user": "Sistema"},
            {"text": "Pago registrado", "time": "Ayer, 16:30", "user": "Miguel"}
        ]
        
        for activity in activities:
            item = ctk.CTkFrame(activity_frame, fg_color=("gray90", "gray20"), corner_radius=6)
            item.pack(fill="x", padx=10, pady=5)
            
            ctk.CTkLabel(
                item, 
                text=activity["text"],
                font=ctk.CTkFont(size=12, weight="bold")
            ).pack(anchor="w", padx=10, pady=(5, 0))
            
            ctk.CTkLabel(
                item,
                text=f"{activity['time']} - {activity['user']}",
                font=ctk.CTkFont(size=10),
                text_color=("gray50", "gray70")
            ).pack(anchor="w", padx=10, pady=(0, 5))