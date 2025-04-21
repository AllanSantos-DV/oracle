import os
import tkinter as tk
import threading
from tkinter import ttk, filedialog, messagebox, scrolledtext
from src.gui.widgets.file_list import FileList
from src.gui.widgets.output_panel import OutputPanel
from src.config.config_manager import ConfigManager
from src.database.oracle_connector import OracleConnector
from src.utils.validators import Validators

# Constantes para as respostas do diálogo de erro
IGNORAR = 1
IGNORAR_TODOS = 2
PARAR = 3

class MainWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Executor de Scripts SQL Oracle v1.1")
        self.root.geometry("800x600")  # Reduzido para 800x600
        self.root.minsize(800, 600)    # Tamanho mínimo da janela
        
        self.config_manager = ConfigManager()
        self.oracle_connector = OracleConnector()
        
        # Flag para controlar operações em andamento
        self.operation_in_progress = False
        
        self._setup_styles()
        self._setup_layout()
        self._load_initial_config()

    def _setup_styles(self):
        """Configura os estilos da interface."""
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TFrame", background="#ececec")
        style.configure("TLabel", background="#ececec", font=("Segoe UI", 9))  # Fonte reduzida
        style.configure("TButton", font=("Segoe UI", 9), padding=3)  # Botões menores
        style.configure("TEntry", font=("Segoe UI", 9), padding=3)  # Entradas menores
        style.configure("Treeview", font=("Segoe UI", 9), rowheight=22)  # Linhas menores
        style.configure("Treeview.Heading", font=("Segoe UI", 9, "bold"))
        style.configure("TLabelframe", background="#ececec", padding=6)  # Padding reduzido
        style.configure("TLabelframe.Label", background="#ececec", font=("Segoe UI", 10, "bold"))

    def _setup_layout(self):
        """Configura o layout da janela principal."""
        # Divisor principal vertical
        main_paned_window = ttk.PanedWindow(self.root, orient=tk.VERTICAL)
        main_paned_window.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)  # Menos padding

        # Painel superior
        top_frame = ttk.Frame(main_paned_window, padding=6)  # Padding reduzido
        main_paned_window.add(top_frame, weight=0)

        # Frame de configuração - reduzido
        config_frame = ttk.LabelFrame(top_frame, text="Configuração de Conexão")
        config_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 8))

        # Campos de configuração
        self._setup_config_fields(config_frame)

        # Botões principais
        main_button_frame = ttk.Frame(top_frame)
        main_button_frame.grid(row=0, column=1, sticky=(tk.N, tk.S, tk.E, tk.W), padx=(8, 0))
        
        validar_btn = ttk.Button(main_button_frame, text="Validar Conexão", command=self.validar_conexao)
        validar_btn.pack(pady=3, fill=tk.X)  # Menos espaço
        
        executar_btn = ttk.Button(main_button_frame, text="Executar Scripts", command=self.executar_scripts)
        executar_btn.pack(pady=3, fill=tk.X)  # Menos espaço
        
        sair_btn = ttk.Button(main_button_frame, text="Sair", command=self.root.destroy)
        sair_btn.pack(pady=3, fill=tk.X)  # Menos espaço

        # Configura o frame de configuração para expandir
        top_frame.columnconfigure(0, weight=3)  # Dá mais espaço ao campo de configuração
        top_frame.columnconfigure(1, weight=1)  # Menos espaço para botões

        # Painel inferior
        bottom_paned_window = ttk.PanedWindow(main_paned_window, orient=tk.HORIZONTAL)
        main_paned_window.add(bottom_paned_window, weight=5)  # Dá mais peso ao painel inferior

        # Painel esquerdo (lista de arquivos)
        files_panel = ttk.Frame(bottom_paned_window, padding=3)  # Menos padding
        bottom_paned_window.add(files_panel, weight=1)
        self.file_list = FileList(files_panel)

        # Painel direito (saída)
        output_panel = ttk.Frame(bottom_paned_window, padding=3)  # Menos padding
        bottom_paned_window.add(output_panel, weight=1)
        self.output_panel = OutputPanel(output_panel)
        
        # Configura a posição inicial do divisor (40% para arquivos, 60% para saída)
        bottom_paned_window.sashpos(0, 320)

    def _setup_config_fields(self, parent):
        """Configura os campos de configuração."""
        # Reduz tamanho e padding para economizar espaço
        
        # Pasta inicial
        ttk.Label(parent, text="Pasta Inicial:").grid(row=0, column=0, sticky=tk.W, padx=3, pady=2)
        self.folder_entry = ttk.Entry(parent, width=40)  # Reduzido de 50 para 40
        self.folder_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=3, pady=2)
        ttk.Button(parent, text="Procurar", command=self.selecionar_pasta).grid(row=0, column=2, padx=3, pady=2)  # Texto reduzido

        # Usuário
        ttk.Label(parent, text="Usuário:").grid(row=1, column=0, sticky=tk.W, padx=3, pady=2)
        self.user_entry = ttk.Entry(parent)
        self.user_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=3, pady=2)

        # Senha
        ttk.Label(parent, text="Senha:").grid(row=2, column=0, sticky=tk.W, padx=3, pady=2)
        self.password_entry = ttk.Entry(parent, show="*")
        self.password_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=3, pady=2)

        # Host
        ttk.Label(parent, text="Host:").grid(row=3, column=0, sticky=tk.W, padx=3, pady=2)
        self.host_entry = ttk.Entry(parent)
        self.host_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), padx=3, pady=2)

        # Porta
        ttk.Label(parent, text="Porta:").grid(row=4, column=0, sticky=tk.W, padx=3, pady=2)
        self.port_entry = ttk.Entry(parent)
        self.port_entry.grid(row=4, column=1, sticky=(tk.W, tk.E), padx=3, pady=2)

        # Service Name
        ttk.Label(parent, text="Service Name:").grid(row=5, column=0, sticky=tk.W, padx=3, pady=2)
        self.service_entry = ttk.Entry(parent)
        self.service_entry.grid(row=5, column=1, sticky=(tk.W, tk.E), padx=3, pady=2)

        # Configura a coluna dos campos para expandir
        parent.columnconfigure(1, weight=1)

    def _load_initial_config(self):
        """Carrega a configuração inicial."""
        config = self.config_manager.get_config()
        
        # Preenche os campos com os valores salvos
        self.folder_entry.insert(0, config.get("folder", ""))
        self.user_entry.insert(0, config.get("user", ""))
        self.password_entry.insert(0, config.get("password", ""))
        self.host_entry.insert(0, config.get("host", "localhost"))
        self.port_entry.insert(0, config.get("port", "1521"))
        self.service_entry.insert(0, config.get("service", "XE"))

        # Carrega scripts da pasta inicial
        if config.get("folder"):
            try:
                initial_folder = config["folder"]
                if os.path.isdir(initial_folder):
                    initial_files = sorted([
                        os.path.join(initial_folder, f) 
                        for f in os.listdir(initial_folder) 
                        if f.lower().endswith('.sql')
                    ])
                    self.file_list.loaded_scripts = initial_files
                    self.file_list.atualizar_lista_arquivos()
                else:
                    self.folder_entry.delete(0, tk.END)
                    messagebox.showwarning(
                        "Pasta Não Encontrada", 
                        f"A pasta inicial configurada '{initial_folder}' não foi encontrada."
                    )
                    config.pop("folder")
                    self.config_manager.save_config(config)
            except Exception as e:
                messagebox.showerror(
                    "Erro ao Carregar Pasta Inicial", 
                    f"Erro inesperado ao processar '{config.get('folder')}': {e}"
                )

    def selecionar_pasta(self):
        """Abre diálogo para selecionar pasta com scripts."""
        folder = filedialog.askdirectory(title="Selecionar Pasta com Scripts SQL")
        if folder:
            self.folder_entry.delete(0, tk.END)
            self.folder_entry.insert(0, folder)
            try:
                files = sorted([
                    os.path.join(folder, f) 
                    for f in os.listdir(folder) 
                    if f.lower().endswith('.sql')
                ])
                self.file_list.loaded_scripts = files
                self.file_list.atualizar_lista_arquivos()
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao listar arquivos da pasta '{folder}': {e}")
                self.file_list.loaded_scripts = []
                self.file_list.atualizar_lista_arquivos()

    def executar_scripts(self):
        """Executa os scripts SQL selecionados em uma thread separada."""
        # Verifica se já há uma operação em andamento
        if self.operation_in_progress:
            messagebox.showinfo("Operação em Andamento", "Aguarde a conclusão da operação atual.")
            return
            
        # Valida campos
        if not Validators.validate_connection_fields(
            self.folder_entry.get(),
            self.user_entry.get(),
            self.password_entry.get(),
            self.host_entry.get(),
            self.port_entry.get(),
            self.service_entry.get()
        ):
            return

        scripts = self.file_list.get_scripts()
        if not Validators.validate_scripts_list(scripts):
            return

        # Salva configuração atual
        config_data = {
            "folder": self.folder_entry.get(),
            "user": self.user_entry.get(),
            "password": self.password_entry.get(),
            "host": self.host_entry.get(),
            "port": self.port_entry.get(),
            "service": self.service_entry.get()
        }
        self.config_manager.update_config(config_data)
        
        # Define a operação como em andamento
        self.operation_in_progress = True
        
        # Desabilita os botões durante a execução
        self._toggle_buttons_state(tk.DISABLED)
        
        # Mostra indicador de progresso
        self.output_panel.clear()
        self.output_panel.append_text("Iniciando a execução dos scripts...\n")
        
        # Executa em uma thread separada
        thread = threading.Thread(target=self._run_scripts_thread, args=(scripts, config_data))
        thread.daemon = True
        thread.start()

    def _run_scripts_thread(self, scripts, config):
        """Executa os scripts em uma thread separada."""
        try:
            self._run_scripts(scripts, config)
        finally:
            # Garante que a UI seja atualizada no thread principal
            self.root.after(0, self._finish_execution)
    
    def _finish_execution(self):
        """Finaliza a execução e restaura o estado da interface."""
        self.operation_in_progress = False
        self._toggle_buttons_state(tk.NORMAL)
    
    def _toggle_buttons_state(self, state):
        """Altera o estado dos botões da interface."""
        # Busca todos os botões na aplicação e muda o estado
        for widget in self.root.winfo_children():
            self._set_widget_state(widget, state)
    
    def _set_widget_state(self, widget, state):
        """Altera o estado de um widget e seus filhos recursivamente."""
        if widget.winfo_children():
            for child in widget.winfo_children():
                self._set_widget_state(child, state)
        
        if isinstance(widget, ttk.Button) or isinstance(widget, tk.Button):
            # Não desabilita o botão de "Sair"
            if widget.cget("text") != "Sair":
                widget.configure(state=state)

    def _show_error_dialog(self, file_name, error_message):
        """Mostra um diálogo de erro com opções para continuar ou parar a execução."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Erro na Execução do Script")
        dialog.geometry("600x350")
        dialog.transient(self.root)
        dialog.grab_set()  # Torna o diálogo modal
        
        # Adiciona um ícone de erro
        error_frame = ttk.Frame(dialog, padding=(20, 20, 20, 10))
        error_frame.pack(fill=tk.BOTH, expand=True)
        
        # Mensagem de erro
        ttk.Label(
            error_frame, 
            text=f"Erro ao executar o script '{file_name}':", 
            font=("Segoe UI", 11, "bold")
        ).pack(anchor=tk.W, pady=(0, 10))
        
        # Área de texto para mostrar o erro
        error_text = scrolledtext.ScrolledText(
            error_frame, 
            width=70, 
            height=12, 
            wrap=tk.WORD,
            font=("Consolas", 10)
        )
        error_text.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        error_text.insert(tk.END, error_message)
        error_text.configure(state=tk.DISABLED)
        
        # Mensagem de pergunta
        ttk.Label(
            error_frame, 
            text="O que você deseja fazer?", 
            font=("Segoe UI", 10)
        ).pack(anchor=tk.W, pady=(0, 10))
        
        # Variável para armazenar a escolha do usuário
        result = tk.IntVar(value=PARAR)
        
        # Frame para os botões
        buttons_frame = ttk.Frame(error_frame)
        buttons_frame.pack(fill=tk.X, pady=10)
        
        # Botões de ação
        ignore_btn = ttk.Button(
            buttons_frame, 
            text="Ignorar e Continuar", 
            command=lambda: self._close_dialog(dialog, IGNORAR, result)
        )
        ignore_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        ignore_all_btn = ttk.Button(
            buttons_frame, 
            text="Ignorar Todos", 
            command=lambda: self._close_dialog(dialog, IGNORAR_TODOS, result)
        )
        ignore_all_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        stop_btn = ttk.Button(
            buttons_frame, 
            text="Parar Execução", 
            command=lambda: self._close_dialog(dialog, PARAR, result)
        )
        stop_btn.pack(side=tk.LEFT)
        
        # Centraliza o diálogo em relação à janela principal
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = self.root.winfo_x() + (self.root.winfo_width() - width) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - height) // 2
        dialog.geometry(f"{width}x{height}+{x}+{y}")
        
        # Espera até que o diálogo seja fechado
        self.root.wait_window(dialog)
        return result.get()
    
    def _close_dialog(self, dialog, choice, result_var):
        """Fecha o diálogo e define o resultado."""
        result_var.set(choice)
        dialog.destroy()

    def _run_scripts(self, scripts, config):
        """Executa a lista de scripts SQL."""
        success, error = self.oracle_connector.connect(
            config["user"],
            config["password"],
            config["host"],
            config["port"],
            config["service"]
        )
        
        if not success:
            # Mostra o erro na thread principal
            self.root.after(0, lambda: messagebox.showerror("Erro de Conexão", error))
            return

        # Limpa e inicializa o painel de saída na thread principal
        self.root.after(0, lambda: self._init_output_panel(len(scripts)))

        # Flag para controlar se deve mostrar diálogos de erro
        ignore_all_errors = False
        
        # Contador de scripts executados com sucesso
        success_count = 0
        error_count = 0

        for file_path in scripts:
            file_name = os.path.basename(file_path)
            try:
                with open(file_path, encoding='utf-8') as f:
                    sql = f.read()
                
                # Executa o script e obtém o resultado
                success, error = self.oracle_connector.execute_script(sql)
                
                if success:
                    # Atualiza o UI na thread principal
                    self.root.after(0, lambda fn=file_name: self._append_success(fn))
                    success_count += 1
                else:
                    error_count += 1
                    # Exibe o erro no painel de saída na thread principal
                    self.root.after(0, lambda fn=file_name, err=error: self._append_error(fn, err))
                    
                    # Se não estiver ignorando todos os erros, mostra o diálogo
                    if not ignore_all_errors:
                        # Como não podemos bloquear uma thread secundária com um diálogo,
                        # precisamos voltar para a thread principal, mostrar o diálogo e esperar
                        choice_var = threading.Event()
                        choice_result = [PARAR]  # Valor padrão
                        
                        # Função que será executada na thread principal para mostrar o diálogo
                        def show_dialog_in_main_thread():
                            result = self._show_error_dialog(file_name, error)
                            choice_result[0] = result
                            choice_var.set()
                            
                        # Agenda a execução na thread principal e espera
                        self.root.after(0, show_dialog_in_main_thread)
                        choice_var.wait()
                        
                        choice = choice_result[0]
                        
                        if choice == IGNORAR:
                            # Continua com o próximo script
                            continue
                        elif choice == IGNORAR_TODOS:
                            # Continua sem mostrar mais diálogos
                            ignore_all_errors = True
                        elif choice == PARAR:
                            # Para a execução
                            break
            except Exception as e:
                error_count += 1
                # Exibe o erro no painel de saída na thread principal
                self.root.after(0, lambda fn=file_name, err=str(e): self._append_general_error(fn, err))
                
                # Se não estiver ignorando todos os erros, mostra o diálogo
                if not ignore_all_errors:
                    # Como não podemos bloquear uma thread secundária com um diálogo,
                    # precisamos voltar para a thread principal, mostrar o diálogo e esperar
                    choice_var = threading.Event()
                    choice_result = [PARAR]  # Valor padrão
                    
                    # Função que será executada na thread principal para mostrar o diálogo
                    def show_dialog_in_main_thread():
                        result = self._show_error_dialog(file_name, str(e))
                        choice_result[0] = result
                        choice_var.set()
                        
                    # Agenda a execução na thread principal e espera
                    self.root.after(0, show_dialog_in_main_thread)
                    choice_var.wait()
                    
                    choice = choice_result[0]
                    
                    if choice == IGNORAR:
                        # Continua com o próximo script
                        continue
                    elif choice == IGNORAR_TODOS:
                        # Continua sem mostrar mais diálogos
                        ignore_all_errors = True
                    elif choice == PARAR:
                        # Para a execução
                        break

        self.oracle_connector.close()
        
        # Atualiza o resumo na thread principal
        self.root.after(0, lambda sc=success_count, ec=error_count: self._show_execution_summary(sc, ec))
    
    def _init_output_panel(self, script_count):
        """Inicializa o painel de saída."""
        self.output_panel.clear()
        self.output_panel.append_text(f"Iniciando execução de {script_count} script(s)...\n\n")

    def _append_success(self, file_name):
        """Adiciona uma mensagem de sucesso ao painel de saída."""
        self.output_panel.append_success(f"[OK] {file_name}\n")
    
    def _append_error(self, file_name, error):
        """Adiciona uma mensagem de erro ao painel de saída."""
        self.output_panel.append_sql_error(file_name, error)
    
    def _append_general_error(self, file_name, error):
        """Adiciona uma mensagem de erro geral ao painel de saída."""
        self.output_panel.append_error(f"[ERRO] {file_name}: {error}\n")
    
    def _show_execution_summary(self, success_count, error_count):
        """Mostra o resumo da execução."""
        self.output_panel.append_text(f"\n{'=' * 50}\n")
        self.output_panel.append_text(f"Execução finalizada. Resumo:\n")
        self.output_panel.append_success(f"✓ Scripts executados com sucesso: {success_count}\n")
        if error_count > 0:
            self.output_panel.append_error(f"✗ Scripts com erros: {error_count}\n")
        
        if error_count == 0:
            messagebox.showinfo("Sucesso", "Todos os scripts foram executados com sucesso!")
        else:
            messagebox.showinfo("Concluído", f"Execução concluída com {error_count} erro(s).")

    def validar_conexao(self):
        """Valida a conexão com o banco de dados em uma thread separada."""
        # Verifica se já há uma operação em andamento
        if self.operation_in_progress:
            messagebox.showinfo("Operação em Andamento", "Aguarde a conclusão da operação atual.")
            return
            
        # Valida campos
        if not Validators.validate_connection_fields(
            self.folder_entry.get(),
            self.user_entry.get(),
            self.password_entry.get(),
            self.host_entry.get(),
            self.port_entry.get(),
            self.service_entry.get()
        ):
            return
        
        # Define a operação como em andamento
        self.operation_in_progress = True
        
        # Desabilita os botões durante a execução
        self._toggle_buttons_state(tk.DISABLED)
        
        # Executa em uma thread separada
        thread = threading.Thread(target=self._validate_connection_thread)
        thread.daemon = True
        thread.start()
    
    def _validate_connection_thread(self):
        """Executa a validação de conexão em uma thread separada."""
        try:
            # Tenta conectar
            success, error = self.oracle_connector.connect(
                self.user_entry.get(),
                self.password_entry.get(),
                self.host_entry.get(),
                self.port_entry.get(),
                self.service_entry.get()
            )
            
            # Armazena o resultado para mostrar após retornar ao thread principal
            self._connection_result = (success, error)
            
            # Se conectou com sucesso, fecha a conexão
            if success:
                self.oracle_connector.close()
                
            # Atualiza a UI no thread principal
            self.root.after(0, self._show_connection_result)
        except Exception as e:
            # Em caso de erro inesperado, atualiza a UI no thread principal
            self._connection_result = (False, f"Erro inesperado: {str(e)}")
            self.root.after(0, self._show_connection_result)
    
    def _show_connection_result(self):
        """Mostra o resultado da conexão e restaura a interface."""
        success, error = self._connection_result
        
        if success:
            messagebox.showinfo("Sucesso", "Conexão com o banco de dados estabelecida com sucesso!")
        else:
            messagebox.showerror("Erro de Conexão", error)
        
        # Finaliza a operação
        self.operation_in_progress = False
        self._toggle_buttons_state(tk.NORMAL)

    def run(self):
        """Inicia a aplicação."""
        self.root.mainloop() 