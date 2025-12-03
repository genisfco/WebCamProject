"""
Script de migração do banco de dados
Migra a estrutura antiga (campo 'ra') para a nova estrutura
(campo 'numero_identificacao' + 'tipo_identificacao')
"""
import sqlite3
import os
from typing import Optional


def migrate_database(db_path: str = "database/access_control.db"):
    """
    Migra o banco de dados da estrutura antiga para a nova
    
    Args:
        db_path: Caminho para o arquivo do banco de dados
    """
    if not os.path.exists(db_path):
        print(f"Banco de dados não encontrado: {db_path}")
        print("O banco será criado automaticamente com a nova estrutura.")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Verifica se já foi migrado (verifica se existe coluna tipo_identificacao)
        cursor.execute("PRAGMA table_info(usuarios)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'tipo_identificacao' in columns:
            print("Banco de dados já está na versão mais recente.")
            conn.close()
            return
        
        print("Iniciando migração do banco de dados...")
        
        # Backup da tabela antiga
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios_backup AS 
            SELECT * FROM usuarios
        """)
        print("✓ Backup criado (usuarios_backup)")
        
        # Cria nova tabela com estrutura atualizada
        cursor.execute("DROP TABLE IF EXISTS usuarios_new")
        cursor.execute("""
            CREATE TABLE usuarios_new (
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
        print("✓ Nova tabela criada")
        
        # Migra dados existentes
        cursor.execute("SELECT * FROM usuarios")
        usuarios_antigos = cursor.fetchall()
        
        # Mapeamento de tipo_acesso antigo para tipo_identificacao
        def get_tipo_identificacao(tipo_acesso_antigo: str) -> str:
            """Determina o tipo de identificação baseado no tipo de acesso"""
            tipo_acesso_antigo = tipo_acesso_antigo.lower()
            if tipo_acesso_antigo == 'professor' or tipo_acesso_antigo == 'direcao':
                return 'RM'
            elif tipo_acesso_antigo == 'funcionario':
                return 'RG'
            else:
                # Assume RA como padrão para casos antigos
                return 'RA'
        
        # Migra cada registro
        for usuario in usuarios_antigos:
            # Estrutura antiga: id, nome, ra, tipo_acesso, ativo, data_cadastro, face_id
            id_antigo = usuario[0]
            nome = usuario[1]
            ra_antigo = usuario[2]
            tipo_acesso_antigo = usuario[3]
            ativo = usuario[4]
            data_cadastro = usuario[5]
            face_id = usuario[6] if len(usuario) > 6 else None
            
            # Determina tipo de identificação
            tipo_identificacao = get_tipo_identificacao(tipo_acesso_antigo)
            
            # Se tipo_acesso antigo não inclui 'aluno', mantém o original
            tipo_acesso_novo = tipo_acesso_antigo
            if tipo_acesso_antigo not in ['aluno', 'professor', 'direcao', 'funcionario', 'visitante']:
                # Se não está na lista, assume como funcionário (mais seguro)
                tipo_acesso_novo = 'funcionario'
            
            try:
                cursor.execute("""
                    INSERT INTO usuarios_new 
                    (id, nome, numero_identificacao, tipo_identificacao, tipo_acesso, ativo, data_cadastro, face_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (id_antigo, nome, ra_antigo, tipo_identificacao, tipo_acesso_novo, ativo, data_cadastro, face_id))
            except sqlite3.IntegrityError as e:
                print(f"⚠ Aviso: Erro ao migrar usuário {nome} (ID: {id_antigo}): {e}")
        
        print(f"✓ {len(usuarios_antigos)} usuário(s) migrado(s)")
        
        # Remove tabela antiga e renomeia a nova
        cursor.execute("DROP TABLE usuarios")
        cursor.execute("ALTER TABLE usuarios_new RENAME TO usuarios")
        print("✓ Tabela atualizada")
        
        # Commit das mudanças
        conn.commit()
        print("✓ Migração concluída com sucesso!")
        
    except Exception as e:
        conn.rollback()
        print(f"✗ Erro na migração: {e}")
        print("Rollback realizado. Banco de dados não foi alterado.")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    migrate_database()

