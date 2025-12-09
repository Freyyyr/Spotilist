# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files
from PyInstaller.utils.hooks import copy_metadata

datas = []
datas += collect_data_files("streamlit")
datas += copy_metadata("streamlit")

# La syntaxe est ('chemin_source', 'dossier_destination_interne')
datas += [('app/script.py', 'app')] 

block_cipher = None

a = Analysis(
    ['run_app.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'streamlit.runtime.scriptrunner.magic_funcs',
        'streamlit.runtime.scriptrunner.script_runner',
        'streamlit.web.cli',
        'spotipy',
        'spotipy.oauth2',
        'pandas',
        'dotenv',
        'zipfile',         
        'io'      
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Spotilist',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
