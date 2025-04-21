import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

class FileList:
    def __init__(self, parent):
        self.parent = parent
        self.loaded_scripts = []
        self._setup_widgets()

    def _setup_widgets(self):
        """Configura os widgets da lista de arquivos."""
        self.files_frame = ttk.LabelFrame(self.parent, text="Scripts SQL para Execução")
        self.files_frame.pack(fill=tk.BOTH, expand=True)

        # Frame interno para a Treeview
        tree_frame = ttk.Frame(self.files_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))

        # Treeview
        columns = ("#", "Nome do Arquivo")
        self.arquivos_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", selectmode='extended')
        self.arquivos_tree.heading("#", text="#")
        self.arquivos_tree.heading("Nome do Arquivo", text="Nome do Arquivo")
        self.arquivos_tree.column("#", width=40, anchor="center", stretch=tk.NO)
        self.arquivos_tree.column("Nome do Arquivo", width=400)
        self.arquivos_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Adiciona evento de seleção
        self.arquivos_tree.bind('<<TreeviewSelect>>', self.update_reorder_buttons_state)

        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.arquivos_tree.yview)
        self.arquivos_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # Configuração do grid
        tree_frame.rowconfigure(0, weight=1)
        tree_frame.columnconfigure(0, weight=1)

        # Botões
        self._setup_buttons()
        
        # Contador
        self.contador_label = ttk.Label(self.files_frame, text="Total: 0 script(s)", font=("Segoe UI", 9, "italic"))
        self.contador_label.pack(anchor=tk.W, pady=(5,0))

    def _setup_buttons(self):
        """Configura os botões de gerenciamento."""
        manage_buttons_frame = ttk.Frame(self.files_frame)
        manage_buttons_frame.pack(fill=tk.X, pady=5)

        add_btn = ttk.Button(manage_buttons_frame, text="Adicionar", command=self.adicionar_scripts)
        add_btn.pack(side=tk.LEFT, padx=3)
        
        remove_btn = ttk.Button(manage_buttons_frame, text="Remover", command=self.remover_scripts)
        remove_btn.pack(side=tk.LEFT, padx=3)
        
        self.move_up_btn = ttk.Button(manage_buttons_frame, text="Mover Acima", 
                                    command=lambda: self.mover_script("cima"), state=tk.DISABLED)
        self.move_up_btn.pack(side=tk.LEFT, padx=3)
        
        self.move_down_btn = ttk.Button(manage_buttons_frame, text="Mover Abaixo", 
                                      command=lambda: self.mover_script("baixo"), state=tk.DISABLED)
        self.move_down_btn.pack(side=tk.LEFT, padx=3)

    def adicionar_scripts(self):
        """Adiciona scripts à lista."""
        files_to_add = filedialog.askopenfilenames(
            title="Selecionar Scripts SQL para Adicionar",
            filetypes=(("SQL files", "*.sql"), ("All files", "*.*"))
        )
        
        if files_to_add:
            added_count = 0
            for file_path in files_to_add:
                if file_path not in self.loaded_scripts:
                    self.loaded_scripts.append(file_path)
                    added_count += 1
            
            if added_count > 0:
                self.atualizar_lista_arquivos()
            else:
                messagebox.showinfo("Nenhum Script Adicionado", "Os scripts selecionados já estavam na lista.")

    def remover_scripts(self):
        """Remove scripts selecionados da lista."""
        selected_items_ids = self.arquivos_tree.selection()
        if not selected_items_ids:
            messagebox.showwarning("Seleção Vazia", "Selecione um ou mais scripts para remover.")
            return

        self.loaded_scripts = [script for script in self.loaded_scripts if script not in selected_items_ids]
        self.atualizar_lista_arquivos()

    def mover_script(self, direcao):
        """Move um script na lista."""
        selected_items = self.arquivos_tree.selection()
        if not selected_items or len(selected_items) > 1:
            messagebox.showwarning("Seleção Inválida", "Selecione um único script para mover.")
            return

        selected_id = selected_items[0]
        try:
            index = self.loaded_scripts.index(selected_id)
            if direcao == "cima" and index > 0:
                # Troca os elementos na lista
                self.loaded_scripts[index], self.loaded_scripts[index - 1] = self.loaded_scripts[index - 1], self.loaded_scripts[index]
                new_index = index - 1
            elif direcao == "baixo" and index < len(self.loaded_scripts) - 1:
                # Troca os elementos na lista
                self.loaded_scripts[index], self.loaded_scripts[index + 1] = self.loaded_scripts[index + 1], self.loaded_scripts[index]
                new_index = index + 1
            else:
                return

            # Atualiza a exibição
            self.atualizar_lista_arquivos()
            
            # Seleciona o item movido
            if new_index != -1:
                moved_item = self.loaded_scripts[new_index]
                self.arquivos_tree.selection_set(moved_item)
                self.arquivos_tree.focus(moved_item)
                self.arquivos_tree.see(moved_item)
        except ValueError:
            messagebox.showerror("Erro Interno", "Script selecionado não encontrado na lista interna.")

    def atualizar_lista_arquivos(self):
        """Atualiza a exibição da lista de arquivos."""
        for item in self.arquivos_tree.get_children():
            self.arquivos_tree.delete(item)
        
        for i, file_path in enumerate(self.loaded_scripts, 1):
            file_name = os.path.basename(file_path)
            self.arquivos_tree.insert("", "end", iid=file_path, values=(i, file_name))
        
        self.contador_label.config(text=f"Total: {len(self.loaded_scripts)} script(s)")
        self.update_reorder_buttons_state()

    def update_reorder_buttons_state(self, *args):
        """Atualiza o estado dos botões de reordenação."""
        selected_items = self.arquivos_tree.selection()
        can_move_up = False
        can_move_down = False

        if len(selected_items) == 1:
            selected_id = selected_items[0]
            try:
                index = self.loaded_scripts.index(selected_id)
                if index > 0:
                    can_move_up = True
                if index < len(self.loaded_scripts) - 1:
                    can_move_down = True
            except ValueError:
                pass

        self.move_up_btn.config(state=tk.NORMAL if can_move_up else tk.DISABLED)
        self.move_down_btn.config(state=tk.NORMAL if can_move_down else tk.DISABLED)

    def get_scripts(self):
        """Retorna a lista de scripts carregados."""
        return self.loaded_scripts 