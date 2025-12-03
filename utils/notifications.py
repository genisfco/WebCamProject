"""
Sistema de notificações visuais e sonoras
"""
import winsound
from typing import Optional, Callable


class NotificationManager:
    """Gerenciador de notificações do sistema"""
    
    def __init__(self):
        """Inicializa o gerenciador de notificações"""
        self.callback_log: Optional[Callable[[str], None]] = None
    
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
        
        # Som de sucesso (frequência alta, curta)
        try:
            winsound.Beep(1000, 200)  # Beep agudo e curto
        except Exception:
            pass  # Ignora erros de áudio
    
    def acesso_negado(self, motivo: str, nome_usuario: Optional[str] = None):
        """
        Notifica acesso negado
        
        Args:
            motivo: Motivo da negação
            nome_usuario: Nome do usuário (se identificado)
        """
        if nome_usuario:
            mensagem = f"✗ ACESSO NEGADO: {nome_usuario} - {motivo}"
        else:
            mensagem = f"✗ ACESSO NEGADO: {motivo}"
        
        self._log(mensagem)
        
        # Som de erro (frequência baixa, longa)
        try:
            winsound.Beep(400, 500)  # Beep grave e longo
        except Exception:
            pass  # Ignora erros de áudio
    
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

