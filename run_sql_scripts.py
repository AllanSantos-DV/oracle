import os
import json
import cx_Oracle
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext
from tkinter import messagebox
from tkinter.font import Font

# --- Oracle Client Initialization ---
# Essencial para o cx_Oracle encontrar as bibliotecas do Oracle Instant Client.
# Define o diretório onde as DLLs/SOs estão localizadas.
try:
    instant_client_dir = os.path.abspath("./instantclient/instantclient_23_7")
    # Tenta inicializar o cliente Oracle
    cx_Oracle.init_oracle_client(lib_dir=instant_client_dir)
except Exception as e:
    messagebox.showerror("Erro Crítico - Oracle Client", 
                       f"Não foi possível inicializar o Oracle Instant Client.\n"
                       f"Verifique se a pasta '{instant_client_dir}' existe e contém os arquivos necessários.\n\n"
                       f"Erro: {e}")
    # Se não conseguir inicializar, encerra a aplicação para evitar erros posteriores.
    exit()
# ----------------------------------

# Nome do arquivo para salvar/carregar configurações da conexão.
CONFIG_FILE = "config.json"
# Lista global para armazenar os caminhos completos dos scripts SQL carregados na interface.
loaded_scripts = [] 

def carregar_config():
    """Carrega as configurações de conexão do arquivo JSON."""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            messagebox.showerror("Erro de Configuração", f"Erro ao ler o arquivo {CONFIG_FILE}. Verifique o formato JSON.")
            return {}
        except Exception as e:
             messagebox.showerror("Erro de Configuração", f"Erro inesperado ao carregar {CONFIG_FILE}: {e}")
             return {}
    return {}

def salvar_config(data):
    """Salva as configurações de conexão no arquivo JSON.

    Args:
        data (dict): Dicionário contendo os dados de configuração.
    """
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(data, f, indent=4) # Adiciona indentação para legibilidade
    except Exception as e:
        messagebox.showerror("Erro de Configuração", f"Erro ao salvar configurações em {CONFIG_FILE}: {e}")

def validar_campos():
    """Verifica se todos os campos de configuração e a lista de scripts estão preenchidos."""
    campos = {
        "Pasta com scripts": folder_entry.get(), # Usado apenas para salvar, não para execução direta
        "Usuário": user_entry.get(),
        "Senha": password_entry.get(),
        "Host": host_entry.get(),
        "Porta": port_entry.get(),
        "Service Name": service_entry.get()
    }
    
    campos_vazios = [campo for campo, valor in campos.items() if not valor]
    if campos_vazios:
        messagebox.showerror("Erro de Validação", 
                           "Os seguintes campos de conexão são obrigatórios:\n" + 
                           "\n".join(f"- {campo}" for campo in campos_vazios))
        return False
        
    # Verifica se há scripts carregados na lista da interface
    if not loaded_scripts:
         messagebox.showerror("Erro de Validação", "Nenhum script SQL foi carregado para execução.")
         return False
         
    return True

def run_sql_scripts(scripts_para_executar, user, password, host, port, service):
    """Conecta ao banco Oracle e executa a lista de scripts fornecida.

    Args:
        scripts_para_executar (list): Lista de caminhos completos dos arquivos SQL.
        user (str): Usuário do banco de dados.
        password (str): Senha do banco de dados.
        host (str): Host do banco de dados.
        port (str): Porta do banco de dados.
        service (str): Nome do serviço Oracle.
    """
    try:
        dsn = cx_Oracle.makedsn(host, port, service_name=service)
        # Estabelece a conexão com o banco de dados
        connection = cx_Oracle.connect(user=user, password=password, dsn=dsn)
        cursor = connection.cursor()

        # Limpa a área de saída antes de iniciar
        output_text.delete(1.0, tk.END)
        output_text.insert(tk.END, f"Iniciando execução de {len(scripts_para_executar)} script(s)...\n\n")

        # Itera sobre a lista de scripts carregados na interface
        for file_path in scripts_para_executar:
            file_name = os.path.basename(file_path)
            try:
                # Lê o conteúdo do arquivo SQL
                with open(file_path, encoding='utf-8') as f:
                    sql = f.read()
                # Executa o SQL
                cursor.execute(sql)
                # Comita a transação após cada script (pode ser ajustado se necessário)
                connection.commit()
                # Exibe mensagem de sucesso na área de saída
                output_text.insert(tk.END, f"[OK] {file_name}\n", "success")
            except Exception as e:
                # Exibe mensagem de erro na área de saída
                output_text.insert(tk.END, f"[ERRO] {file_name}: {e}\n", "error")
                # Opcional: Poderia adicionar uma opção para parar a execução em caso de erro.

        # Fecha cursor e conexão
        cursor.close()
        connection.close()
        messagebox.showinfo("Sucesso", "Execução concluída!")
        
    except cx_Oracle.DatabaseError as e:
        # Trata erros específicos de conexão com o Oracle
        error, = e.args
        messagebox.showerror("Erro de Conexão", 
                           f"Erro ao conectar ao banco de dados:\n"
                           f"Código: {error.code}\n"
                           f"Mensagem: {error.message}")
    except Exception as e:
        # Trata outros erros inesperados durante a execução
        messagebox.showerror("Erro", f"Erro inesperado durante a execução: {e}")

