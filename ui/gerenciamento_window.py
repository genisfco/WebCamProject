"""
Janela de gerenciamento de usuários
"""
import tkinter as tk
from tkinter import ttk, messagebox
from database.db_manager import DatabaseManager


class GerenciamentoWindow:
    """Janela para gerenciamento de usuários"""
    
    def __init__(self, parent: tk.Tk, db_manager: DatabaseManager):
        """
        Inicializa a janela de gerenciamento
        
        Args:
            parent: Janela pai
            db_manager: Gerenciador do banco de dados
        """
        self.parent = parent
        self.db_manager = db_manager
        
        self.window = tk.Toplevel(parent)
        self.window.title("Gerenciamento de Usuários")
        self.window.geometry("900x500")
        self.window.resizable(True, True)
        
        # Cria interface
        self._create_widgets()
        
        # Carrega dados
        self._load_users()
        
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
            text="Gerenciamento de Usuários",
            font=("Arial", 14, "bold")
        )
        title_label.pack(pady=(0, 10))
        
        # Frame de filtros
        filter_frame = ttk.Frame(main_frame)
        filter_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(filter_frame, text="Filtrar:").pack(side=tk.LEFT, padx=5)
        
        self.filter_var = tk.StringVar(value="todos")
        ttk.Radiobutton(
            filter_frame,
            text="Todos",
            variable=self.filter_var,
            value="todos",
            command=self._load_users
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Radiobutton(
            filter_frame,
            text="Apenas Ativos",
            variable=self.filter_var,
            value="ativos",
            command=self._load_users
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Radiobutton(
            filter_frame,
            text="Apenas Inativos",
            variable=self.filter_var,
            value="inativos",
            command=self._load_users
        ).pack(side=tk.LEFT, padx=5)
        
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
            columns=("id", "nome", "identificacao", "tipo_acesso", "ativo", "data_cadastro"),
            show="headings",
            yscrollcommand=v_scrollbar.set,
            xscrollcommand=h_scrollbar.set
        )
        
        v_scrollbar.config(command=self.tree.yview)
        h_scrollbar.config(command=self.tree.xview)
        
        # Configura colunas
        self.tree.heading("id", text="ID")
        self.tree.heading("nome", text="Nome")
        self.tree.heading("identificacao", text="Identificação")
        self.tree.heading("tipo_acesso", text="Tipo de Acesso")
        self.tree.heading("ativo", text="Status")
        self.tree.heading("data_cadastro", text="Data Cadastro")
        
        self.tree.column("id", width=50)
        self.tree.column("nome", width=200)
        self.tree.column("identificacao", width=180)
        self.tree.column("tipo_acesso", width=120)
        self.tree.column("ativo", width=80)
        self.tree.column("data_cadastro", width=150)
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Botões
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        self.btn_editar = ttk.Button(
            button_frame,
            text="✏️ Editar",
            command=self._edit_user,
            width=15
        )
        self.btn_editar.pack(side=tk.LEFT, padx=5)
        
        self.btn_ativar = ttk.Button(
            button_frame,
            text="✅ Ativar",
            command=self._activate_user,
            width=15
        )
        self.btn_ativar.pack(side=tk.LEFT, padx=5)
        
        self.btn_desativar = ttk.Button(
            button_frame,
            text="❌ Desativar",
            command=self._deactivate_user,
            width=15
        )
        self.btn_desativar.pack(side=tk.LEFT, padx=5)
        
        self.btn_remover = ttk.Button(
            button_frame,
            text="🗑️ Remover",
            command=self._remove_user,
            width=15
        )
        self.btn_remover.pack(side=tk.LEFT, padx=5)
        
        self.btn_atualizar = ttk.Button(
            button_frame,
            text="🔄 Atualizar",
            command=self._load_users,
            width=15
        )
        self.btn_atualizar.pack(side=tk.LEFT, padx=5)
        
        self.btn_fechar = ttk.Button(
            button_frame,
            text="❌ Fechar",
            command=self.window.destroy,
            width=15
        )
        self.btn_fechar.pack(side=tk.RIGHT, padx=5)
    
    def _load_users(self):
        """Carrega usuários na árvore"""
        # Limpa árvore
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Busca usuários
        filter_value = self.filter_var.get()
        
        if filter_value == "ativos":
            usuarios = self.db_manager.listar_usuarios(apenas_ativos=True)
        elif filter_value == "inativos":
            usuarios = self.db_manager.listar_usuarios(apenas_ativos=False)
            usuarios = [u for u in usuarios if not u['ativo']]
        else:
            usuarios = self.db_manager.listar_usuarios(apenas_ativos=False)
        
        # Adiciona à árvore
        for usuario in usuarios:
            status = "Ativo" if usuario['ativo'] else "Inativo"
            # Formata identificação: "RA: 123456" ou "RM: 789012" etc
            tipo_id = usuario.get('tipo_identificacao', 'RA')
            num_id = usuario.get('numero_identificacao', usuario.get('ra', 'N/A'))
            identificacao = f"{tipo_id}: {num_id}"
            
            self.tree.insert(
                "",
                tk.END,
                values=(
                    usuario['id'],
                    usuario['nome'],
                    identificacao,
                    usuario['tipo_acesso'],
                    status,
                    usuario['data_cadastro']
                )
            )
    
    def _get_selected_user(self):
        """Retorna o usuário selecionado"""
        selection = self.tree.selection()
        if not selection:
            return None
        
        item = self.tree.item(selection[0])
        values = item['values']
        
        if not values:
            return None
        
        return {
            'id': values[0],
            'nome': values[1],
            'ra': values[2],
            'tipo_acesso': values[3],
            'ativo': values[4] == "Ativo"
        }
    
    def _edit_user(self):
        """Edita usuário selecionado"""
        usuario = self._get_selected_user()
        if not usuario:
            messagebox.showwarning("Aviso", "Selecione um usuário para editar.")
            return
        
        # Cria janela de edição
        edit_window = tk.Toplevel(self.window)
        edit_window.title("Editar Usuário")
        edit_window.geometry("400x250")
        edit_window.transient(self.window)
        edit_window.grab_set()
        
        frame = ttk.Frame(edit_window, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Nome
        ttk.Label(frame, text="Nome:").grid(row=0, column=0, sticky=tk.W, pady=5)
        entry_nome = ttk.Entry(frame, width=30)
        entry_nome.insert(0, usuario['nome'])
        entry_nome.grid(row=0, column=1, pady=5, padx=5)
        
        # Tipo de acesso (deve vir antes para determinar o label)
        ttk.Label(frame, text="Tipo de Acesso:").grid(row=1, column=0, sticky=tk.W, pady=5)
        combo_tipo = ttk.Combobox(
            frame,
            values=["aluno", "professor", "direcao", "funcionario", "visitante"],
            state="readonly",
            width=27
        )
        combo_tipo.set(usuario['tipo_acesso'])
        combo_tipo.grid(row=1, column=1, pady=5, padx=5)
        
        # Função para determinar tipo de identificação
        def get_tipo_identificacao(tipo_acesso: str) -> str:
            if tipo_acesso == "aluno":
                return "RA"
            elif tipo_acesso in ["professor", "direcao"]:
                return "RM"
            elif tipo_acesso in ["funcionario", "visitante"]:
                return "RG"
            return "RG"
        
        # Label dinâmico para identificação
        label_identificacao = ttk.Label(frame, text=f"{usuario.get('tipo_identificacao', 'RA')}:")
        label_identificacao.grid(row=2, column=0, sticky=tk.W, pady=5)
        
        entry_identificacao = ttk.Entry(frame, width=30)
        entry_identificacao.insert(0, usuario.get('numero_identificacao', ''))
        entry_identificacao.grid(row=2, column=1, pady=5, padx=5)
        
        # Atualiza label quando tipo de acesso muda
        def on_tipo_changed(event=None):
            tipo_acesso = combo_tipo.get()
            tipo_id = get_tipo_identificacao(tipo_acesso)
            label_identificacao.config(text=f"{tipo_id}:")
        
        combo_tipo.bind("<<ComboboxSelected>>", on_tipo_changed)
        
        def salvar():
            try:
                nome = entry_nome.get().strip() or None
                numero_identificacao = entry_identificacao.get().strip() or None
                tipo_acesso = combo_tipo.get() or None
                tipo_identificacao = get_tipo_identificacao(combo_tipo.get()) if tipo_acesso else None
                
                self.db_manager.atualizar_usuario(
                    usuario['id'],
                    nome=nome,
                    numero_identificacao=numero_identificacao,
                    tipo_identificacao=tipo_identificacao,
                    tipo_acesso=tipo_acesso
                )
                messagebox.showinfo("Sucesso", "Usuário atualizado com sucesso!")
                edit_window.destroy()
                self._load_users()
            except ValueError as e:
                messagebox.showerror("Erro", str(e))
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao atualizar: {e}")
        
        ttk.Button(frame, text="Salvar", command=salvar).grid(
            row=3, column=0, columnspan=2, pady=10
        )
    
    def _activate_user(self):
        """Ativa usuário selecionado"""
        usuario = self._get_selected_user()
        if not usuario:
            messagebox.showwarning("Aviso", "Selecione um usuário.")
            return
        
        if usuario['ativo']:
            messagebox.showinfo("Info", "Usuário já está ativo.")
            return
        
        try:
            self.db_manager.atualizar_usuario(usuario['id'], ativo=True)
            messagebox.showinfo("Sucesso", "Usuário ativado com sucesso!")
            self._load_users()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao ativar usuário: {e}")
    
    def _deactivate_user(self):
        """Desativa usuário selecionado"""
        usuario = self._get_selected_user()
        if not usuario:
            messagebox.showwarning("Aviso", "Selecione um usuário.")
            return
        
        if not usuario['ativo']:
            messagebox.showinfo("Info", "Usuário já está inativo.")
            return
        
        if messagebox.askyesno("Confirmar", "Deseja desativar este usuário?"):
            try:
                self.db_manager.atualizar_usuario(usuario['id'], ativo=False)
                messagebox.showinfo("Sucesso", "Usuário desativado com sucesso!")
                self._load_users()
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao desativar usuário: {e}")
    
    def _remove_user(self):
        """Remove usuário selecionado"""
        usuario = self._get_selected_user()
        if not usuario:
            messagebox.showwarning("Aviso", "Selecione um usuário.")
            return
        
        if messagebox.askyesno(
            "Confirmar Remoção",
            f"Deseja realmente remover o usuário {usuario['nome']}?\n\n"
            "Esta ação não pode ser desfeita!"
        ):
            try:
                self.db_manager.remover_usuario(usuario['id'])
                messagebox.showinfo("Sucesso", "Usuário removido com sucesso!")
                self._load_users()
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao remover usuário: {e}")

