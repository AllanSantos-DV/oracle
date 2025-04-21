# Executor de Scripts SQL Oracle

Aplicação para execução de scripts SQL em bancos de dados Oracle.

## Requisitos

- Python 3.8+
- Oracle Instant Client
- cx_Oracle

## Instalação

1. Clone o repositório:
```bash
git clone <url-do-repositorio>
cd oracle
```

2. Crie e ative um ambiente virtual:
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate
```

3. Instale as dependências:
```bash
pip install -e .
```

4. Configure o Oracle Instant Client:
   - Baixe o Oracle Instant Client do site oficial
   - Extraia o conteúdo para a pasta `instantclient` na raiz do projeto
   - A estrutura deve ser: `oracle/instantclient/instantclient_23_7/`

## Uso

1. Execute a aplicação:
```bash
python src/main.py
```

2. Ou use o comando após a instalação:
```bash
oracle-script-executor
```

## Estrutura do Projeto

```
oracle/
├── src/
│   ├── config/         # Gerenciamento de configurações
│   ├── database/       # Conexão com o banco de dados
│   ├── gui/            # Interface gráfica
│   │   └── widgets/    # Componentes da interface
│   └── utils/          # Utilitários
├── instantclient/      # Oracle Instant Client
├── setup.py           # Configuração do pacote
└── requirements.txt   # Dependências
```

## Configuração

A aplicação salva as configurações em `src/config.json`. Você pode:
- Configurar manualmente o arquivo
- Usar a interface gráfica para definir as configurações

## Suporte

Para problemas ou dúvidas, abra uma issue no repositório. 