def executar_scripts():
    """Função chamada pelo botão 'Executar Scripts'. Valida os campos e inicia a execução."""
    if not validar_campos():
        return # Para se a validação falhar
    
    # Coleta dados de configuração dos campos da interface
    config_data = {
        "folder": folder_entry.get(), # Salva a última pasta selecionada
        "user": user_entry.get(),
        "password": password_entry.get(),
        "host": host_entry.get(),
        "port": port_entry.get(),
        "service": service_entry.get()
    }
    
    # Salva a configuração atual para uso futuro
    salvar_config(config_data)
    
    # Chama a função principal de execução, passando a lista atual de scripts
    run_sql_scripts(
        loaded_scripts, 
        config_data["user"],
        config_data["password"],
        config_data["host"],
        config_data["port"],
        config_data["service"]
    )

def selecionar_pasta():
    """Abre um diálogo para selecionar uma pasta e carrega os scripts .sql dela.
       Substitui a lista de scripts atual pelos arquivos da pasta selecionada.
    """
    global loaded_scripts
    folder = filedialog.askdirectory(title="Selecionar Pasta com Scripts SQL")
    if folder:
        # Atualiza o campo de entrada com a pasta selecionada
        folder_entry.delete(0, tk.END)
        folder_entry.insert(0, folder)
        try:
            # Lista e ordena os arquivos .sql na pasta selecionada
            files = sorted([os.path.join(folder, f) for f in os.listdir(folder) if f.lower().endswith('.sql')])
            # Atualiza a lista global de scripts
            loaded_scripts = files
            # Atualiza a exibição na Treeview
            atualizar_lista_arquivos()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao listar arquivos da pasta '{folder}': {e}")
            # Limpa a lista se ocorrer um erro
            loaded_scripts = []
            atualizar_lista_arquivos()

def atualizar_lista_arquivos():
    """Atualiza a Treeview (lista de scripts) com base na lista global 'loaded_scripts'."""
    # Limpa todos os itens existentes na Treeview
    for item in arquivos_tree.get_children():
        arquivos_tree.delete(item)
    
    # Preenche a Treeview com os scripts da lista global
    for i, file_path in enumerate(loaded_scripts, 1):
        file_name = os.path.basename(file_path)
        # Insere o item usando o caminho completo como ID único (iid)
        arquivos_tree.insert("", "end", iid=file_path, values=(i, file_name))
        
    # Atualiza o label do contador de scripts
    contador_label.config(text=f"Total: {len(loaded_scripts)} script(s)")
    # Habilita/desabilita botões de reordenação com base na seleção atual
    update_reorder_buttons_state()

def adicionar_scripts():
    """Abre um diálogo para adicionar mais arquivos .sql à lista existente."""
    global loaded_scripts
    # Permite selecionar múltiplos arquivos
    files_to_add = filedialog.askopenfilenames(title="Selecionar Scripts SQL para Adicionar", 
                                             filetypes=(("SQL files", "*.sql"), ("All files", "*.*")))
    if files_to_add:
        added_count = 0
        for file_path in files_to_add:
            # Adiciona apenas se o script ainda não estiver na lista
            if file_path not in loaded_scripts:
                loaded_scripts.append(file_path)
                added_count += 1
        # Atualiza a Treeview se algum script foi adicionado
        if added_count > 0:
            atualizar_lista_arquivos()
        else:
             messagebox.showinfo("Nenhum Script Adicionado", "Os scripts selecionados já estavam na lista.")

