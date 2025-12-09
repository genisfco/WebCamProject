"""
Script para resetar o banco de dados e dados de treinamento
"""
import os
import shutil
import sqlite3

def reset_database():
    """Remove todos os dados do sistema"""
    
    print("=" * 60)
    print("RESETANDO SISTEMA - REMOVENDO TODOS OS DADOS")
    print("=" * 60)
    
    # Confirmação
    resposta = input("\n⚠️  ATENÇÃO: Isso irá deletar TODOS os usuários e fotos!\n"
                     "Deseja continuar? (digite 'SIM' para confirmar): ")
    
    if resposta != "SIM":
        print("Operação cancelada.")
        return
    
    # Remove pastas de imagens
    print("\n1. Removendo pastas de imagens...")
    for pasta in ['dataset', 'dataset_full']:
        if os.path.exists(pasta):
            try:
                shutil.rmtree(pasta)
                print(f"   ✓ Pasta '{pasta}' removida")
            except Exception as e:
                print(f"   ✗ Erro ao remover pasta '{pasta}': {e}")
        else:
            print(f"   - Pasta '{pasta}' não encontrada")
    
    # Remove classificadores treinados
    print("\n2. Removendo classificadores treinados...")
    arquivos_classificadores = [
        'eigen_classifier.yml',
        'fisher_classifier.yml',
        'lbph_classifier.yml',
        'face_names.pickle'
    ]
    
    for arquivo in arquivos_classificadores:
        if os.path.exists(arquivo):
            try:
                os.remove(arquivo)
                print(f"   ✓ Arquivo '{arquivo}' removido")
            except Exception as e:
                print(f"   ✗ Erro ao remover arquivo '{arquivo}': {e}")
        else:
            print(f"   - Arquivo '{arquivo}' não encontrado")
    
    # Remove banco de dados
    print("\n3. Removendo banco de dados...")
    db_path = 'database/access_control.db'
    db_journal = 'database/access_control.db-journal'
    
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
            print(f"   ✓ Banco de dados removido")
        except Exception as e:
            print(f"   ✗ Erro ao remover banco de dados: {e}")
    else:
        print(f"   - Banco de dados não encontrado")
    
    if os.path.exists(db_journal):
        try:
            os.remove(db_journal)
            print(f"   ✓ Arquivo journal removido")
        except Exception as e:
            print(f"   ✗ Erro ao remover arquivo journal: {e}")
    
    print("\n" + "=" * 60)
    print("✓ RESET CONCLUÍDO COM SUCESSO!")
    print("=" * 60)
    print("\nO sistema será reinicializado na próxima execução.")
    print("Execute: python main.py")

if __name__ == "__main__":
    reset_database()

