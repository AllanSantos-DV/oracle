@echo off
echo Limpando arquivos temporarios...
rmdir /s /q dist 2>nul
rmdir /s /q build 2>nul
if exist OracleScriptExecutor.spec del OracleScriptExecutor.spec

echo Instalando dependencias...
pip install -r requirements.txt

echo Gerando executavel...
pyinstaller oracle_script_executor.spec --clean

echo Copiando Oracle Instant Client...
xcopy /E /I /Y "instantclient\instantclient_23_7" "dist\instantclient_23_7"

echo Build concluido!
echo ----------------------------------------------------
echo DISTRIBUICAO:
echo 1. O arquivo executavel "dist\OracleScriptExecutor.exe"
echo 2. A pasta "dist\instantclient_23_7"
echo ----------------------------------------------------
echo IMPORTANTE: Distribua sempre o executavel e a pasta instantclient_23_7 juntos! 
echo            Ambos devem estar no mesmo diretorio.
pause 