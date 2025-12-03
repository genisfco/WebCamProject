"""
Gerenciador do banco de dados SQLite para o sistema de controle de acesso
"""
import sqlite3
import os
from datetime import datetime
from typing import Optional, List, Dict, Tuple


class DatabaseManager:
    """Gerenciador do banco de dados SQLite"""
    
    def __init__(self, db_path: str = "database/access_control.db"):
        """
        Inicializa o gerenciador do banco de dados
        
        Args:
            db_path: Caminho para o arquivo do banco de dados
        """
        self.db_path = db_path
        # Garante que o diretório existe
        db_dir = os.path.dirname(db_path)
        if db_dir:  # Se não for vazio
            os.makedirs(db_dir, exist_ok=True)
        self.init_database()
    
    def get_connection(self) -> sqlite3.Connection:
        """Retorna uma conexão com o banco de dados"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Permite acesso por nome de coluna
        return conn
    
    def init_database(self):
        """Inicializa as tabelas do banco de dados"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Verifica se precisa migrar
        cursor.execute("PRAGMA table_info(usuarios)")
        columns = [row[1] for row in cursor.fetchall()]
        
        # Se a tabela existe mas não tem tipo_identificacao, precisa migrar
        if columns and 'tipo_identificacao' not in columns:
            conn.close()
            # Executa migração
            from database.migrate_db import migrate_database
            migrate_database(self.db_path)
            conn = self.get_connection()
            cursor = conn.cursor()
        
        # Tabela de usuários (nova estrutura)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                numero_identificacao TEXT UNIQUE NOT NULL,
                tipo_identificacao TEXT NOT NULL CHECK(tipo_identificacao IN ('RA', 'RM', 'RG')),
                tipo_acesso TEXT NOT NULL CHECK(tipo_acesso IN ('aluno', 'professor', 'direcao', 'funcionario', 'visitante')),
                ativo INTEGER NOT NULL DEFAULT 1,
                data_cadastro TEXT NOT NULL,
                face_id INTEGER
            )
        """)
        
        # Tabela de histórico de acessos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS historico_acessos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER,
                data_hora TEXT NOT NULL,
                tipo_evento TEXT NOT NULL CHECK(tipo_evento IN ('entrada', 'saida')),
                status TEXT NOT NULL CHECK(status IN ('liberado', 'negado')),
                confianca REAL,
                motivo_negacao TEXT,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
            )
        """)
        
        # Tabela de permissões
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS permissoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER NOT NULL,
                setor_permitido TEXT,
                horario_inicio TEXT,
                horario_fim TEXT,
                dias_semana TEXT,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    # ========== CRUD de Usuários ==========
    
    def criar_usuario(self, nome: str, numero_identificacao: str, 
                     tipo_identificacao: str, tipo_acesso: str, 
                     face_id: Optional[int] = None) -> int:
        """
        Cria um novo usuário no banco de dados
        
        Args:
            nome: Nome do usuário
            numero_identificacao: Número de identificação (RA, RM ou RG)
            tipo_identificacao: Tipo de identificação ('RA', 'RM' ou 'RG')
            tipo_acesso: Tipo de acesso ('aluno', 'professor', 'direcao', 'funcionario', 'visitante')
            face_id: ID da face no sistema de reconhecimento (opcional)
        
        Returns:
            ID do usuário criado
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        data_cadastro = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        try:
            print(f"Executando INSERT: nome={nome}, numero_identificacao={numero_identificacao}, tipo_identificacao={tipo_identificacao}, tipo_acesso={tipo_acesso}")
            
            cursor.execute("""
                INSERT INTO usuarios (nome, numero_identificacao, tipo_identificacao, tipo_acesso, ativo, data_cadastro, face_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (nome, numero_identificacao, tipo_identificacao, tipo_acesso, 1, data_cadastro, face_id))
            
            usuario_id = cursor.lastrowid
            print(f"INSERT executado. ID retornado: {usuario_id}")
            
            conn.commit()
            print(f"Commit realizado. Usuário ID {usuario_id} salvo no banco.")
            
            return usuario_id
        except sqlite3.IntegrityError as e:
            conn.rollback()
            print(f"Erro de integridade: {e}")
            raise ValueError(f"{tipo_identificacao} já cadastrado: {numero_identificacao}") from e
        except sqlite3.Error as e:
            conn.rollback()
            print(f"Erro SQLite: {e}")
            raise Exception(f"Erro no banco de dados: {e}") from e
        except Exception as e:
            conn.rollback()
            print(f"Erro inesperado: {e}")
            raise
        finally:
            conn.close()
    
    def buscar_usuario_por_id(self, usuario_id: int) -> Optional[Dict]:
        """Busca um usuário por ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM usuarios WHERE id = ?", (usuario_id,))
        row = cursor.fetchone()
        conn.close()
        
        return dict(row) if row else None
    
    def buscar_usuario_por_identificacao(self, numero_identificacao: str) -> Optional[Dict]:
        """Busca um usuário por número de identificação"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM usuarios WHERE numero_identificacao = ?", (numero_identificacao,))
        row = cursor.fetchone()
        conn.close()
        
        return dict(row) if row else None
    
    def buscar_usuario_por_ra(self, ra: str) -> Optional[Dict]:
        """Busca um usuário por RA (método legado - mantido para compatibilidade)"""
        return self.buscar_usuario_por_identificacao(ra)
    
    def buscar_usuario_por_face_id(self, face_id: int) -> Optional[Dict]:
        """Busca um usuário por face_id"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM usuarios WHERE face_id = ?", (face_id,))
        row = cursor.fetchone()
        conn.close()
        
        return dict(row) if row else None
    
    def listar_usuarios(self, apenas_ativos: bool = False) -> List[Dict]:
        """
        Lista todos os usuários
        
        Args:
            apenas_ativos: Se True, retorna apenas usuários ativos
        
        Returns:
            Lista de dicionários com informações dos usuários
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if apenas_ativos:
            cursor.execute("SELECT * FROM usuarios WHERE ativo = 1 ORDER BY nome")
        else:
            cursor.execute("SELECT * FROM usuarios ORDER BY nome")
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def atualizar_usuario(self, usuario_id: int, nome: Optional[str] = None, 
                         numero_identificacao: Optional[str] = None,
                         tipo_identificacao: Optional[str] = None,
                         tipo_acesso: Optional[str] = None,
                         ativo: Optional[bool] = None) -> bool:
        """
        Atualiza informações de um usuário
        
        Args:
            usuario_id: ID do usuário
            nome: Novo nome
            numero_identificacao: Novo número de identificação
            tipo_identificacao: Novo tipo de identificação
            tipo_acesso: Novo tipo de acesso
            ativo: Novo status (ativo/inativo)
        
        Returns:
            True se atualizado com sucesso, False caso contrário
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        updates = []
        values = []
        
        if nome is not None:
            updates.append("nome = ?")
            values.append(nome)
        if numero_identificacao is not None:
            updates.append("numero_identificacao = ?")
            values.append(numero_identificacao)
        if tipo_identificacao is not None:
            updates.append("tipo_identificacao = ?")
            values.append(tipo_identificacao)
        if tipo_acesso is not None:
            updates.append("tipo_acesso = ?")
            values.append(tipo_acesso)
        if ativo is not None:
            updates.append("ativo = ?")
            values.append(1 if ativo else 0)
        
        if not updates:
            conn.close()
            return False
        
        values.append(usuario_id)
        query = f"UPDATE usuarios SET {', '.join(updates)} WHERE id = ?"
        
        try:
            cursor.execute(query, values)
            conn.commit()
            success = cursor.rowcount > 0
            conn.close()
            return success
        except sqlite3.IntegrityError:
            conn.rollback()
            conn.close()
            raise ValueError("Número de identificação já cadastrado")
    
    def remover_usuario(self, usuario_id: int) -> bool:
        """
        Remove um usuário do banco de dados
        
        Returns:
            True se removido com sucesso, False caso contrário
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM usuarios WHERE id = ?", (usuario_id,))
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        
        return success
    
    # ========== Histórico de Acessos ==========
    
    def registrar_acesso(self, usuario_id: Optional[int], tipo_evento: str, 
                        status: str, confianca: Optional[float] = None,
                        motivo_negacao: Optional[str] = None) -> int:
        """
        Registra um acesso no histórico
        
        Args:
            usuario_id: ID do usuário (None se não identificado)
            tipo_evento: 'entrada' ou 'saida'
            status: 'liberado' ou 'negado'
            confianca: Nível de confiança do reconhecimento
            motivo_negacao: Motivo da negação (se aplicável)
        
        Returns:
            ID do registro criado
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        cursor.execute("""
            INSERT INTO historico_acessos 
            (usuario_id, data_hora, tipo_evento, status, confianca, motivo_negacao)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (usuario_id, data_hora, tipo_evento, status, confianca, motivo_negacao))
        
        registro_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return registro_id
    
    def buscar_historico(self, usuario_id: Optional[int] = None, 
                        data_inicio: Optional[str] = None,
                        data_fim: Optional[str] = None,
                        status: Optional[str] = None,
                        limite: int = 100) -> List[Dict]:
        """
        Busca histórico de acessos com filtros
        
        Args:
            usuario_id: Filtrar por usuário específico
            data_inicio: Data inicial (formato: YYYY-MM-DD)
            data_fim: Data final (formato: YYYY-MM-DD)
            status: Filtrar por status ('liberado' ou 'negado')
            limite: Número máximo de registros
        
        Returns:
            Lista de registros de histórico
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT h.*, u.nome, u.numero_identificacao, u.tipo_identificacao
            FROM historico_acessos h
            LEFT JOIN usuarios u ON h.usuario_id = u.id
            WHERE 1=1
        """
        params = []
        
        if usuario_id is not None:
            query += " AND h.usuario_id = ?"
            params.append(usuario_id)
        
        if data_inicio:
            query += " AND DATE(h.data_hora) >= ?"
            params.append(data_inicio)
        
        if data_fim:
            query += " AND DATE(h.data_hora) <= ?"
            params.append(data_fim)
        
        if status:
            query += " AND h.status = ?"
            params.append(status)
        
        query += " ORDER BY h.data_hora DESC LIMIT ?"
        params.append(limite)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def obter_estatisticas(self, data_inicio: Optional[str] = None,
                           data_fim: Optional[str] = None) -> Dict:
        """
        Obtém estatísticas de acesso
        
        Returns:
            Dicionário com estatísticas
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        where_clause = ""
        params = []
        
        if data_inicio or data_fim:
            conditions = []
            if data_inicio:
                conditions.append("DATE(data_hora) >= ?")
                params.append(data_inicio)
            if data_fim:
                conditions.append("DATE(data_hora) <= ?")
                params.append(data_fim)
            where_clause = "WHERE " + " AND ".join(conditions)
        
        # Total de acessos
        cursor.execute(f"SELECT COUNT(*) FROM historico_acessos {where_clause}", params)
        total_acessos = cursor.fetchone()[0]
        
        # Acessos liberados
        cursor.execute(
            f"SELECT COUNT(*) FROM historico_acessos {where_clause} AND status = 'liberado'",
            params
        )
        acessos_liberados = cursor.fetchone()[0]
        
        # Acessos negados
        cursor.execute(
            f"SELECT COUNT(*) FROM historico_acessos {where_clause} AND status = 'negado'",
            params
        )
        acessos_negados = cursor.fetchone()[0]
        
        # Taxa de sucesso
        taxa_sucesso = (acessos_liberados / total_acessos * 100) if total_acessos > 0 else 0
        
        conn.close()
        
        return {
            'total_acessos': total_acessos,
            'acessos_liberados': acessos_liberados,
            'acessos_negados': acessos_negados,
            'taxa_sucesso': round(taxa_sucesso, 2)
        }
    
    # ========== Permissões ==========
    
    def criar_permissao(self, usuario_id: int, setor_permitido: Optional[str] = None,
                       horario_inicio: Optional[str] = None,
                       horario_fim: Optional[str] = None,
                       dias_semana: Optional[str] = None) -> int:
        """
        Cria uma permissão para um usuário
        
        Args:
            usuario_id: ID do usuário
            setor_permitido: Setor permitido (opcional)
            horario_inicio: Horário de início (formato: HH:MM)
            horario_fim: Horário de fim (formato: HH:MM)
            dias_semana: Dias da semana permitidos (ex: "1,2,3,4,5" para segunda a sexta)
        
        Returns:
            ID da permissão criada
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO permissoes 
            (usuario_id, setor_permitido, horario_inicio, horario_fim, dias_semana)
            VALUES (?, ?, ?, ?, ?)
        """, (usuario_id, setor_permitido, horario_inicio, horario_fim, dias_semana))
        
        permissao_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return permissao_id
    
    def buscar_permissoes_usuario(self, usuario_id: int) -> List[Dict]:
        """Busca todas as permissões de um usuário"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM permissoes WHERE usuario_id = ?", (usuario_id,))
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def remover_permissao(self, permissao_id: int) -> bool:
        """Remove uma permissão"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM permissoes WHERE id = ?", (permissao_id,))
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        
        return success
    
    def atualizar_face_id(self, usuario_id: int, face_id: int) -> bool:
        """
        Atualiza o face_id de um usuário após o treinamento
        
        Args:
            usuario_id: ID do usuário
            face_id: ID da face no sistema de reconhecimento
        
        Returns:
            True se atualizado com sucesso
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("UPDATE usuarios SET face_id = ? WHERE id = ?", (face_id, usuario_id))
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        
        return success

