import os
import sys
import cx_Oracle
from tkinter import messagebox

# Adiciona o diretório src ao PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.gui.main_window import MainWindow

def get_application_path():
    """Retorna o caminho base da aplicação, seja em desenvolvimento ou no executável."""
    if getattr(sys, 'frozen', False):
        # Se estiver rodando como executável
        return os.path.dirname(sys.executable)
    # Se estiver rodando em desenvolvimento
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def initialize_oracle_client():
    """Inicializa o cliente Oracle."""
    try:
        base_path = get_application_path()
        
        # O Instant Client deve estar na mesma pasta do executável
        if getattr(sys, 'frozen', False):
            instant_client_dir = os.path.join(base_path, "instantclient_23_7")
        else:
            instant_client_dir = os.path.join(base_path, "instantclient", "instantclient_23_7")
        
        if not os.path.exists(instant_client_dir):
            messagebox.showerror(
                "Erro Crítico - Oracle Client", 
                f"Pasta do Oracle Instant Client não encontrada em:\n{instant_client_dir}\n\n"
                f"Por favor, certifique-se de que a pasta 'instantclient_23_7' está no mesmo diretório do executável."
            )
            return False

        # Adiciona o diretório ao PATH do sistema
        if instant_client_dir not in os.environ['PATH']:
            os.environ['PATH'] = instant_client_dir + os.pathsep + os.environ['PATH']

        cx_Oracle.init_oracle_client(lib_dir=instant_client_dir)
        return True
    except Exception as e:
        messagebox.showerror(
            "Erro Crítico - Oracle Client", 
            f"Não foi possível inicializar o Oracle Instant Client.\n"
            f"Erro: {str(e)}\n\n"
            f"Caminho tentado: {instant_client_dir if 'instant_client_dir' in locals() else 'Nenhum'}"
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