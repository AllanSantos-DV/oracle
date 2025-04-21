import cx_Oracle
from tkinter import messagebox
import re

class OracleConnector:
    def __init__(self):
        self.connection = None
        self.cursor = None

    def connect(self, user, password, host, port, service):
        """Estabelece conexão com o banco de dados Oracle."""
        try:
            dsn = cx_Oracle.makedsn(host, port, service_name=service)
            self.connection = cx_Oracle.connect(user=user, password=password, dsn=dsn)
            self.cursor = self.connection.cursor()
            return True, None
        except cx_Oracle.DatabaseError as e:
            error, = e.args
            error_msg = f"Erro ao conectar ao banco de dados:\nCódigo: {error.code}\nMensagem: {error.message}"
            return False, error_msg
        except Exception as e:
            error_msg = f"Erro inesperado durante a conexão: {e}"
            return False, error_msg

    def execute_script(self, sql):
        """Executa um script SQL com múltiplos blocos/comandos."""
        overall_success = True
        error_messages = []
        
        # Remove comentários e divide o script em blocos
        blocks = self._split_sql_blocks(sql)
        
        for i, block in enumerate(blocks, 1):
            # Ignora blocos vazios
            if not block.strip():
                continue
                
            try:
                # Executa o bloco SQL
                self.cursor.execute(block)
                
                # Commit após cada comando DDL ou DML bem-sucedido
                # (não afeta comandos SELECT)
                self.connection.commit()
            except Exception as e:
                overall_success = False
                
                # Preparando o bloco para exibição (limitado a 500 caracteres para não sobrecarregar a UI)
                block_preview = block
                if len(block_preview) > 500:
                    block_preview = block_preview[:497] + "..."
                
                # Formata a mensagem de erro incluindo o bloco que falhou
                error_message = f"Erro no bloco {i}:\n{str(e)}\n\n"
                error_message += f"Bloco com erro:\n{block_preview}\n"
                error_message += "-" * 50 + "\n"
                
                error_messages.append(error_message)
        
        if overall_success:
            return True, None
        else:
            # Retorna todos os erros encontrados
            return False, "\n".join(error_messages)

    def _remove_comments(self, sql_script):
        """Remove comentários de uma linha (--) e blocos de comentários (/* */) do script SQL."""
        # Primeiro, normaliza as quebras de linha
        script = sql_script.replace('\r\n', '\n').replace('\r', '\n')
        
        # Remove blocos de comentários (/* ... */)
        # Usamos expressão regular não-gulosa (?:.*?) para capturar conteúdo entre /* e */
        block_comments_pattern = re.compile(r'/\*(?:.*?)\*/', re.DOTALL)
        script = block_comments_pattern.sub(' ', script)
        
        # Remove comentários de uma linha (--) até o final da linha
        lines = []
        for line in script.split('\n'):
            # Encontra a posição do comentário de linha
            comment_pos = line.find('--')
            if comment_pos >= 0:
                # Mantém apenas o que está antes do comentário
                line = line[:comment_pos]
            lines.append(line)
        
        return '\n'.join(lines)

    def _split_sql_blocks(self, sql_script):
        """Divide um script SQL em blocos executáveis.
        
        Lida com:
        1. Remove comentários (-- e /* */)
        2. Blocos PL/SQL terminados por '/' em uma linha isolada
        3. Múltiplos comandos SQL separados por ';'
        4. Preserva blocos PL/SQL com ';' internos
        """
        # Primeiro, remove todos os comentários
        script = self._remove_comments(sql_script)
        
        # Divide em blocos delimitados por '/' em uma linha isolada
        # (comum em scripts PL/SQL Oracle)
        slash_pattern = re.compile(r'\n\s*/\s*\n')
        blocks = slash_pattern.split(script)
        
        result_blocks = []
        for block in blocks:
            block = block.strip()
            if not block:
                continue
                
            # Se o bloco parece ser PL/SQL (contém BEGIN/DECLARE/CREATE), 
            # mantém o bloco inteiro
            if re.search(r'\b(BEGIN|DECLARE|CREATE\s+(OR\s+REPLACE\s+)?'
                         r'(PROCEDURE|FUNCTION|TRIGGER|PACKAGE|TYPE))\b', 
                         block, re.IGNORECASE):
                result_blocks.append(block)
            else:
                # Para SQL regular, divide em comandos separados por ';'
                sql_commands = [cmd.strip() for cmd in block.split(';') if cmd.strip()]
                result_blocks.extend(sql_commands)
        
        return result_blocks

    def close(self):
        """Fecha a conexão com o banco de dados."""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close() 