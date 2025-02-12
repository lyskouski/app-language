# python -m PyInstaller tlum.spec

# -*- mode: python ; coding: utf-8 -*-
from kivy_deps import sdl2, glew, angle, gstreamer
from PyInstaller.utils.hooks import collect_dynamic_libs

a = Analysis(
    ['..\\src\\main.py'],
    pathex=['.'],
    binaries=collect_dynamic_libs('kivy'),
    datas=[
        ("..\\src\\component\\*.py","component"),
        ("..\\src\\template\\*.kv","template"),
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
    a.binaries,
    a.datas,
    *[Tree(p) for p in (sdl2.dep_bins + glew.dep_bins)],
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
    icon=['tlum.ico'],
)
