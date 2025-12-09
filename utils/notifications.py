"""
Sistema de notificações visuais e sonoras
"""
import winsound
import cv2
import numpy as np
import threading
import time
from typing import Optional, Callable

# Tenta importar bibliotecas de síntese de voz
try:
    import win32com.client
    TTS_AVAILABLE = True
    TTS_TYPE = 'win32'
except ImportError:
    try:
        import pyttsx3
        TTS_AVAILABLE = True
        TTS_TYPE = 'pyttsx3'
    except ImportError:
        TTS_AVAILABLE = False
        TTS_TYPE = None


class NotificationManager:
    """Gerenciador de notificações do sistema"""
    
    def __init__(self):
        """Inicializa o gerenciador de notificações"""
        self.callback_log: Optional[Callable[[str], None]] = None
        self.tts_engine = None
        self._init_tts()
        
        # Controle de notificação visual ativa
        self.active_notification: Optional[dict] = None
        self.notification_duration = 3.0  # 3 segundos
    
    def _init_tts(self):
        """Inicializa o motor de síntese de voz"""
        if not TTS_AVAILABLE:
            return
            
        try:
            if TTS_TYPE == 'win32':
                self.tts_engine = win32com.client.Dispatch("SAPI.SpVoice")
            elif TTS_TYPE == 'pyttsx3':
                self.tts_engine = pyttsx3.init()
                # Configura velocidade e volume
                self.tts_engine.setProperty('rate', 150)
                self.tts_engine.setProperty('volume', 0.8)
        except Exception as e:
            print(f"⚠ Aviso: Não foi possível inicializar síntese de voz: {e}")
            self.tts_engine = None
    
    def _speak(self, text: str):
        """Fala um texto usando síntese de voz"""
        if not self.tts_engine:
            return
            
        def speak_thread():
            try:
                if TTS_TYPE == 'win32':
                    self.tts_engine.Speak(text)
                elif TTS_TYPE == 'pyttsx3':
                    self.tts_engine.say(text)
                    self.tts_engine.runAndWait()
            except Exception:
                pass  # Ignora erros de voz
        
        # Executa em thread separada para não bloquear
        thread = threading.Thread(target=speak_thread, daemon=True)
        thread.start()
    
    def _draw_notification_box(self, frame: np.ndarray, nome_usuario: str, 
                               status: str, color: tuple):
        """
        Desenha um quadro de notificação grande na tela
        
        Args:
            frame: Frame do OpenCV para desenhar
            nome_usuario: Nome do usuário
            status: Status ("LIBERADO" ou "NEGADO") ou texto com múltiplas linhas
            color: Cor do quadro (B, G, R)
        """
        if frame is None:
            return
            
        h, w = frame.shape[:2]
        
        # Define tamanho do quadro retangular vertical (altura > largura)
        # Largura: 50% da largura do frame
        # Altura: 75% da altura do frame (maior que a largura)
        box_width = int(w * 0.5)
        box_height = int(h * 0.75)
        box_x = (w - box_width) // 2
        box_y = (h - box_height) // 2  # Centralizado verticalmente
        
        # Desenha retângulo de fundo semi-transparente
        overlay = frame.copy()
        cv2.rectangle(overlay, (box_x, box_y), 
                     (box_x + box_width, box_y + box_height), 
                     color, -1)  # Preenchido
        cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)
        
        # Desenha borda do quadro
        cv2.rectangle(frame, (box_x, box_y), 
                     (box_x + box_width, box_y + box_height), 
                     color, 4)
        
        # Texto do nome do usuário (só desenha se não estiver vazio)
        if nome_usuario:
            nome_font_scale = 1
            nome_thickness = 3
            nome_text = nome_usuario.upper()
            (nome_text_width, nome_text_height), _ = cv2.getTextSize(
                nome_text, cv2.FONT_HERSHEY_SIMPLEX, nome_font_scale, nome_thickness
            )
            nome_x = box_x + (box_width - nome_text_width) // 2
            nome_y = box_y + box_height // 2 - 30
            
            cv2.putText(frame, nome_text, (nome_x, nome_y),
                       cv2.FONT_HERSHEY_SIMPLEX, nome_font_scale, 
                       (255, 255, 255), nome_thickness, cv2.LINE_AA)
        
        # Texto do status - suporta múltiplas linhas
        status_font_scale = 1.3
        status_thickness = 5
        
        # Divide o status em linhas (por espaços)
        status_lines = status.split()
        
        # Calcula altura total do texto para centralizar
        line_height = 0
        max_line_width = 0
        for line in status_lines:
            (line_width, line_height_temp), _ = cv2.getTextSize(
                line, cv2.FONT_HERSHEY_SIMPLEX, status_font_scale, status_thickness
            )
            line_height = line_height_temp
            max_line_width = max(max_line_width, line_width)
        
        # Calcula posição inicial (centralizada verticalmente)
        total_text_height = line_height * len(status_lines) + 20 * (len(status_lines) - 1)  # Espaçamento entre linhas
        start_y_offset = total_text_height // 2
        
        # Ajusta posição vertical: se não tem nome, centraliza mais
        if nome_usuario:
            base_y = box_y + box_height // 2 + 50
        else:
            base_y = box_y + box_height // 2
        
        # Desenha cada linha do status
        for i, line in enumerate(status_lines):
            (line_width, _), _ = cv2.getTextSize(
                line, cv2.FONT_HERSHEY_SIMPLEX, status_font_scale, status_thickness
            )
            line_x = box_x + (box_width - line_width) // 2
            line_y = base_y - start_y_offset + i * (line_height + 20)
            
            cv2.putText(frame, line, (line_x, line_y),
                       cv2.FONT_HERSHEY_SIMPLEX, status_font_scale, 
                       (255, 255, 255), status_thickness, cv2.LINE_AA)
    
    def draw_active_notification(self, frame: np.ndarray):
        """
        Desenha a notificação ativa no frame se ainda estiver dentro do tempo
        
        Args:
            frame: Frame do OpenCV para desenhar
        """
        if self.active_notification is None or frame is None:
            return
        
        current_time = time.time()
        elapsed = current_time - self.active_notification['start_time']
        
        # Verifica se ainda está dentro do tempo de exibição
        if elapsed < self.notification_duration:
            self._draw_notification_box(
                frame,
                self.active_notification['nome'],
                self.active_notification['status'],
                self.active_notification['color']
            )
        else:
            # Tempo expirado, limpa a notificação
            self.active_notification = None
    
    def _set_active_notification(self, nome_usuario: str, status: str, color: tuple):
        """
        Define uma notificação visual ativa
        
        Args:
            nome_usuario: Nome do usuário
            status: Status ("LIBERADO" ou "NEGADO")
            color: Cor do quadro (B, G, R)
        """
        self.active_notification = {
            'nome': nome_usuario,
            'status': status,
            'color': color,
            'start_time': time.time()
        }
    
    def set_log_callback(self, callback: Callable[[str], None]):
        """
        Define um callback para registrar logs
        
        Args:
            callback: Função que recebe uma string de log
        """
        self.callback_log = callback
    
    def _log(self, message: str):
        """Registra uma mensagem de log"""
        if self.callback_log:
            self.callback_log(message)
    
    def acesso_liberado(self, nome_usuario: str, confianca: Optional[float] = None):
        """
        Notifica acesso liberado
        
        Args:
            nome_usuario: Nome do usuário
            confianca: Nível de confiança do reconhecimento
        """
        conf_text = f" (Confiança: {confianca:.2f})" if confianca else ""
        mensagem = f"✓ ACESSO LIBERADO: {nome_usuario}{conf_text}"
        
        self._log(mensagem)
        
        # Define notificação visual ativa (será desenhada por 3 segundos)
        self._set_active_notification(nome_usuario, "LIBERADO", (0, 255, 0))
        
        # Voz ao invés de beep
        self._speak(" ACESSO LIBERADO")
    
    def acesso_negado(self, motivo: str, nome_usuario: Optional[str] = None):
        """
        Notifica acesso negado
        
        Args:
            motivo: Motivo da negação
            nome_usuario: Nome do usuário (se identificado)
        """
        if nome_usuario:
            mensagem = f"✗ ACESSO NEGADO: {nome_usuario} - {motivo}"
            display_name = nome_usuario
        else:
            mensagem = f"✗ ACESSO NEGADO: {motivo}"
            display_name = "USUÁRIO"
        
        self._log(mensagem)
        
        # Define notificação visual ativa (será desenhada por 3 segundos)
        self._set_active_notification(display_name, "NEGADO", (0, 0, 255))
        
        # Voz ao invés de beep
        self._speak("ACESSO NEGADO")
    
    def face_nao_identificada(self):
        """Notifica que nenhuma face foi identificada"""
        mensagem = "⚠ Face não identificada"
        self._log(mensagem)
    
    def erro_reconhecimento(self, erro: str):
        """
        Notifica erro no reconhecimento
        
        Args:
            erro: Mensagem de erro
        """
        mensagem = f"❌ ERRO: {erro}"
        self._log(mensagem)
    
    def info(self, mensagem: str):
        """
        Notificação informativa
        
        Args:
            mensagem: Mensagem informativa
        """
        self._log(f"ℹ {mensagem}")
    
    def sucesso_cadastro(self, nome_usuario: str):
        """
        Notifica cadastro bem-sucedido
        
        Args:
            nome_usuario: Nome do usuário cadastrado
        """
        mensagem = f"✓ Usuário {nome_usuario} cadastrado com sucesso!"
        self._log(mensagem)
        
        try:
            winsound.Beep(800, 300)
        except Exception:
            pass
    
    def aviso(self, mensagem: str):
        """
        Notificação de aviso
        
        Args:
            mensagem: Mensagem de aviso
        """
        self._log(f"⚠ AVISO: {mensagem}")
    
    def nenhum_usuario_cadastrado(self):
        """
        Notifica que nenhum usuário está cadastrado no sistema
        """
        mensagem = "⚠ NENHUM USUÁRIO CADASTRADO"
        self._log(mensagem)
        
        # Define notificação visual ativa (será desenhada por 3 segundos)
        # Usa nome vazio e status completo - cada palavra será exibida em uma linha
        self._set_active_notification("", "NENHUM USUARIO CADASTRADO", (0, 165, 255))
        
        # Voz
        self._speak("NENHUM USUÁRIO CADASTRADO")

