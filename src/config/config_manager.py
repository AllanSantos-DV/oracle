import os
import json
from tkinter import messagebox

class ConfigManager:
    def __init__(self, config_file="config.json"):
        self.config_file = config_file
        self.config = self._load_config()

    def _load_config(self):
        """Carrega as configurações do arquivo JSON."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                messagebox.showerror("Erro de Configuração", f"Erro ao ler o arquivo {self.config_file}. Verifique o formato JSON.")
                return {}
            except Exception as e:
                messagebox.showerror("Erro de Configuração", f"Erro inesperado ao carregar {self.config_file}: {e}")
                return {}
        return {}

    def save_config(self, data):
        """Salva as configurações no arquivo JSON."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            messagebox.showerror("Erro de Configuração", f"Erro ao salvar configurações em {self.config_file}: {e}")

    def get_config(self):
        """Retorna as configurações atuais."""
        return self.config

    def update_config(self, new_config):
        """Atualiza as configurações e salva no arquivo."""
        self.config.update(new_config)
        self.save_config(self.config) 