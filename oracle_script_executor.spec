# -*- mode: python ; coding: utf-8 -*-

import os
import sys
from PyInstaller.utils.hooks import collect_data_files

block_cipher = None

# Caminho para o Oracle Instant Client
instant_client_path = os.path.abspath('./instantclient/instantclient_23_7')

a = Analysis(
    ['src/main.py'],
    pathex=[],
    binaries=[],  # Não incluímos o Instant Client aqui
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

# Criamos um único executável que contém tudo, exceto o Instant Client
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
    console=True,  # Mantém True para debugar
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='src/assets/icon.ico',
) 