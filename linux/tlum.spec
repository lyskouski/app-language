# python -m PyInstaller tlum.spec

# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['../src/main.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ("../src/component/*.py","component"),
        ("../src/template/*.kv","template"),
    ],
    hiddenimports=['kivy.core.audio.audio_gstplayer'],
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
    name='tlum',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['logo.png'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='tlum',
)
