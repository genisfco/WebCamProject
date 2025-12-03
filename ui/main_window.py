"""
Janela principal do sistema de controle de acesso
"""
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import cv2
import numpy as np
from typing import Optional
from database.db_manager import DatabaseManager
from modules.face_recognition_module import FaceRecognitionModule


class MainWindow:
    """Janela principal do sistema"""
    
    def __init__(self, root: tk.Tk, db_manager: DatabaseManager):
        """
        Inicializa a janela principal
        
        Args:
            root: Raiz do Tkinter
            db_manager: Gerenciador do banco de dados
        """
        self.root = root
        self.db_manager = db_manager
        
        self.root.title("Sistema de Controle de Acesso - Reconhecimento Facial")
        self.root.geometry("1000x700")
        self.root.resizable(True, True)
        
        # Módulo de reconhecimento
        self.recognition_module: Optional[FaceRecognitionModule] = None
        
        # Estado
        self.is_recognition_running = False
        self.current_frame: Optional[np.ndarray] = None
        
        # Cria interface
        self._create_widgets()
        
        # Atualiza status inicial
        self._update_status()
    
    def _create_widgets(self):
        """Cria os widgets da interface"""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Título
        title_label = ttk.Label(
            main_frame, 
            text="Sistema de Controle de Acesso",
            font=("Arial", 16, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        # Frame esquerdo - Controles
        left_frame = ttk.LabelFrame(main_frame, text="Controles", padding="10")
        left_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # Botões de controle
        self.btn_start = ttk.Button(
            left_frame, 
            text="▶ Iniciar Reconhecimento",
            command=self._start_recognition,
            width=25
        )
        self.btn_start.grid(row=0, column=0, pady=5, sticky=tk.W+tk.E)
        
        self.btn_stop = ttk.Button(
            left_frame,
            text="⏹ Parar Reconhecimento",
            command=self._stop_recognition,
            width=25,
            state=tk.DISABLED
        )
        self.btn_stop.grid(row=1, column=0, pady=5, sticky=tk.W+tk.E)
        
        ttk.Separator(left_frame, orient=tk.HORIZONTAL).grid(
            row=2, column=0, sticky=(tk.W, tk.E), pady=10
        )
        
        self.btn_cadastro = ttk.Button(
            left_frame,
            text="➕ Cadastrar Usuário",
            command=self._open_cadastro,
            width=25
        )
        self.btn_cadastro.grid(row=3, column=0, pady=5, sticky=tk.W+tk.E)
        
        self.btn_gerenciar = ttk.Button(
            left_frame,
            text="👥 Gerenciar Usuários",
            command=self._open_gerenciamento,
            width=25
        )
        self.btn_gerenciar.grid(row=4, column=0, pady=5, sticky=tk.W+tk.E)
        
        self.btn_historico = ttk.Button(
            left_frame,
            text="📊 Ver Histórico",
            command=self._open_historico,
            width=25
        )
        self.btn_historico.grid(row=5, column=0, pady=5, sticky=tk.W+tk.E)
        
        # Indicador de status
        status_frame = ttk.LabelFrame(left_frame, text="Status", padding="10")
        status_frame.grid(row=6, column=0, pady=10, sticky=(tk.W, tk.E))
        
        self.status_label = ttk.Label(
            status_frame,
            text="Sistema parado",
            font=("Arial", 10)
        )
        self.status_label.grid(row=0, column=0)
        
        # LED de acesso
        self.access_led = tk.Canvas(
            status_frame,
            width=30,
            height=30,
            bg="gray",
            relief=tk.RAISED,
            borderwidth=2
        )
        self.access_led.grid(row=1, column=0, pady=5)
        self._draw_led("gray")
        
        # Frame direito - Vídeo e Log
        right_frame = ttk.Frame(main_frame)
        right_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(0, weight=1)
        
        # Área de vídeo
        video_frame = ttk.LabelFrame(right_frame, text="Vídeo", padding="5")
        video_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        video_frame.columnconfigure(0, weight=1)
        video_frame.rowconfigure(0, weight=1)
        
        self.video_label = ttk.Label(
            video_frame,
            text="Câmera não iniciada",
            background="black",
            foreground="white",
            anchor=tk.CENTER
        )
        self.video_label.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Área de log
        log_frame = ttk.LabelFrame(right_frame, text="Log de Eventos", padding="5")
        log_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        # Scrollbar para log
        log_scrollbar = ttk.Scrollbar(log_frame)
        log_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        self.log_text = tk.Text(
            log_frame,
            height=10,
            wrap=tk.WORD,
            yscrollcommand=log_scrollbar.set,
            font=("Consolas", 9)
        )
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        log_scrollbar.config(command=self.log_text.yview)
        
        # Configura reconhecimento
        self._setup_recognition()
    
    def _setup_recognition(self):
        """Configura o módulo de reconhecimento"""
        try:
            self.recognition_module = FaceRecognitionModule(
                self.db_manager,
                recognizer_type="lbph",
                threshold=10e5,
                max_width=640
            )
            
            # Callbacks
            self.recognition_module.set_frame_callback(self._on_frame_received)
            self.recognition_module.set_access_callback(self._on_access_event)
            self.recognition_module.set_log_callback(self._log_message)
        except Exception as e:
            self._log_message(f"⚠ Aviso: Erro ao inicializar módulo de reconhecimento: {e}")
            self._log_message("⚠ O sistema funcionará, mas o reconhecimento não estará disponível até treinar usuários.")
    
    def _on_frame_received(self, frame: np.ndarray):
        """Callback quando um frame é processado"""
        self.current_frame = frame
        self._update_video_display()
    
    def _update_video_display(self):
        """Atualiza a exibição do vídeo"""
        if self.current_frame is None:
            return
        
        # Converte BGR para RGB
        frame_rgb = cv2.cvtColor(self.current_frame, cv2.COLOR_BGR2RGB)
        
        # Redimensiona para caber no label
        height, width = frame_rgb.shape[:2]
        max_width = 640
        max_height = 480
        
        if width > max_width or height > max_height:
            scale = min(max_width / width, max_height / height)
            new_width = int(width * scale)
            new_height = int(height * scale)
            frame_rgb = cv2.resize(frame_rgb, (new_width, new_height))
        
        # Converte para ImageTk
        image = Image.fromarray(frame_rgb)
        photo = ImageTk.PhotoImage(image=image)
        
        # Atualiza label
        self.video_label.configure(image=photo, text="")
        self.video_label.image = photo  # Mantém referência
        
        # Agenda próxima atualização
        self.root.after(33, self._update_video_display)  # ~30 FPS
    
    def _on_access_event(self, event_data: dict):
        """Callback quando há um evento de acesso"""
        status = event_data.get('status', '')
        
        if status == 'liberado':
            self._draw_led("green")
            self.root.after(2000, lambda: self._draw_led("gray"))
        elif status == 'negado':
            self._draw_led("red")
            self.root.after(2000, lambda: self._draw_led("gray"))
    
    def _draw_led(self, color: str):
        """Desenha o LED de status"""
        self.access_led.delete("all")
        self.access_led.create_oval(5, 5, 25, 25, fill=color, outline="black", width=2)
    
    def _log_message(self, message: str):
        """Adiciona mensagem ao log"""
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        
        # Limita tamanho do log
        lines = self.log_text.get("1.0", tk.END).split('\n')
        if len(lines) > 100:
            self.log_text.delete("1.0", f"{len(lines) - 100}.0")
    
    def _start_recognition(self):
        """Inicia o reconhecimento facial"""
        if self.is_recognition_running:
            return
        
        try:
            self.recognition_module.start_recognition()
            self.is_recognition_running = True
            
            self.btn_start.config(state=tk.DISABLED)
            self.btn_stop.config(state=tk.NORMAL)
            self.status_label.config(text="Reconhecimento ativo")
            
            self._log_message("Sistema de reconhecimento iniciado")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao iniciar reconhecimento: {e}")
            self._log_message(f"ERRO: {e}")
    
    def _stop_recognition(self):
        """Para o reconhecimento facial"""
        if not self.is_recognition_running:
            return
        
        try:
            self.recognition_module.stop_recognition()
            self.is_recognition_running = False
            
            self.btn_start.config(state=tk.NORMAL)
            self.btn_stop.config(state=tk.DISABLED)
            self.status_label.config(text="Sistema parado")
            
            # Limpa vídeo
            self.current_frame = None
            self.video_label.configure(image="", text="Câmera parada")
            
            self._log_message("Sistema de reconhecimento parado")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao parar reconhecimento: {e}")
    
    def _open_cadastro(self):
        """Abre janela de cadastro"""
        if self.is_recognition_running:
            messagebox.showwarning(
                "Aviso",
                "Pare o reconhecimento antes de cadastrar um novo usuário."
            )
            return
        
        # Importação tardia para evitar circular import
        from ui.cadastro_window import CadastroWindow
        cadastro_window = CadastroWindow(self.root, self.db_manager, self)
        # grab_set() já é chamado no __init__ do CadastroWindow
    
    def _open_gerenciamento(self):
        """Abre janela de gerenciamento"""
        # Importação tardia para evitar circular import
        from ui.gerenciamento_window import GerenciamentoWindow
        gerenciamento_window = GerenciamentoWindow(self.root, self.db_manager)
        # grab_set() já é chamado no __init__ do GerenciamentoWindow
    
    def _open_historico(self):
        """Abre janela de histórico"""
        # Importação tardia para evitar circular import
        from ui.historico_window import HistoricoWindow
        historico_window = HistoricoWindow(self.root, self.db_manager)
        # grab_set() já é chamado no __init__ do HistoricoWindow
    
    def _update_status(self):
        """Atualiza status do sistema"""
        usuarios_count = len(self.db_manager.listar_usuarios(apenas_ativos=True))
        self._log_message(f"Sistema inicializado. {usuarios_count} usuário(s) ativo(s) cadastrado(s).")
    
    def reload_recognizer(self):
        """Recarrega o reconhecedor (chamado após novo cadastro)"""
        if self.recognition_module:
            self.recognition_module.reload_recognizer()
            self._log_message("Reconhecedor recarregado com sucesso")