def remover_scripts():
    """Remove os scripts selecionados na Treeview da lista 'loaded_scripts'."""
    global loaded_scripts
    # Obtém os IDs (caminhos dos arquivos) dos itens selecionados na Treeview
    selected_items_ids = arquivos_tree.selection()
    if not selected_items_ids:
        messagebox.showwarning("Seleção Vazia", "Selecione um ou mais scripts para remover.")
        return

    # Cria uma nova lista contendo apenas os scripts que NÃO foram selecionados
    loaded_scripts = [script for script in loaded_scripts if script not in selected_items_ids]
    # Atualiza a Treeview
    atualizar_lista_arquivos()

def mover_script(direcao):
    """Move o script selecionado (um único) para cima ou para baixo na lista.

    Args:
        direcao (str): "cima" ou "baixo".
    """
    global loaded_scripts
    selected_items = arquivos_tree.selection()
    # Verifica se exatamente um item está selecionado
    if not selected_items or len(selected_items) > 1:
        messagebox.showwarning("Seleção Inválida", "Selecione um único script para mover.")
        return

    selected_id = selected_items[0] # ID é o caminho do arquivo
    try:
        # Encontra o índice do item selecionado na lista global
        index = loaded_scripts.index(selected_id)
    except ValueError:
        # Caso raro onde o item da treeview não está na lista (deve ser evitado)
        messagebox.showerror("Erro Interno", "Script selecionado não encontrado na lista interna.")
        return 

    new_index = -1
    # Lógica para mover para cima
    if direcao == "cima" and index > 0:
        loaded_scripts[index], loaded_scripts[index - 1] = loaded_scripts[index - 1], loaded_scripts[index]
        new_index = index - 1
    # Lógica para mover para baixo
    elif direcao == "baixo" and index < len(loaded_scripts) - 1:
        loaded_scripts[index], loaded_scripts[index + 1] = loaded_scripts[index + 1], loaded_scripts[index]
        new_index = index + 1
    else:
        # Não pode mover (já é o primeiro ou o último)
        return

    # Atualiza a Treeview com a nova ordem
    atualizar_lista_arquivos()
    
    # Mantém o item movido selecionado e visível na Treeview
    if new_index != -1:
        arquivos_tree.selection_set(selected_id)
        arquivos_tree.focus(selected_id)
        arquivos_tree.see(selected_id)

def update_reorder_buttons_state(*args):
    """Habilita ou desabilita os botões 'Mover Acima' e 'Mover Abaixo' 
       com base na seleção atual da Treeview.
    """
    selected_items = arquivos_tree.selection()
    can_move_up = False
    can_move_down = False

    # Só habilita se exatamente um item estiver selecionado
    if len(selected_items) == 1:
        selected_id = selected_items[0]
        try:
            index = loaded_scripts.index(selected_id)
            # Pode mover para cima se não for o primeiro item
            if index > 0:
                can_move_up = True
            # Pode mover para baixo se não for o último item
            if index < len(loaded_scripts) - 1:
                can_move_down = True
        except ValueError:
            pass # Item selecionado não está (mais) na lista

    # Atualiza o estado dos botões
    move_up_btn.config(state=tk.NORMAL if can_move_up else tk.DISABLED)
    move_down_btn.config(state=tk.NORMAL if can_move_down else tk.DISABLED)

# --- Inicialização da Aplicação ---

# Carrega as configurações salvas
config = carregar_config()

# Cria a janela principal
root = tk.Tk()
root.title("Executor de Scripts SQL Oracle v1.1")
root.geometry("1200x800") # Define o tamanho inicial da janela

# --- Configuração de Estilos (Aparência) ---
style = ttk.Style()
style.theme_use('clam') # Define um tema visual mais moderno
# Configurações de fonte, padding e background para diferentes widgets
style.configure("TFrame", background="#ececec")
style.configure("TLabel", background="#ececec", font=("Segoe UI", 10))
style.configure("TButton", font=("Segoe UI", 10), padding=5)
style.configure("TEntry", font=("Segoe UI", 10), padding=5)
style.configure("Treeview", font=("Segoe UI", 10), rowheight=25) # Altura das linhas na lista
style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold")) # Cabeçalho da lista em negrito
style.configure("TLabelframe", background="#ececec", padding=10)
style.configure("TLabelframe.Label", background="#ececec", font=("Segoe UI", 11, "bold"))

