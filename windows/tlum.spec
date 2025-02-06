# python -m PyInstaller tlum.spec

# -*- mode: python ; coding: utf-8 -*-
from kivy_deps import sdl2, glew, angle, gstreamer

a = Analysis(
    ['..\\src\\main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ("..\\assets\\data\\dictionary.txt","assets\\data"),
        ("..\\assets\\images\\error.png","assets\\images"),
        ("..\\assets\\images\\success.png","assets\\images"),
        ("..\\src\\component\\harmonica_widget.py","component"),
        ("..\\src\\template\\game_harmonica.kv","template"),
        ("..\\src\\template\\game_parrot.kv","template"),
        ("..\\src\\template\\game_phonetics.kv","template"),
        ("..\\src\\template\\main.kv","template"),
    ],
    hiddenimports=[],
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
    name='tlum',
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
)
