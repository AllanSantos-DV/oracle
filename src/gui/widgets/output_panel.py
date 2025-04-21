import tkinter as tk
from tkinter import ttk, scrolledtext
from tkinter.font import Font

class OutputPanel:
    def __init__(self, parent):
        self.parent = parent
        self._setup_widgets()

    def _setup_widgets(self):
        """Configura os widgets do painel de saída."""
        self.output_frame = ttk.LabelFrame(self.parent, text="Saída da Execução")
        self.output_frame.pack(fill=tk.BOTH, expand=True)

        # Configura a fonte para a área de texto - reduzida
        output_font = Font(family="Consolas", size=9)
        
        # Área de texto rolável
        self.output_text = scrolledtext.ScrolledText(
            self.output_frame, 
            width=50,  # Redução do tamanho
            height=18,  # Redução do tamanho
            font=output_font, 
            wrap=tk.WORD
        )
        self.output_text.pack(fill=tk.BOTH, expand=True)

        # Configura as tags para colorir a saída
        self.output_text.tag_configure("success", foreground="#008000")  # Verde escuro
        self.output_text.tag_configure("error", foreground="#cc0000")    # Vermelho escuro
        self.output_text.tag_configure("code_block", background="#f5f5f5")  # Fundo cinza claro
        self.output_text.tag_configure("separator", foreground="#666666")  # Cinza escuro

    def clear(self):
        """Limpa a área de saída."""
        self.output_text.delete(1.0, tk.END)

    def append_success(self, text):
        """Adiciona texto de sucesso à área de saída."""
        self.output_text.insert(tk.END, text, "success")
        self.output_text.see(tk.END)

    def append_error(self, text):
        """Adiciona texto de erro à área de saída."""
        self.output_text.insert(tk.END, text, "error")
        self.output_text.see(tk.END)

    def append_sql_error(self, file_name, error_message):
        """Adiciona erro SQL formatado com o bloco de código destacado."""
        # Verifica se a mensagem contém "Bloco com erro:"
        if "Bloco com erro:" in error_message:
            # Divide a mensagem em partes
            parts = error_message.split("Bloco com erro:")
            header = parts[0]
            
            # Verifica se há um separador no final
            separator_pos = parts[1].rfind("-" * 50)
            if separator_pos > 0:
                code_block = parts[1][:separator_pos].strip()
                footer = parts[1][separator_pos:].strip()
            else:
                code_block = parts[1].strip()
                footer = ""
            
            # Adiciona o cabeçalho do erro
            self.output_text.insert(tk.END, f"[ERRO] {file_name}:\n", "error")
            self.output_text.insert(tk.END, f"{header.strip()}\n\n")
            
            # Adiciona o bloco de código com formatação especial
            self.output_text.insert(tk.END, "Bloco com erro:\n")
            self.output_text.insert(tk.END, f"{code_block}\n", "code_block")
            
            # Adiciona o separador, se houver
            if footer:
                self.output_text.insert(tk.END, f"{footer}\n", "separator")
        else:
            # Se não contém o formato esperado, adiciona como erro normal
            self.output_text.insert(tk.END, f"[ERRO] {file_name}: {error_message}\n", "error")
            
        self.output_text.see(tk.END)

    def append_text(self, text):
        """Adiciona texto normal à área de saída."""
        self.output_text.insert(tk.END, text)
        self.output_text.see(tk.END) 