# Configura a fonte para a área de texto de saída
output_font = Font(family="Consolas", size=10) # Fonte monoespaçada para melhor visualização de logs
# Nomes das tags para colorir a saída
success_tag = "success"
error_tag = "error"

# --- Estrutura da Interface Gráfica (Layout com PanedWindow) ---

# Cria um divisor principal vertical (divide a janela em cima/baixo)
main_paned_window = ttk.PanedWindow(root, orient=tk.VERTICAL)
main_paned_window.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# --- Painel Superior: Configuração e Botões Principais ---
top_frame = ttk.Frame(main_paned_window, padding=10)
main_paned_window.add(top_frame, weight=0) # Define que este painel não cresce verticalmente

# Frame para os campos de configuração da conexão
config_frame = ttk.LabelFrame(top_frame, text="Configuração de Conexão")
config_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))

# Widgets de entrada para os dados de conexão (Labels, Entries, Button)
ttk.Label(config_frame, text="Pasta Inicial:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=3)
folder_entry = ttk.Entry(config_frame, width=50)
folder_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5, pady=3)
folder_entry.insert(0, config.get("folder", "")) # Preenche com valor salvo
ttk.Button(config_frame, text="Procurar Pasta", command=selecionar_pasta).grid(row=0, column=2, padx=5, pady=3)

ttk.Label(config_frame, text="Usuário:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=3)
user_entry = ttk.Entry(config_frame)
user_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=5, pady=3)
user_entry.insert(0, config.get("user", ""))

ttk.Label(config_frame, text="Senha:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=3)
password_entry = ttk.Entry(config_frame, show="*") # Esconde a senha
password_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=5, pady=3)
password_entry.insert(0, config.get("password", ""))

ttk.Label(config_frame, text="Host:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=3)
host_entry = ttk.Entry(config_frame)
host_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), padx=5, pady=3)
host_entry.insert(0, config.get("host", "localhost"))

ttk.Label(config_frame, text="Porta:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=3)
port_entry = ttk.Entry(config_frame)
port_entry.grid(row=4, column=1, sticky=(tk.W, tk.E), padx=5, pady=3)
port_entry.insert(0, config.get("port", "1521"))

ttk.Label(config_frame, text="Service Name:").grid(row=5, column=0, sticky=tk.W, padx=5, pady=3)
service_entry = ttk.Entry(config_frame)
service_entry.grid(row=5, column=1, sticky=(tk.W, tk.E), padx=5, pady=3)
service_entry.insert(0, config.get("service", "XE"))

# Configura a coluna dos campos de entrada para expandir horizontalmente
config_frame.columnconfigure(1, weight=1)

# Frame para os botões principais (Executar, Sair)
main_button_frame = ttk.Frame(top_frame)
main_button_frame.grid(row=0, column=1, sticky=(tk.N, tk.S, tk.E, tk.W), padx=(10, 0))
executar_btn = ttk.Button(main_button_frame, text="Executar Scripts", command=executar_scripts)
executar_btn.pack(pady=5, fill=tk.X)
sair_btn = ttk.Button(main_button_frame, text="Sair", command=root.destroy)
sair_btn.pack(pady=5, fill=tk.X)

# Configura o frame de configuração para expandir horizontalmente dentro do painel superior
top_frame.columnconfigure(0, weight=1)

# --- Painel Inferior: Lista de Scripts e Saída ---
# Cria um divisor horizontal (divide a área inferior em esquerda/direita)
bottom_paned_window = ttk.PanedWindow(main_paned_window, orient=tk.HORIZONTAL)
main_paned_window.add(bottom_paned_window, weight=1) # Define que este painel cresce verticalmente

# --- Painel Esquerdo: Gerenciamento de Scripts ---
files_panel = ttk.Frame(bottom_paned_window, padding=5)
bottom_paned_window.add(files_panel, weight=1) # Define que este painel cresce horizontalmente

# Frame com título para a lista de scripts
files_frame = ttk.LabelFrame(files_panel, text="Scripts SQL para Execução")
files_frame.pack(fill=tk.BOTH, expand=True)

# Frame interno para a Treeview e sua Scrollbar
tree_frame = ttk.Frame(files_frame)
tree_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))

