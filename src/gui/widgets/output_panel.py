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

        # Configura a fonte para a área de texto
        output_font = Font(family="Consolas", size=10)
        
        # Área de texto rolável
        self.output_text = scrolledtext.ScrolledText(
            self.output_frame, 
            width=60, 
            height=20, 
            font=output_font, 
            wrap=tk.WORD
        )
        self.output_text.pack(fill=tk.BOTH, expand=True)

        # Configura as tags para colorir a saída
        self.output_text.tag_configure("success", foreground="#008000")  # Verde escuro
        self.output_text.tag_configure("error", foreground="#cc0000")    # Vermelho escuro

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

    def append_text(self, text):
        """Adiciona texto normal à área de saída."""
        self.output_text.insert(tk.END, text)
        self.output_text.see(tk.END) 