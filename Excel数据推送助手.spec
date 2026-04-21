# -*- mode: python ; coding: utf-8 -*-

import sys
import os
from pathlib import Path

sys.setrecursionlimit(5000)

# 获取项目根目录
project_root = Path(os.getcwd())
src_path = project_root / 'src'

block_cipher = None

# 收集所有Python文件作为datas，确保模块路径正确
pathex = [str(project_root), str(src_path)]

a = Analysis(
    [str(src_path / 'app.py')],  # 使用完整路径
    pathex=pathex,
    binaries=[],
    datas=[
        # 确保src目录下的所有Python文件都被包含
        (str(src_path / 'core'), 'src/core'),
        (str(src_path / 'gui'), 'src/gui'),
    ],
    hiddenimports=[
        # 核心模块
        'core',
        'core.excel_reader',
        'core.column_detector',
        'core.formatter',
        'core.config',
        'core.wechat_client',
        'core.exceptions',
        'core.preview',
        'core.image_generator',
        # GUI模块
        'gui',
        'gui.main_window',
        # 第三方库
        'openpyxl',
        'openpyxl.cell',
        'openpyxl.styles',
        'openpyxl.workbook',
        'openpyxl.worksheet',
        'xlrd',
        'xlrd.book',
        'xlrd.sheet',
        'requests',
        'urllib3',
        'charset_normalizer',
        'certifi',
        'idna',
        'PIL',
        'PIL.Image',
        'PIL.ImageDraw',
        'PIL.ImageFont',
        'PIL._imaging',
        # PyQt6
        'PyQt6',
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
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
        'PyQt6.Qt6WebChannel',
        'PyQt6.Qt6WebSockets',
        'PyQt6.Qt6Test',
        'PyQt6.Qt6Multimedia',
        'PyQt6.Qt6Sql',
        'PyQt6.Qt6Help',
        'PyQt6.Qt6Network',
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
