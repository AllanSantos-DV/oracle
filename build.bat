@echo off
echo Instalando dependencias...
pip install -r requirements.txt

echo Gerando executavel...
pyinstaller oracle_script_executor.spec --clean

echo Copiando arquivos necessarios...
xcopy /E /I /Y "instantclient" "dist\OracleScriptExecutor\instantclient"

echo Build concluido! O executavel esta na pasta dist\OracleScriptExecutor 