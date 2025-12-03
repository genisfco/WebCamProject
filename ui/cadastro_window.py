"""
Janela de cadastro de usuários
"""
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import cv2
import numpy as np
import os
import threading
from typing import Optional, Any

from database.db_manager import DatabaseManager
from modules.face_capture_module import FaceCaptureModule
from modules.training_module import TrainingModule


class CadastroWindow:
    """Janela para cadastro de novos usuários"""
    
    def __init__(self, parent: tk.Tk, db_manager: DatabaseManager, main_window: Any = None):
        """
        Inicializa a janela de cadastro
        
        Args:
            parent: Janela pai
            db_manager: Gerenciador do banco de dados
            main_window: Referência à janela principal
        """
        self.parent = parent
        self.db_manager = db_manager
        self.main_window = main_window
        
        self.window = tk.Toplevel(parent)
        self.window.title("Cadastro de Usuário")
        self.window.geometry("700x650")  # Aumenta altura para garantir espaço para botões
        self.window.resizable(True, True)  # Permite redimensionar para ajustar se necessário
        self.window.minsize(700, 650)  # Define tamanho mínimo
        
        # Módulos
        self.capture_module: Optional[FaceCaptureModule] = None
        self.is_capturing = False
        
        # Estado
        self.current_frame: Optional[np.ndarray] = None
        self.capture_thread: Optional[threading.Thread] = None
        
        # Cria interface
        self._create_widgets()
        
        # Centraliza janela
        self.window.transient(parent)
        self.window.grab_set()
    
    def _create_widgets(self):
        """Cria os widgets da interface"""
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Configura grid para melhor controle do layout
        main_frame.grid_rowconfigure(2, weight=1)  # Linha do vídeo pode expandir
        main_frame.grid_columnconfigure(0, weight=1)
        
        # Título
        title_label = ttk.Label(
            main_frame,
            text="Cadastro de Novo Usuário",
            font=("Arial", 14, "bold")
        )
        title_label.grid(row=0, column=0, pady=(0, 20), sticky=tk.W+tk.E)
        
        # Formulário
        form_frame = ttk.LabelFrame(main_frame, text="Dados do Usuário", padding="10")
        form_frame.grid(row=1, column=0, sticky=tk.W+tk.E, pady=(0, 10))
        form_frame.grid_columnconfigure(1, weight=1)
        
        # Nome
        ttk.Label(form_frame, text="Nome:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.entry_nome = ttk.Entry(form_frame, width=30)
        self.entry_nome.grid(row=0, column=1, pady=5, padx=5)
        
        # Tipo de acesso (deve vir antes do campo de identificação)
        ttk.Label(form_frame, text="Tipo de Acesso:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.combo_tipo = ttk.Combobox(
            form_frame,
            values=["aluno", "professor", "direcao", "funcionario", "visitante"],
            state="readonly",
            width=27
        )
        self.combo_tipo.current(0)
        self.combo_tipo.grid(row=1, column=1, pady=5, padx=5)
        self.combo_tipo.bind("<<ComboboxSelected>>", self._on_tipo_changed)
        
        # Campo de identificação (dinâmico baseado no tipo de acesso)
        self.label_identificacao = ttk.Label(form_frame, text="RA:")
        self.label_identificacao.grid(row=2, column=0, sticky=tk.W, pady=5)
        self.entry_identificacao = ttk.Entry(form_frame, width=30)
        self.entry_identificacao.grid(row=2, column=1, pady=5, padx=5)
        
        # Área de vídeo - com altura máxima para não empurrar botões
        self.video_frame = ttk.LabelFrame(main_frame, text="Captura de Face", padding="5")
        self.video_frame.grid(row=2, column=0, sticky=tk.W+tk.E+tk.N+tk.S, pady=(0, 10))
        self.video_frame.grid_columnconfigure(0, weight=1)
        self.video_frame.grid_rowconfigure(0, weight=1)
        
        self.video_label = ttk.Label(
            self.video_frame,
            text="Clique em 'Iniciar Captura' para começar",
            background="black",
            foreground="white",
            anchor=tk.CENTER
        )
        self.video_label.grid(row=0, column=0, sticky=tk.W+tk.E+tk.N+tk.S)
        
        # Progresso
        progress_frame = ttk.Frame(self.video_frame)
        progress_frame.grid(row=1, column=0, sticky=tk.W+tk.E, pady=5)
        progress_frame.grid_columnconfigure(0, weight=1)
        
        self.progress_label = ttk.Label(progress_frame, text="")
        self.progress_label.grid(row=0, column=0)
        
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            mode='determinate',
            maximum=30
        )
        self.progress_bar.grid(row=1, column=0, sticky=tk.W+tk.E, pady=5)
        
        # Botões - SEMPRE na última linha (row=3), garantindo que fiquem visíveis
        self.button_frame = ttk.Frame(main_frame)
        self.button_frame.grid(row=3, column=0, sticky=tk.W+tk.E, pady=(10, 0))
        
        self.btn_start_capture = ttk.Button(
            self.button_frame,
            text="▶ Iniciar Captura",
            command=self._start_capture,
            width=20
        )
        self.btn_start_capture.grid(row=0, column=0, padx=5)
        
        self.btn_stop_capture = ttk.Button(
            self.button_frame,
            text="⏹ Parar Captura",
            command=self._stop_capture,
            width=20,
            state=tk.DISABLED
        )
        self.btn_stop_capture.grid(row=0, column=1, padx=5)
        
        self.btn_salvar = ttk.Button(
            self.button_frame,
            text="💾 Salvar e Treinar",
            command=self._on_save_button_clicked,
            width=20,
            state=tk.DISABLED
        )
        self.btn_salvar.grid(row=0, column=2, padx=5)
        
        self.btn_cancelar = ttk.Button(
            self.button_frame,
            text="❌ Cancelar",
            command=self._cancel,
            width=20
        )
        self.btn_cancelar.grid(row=0, column=3, padx=5)
        
        # Variáveis de controle
        self.captured_samples = 0
        self.person_name = ""
        
        # Atualiza label inicial
        self._on_tipo_changed()
    
    def _on_tipo_changed(self, event=None):
        """Atualiza o label do campo de identificação baseado no tipo de acesso"""
        tipo_acesso = self.combo_tipo.get()
        
        if tipo_acesso == "aluno":
            self.label_identificacao.config(text="RA:")
        elif tipo_acesso in ["professor", "direcao"]:
            self.label_identificacao.config(text="RM:")
        elif tipo_acesso in ["funcionario", "visitante"]:
            self.label_identificacao.config(text="RG:")
    
    def _get_tipo_identificacao(self, tipo_acesso: str) -> str:
        """Retorna o tipo de identificação baseado no tipo de acesso"""
        if tipo_acesso == "aluno":
            return "RA"
        elif tipo_acesso in ["professor", "direcao"]:
            return "RM"
        elif tipo_acesso in ["funcionario", "visitante"]:
            return "RG"
        else:
            return "RG"  # Padrão
    
    def _start_capture(self):
        """Inicia a captura de faces"""
        # Valida formulário
        nome = self.entry_nome.get().strip()
        numero_identificacao = self.entry_identificacao.get().strip()
        tipo_acesso = self.combo_tipo.get()
        tipo_identificacao = self._get_tipo_identificacao(tipo_acesso)
        
        if not nome:
            messagebox.showerror("Erro", "Por favor, informe o nome do usuário.")
            return
        
        if not numero_identificacao:
            label_text = self.label_identificacao.cget("text")
            messagebox.showerror("Erro", f"Por favor, informe o {label_text} do usuário.")
            return
        
        # Verifica se número de identificação já existe
        if self.db_manager.buscar_usuario_por_identificacao(numero_identificacao):
            messagebox.showerror("Erro", f"{tipo_identificacao} {numero_identificacao} já está cadastrado no sistema.")
            return
        
        if self.is_capturing:
            return
        
        self.person_name = nome
        self.is_capturing = True
        self.captured_samples = 0
        
        # Desabilita campos do formulário
        self.entry_nome.config(state=tk.DISABLED)
        self.entry_identificacao.config(state=tk.DISABLED)
        self.combo_tipo.config(state=tk.DISABLED)
        
        # Atualiza botões
        self.btn_start_capture.config(state=tk.DISABLED)
        self.btn_stop_capture.config(state=tk.NORMAL)
        
        # Garante que os botões estão visíveis antes de iniciar a captura
        self._ensure_buttons_visible()
        
        # Inicia captura em thread separada
        self.capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.capture_thread.start()
    
    def _capture_loop(self):
        """Loop de captura em thread separada"""
        try:
            # Normaliza nome para pasta
            import re
            folder_name = re.sub(r"[^\w\s]", '', self.person_name)
            folder_name = re.sub(r"\s+", '_', folder_name)
            
            output_path = os.path.join("dataset", folder_name)
            output_path_full = os.path.join("dataset_full", folder_name)
            
            # Cria módulo de captura
            self.capture_module = FaceCaptureModule(
                detector_type="haarcascade",
                max_width=640
            )
            
            # Callback para frames
            def frame_callback(frame):
                self.current_frame = frame
                self.window.after(0, self._update_video_display)
            
            self.capture_module.set_frame_callback(frame_callback)
            
            # Callback para progresso
            def progress_callback(current, total):
                self.captured_samples = current
                self.window.after(0, lambda: self._update_progress(current, total))
            
            # Captura faces
            samples = self.capture_module.capture_faces(
                self.person_name,
                output_path,
                output_path_full,
                max_samples=30,
                capture_interval=0.33,  # 3 fotos por segundo (1/3 = 0.33)
                progress_callback=progress_callback
            )
            
            # Finaliza - garante que captured_samples está atualizado
            self.captured_samples = samples
            print(f"Captura concluída na thread. Samples: {samples}, captured_samples: {self.captured_samples}")
            self.window.after(0, lambda s=samples: self._capture_finished(s))
        
        except Exception as e:
            self.window.after(0, lambda: messagebox.showerror("Erro", f"Erro na captura: {e}"))
            self.window.after(0, self._stop_capture)
    
    def _update_video_display(self):
        """Atualiza exibição do vídeo"""
        if self.current_frame is None:
            return
        
        frame_rgb = cv2.cvtColor(self.current_frame, cv2.COLOR_BGR2RGB)
        height, width = frame_rgb.shape[:2]
        
        # Redimensiona
        max_width = 640
        max_height = 360
        if width > max_width or height > max_height:
            scale = min(max_width / width, max_height / height)
            new_width = int(width * scale)
            new_height = int(height * scale)
            frame_rgb = cv2.resize(frame_rgb, (new_width, new_height))
        
        image = Image.fromarray(frame_rgb)
        photo = ImageTk.PhotoImage(image=image)
        
        self.video_label.configure(image=photo, text="")
        self.video_label.image = photo
        
        # Garante que os botões permaneçam visíveis após atualizar o vídeo
        self._ensure_buttons_visible()
        
        if self.is_capturing:
            self.window.after(33, self._update_video_display)
    
    def _update_progress(self, current: int, total: int):
        """Atualiza barra de progresso"""
        self.progress_bar['value'] = current
        self.progress_label.config(text=f"Capturadas: {current}/{total} faces")
        # Garante que os botões permaneçam visíveis durante o progresso
        self._ensure_buttons_visible()
    
    def _ensure_buttons_visible(self):
        """Garante que o frame de botões e todos os botões estão visíveis"""
        try:
            # Garante que o frame de botões está no grid
            if not self.button_frame.winfo_viewable():
                self.button_frame.grid(row=3, column=0, sticky=tk.W+tk.E, pady=(10, 0))
            
            # Garante que todos os botões estão no grid
            buttons = [
                (self.btn_start_capture, 0),
                (self.btn_stop_capture, 1),
                (self.btn_salvar, 2),
                (self.btn_cancelar, 3)
            ]
            for btn, col in buttons:
                try:
                    btn.grid(row=0, column=col, padx=5)
                except:
                    pass
            
            # Força atualização da UI
            self.window.update_idletasks()
        except Exception as e:
            print(f"Erro ao garantir visibilidade dos botões: {e}")
    
    def _capture_finished(self, samples: int):
        """Chamado quando a captura termina"""
        print(f"\n>>> Captura finalizada! {samples} amostras capturadas")
        self.is_capturing = False
        
        # Reabilita campos do formulário
        self.entry_nome.config(state=tk.NORMAL)
        self.entry_identificacao.config(state=tk.NORMAL)
        self.combo_tipo.config(state=tk.NORMAL)
        
        # Garante que os botões estão visíveis e configurados corretamente
        self.btn_start_capture.config(state=tk.NORMAL)
        self.btn_stop_capture.config(state=tk.DISABLED)
        
        # Força atualização da UI antes de mostrar o messagebox
        self.window.update_idletasks()
        
        if samples > 0:
            self.captured_samples = samples  # Garante que o valor está atualizado
            self.progress_label.config(text=f"Captura concluída! {samples} faces capturadas.")
            
            # Habilita o botão de salvar ANTES de mostrar o messagebox
            self.btn_salvar.config(state=tk.NORMAL)
            
            # Garante que o botão está visível
            self.btn_salvar.pack(side=tk.LEFT, padx=5)
            
            print(f">>> Botão 'Salvar e Treinar' habilitado. captured_samples={self.captured_samples}")
            print(f">>> Botão está visível: {self.btn_salvar.winfo_viewable()}")
            
            # Atualiza a UI novamente antes de mostrar o messagebox
            self.window.update_idletasks()
            
            # Mostra o messagebox após um pequeno delay para garantir que a UI foi atualizada
            def show_message_and_refocus():
                messagebox.showinfo("Sucesso", f"Captura concluída! {samples} faces capturadas.")
                # Após fechar o messagebox, garante que a janela está ativa e os botões visíveis
                self.window.focus_set()
                
                # Garante que o frame de botões está visível
                self.button_frame.pack(fill=tk.X)
                
                # Garante que os botões estão visíveis e habilitados
                self.btn_salvar.config(state=tk.NORMAL)
                self.btn_start_capture.config(state=tk.NORMAL)
                self.btn_stop_capture.config(state=tk.DISABLED)
                
                # Garante que os botões estão empacotados corretamente
                self.btn_salvar.pack(side=tk.LEFT, padx=5)
                self.btn_start_capture.pack(side=tk.LEFT, padx=5)
                self.btn_stop_capture.pack(side=tk.LEFT, padx=5)
                self.btn_cancelar.pack(side=tk.LEFT, padx=5)
                
                # Força atualização da UI
                self.window.update_idletasks()
                print(f">>> Após messagebox: Botão está visível e habilitado")
                print(f">>> Botão salvar visível: {self.btn_salvar.winfo_viewable()}")
                print(f">>> Botão salvar estado: {self.btn_salvar.cget('state')}")
                print(f">>> Frame de botões visível: {self.button_frame.winfo_viewable()}")
            
            self.window.after(100, show_message_and_refocus)
        else:
            self.progress_label.config(text="Nenhuma face capturada.")
            def show_warning_and_refocus():
                messagebox.showwarning("Aviso", "Nenhuma face foi capturada.")
                self.window.focus_set()
                self.window.update_idletasks()
            
            self.window.after(100, show_warning_and_refocus)
    
    def _stop_capture(self):
        """Para a captura"""
        self.is_capturing = False
        if self.capture_module:
            self.capture_module.stop_capture()
        
        self.btn_start_capture.config(state=tk.NORMAL)
        self.btn_stop_capture.config(state=tk.DISABLED)
        
        # Reabilita formulário
        self.entry_nome.config(state=tk.NORMAL)
        self.entry_identificacao.config(state=tk.NORMAL)
        self.combo_tipo.config(state=tk.NORMAL)
    
    def _on_save_button_clicked(self):
        """Callback do botão Salvar e Treinar - garante que o método seja chamado"""
        print("\n" + "=" * 60)
        print(">>> BOTÃO 'SALVAR E TREINAR' CLICADO!")
        print("=" * 60)
        print(f">>> Estado do botão: {self.btn_salvar.cget('state')}")
        print(f">>> captured_samples: {self.captured_samples}")
        print(f">>> is_capturing: {self.is_capturing}")
        
        try:
            self._save_and_train()
        except Exception as e:
            import traceback
            error_msg = f"ERRO ao chamar _save_and_train: {e}\n{traceback.format_exc()}"
            print(error_msg)
            messagebox.showerror("Erro", f"Erro ao salvar: {e}")
    
    def _save_and_train(self):
        """Salva usuário e treina reconhecedores"""
        print("=" * 50)
        print("MÉTODO _save_and_train CHAMADO")
        print("=" * 50)
        
        if self.captured_samples == 0:
            print("AVISO: Nenhuma face foi capturada")
            messagebox.showwarning("Aviso", "Nenhuma face foi capturada.")
            return
        
        print(f"Captured samples: {self.captured_samples}")
        
        nome = self.entry_nome.get().strip()
        numero_identificacao = self.entry_identificacao.get().strip()
        tipo_acesso = self.combo_tipo.get()
        tipo_identificacao = self._get_tipo_identificacao(tipo_acesso)
        
        print(f"Dados coletados: nome='{nome}', numero='{numero_identificacao}', tipo_acesso='{tipo_acesso}', tipo_identificacao='{tipo_identificacao}'")
        
        # Validação dos campos
        if not nome:
            print("ERRO: Nome vazio")
            messagebox.showerror("Erro", "Por favor, informe o nome do usuário.")
            return
        
        if not numero_identificacao:
            print("ERRO: Número de identificação vazio")
            label_text = self.label_identificacao.cget("text")
            messagebox.showerror("Erro", f"Por favor, informe o {label_text} do usuário.")
            return
        
        if not tipo_acesso:
            print("ERRO: Tipo de acesso não selecionado")
            messagebox.showerror("Erro", "Por favor, selecione o tipo de acesso.")
            return
        
        try:
            print(f"\n>>> Tentando criar usuário no banco de dados...")
            print(f"    Nome: {nome}")
            print(f"    Número Identificação: {numero_identificacao}")
            print(f"    Tipo Identificação: {tipo_identificacao}")
            print(f"    Tipo Acesso: {tipo_acesso}")
            
            # Cria usuário no banco
            usuario_id = self.db_manager.criar_usuario(
                nome, 
                numero_identificacao, 
                tipo_identificacao, 
                tipo_acesso
            )
            
            print(f"\n>>> ✓✓✓ Usuário criado com SUCESSO! ID: {usuario_id} ✓✓✓\n")
            
            # Treina reconhecedores
            self.progress_label.config(text="Treinando reconhecedores...")
            self.btn_salvar.config(state=tk.DISABLED)
            
            # Treina em thread separada
            training_thread = threading.Thread(
                target=self._train_recognizers,
                args=(usuario_id,),
                daemon=True
            )
            training_thread.start()
            print("Thread de treinamento iniciada")
        
        except ValueError as e:
            print(f"\n✗✗✗ ERRO DE VALIDAÇÃO: {e} ✗✗✗\n")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Erro", str(e))
        except Exception as e:
            import traceback
            error_msg = f"Erro ao salvar usuário: {e}\n\n{traceback.format_exc()}"
            print(f"\n✗✗✗ ERRO INESPERADO: ✗✗✗\n{error_msg}\n")
            messagebox.showerror("Erro", f"Erro ao salvar usuário: {e}")
    
    def _train_recognizers(self, usuario_id: int):
        """Treina reconhecedores em thread separada"""
        try:
            training_module = TrainingModule()
            results = training_module.train_all_recognizers()
            
            # Busca face_id do mapeamento
            face_names = training_module.get_face_names()
            
            # Normaliza nome para buscar no mapeamento
            import re
            folder_name = re.sub(r"[^\w\s]", '', self.person_name)
            folder_name = re.sub(r"\s+", '_', folder_name)
            
            face_id = face_names.get(folder_name)
            
            if face_id:
                self.db_manager.atualizar_face_id(usuario_id, face_id)
            
            # Atualiza UI
            self.window.after(0, lambda: self._training_finished(results))
        
        except Exception as e:
            self.window.after(0, lambda: messagebox.showerror("Erro", f"Erro no treinamento: {e}"))
    
    def _training_finished(self, results: dict):
        """Chamado quando o treinamento termina"""
        success_count = sum(1 for v in results.values() if v)
        
        if success_count > 0:
            messagebox.showinfo(
                "Sucesso",
                f"Usuário cadastrado e treinamento concluído!\n"
                f"{success_count} reconhecedor(es) treinado(s) com sucesso."
            )
            
            # Recarrega reconhecedor na janela principal
            if self.main_window:
                self.main_window.reload_recognizer()
            
            # Fecha janela
            self._cancel()
        else:
            messagebox.showerror("Erro", "Erro ao treinar reconhecedores.")
            self.btn_salvar.config(state=tk.NORMAL)
    
    def _cancel(self):
        """Cancela e fecha a janela"""
        if self.is_capturing:
            self._stop_capture()
        
        self.window.destroy()

