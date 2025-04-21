# Executor de Scripts SQL Oracle v1.1

## Descrição
Aplicação desenvolvida em Python com interface gráfica (Tkinter) para execução automatizada e gerenciamento de scripts SQL em bancos de dados Oracle. Permite configurar a conexão, carregar scripts de uma pasta inicial, adicionar/remover scripts individualmente e reordenar a lista de execução.

## Requisitos
- Python 3.8 ou superior
- Oracle Instant Client (versão compatível com seu sistema e cx_Oracle)
- Bibliotecas Python:
  - cx_Oracle
  - tkinter (nativo do Python)

## Estrutura do Projeto
```
.
├── README.md
├── requirements.txt
├── run_sql_scripts.py
├── config.json       # Salva as configurações da última execução
└── instantclient/    # Pasta contendo o Oracle Instant Client
    └── instantclient_23_7/ # Exemplo de subpasta da versão
        ├── oci.dll
        ├── oraociicus.dll
        ├── orannz.dll
        ├── ojdbc8.jar
        └── ... (outros arquivos do Instant Client)
```
*Nota: A estrutura exata dentro da pasta `instantclient` pode variar conforme a versão baixada.* 

## Instalação

1.  Clone o repositório ou baixe os arquivos.
2.  **Oracle Instant Client:**
    *   Baixe o Oracle Instant Client Basic ou Basic Light compatível com seu sistema operacional (ex: 64-bit) e a versão do `cx_Oracle`.
    *   Descompacte o conteúdo na pasta `instantclient/instantclient_XX_Y` (substitua X e Y pela versão baixada, ex: `instantclient_23_7`).
    *   **Importante:** O script `run_sql_scripts.py` espera encontrar os arquivos do Instant Client dentro de uma subpasta como `instantclient_23_7`. Ajuste o caminho no início do script (`instant_client_dir = ...`) se sua estrutura for diferente.
3.  Instale as dependências Python:
    ```bash
    pip install -r requirements.txt
    ```

## Configuração

1.  O arquivo `config.json` armazena as configurações da última conexão bem-sucedida e a última pasta inicial selecionada:
    ```json
    {
        "folder": "caminho/para/ultima/pasta",
        "user": "ultimo_usuario",
        "password": "ultima_senha",
        "host": "ultimo_host",
        "port": "ultima_porta",
        "service": "ultimo_service_name"
    }
    ```
2.  As configurações são salvas automaticamente ao clicar em "Executar Scripts".
3.  A senha não é armazenada de forma segura, apenas salva em texto plano no `config.json` local.

## Uso

1.  Execute o programa:
    ```bash
    python run_sql_scripts.py
    ```
2.  **Configuração:** Preencha os dados de conexão com o banco Oracle (Usuário, Senha, Host, Porta, Service Name).
3.  **Carregar Scripts Iniciais:**
    *   Clique em "Procurar Pasta" para selecionar um diretório. Todos os arquivos `.sql` encontrados serão carregados na lista "Scripts SQL para Execução", substituindo os anteriores.
    *   A pasta selecionada aqui é salva no `config.json` como "Pasta Inicial" para a próxima vez que abrir.
4.  **Gerenciar Lista de Scripts:**
    *   **Adicionar:** Clique em "Adicionar" para abrir um diálogo e selecionar arquivos `.sql` adicionais de qualquer local. Eles serão acrescentados ao final da lista existente.
    *   **Remover:** Selecione um ou mais scripts na lista e clique em "Remover".
    *   **Reordenar:** Selecione *um único* script na lista e use os botões "Mover Acima" ou "Mover Abaixo" para ajustar a ordem de execução.
5.  **Execução:** Clique em "Executar Scripts".
    *   O programa validará os campos de conexão e se há scripts na lista.
    *   Os scripts na lista serão executados na ordem exibida.
    *   O resultado (OK ou ERRO com detalhes) de cada script será mostrado na área "Saída da Execução".

## Funcionalidades

- Interface gráfica intuitiva com Tkinter e tema moderno.
- Configuração de conexão com banco de dados Oracle.
- Salvamento automático das configurações de conexão e pasta inicial.
- Carregamento inicial de scripts a partir de uma pasta.
- Gerenciamento da lista de execução:
    - Adição de scripts individuais.
    - Remoção de scripts selecionados.
    - Reordenação da sequência de execução.
- Execução sequencial dos scripts na ordem definida.
- Exibição de resultados (sucesso/erro) em tempo real na área de saída.
- Validação de campos obrigatórios antes da execução.
- Tratamento de erros de conexão e de execução de scripts.
- Layout responsivo com painéis redimensionáveis.

## Arquivos SQL

- Devem ter a extensão `.sql` (não diferencia maiúsculas/minúsculas).
- São executados na ordem em que aparecem na lista da interface.
- Cada arquivo é tratado como uma transação separada (commit após cada arquivo bem-sucedido).
- Devem ser codificados em UTF-8 para evitar problemas com caracteres especiais.

## Tratamento de Erros

- **Erro Crítico (Oracle Client):** Se o Instant Client não for encontrado ou inicializado corretamente, um erro será exibido ao iniciar e a aplicação fechará.
- **Erro de Validação:** Se campos de conexão estiverem vazios ou nenhum script estiver carregado, um aviso será exibido ao tentar executar.
- **Erro de Conexão:** Se a conexão com o banco falhar, uma mensagem detalhada do Oracle será exibida.
- **Erro de Execução de Script:** Se um script falhar, o erro será registrado na saída, mas a aplicação tentará executar os scripts seguintes na lista.

## Limitações

- Suporte exclusivo para Oracle Database via cx_Oracle.
- Requer instalação manual e configuração correta do Oracle Instant Client.
- A senha é salva em texto plano no `config.json`.
- A interface está em português brasileiro.

## Contribuição

1.  Faça um fork do projeto.
2.  Crie uma branch para sua feature (`git checkout -b feature/nova-feature`).
3.  Commit suas mudanças (`git commit -m 'Adiciona nova feature'`).
4.  Push para a branch (`git push origin feature/nova-feature`).
5.  Abra um Pull Request.

## Licença

Este projeto está sob a licença MIT.

## Suporte

Para suporte, abra uma issue no repositório.

## Histórico de Versões

### v1.1 (Atual)
- Reestruturação da interface com PanedWindow.
- Adição de funcionalidades de gerenciamento de scripts (Adicionar, Remover, Reordenar).
- Melhoria nos estilos visuais (tema 'clam', fontes).
- Refatoração da lógica de execução para usar lista dinâmica.
- Melhor tratamento de erros no carregamento inicial da pasta.

### v1.0
- Interface gráfica inicial com Tkinter (substituindo PySimpleGUI).
- Execução básica de scripts SQL de uma pasta.
- Configuração de conexão e salvamento em `config.json`.
- Validação de campos e tratamento inicial de erros.
- Configuração do Oracle Instant Client via `cx_Oracle.init_oracle_client()`.

## Próximas Melhorias (Sugestões)

- [ ] Opção para parar execução em caso de erro em um script.
- [ ] Log de execução detalhado em arquivo.
- [ ] Suporte a múltiplos bancos de dados (ex: PostgreSQL, MySQL) - Requer refatoração significativa.
- [ ] Interface em múltiplos idiomas (internacionalização).
- [ ] Validação básica da sintaxe SQL antes da execução.
- [ ] Suporte a execução de scripts dentro de uma única transação.
- [ ] Melhorar segurança no armazenamento da senha (ex: usar keyring do sistema). 