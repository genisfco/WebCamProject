"""
Sistema de permissões para controle de acesso
"""
from datetime import datetime, time
from typing import Optional, List, Dict, Tuple
from database.db_manager import DatabaseManager


class PermissionChecker:
    """Verificador de permissões de acesso"""
    
    def __init__(self, db_manager: DatabaseManager):
        """
        Inicializa o verificador de permissões
        
        Args:
            db_manager: Instância do gerenciador de banco de dados
        """
        self.db_manager = db_manager
    
    def verificar_acesso(self, usuario_id: int, setor: Optional[str] = None) -> Tuple[bool, str]:
        """
        Verifica se um usuário tem permissão de acesso
        
        Args:
            usuario_id: ID do usuário
            setor: Setor onde está tentando acessar (opcional)
        
        Returns:
            Tupla (permitido: bool, motivo: str)
        """
        # Verifica se o usuário existe e está ativo
        usuario = self.db_manager.buscar_usuario_por_id(usuario_id)
        
        if not usuario:
            return False, "Usuário não encontrado"
        
        if not usuario['ativo']:
            return False, "Usuário inativo"
        
        # Busca permissões do usuário
        permissoes = self.db_manager.buscar_permissoes_usuario(usuario_id)
        
        # Se não há permissões específicas, permite acesso (comportamento padrão)
        if not permissoes:
            return True, "Acesso permitido"
        
        # Verifica cada permissão
        agora = datetime.now()
        hora_atual = agora.time()
        dia_semana = agora.weekday()  # 0 = segunda, 6 = domingo
        
        for permissao in permissoes:
            # Verifica setor
            if permissao['setor_permitido'] and setor:
                if permissao['setor_permitido'] != setor:
                    continue
            
            # Verifica horário
            if permissao['horario_inicio'] and permissao['horario_fim']:
                try:
                    hora_inicio = datetime.strptime(permissao['horario_inicio'], "%H:%M").time()
                    hora_fim = datetime.strptime(permissao['horario_fim'], "%H:%M").time()
                    
                    if not (hora_inicio <= hora_atual <= hora_fim):
                        continue
                except ValueError:
                    # Se formato inválido, ignora verificação de horário
                    pass
            
            # Verifica dias da semana
            if permissao['dias_semana']:
                dias_permitidos = [int(d) for d in permissao['dias_semana'].split(',') if d.strip()]
                # Ajusta para formato Python (0=segunda, 6=domingo)
                # Se no banco está 0=domingo, ajustar conforme necessário
                if dia_semana not in dias_permitidos:
                    continue
            
            # Se passou em todas as verificações, permite acesso
            return True, "Acesso permitido"
        
        # Se nenhuma permissão foi satisfeita
        return False, "Acesso negado: fora do horário/período permitido"
    
    def verificar_status_usuario(self, usuario_id: int) -> Tuple[bool, str]:
        """
        Verifica apenas o status do usuário (ativo/inativo)
        
        Returns:
            Tupla (ativo: bool, motivo: str)
        """
        usuario = self.db_manager.buscar_usuario_por_id(usuario_id)
        
        if not usuario:
            return False, "Usuário não encontrado"
        
        if usuario['ativo']:
            return True, "Usuário ativo"
        else:
            return False, "Usuário inativo"
    
    def obter_nivel_acesso(self, usuario_id: int) -> Optional[str]:
        """
        Obtém o nível de acesso do usuário
        
        Returns:
            Tipo de acesso (professor, direcao, funcionario) ou None
        """
        usuario = self.db_manager.buscar_usuario_por_id(usuario_id)
        return usuario['tipo_acesso'] if usuario else None
    
    def pode_acessar_setor(self, usuario_id: int, setor: str) -> bool:
        """
        Verifica se o usuário pode acessar um setor específico
        
        Args:
            usuario_id: ID do usuário
            setor: Nome do setor
        
        Returns:
            True se pode acessar, False caso contrário
        """
        permissoes = self.db_manager.buscar_permissoes_usuario(usuario_id)
        
        # Se não há permissões específicas, permite acesso
        if not permissoes:
            return True
        
        # Verifica se alguma permissão permite acesso ao setor
        for permissao in permissoes:
            if not permissao['setor_permitido'] or permissao['setor_permitido'] == setor:
                return True
        
        return False

