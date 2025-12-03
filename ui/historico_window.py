"""
Janela de histórico de acessos
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, timedelta
import csv
from database.db_manager import DatabaseManager


class HistoricoWindow:
    """Janela para visualização do histórico de acessos"""
    
    def __init__(self, parent: tk.Tk, db_manager: DatabaseManager):
        """
        Inicializa a janela de histórico
        
        Args:
            parent: Janela pai
            db_manager: Gerenciador do banco de dados
        """
        self.parent = parent
        self.db_manager = db_manager
        
        self.window = tk.Toplevel(parent)
        self.window.title("Histórico de Acessos")
        self.window.geometry("1100x600")
        self.window.resizable(True, True)
        
        # Cria interface
        self._create_widgets()
        
        # Carrega histórico
        self._load_history()
        
        # Centraliza janela
        self.window.transient(parent)
        self.window.grab_set()
    
    def _create_widgets(self):
        """Cria os widgets da interface"""
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title_label = ttk.Label(
            main_frame,
            text="Histórico de Acessos",
            font=("Arial", 14, "bold")
        )
        title_label.pack(pady=(0, 10))
        
        # Frame de filtros
        filter_frame = ttk.LabelFrame(main_frame, text="Filtros", padding="10")
        filter_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Data inicial
        ttk.Label(filter_frame, text="Data Inicial:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.entry_data_inicio = ttk.Entry(filter_frame, width=12)
        self.entry_data_inicio.insert(0, (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d"))
        self.entry_data_inicio.grid(row=0, column=1, padx=5)
        
        # Data final
        ttk.Label(filter_frame, text="Data Final:").grid(row=0, column=2, sticky=tk.W, padx=5)
        self.entry_data_fim = ttk.Entry(filter_frame, width=12)
        self.entry_data_fim.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.entry_data_fim.grid(row=0, column=3, padx=5)
        
        # Status
        ttk.Label(filter_frame, text="Status:").grid(row=0, column=4, sticky=tk.W, padx=5)
        self.combo_status = ttk.Combobox(
            filter_frame,
            values=["Todos", "liberado", "negado"],
            state="readonly",
            width=15
        )
        self.combo_status.current(0)
        self.combo_status.grid(row=0, column=5, padx=5)
        
        # Botão filtrar
        ttk.Button(
            filter_frame,
            text="🔍 Filtrar",
            command=self._load_history
        ).grid(row=0, column=6, padx=5)
        
        # Estatísticas
        stats_frame = ttk.LabelFrame(main_frame, text="Estatísticas", padding="10")
        stats_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.stats_label = ttk.Label(stats_frame, text="", font=("Arial", 10))
        self.stats_label.pack()
        
        # Treeview
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Treeview
        self.tree = ttk.Treeview(
            tree_frame,
            columns=("id", "data_hora", "nome", "identificacao", "tipo_evento", "status", "confianca", "motivo"),
            show="headings",
            yscrollcommand=v_scrollbar.set,
            xscrollcommand=h_scrollbar.set
        )
        
        v_scrollbar.config(command=self.tree.yview)
        h_scrollbar.config(command=self.tree.xview)
        
        # Configura colunas
        self.tree.heading("id", text="ID")
        self.tree.heading("data_hora", text="Data/Hora")
        self.tree.heading("nome", text="Nome")
        self.tree.heading("identificacao", text="Identificação")
        self.tree.heading("tipo_evento", text="Tipo")
        self.tree.heading("status", text="Status")
        self.tree.heading("confianca", text="Confiança")
        self.tree.heading("motivo", text="Motivo")
        
        self.tree.column("id", width=50)
        self.tree.column("data_hora", width=150)
        self.tree.column("nome", width=150)
        self.tree.column("identificacao", width=150)
        self.tree.column("tipo_evento", width=80)
        self.tree.column("status", width=100)
        self.tree.column("confianca", width=100)
        self.tree.column("motivo", width=200)
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Botões
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(
            button_frame,
            text="📊 Atualizar Estatísticas",
            command=self._update_stats,
            width=20
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="💾 Exportar CSV",
            command=self._export_csv,
            width=20
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="🔄 Atualizar",
            command=self._load_history,
            width=20
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="❌ Fechar",
            command=self.window.destroy,
            width=20
        ).pack(side=tk.RIGHT, padx=5)
        
        # Atualiza estatísticas inicialmente
        self._update_stats()
    
    def _load_history(self):
        """Carrega histórico na árvore"""
        # Limpa árvore
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Obtém filtros
        data_inicio = self.entry_data_inicio.get().strip() or None
        data_fim = self.entry_data_fim.get().strip() or None
        status = self.combo_status.get()
        status_filter = None if status == "Todos" else status
        
        try:
            # Busca histórico
            historico = self.db_manager.buscar_historico(
                usuario_id=None,
                data_inicio=data_inicio,
                data_fim=data_fim,
                status=status_filter,
                limite=500
            )
            
            # Adiciona à árvore
            for registro in historico:
                confianca_str = f"{registro['confianca']:.2f}" if registro['confianca'] else "N/A"
                motivo = registro['motivo_negacao'] or ""
                
                # Obtém nome - verifica se existe no registro (vem do JOIN)
                nome = registro.get('nome') or "Não identificado"
                
                # Formata identificação
                tipo_id = registro.get('tipo_identificacao') or ''
                num_id = registro.get('numero_identificacao') or ''
                
                if tipo_id and num_id:
                    identificacao = f"{tipo_id}: {num_id}"
                elif num_id:
                    identificacao = num_id
                else:
                    identificacao = "N/A"
                
                # Cor baseada no status
                tag = "liberado" if registro['status'] == 'liberado' else "negado"
                
                self.tree.insert(
                    "",
                    tk.END,
                    values=(
                        registro['id'],
                        registro['data_hora'],
                        nome,
                        identificacao,
                        registro['tipo_evento'],
                        registro['status'].upper(),
                        confianca_str,
                        motivo
                    ),
                    tags=(tag,)
                )
            
            # Configura cores
            self.tree.tag_configure("liberado", foreground="green")
            self.tree.tag_configure("negado", foreground="red")
        
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar histórico: {e}")
    
    def _update_stats(self):
        """Atualiza estatísticas"""
        try:
            data_inicio = self.entry_data_inicio.get().strip() or None
            data_fim = self.entry_data_fim.get().strip() or None
            
            stats = self.db_manager.obter_estatisticas(data_inicio, data_fim)
            
            stats_text = (
                f"Total de Acessos: {stats['total_acessos']} | "
                f"Liberados: {stats['acessos_liberados']} | "
                f"Negados: {stats['acessos_negados']} | "
                f"Taxa de Sucesso: {stats['taxa_sucesso']}%"
            )
            
            self.stats_label.config(text=stats_text)
        
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao calcular estatísticas: {e}")
    
    def _export_csv(self):
        """Exporta histórico para CSV"""
        try:
            # Obtém filtros
            data_inicio = self.entry_data_inicio.get().strip() or None
            data_fim = self.entry_data_fim.get().strip() or None
            status = self.combo_status.get()
            status_filter = None if status == "Todos" else status
            
            # Busca histórico
            historico = self.db_manager.buscar_historico(
                usuario_id=None,
                data_inicio=data_inicio,
                data_fim=data_fim,
                status=status_filter,
                limite=10000
            )
            
            if not historico:
                messagebox.showwarning("Aviso", "Nenhum registro para exportar.")
                return
            
            # Seleciona arquivo
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
            )
            
            if not filename:
                return
            
            # Escreve CSV
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                # Cabeçalho
                writer.writerow([
                    "ID", "Data/Hora", "Nome", "RA", "Tipo Evento",
                    "Status", "Confiança", "Motivo Negação"
                ])
                
                # Dados
                for registro in historico:
                    nome = registro.get('nome') or "Não identificado"
                    tipo_id = registro.get('tipo_identificacao') or ''
                    num_id = registro.get('numero_identificacao') or ''
                    identificacao = f"{tipo_id}: {num_id}" if tipo_id and num_id else (num_id or "N/A")
                    
                    writer.writerow([
                        registro['id'],
                        registro['data_hora'],
                        nome,
                        identificacao,
                        registro['tipo_evento'],
                        registro['status'],
                        registro['confianca'] or "",
                        registro['motivo_negacao'] or ""
                    ])
            
            messagebox.showinfo("Sucesso", f"Histórico exportado para {filename}")
        
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao exportar: {e}")

