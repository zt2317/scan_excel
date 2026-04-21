# -*- mode: python ; coding: utf-8 -*-

import sys
import os

sys.setrecursionlimit(5000)

block_cipher = None

a = Analysis(
    ['src/app.py'],
    pathex=['.'],
    binaries=[],
    datas=[],
    hiddenimports=[
        'openpyxl',
        'openpyxl.cell',
        'openpyxl.styles',
        'xlrd',
        'requests',
        'PIL',
        'PIL.Image',
        'PIL.ImageDraw',
        'PIL.ImageFont',
        'src.core',
        'src.core.excel_reader',
        'src.core.column_detector',
        'src.core.formatter',
        'src.core.config',
        'src.core.wechat_client',
        'src.core.exceptions',
        'src.core.preview',
        'src.core.image_generator',
        'src.gui',
        'src.gui.main_window',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy',
        'scipy',
        'pandas',
        'PyQt6.Qt6Network',
        'PyQt6.Qt6Qml',
        'PyQt6.Qt6Quick',
        'PyQt6.Qt6WebEngine',
    ],
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
    name='Excel数据推送助手',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon.ico' if os.path.exists('assets/icon.ico') else None,
)