# Treeview para exibir a lista de scripts
columns = ("#", "Nome do Arquivo")
# selectmode='extended' permite selecionar múltiplos itens
arquivos_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", selectmode='extended')
arquivos_tree.heading("#", text="#") # Cabeçalho da coluna de número
arquivos_tree.heading("Nome do Arquivo", text="Nome do Arquivo") # Cabeçalho da coluna de nome
arquivos_tree.column("#", width=40, anchor="center", stretch=tk.NO) # Coluna de número fixa
arquivos_tree.column("Nome do Arquivo", width=400) # Coluna de nome com largura inicial
arquivos_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

# Scrollbar vertical para a Treeview
scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=arquivos_tree.yview)
arquivos_tree.configure(yscrollcommand=scrollbar.set)
scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

# Configura a Treeview e a Scrollbar para expandirem dentro do tree_frame
tree_frame.rowconfigure(0, weight=1)
tree_frame.columnconfigure(0, weight=1)

# Frame para os botões de gerenciamento da lista (Adicionar, Remover, Mover)
manage_buttons_frame = ttk.Frame(files_frame)
manage_buttons_frame.pack(fill=tk.X, pady=5)

add_btn = ttk.Button(manage_buttons_frame, text="Adicionar", command=adicionar_scripts)
add_btn.pack(side=tk.LEFT, padx=3)
remove_btn = ttk.Button(manage_buttons_frame, text="Remover", command=remover_scripts)
remove_btn.pack(side=tk.LEFT, padx=3)
move_up_btn = ttk.Button(manage_buttons_frame, text="Mover Acima", command=lambda: mover_script("cima"), state=tk.DISABLED) # Inicia desabilitado
move_up_btn.pack(side=tk.LEFT, padx=3)
move_down_btn = ttk.Button(manage_buttons_frame, text="Mover Abaixo", command=lambda: mover_script("baixo"), state=tk.DISABLED) # Inicia desabilitado
move_down_btn.pack(side=tk.LEFT, padx=3)

# Label para mostrar o número total de scripts carregados
contador_label = ttk.Label(files_frame, text="Total: 0 script(s)", font=("Segoe UI", 9, "italic"))
contador_label.pack(anchor=tk.W, pady=(5,0))

# --- Painel Direito: Saída da Execução ---
output_panel = ttk.Frame(bottom_paned_window, padding=5)
bottom_paned_window.add(output_panel, weight=1) # Define que este painel cresce horizontalmente

# Frame com título para a área de saída
output_frame = ttk.LabelFrame(output_panel, text="Saída da Execução")
output_frame.pack(fill=tk.BOTH, expand=True)

# Área de texto rolável para exibir logs/resultados
# wrap=tk.WORD quebra linhas longas entre palavras
output_text = scrolledtext.ScrolledText(output_frame, width=60, height=20, font=output_font, wrap=tk.WORD)
output_text.pack(fill=tk.BOTH, expand=True)

# Define as cores para as tags de sucesso e erro na área de saída
output_text.tag_configure(success_tag, foreground="#008000") # Verde escuro
output_text.tag_configure(error_tag, foreground="#cc0000")   # Vermelho escuro

# --- Associações de Eventos e Inicialização Final ---

# Associa o evento de seleção na Treeview à função que atualiza os botões de mover
arquivos_tree.bind('<<TreeviewSelect>>', update_reorder_buttons_state)

# Bloco para carregar os scripts da pasta inicial (se configurada) ao iniciar
if config.get("folder"):
    try:
        initial_folder = config["folder"]
        # Verifica se a pasta realmente existe
        if os.path.isdir(initial_folder):
            initial_files = sorted([os.path.join(initial_folder, f) for f in os.listdir(initial_folder) if f.lower().endswith('.sql')])
            loaded_scripts = initial_files # Define a lista global
            atualizar_lista_arquivos() # Atualiza a Treeview
        else:
             # Se a pasta salva não existe mais, limpa o campo e avisa
             folder_entry.delete(0, tk.END)
             messagebox.showwarning("Pasta Não Encontrada", f"A pasta inicial configurada '{initial_folder}' não foi encontrada.")
             config.pop("folder") # Remove a configuração inválida
             salvar_config(config) # Salva sem a pasta

    except Exception as e:
        # Trata outros erros que podem ocorrer ao listar a pasta inicial
        messagebox.showerror("Erro ao Carregar Pasta Inicial", f"Erro inesperado ao processar '{config.get('folder')}': {e}")

# Inicia o loop principal da interface gráfica Tkinter
root.mainloop()
