"""
GUI para Forensic Image Analyzer usando CustomTkinter
"""

"""
GUI para Forensic Image Analyzer usando CustomTkinter
"""

"""
GUI para Forensic Image Analyzer usando CustomTkinter
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
from pathlib import Path
from PIL import Image, ImageTk
from datetime import datetime
import threading
import sys
import os

# Configurar path correctamente
current_dir = Path(__file__).parent. absolute()
project_root = current_dir.parent. parent
sys.path.insert(0, str(project_root))

# Ahora importar módulos del proyecto
try:
    from src.core.acquisition import acquire_image
    from src.core.integrity import verify_integrity
    from src.orchestrator.pipeline import ForensicPipeline
    from src.reporting.consolidator import consolidate_results
    from src.reporting.generator import generate_html_report, generate_json_report
    from src.core.logger import setup_logger
except ImportError as e:
    print(f"Error importing modules: {e}")
    print(f"Current dir: {current_dir}")
    print(f"Project root:  {project_root}")
    print(f"sys.path: {sys.path}")
    sys.exit(1)

# Configurar tema
ctk.set_appearance_mode("dark")  # Modos: "dark", "light", "system"
ctk.set_default_color_theme("blue")  # Temas: "blue", "green", "dark-blue"

class ForensicGUI(ctk.CTk):
    """Interfaz gráfica principal"""
    
    def __init__(self):
        super().__init__()
        
        # Configuración de la ventana
        self. title("🔍 Forensic Image Analyzer")
        self.geometry("1000x700")
        self.minsize(900, 650)
        
        # Variables
        self.image_path = None
        self.output_dir = Path("data/output")
        self.analyzers_state = {}
        self.is_analyzing = False
        
        # Inicializar componentes
        self. logger = setup_logger()
        
        # Crear interfaz
        self.create_widgets()
        
        # Centrar ventana
        self.center_window()
    
    def center_window(self):
        """Centra la ventana en la pantalla"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self. winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_widgets(self):
        """Crea todos los widgets de la interfaz"""
        
        # ===== FRAME PRINCIPAL =====
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
                # ===== SIDEBAR (Izquierda) =====
        self.sidebar = ctk.CTkFrame(self, width=240, corner_radius=0)
        self.sidebar.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar.grid_rowconfigure(6, weight=1)  # ← CAMBIO IMPORTANTE:  dar peso al frame de analyzers
        
        # Logo/Título
        self.logo_label = ctk.CTkLabel(
            self.sidebar, 
            text="🔍 Forensic\nImage Analyzer",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        self.logo_label.grid(row=0, column=0, padx=15, pady=(10, 5))
        
        self.version_label = ctk. CTkLabel(
            self. sidebar,
            text="v1.0.0",
            font=ctk.CTkFont(size=10)
        )
        self.version_label.grid(row=1, column=0, padx=15, pady=(0, 10))
        
        # Botón seleccionar imagen
        self.btn_select_image = ctk.CTkButton(
            self.sidebar,
            text="📁 Select Image",
            command=self.select_image,
            height=35,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.btn_select_image.grid(row=2, column=0, padx=15, pady=5)
        
        # Botón seleccionar output
        self.btn_select_output = ctk.CTkButton(
            self.sidebar,
            text="📂 Output",
            command=self.select_output_dir,
            height=30,
            fg_color="gray30",
            hover_color="gray40",
            font=ctk.CTkFont(size=11)
        )
        self.btn_select_output.grid(row=3, column=0, padx=15, pady=5)
        
        # Separador
        ctk.CTkLabel(self.sidebar, text="").grid(row=4, column=0, pady=3)
        
        # Label "Analyzers"
        self. analyzers_label = ctk. CTkLabel(
            self. sidebar,
            text="Analyzers",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.analyzers_label.grid(row=5, column=0, padx=15, pady=(5, 3))
        
        # Frame scrollable para checkboxes (CON PESO PARA EXPANDIR)
        self.analyzers_frame = ctk.CTkScrollableFrame(
            self. sidebar,
            width=200,
            height=200  # Altura fija moderada
        )
        self.analyzers_frame.grid(row=6, column=0, padx=15, pady=5, sticky="nsew")
        
        # Crear checkboxes para cada analizador
        self.create_analyzer_checkboxes()
        
        # Botón Select All / Deselect All
        self.btn_toggle_all = ctk.CTkButton(
            self.sidebar,
            text="Select All",
            command=self. toggle_all_analyzers,
            height=25,
            fg_color="gray30",
            hover_color="gray40",
            font=ctk.CTkFont(size=10)
        )
        self.btn_toggle_all.grid(row=7, column=0, padx=15, pady=5)
        
        # Separador pequeño
        ctk.CTkLabel(self.sidebar, text="").grid(row=8, column=0, pady=2)
        
        # Botón ANALYZE (grande y llamativo) ← ESTE ES EL IMPORTANTE
        self.btn_analyze = ctk.CTkButton(
            self.sidebar,
            text="🔍 ANALYZE",
            command=self.start_analysis,
            height=45,
            font=ctk. CTkFont(size=14, weight="bold"),
            fg_color="#1f538d",
            hover_color="#14375e"
        )
        self.btn_analyze.grid(row=9, column=0, padx=15, pady=10, sticky="ew")
        
        # ===== ÁREA PRINCIPAL (Derecha) =====
        self.main_frame = ctk.CTkFrame(self, corner_radius=10)
        self.main_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)
        
        # Título área principal
        self.main_title = ctk.CTkLabel(
            self.main_frame,
            text="Image Preview",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.main_title. grid(row=0, column=0, padx=20, pady=(20, 10))
        
        # Frame para imagen
        self.image_frame = ctk.CTkFrame(self.main_frame, fg_color="gray20")
        self.image_frame.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="nsew")
        
        # Label para mostrar imagen
        self.image_label = ctk.CTkLabel(
            self.image_frame,
            text="No image selected\n\n📷\n\nClick 'Select Image' to begin",
            font=ctk.CTkFont(size=16)
        )
        self.image_label.pack(expand=True, fill="both", padx=20, pady=20)
        
        # Frame info de imagen
        self.info_frame = ctk.CTkFrame(self.main_frame)
        self.info_frame. grid(row=2, column=0, padx=20, pady=(0, 20), sticky="ew")
        
        self.info_label = ctk. CTkLabel(
            self. info_frame,
            text="Path: None | Size: N/A | Format: N/A",
            font=ctk. CTkFont(size=12)
        )
        self.info_label.pack(padx=10, pady=10)
        
        # ===== BARRA DE ESTADO (Abajo) =====
        self. status_frame = ctk.CTkFrame(self, corner_radius=0, height=100)
        self.status_frame.grid(row=3, column=1, padx=20, pady=(0, 20), sticky="ew")
        self.status_frame.grid_columnconfigure(0, weight=1)
        
        # Label de estado
        self.status_label = ctk.CTkLabel(
            self.status_frame,
            text="⚪ Ready",
            font=ctk. CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        self.status_label.grid(row=0, column=0, padx=20, pady=(10, 5), sticky="w")
        
        # Barra de progreso
        self. progress_bar = ctk.CTkProgressBar(self.status_frame)
        self.progress_bar. grid(row=1, column=0, padx=20, pady=(0, 10), sticky="ew")
        self.progress_bar.set(0)
        
        # Botones de acción (abajo)
        self.action_frame = ctk.CTkFrame(self. status_frame, fg_color="transparent")
        self.action_frame.grid(row=2, column=0, padx=20, pady=(0, 10), sticky="ew")
        
        self.btn_open_report = ctk.CTkButton(
            self.action_frame,
            text="📄 Open Report",
            command=self.open_report,
            state="disabled",
            fg_color="green",
            hover_color="darkgreen"
        )
        self.btn_open_report.pack(side="left", padx=5)
        
        self. btn_clear = ctk.CTkButton(
            self.action_frame,
            text="🗑️ Clear",
            command=self.clear_all,
            fg_color="gray30",
            hover_color="gray40"
        )
        self.btn_clear.pack(side="left", padx=5)
    
    def create_analyzer_checkboxes(self):
        """Crea checkboxes para cada analizador"""
        analyzers = [
            "Exiftool",
            "ELA (Error Level Analysis)",
            "Clone Detection",
            "Noise Analysis",
            "JPEG Quality Analysis",
            "Luminance Gradient",
            "Edge Inconsistency",
            "Splicing Detection"
        ]
        
        for analyzer in analyzers:
            var = ctk.BooleanVar(value=True)
            checkbox = ctk.CTkCheckBox(
                self.analyzers_frame,
                text=analyzer,
                variable=var,
                font=ctk.CTkFont(size=12)
            )
            checkbox.pack(anchor="w", padx=10, pady=5)
            self.analyzers_state[analyzer] = var
    
    def toggle_all_analyzers(self):
        """Selecciona/deselecciona todos los analizadores"""
        # Verificar si todos están seleccionados
        all_selected = all(var.get() for var in self.analyzers_state.values())
        
        # Invertir estado
        new_state = not all_selected
        for var in self.analyzers_state. values():
            var.set(new_state)
        
        # Actualizar texto del botón
        self.btn_toggle_all.configure(
            text="Deselect All" if new_state else "Select All"
        )
    
    def select_image(self):
        """Abre diálogo para seleccionar imagen"""
        filetypes = [
            ("Image files", "*.jpg *.jpeg *.png *.bmp *.tiff *.tif"),
            ("JPEG files", "*.jpg *. jpeg"),
            ("PNG files", "*.png"),
            ("All files", "*.*")
        ]
        
        filepath = filedialog.askopenfilename(
            title="Select Image to Analyze",
            filetypes=filetypes
        )
        
        if filepath:
            self.image_path = filepath
            self.load_image_preview(filepath)
            self.update_status(f"✅ Image loaded: {Path(filepath).name}", "green")
    
    def load_image_preview(self, filepath):
        """Carga y muestra preview de la imagen"""
        try: 
            # Abrir imagen
            img = Image.open(filepath)
            
            # Obtener info
            width, height = img.size
            format_type = img.format
            file_size = Path(filepath).stat().st_size / 1024  # KB
            
            # Actualizar info
            self.info_label. configure(
                text=f"Path: {filepath} | Size: {width}x{height} | Format:  {format_type} | {file_size:.1f} KB"
            )
            
            # Redimensionar para preview (mantener aspecto)
            max_size = (600, 400)
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Convertir para tkinter
            photo = ctk.CTkImage(light_image=img, dark_image=img, size=img.size)
            
            # Mostrar
            self.image_label.configure(image=photo, text="")
            self.image_label. image = photo  # Mantener referencia
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not load image:\n{str(e)}")
    
    def select_output_dir(self):
        """Selecciona directorio de salida"""
        directory = filedialog.askdirectory(
            title="Select Output Directory",
            initialdir=self.output_dir
        )
        
        if directory:
            self.output_dir = Path(directory)
            self.update_status(f"📂 Output:  {directory}", "blue")
    
    def start_analysis(self):
        """Inicia el análisis en un hilo separado"""
        # Validaciones
        if not self.image_path:
            messagebox.showwarning("No Image", "Please select an image first!")
            return
        
        if self.is_analyzing:
            messagebox.showinfo("Busy", "Analysis already in progress...")
            return
        
        # Verificar que al menos un analizador esté seleccionado
        if not any(var. get() for var in self.analyzers_state.values()):
            messagebox.showwarning("No Analyzers", "Please select at least one analyzer!")
            return
        
        # Deshabilitar botón
        self.btn_analyze. configure(state="disabled")
        self.btn_select_image.configure(state="disabled")
        self.is_analyzing = True
        
        # Ejecutar en hilo separado
        thread = threading.Thread(target=self.run_analysis, daemon=True)
        thread.start()
    
    def run_analysis(self):
        """Ejecuta el análisis completo"""
        try:
            self.update_status("🔄 Starting analysis...", "orange")
            self.progress_bar.set(0.1)
            
            # 1. Copiar imagen a directorio temporal (adquisición simple)
            self.update_status("📥 Preparing image.. .", "orange")
            
            # Crear directorio temporal si no existe
            temp_dir = Path("data/temp")
            temp_dir.mkdir(parents=True, exist_ok=True)
            
            # Copiar imagen con timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            image_name = Path(self.image_path).stem
            image_ext = Path(self.image_path).suffix
            temp_image_path = temp_dir / f"{timestamp}_{image_name}{image_ext}"
            
            import shutil
            shutil.copy2(self.image_path, temp_image_path)
            
            self.progress_bar.set(0.2)
            
            # 2. Pipeline
            self.update_status("🔬 Running analyzers...", "orange")
            pipeline = ForensicPipeline()
            
            # Mapeo de nombres de checkboxes a nombres de analizadores
            analyzer_mapping = {
                "Exiftool": "Exiftool",
                "ELA (Error Level Analysis)": "ELA (Error Level Analysis)",
                "Clone Detection": "Clone Detection",
                "Noise Analysis": "Noise Analysis",
                "JPEG Quality Analysis": "JPEG Quality Analysis",
                "Luminance Gradient": "Luminance Gradient",
                "Edge Inconsistency": "Edge Inconsistency",
                "Splicing Detection":  "Splicing Detection"
            }
            
            # Desactivar analizadores no seleccionados
            for analyzer in pipeline.analyzers:
                checkbox_name = analyzer. name
                
                # Verificar si el checkbox está desmarcado
                if checkbox_name in self.analyzers_state:
                    if not self.analyzers_state[checkbox_name].get():
                        analyzer.enabled = False
                        self.logger.info(f"Desactivando:  {analyzer.name}")
            
            results = pipeline.execute_all(str(temp_image_path))
            self.progress_bar.set(0.6)
            
            # 2.5. Verificar integridad y consolidar resultados
            self.update_status("🔐 Verifying integrity...", "orange")
            integrity_data = verify_integrity(self.image_path)
            
            acquisition_data = {
                'original_path': self.image_path,
                'acquired_path': str(temp_image_path),
                'timestamp': datetime.now().isoformat(),
                'size_bytes': Path(temp_image_path).stat().st_size,
                'filename': Path(self.image_path).name
            }
            
            consolidated = consolidate_results(results, integrity_data, acquisition_data)
            self.progress_bar.set(0.7)
            
            # 3. Generar reportes
            self.update_status("📄 Generating reports.. .", "orange")
            
            # Crear directorio de salida si no existe
            self.output_dir.mkdir(parents=True, exist_ok=True)
            
            # Generar reportes usando las funciones directamente
            self.report_html = generate_html_report(consolidated, str(self.output_dir))
            self.report_json = generate_json_report(consolidated, str(self.output_dir))
            
            self.progress_bar.set(1.0)
            
            # Éxito
            self. update_status("✅ Analysis completed successfully!", "green")
            self.btn_open_report. configure(state="normal")
            
            messagebox.showinfo(
                "Success",
                f"Analysis completed!\n\n"
                f"HTML Report: {self.report_html}\n"
                f"JSON Report:  {self.report_json}"
            )
            
        except Exception as e:
            self. update_status(f"❌ Error: {str(e)}", "red")
            self.logger.error(f"Error en análisis GUI: {str(e)}", exc_info=True)
            messagebox.showerror("Analysis Error", f"An error occurred:\n\n{str(e)}")
        
        finally:
            # Rehabilitar botones
            self.btn_analyze.configure(state="normal")
            self.btn_select_image.configure(state="normal")
            self.is_analyzing = False
    
    def update_status(self, message, color="white"):
        """Actualiza el mensaje de estado"""
        self.status_label.configure(text=message, text_color=color)
        self.update_idletasks()
    
    def open_report(self):
        """Abre el reporte HTML en el navegador"""
        if hasattr(self, 'report_html') and Path(self.report_html).exists():
            import webbrowser
            webbrowser.open(f"file://{Path(self.report_html).absolute()}")
        else:
            messagebox.showwarning("No Report", "No report available to open!")
    
    def clear_all(self):
        """Limpia toda la interfaz"""
        self.image_path = None
        self.image_label.configure(
            image=None,
            text="No image selected\n\n📷\n\nClick 'Select Image' to begin"
        )
        self.info_label.configure(text="Path: None | Size: N/A | Format: N/A")
        self.progress_bar.set(0)
        self.update_status("⚪ Ready", "white")
        self.btn_open_report.configure(state="disabled")


def main():
    """Función principal"""
    app = ForensicGUI()
    app.mainloop()


if __name__ == "__main__":
    main()