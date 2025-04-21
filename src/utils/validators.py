from tkinter import messagebox

class Validators:
    @staticmethod
    def validate_connection_fields(folder, user, password, host, port, service):
        """Valida os campos de conexão."""
        campos = {
            "Pasta com scripts": folder,
            "Usuário": user,
            "Senha": password,
            "Host": host,
            "Porta": port,
            "Service Name": service
        }
        
        campos_vazios = [campo for campo, valor in campos.items() if not valor]
        if campos_vazios:
            messagebox.showerror("Erro de Validação", 
                               "Os seguintes campos de conexão são obrigatórios:\n" + 
                               "\n".join(f"- {campo}" for campo in campos_vazios))
            return False
        return True

    @staticmethod
    def validate_scripts_list(scripts):
        """Valida se há scripts carregados."""
        if not scripts:
            messagebox.showerror("Erro de Validação", "Nenhum script SQL foi carregado para execução.")
            return False
        return True 