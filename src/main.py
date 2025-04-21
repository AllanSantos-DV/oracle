import os
import sys
import cx_Oracle
from tkinter import messagebox

# Adiciona o diretório src ao PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.gui.main_window import MainWindow

def initialize_oracle_client():
    """Inicializa o cliente Oracle."""
    global instant_client_dir
    try:
        # Caminho relativo à raiz do projeto
        instant_client_dir = os.path.abspath(os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "instantclient",
            "instantclient_23_7"
        ))
        cx_Oracle.init_oracle_client(lib_dir=instant_client_dir)
        return True
    except Exception as e:
        messagebox.showerror(
            "Erro Crítico - Oracle Client", 
            f"Não foi possível inicializar o Oracle Instant Client.\n"
            f"Verifique se a pasta '{instant_client_dir}' existe e contém os arquivos necessários.\n\n"
            f"Erro: {e}"
        )
        return False

def main():
    """Função principal da aplicação."""
    if not initialize_oracle_client():
        return

    app = MainWindow()
    app.run()

if __name__ == "__main__":
    main() 