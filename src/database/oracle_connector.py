import cx_Oracle
from tkinter import messagebox

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
        """Executa um script SQL e retorna o resultado."""
        try:
            self.cursor.execute(sql)
            self.connection.commit()
            return True, None
        except Exception as e:
            return False, str(e)

    def close(self):
        """Fecha a conexão com o banco de dados."""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close() 