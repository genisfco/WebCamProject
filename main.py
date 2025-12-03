"""
Aplicação principal do Sistema de Controle de Acesso com Reconhecimento Facial
"""
import tkinter as tk
from tkinter import messagebox
import sys
import os

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.db_manager import DatabaseManager
from ui.main_window import MainWindow


def main():
    """Função principal"""
    try:
        # Inicializa banco de dados
        db_manager = DatabaseManager("database/access_control.db")
        
        # Cria interface gráfica
        root = tk.Tk()
        
        # Cria janela principal
        app = MainWindow(root, db_manager)
        
        # Tratamento de fechamento
        def on_closing():
            if app.is_recognition_running:
                if messagebox.askokcancel(
                    "Fechar",
                    "O reconhecimento está ativo. Deseja realmente fechar o sistema?"
                ):
                    app._stop_recognition()
                    root.destroy()
            else:
                root.destroy()
        
        root.protocol("WM_DELETE_WINDOW", on_closing)
        
        # Inicia loop principal
        root.mainloop()
    
    except Exception as e:
        messagebox.showerror(
            "Erro Fatal",
            f"Erro ao iniciar aplicação:\n{e}\n\n"
            "Verifique se todos os arquivos necessários estão presentes."
        )
        sys.exit(1)


if __name__ == "__main__":
    main()

