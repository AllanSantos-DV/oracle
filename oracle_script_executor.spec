# -*- mode: python ; coding: utf-8 -*-

import os
import sys
from PyInstaller.utils.hooks import collect_data_files

block_cipher = None

# Caminho para o Oracle Instant Client
instant_client_path = os.path.abspath('./instantclient/instantclient_23_7')
instant_client_files = []

# Coleta todos os arquivos do Instant Client
for root, dirs, files in os.walk(instant_client_path):
    for file in files:
        full_path = os.path.join(root, file)
        rel_path = os.path.relpath(full_path, instant_client_path)
        instant_client_files.append((full_path, 'instantclient'))

a = Analysis(
    ['src/main.py'],
    pathex=[],
    binaries=instant_client_files,
    datas=[
        ('config.json', '.'),
    ],
    hiddenimports=['cx_Oracle'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='OracleScriptExecutor',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='src/assets/icon.ico',
) 