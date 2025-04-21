import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from src.gui.widgets.file_list import FileList
from src.gui.widgets.output_panel import OutputPanel
from src.config.config_manager import ConfigManager
from src.database.oracle_connector import OracleConnector
from src.utils.validators import Validators

class MainWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Executor de Scripts SQL Oracle v1.1")
        self.root.geometry("1200x800")
        
        self.config_manager = ConfigManager()
        self.oracle_connector = OracleConnector()
        
        self._setup_styles()
        self._setup_layout()
        self._load_initial_config()

    def _setup_styles(self):
        """Configura os estilos da interface."""
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TFrame", background="#ececec")
        style.configure("TLabel", background="#ececec", font=("Segoe UI", 10))
        style.configure("TButton", font=("Segoe UI", 10), padding=5)
        style.configure("TEntry", font=("Segoe UI", 10), padding=5)
        style.configure("Treeview", font=("Segoe UI", 10), rowheight=25)
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
        style.configure("TLabelframe", background="#ececec", padding=10)
        style.configure("TLabelframe.Label", background="#ececec", font=("Segoe UI", 11, "bold"))

    def _setup_layout(self):
        """Configura o layout da janela principal."""
        # Divisor principal vertical
        main_paned_window = ttk.PanedWindow(self.root, orient=tk.VERTICAL)
        main_paned_window.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Painel superior
        top_frame = ttk.Frame(main_paned_window, padding=10)
        main_paned_window.add(top_frame, weight=0)

        # Frame de configuração
        config_frame = ttk.LabelFrame(top_frame, text="Configuração de Conexão")
        config_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))

        # Campos de configuração
        self._setup_config_fields(config_frame)

        # Botões principais
        main_button_frame = ttk.Frame(top_frame)
        main_button_frame.grid(row=0, column=1, sticky=(tk.N, tk.S, tk.E, tk.W), padx=(10, 0))
        
        validar_btn = ttk.Button(main_button_frame, text="Validar Conexão", command=self.validar_conexao)
        validar_btn.pack(pady=5, fill=tk.X)
        
        executar_btn = ttk.Button(main_button_frame, text="Executar Scripts", command=self.executar_scripts)
        executar_btn.pack(pady=5, fill=tk.X)
        
        sair_btn = ttk.Button(main_button_frame, text="Sair", command=self.root.destroy)
        sair_btn.pack(pady=5, fill=tk.X)

        # Configura o frame de configuração para expandir
        top_frame.columnconfigure(0, weight=1)

        # Painel inferior
        bottom_paned_window = ttk.PanedWindow(main_paned_window, orient=tk.HORIZONTAL)
        main_paned_window.add(bottom_paned_window, weight=1)

        # Painel esquerdo (lista de arquivos)
        files_panel = ttk.Frame(bottom_paned_window, padding=5)
        bottom_paned_window.add(files_panel, weight=1)
        self.file_list = FileList(files_panel)

        # Painel direito (saída)
        output_panel = ttk.Frame(bottom_paned_window, padding=5)
        bottom_paned_window.add(output_panel, weight=1)
        self.output_panel = OutputPanel(output_panel)

    def _setup_config_fields(self, parent):
        """Configura os campos de configuração."""
        # Pasta inicial
        ttk.Label(parent, text="Pasta Inicial:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=3)
        self.folder_entry = ttk.Entry(parent, width=50)
        self.folder_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5, pady=3)
        ttk.Button(parent, text="Procurar Pasta", command=self.selecionar_pasta).grid(row=0, column=2, padx=5, pady=3)

        # Usuário
        ttk.Label(parent, text="Usuário:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=3)
        self.user_entry = ttk.Entry(parent)
        self.user_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=5, pady=3)

        # Senha
        ttk.Label(parent, text="Senha:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=3)
        self.password_entry = ttk.Entry(parent, show="*")
        self.password_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=5, pady=3)

        # Host
        ttk.Label(parent, text="Host:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=3)
        self.host_entry = ttk.Entry(parent)
        self.host_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), padx=5, pady=3)

        # Porta
        ttk.Label(parent, text="Porta:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=3)
        self.port_entry = ttk.Entry(parent)
        self.port_entry.grid(row=4, column=1, sticky=(tk.W, tk.E), padx=5, pady=3)

        # Service Name
        ttk.Label(parent, text="Service Name:").grid(row=5, column=0, sticky=tk.W, padx=5, pady=3)
        self.service_entry = ttk.Entry(parent)
        self.service_entry.grid(row=5, column=1, sticky=(tk.W, tk.E), padx=5, pady=3)

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
        """Executa os scripts SQL selecionados."""
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

        # Executa scripts
        self._run_scripts(scripts, config_data)

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
            messagebox.showerror("Erro de Conexão", error)
            return

        self.output_panel.clear()
        self.output_panel.append_text(f"Iniciando execução de {len(scripts)} script(s)...\n\n")

        for file_path in scripts:
            file_name = os.path.basename(file_path)
            try:
                with open(file_path, encoding='utf-8') as f:
                    sql = f.read()
                success, error = self.oracle_connector.execute_script(sql)
                if success:
                    self.output_panel.append_success(f"[OK] {file_name}\n")
                else:
                    self.output_panel.append_error(f"[ERRO] {file_name}: {error}\n")
            except Exception as e:
                self.output_panel.append_error(f"[ERRO] {file_name}: {e}\n")

        self.oracle_connector.close()
        messagebox.showinfo("Sucesso", "Execução concluída!")

    def validar_conexao(self):
        """Valida a conexão com o banco de dados."""
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

        # Tenta conectar
        success, error = self.oracle_connector.connect(
            self.user_entry.get(),
            self.password_entry.get(),
            self.host_entry.get(),
            self.port_entry.get(),
            self.service_entry.get()
        )
        
        if success:
            messagebox.showinfo("Sucesso", "Conexão com o banco de dados estabelecida com sucesso!")
            self.oracle_connector.close()
        else:
            messagebox.showerror("Erro de Conexão", error)

    def run(self):
        """Inicia a aplicação."""
        self.root.mainloop() 