# build_scripts/citation_linker.spec
# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path

# Paths
project_root = Path('..').resolve()
citation_linker_src = project_root / 'citationLinker' / 'src'
qtapp_src = project_root / 'QtApp' / 'src'

a = Analysis(
    [str(qtapp_src / 'qtapp' / 'main.py')],
    pathex=[
        str(citation_linker_src),
        str(qtapp_src),
    ],
    binaries=[],
    datas=[
        # Include citation_linker data files
        (str(citation_linker_src / 'citation_linker' / 'data'), 'citation_linker/data'),
    ],
    hiddenimports=[
        # Add all citation_linker modules
        'citation_linker',
        'citation_linker.citationLinker',
        'citation_linker.multiArticle',
        'citation_linker.multiFile',
        'citation_linker.citationConfig',
        'citation_linker.bibliographyFinder',
        'citation_linker.inParenthesesExtractor',
        'citation_linker.referenceConnector',
        'citation_linker.textScreener',
        'citation_linker.utils',
        'citation_linker.configLoad',
        'citation_linker.configPaths',
        'citation_linker.debugUtils',
        # Add all qtapp modules
        'qtapp',
        'qtapp.main',
        'qtapp.components',
        'qtapp.utils',
        'qtapp.viewerUtils',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude unused modules to reduce size
        'tkinter',
        'matplotlib',
        'numpy',  # Only if you don't use numpy
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Citation Linker',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,  # Compress (reduces size by ~30%)
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window for GUI
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico' if sys.platform == 'win32' else None,
)

# macOS: Create .app bundle
if sys.platform == 'darwin':
    app = BUNDLE(
        exe,
        name='Citation Linker.app',
        icon='icon.icns',
        bundle_identifier='com.n1smm.citationlinker',
        info_plist={
            'NSPrincipalClass': 'NSApplication',
            'NSHighResolutionCapable': 'True',
        },
    )
