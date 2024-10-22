# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_submodules

hiddenimports = []
hiddenimports += collect_submodules('App/audio_processing.py')
hiddenimports += collect_submodules('App/text_processing.py')
hiddenimports += collect_submodules('App/video_processing.py')


a = Analysis(
    ['App/main.py'],
    pathex=[],
    binaries=[('App/Vendor', '.')],
    datas=[],
    hiddenimports=hiddenimports,
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
    [],
    exclude_binaries=True,
    name='main',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='main',
)
app = BUNDLE(exe,
     a.binaries,
     a.hiddenimports,
     name='DYH.app',
     target_arch='universal2',
     icon='App/Assets/icon_512.icns',
     bundle_identifier=None,
     version='0.1.0',
)