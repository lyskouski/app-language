# Build Linux application:
# > cd linux
# > python -m PyInstaller tlum.spec
# > mkdir -p ./dist/assets
# > cp -r ./../assets/* ./dist/assets/

# Dependencies:
# > sudo apt-get install libsdl2-mixer-2.0-0 libsdl2-mixer-dev
# > sudo apt-get install libvorbisfile3 libmpg123-0
# > sudo apt-get install ffmpeg libavdevice-dev libavformat-dev libavfilter-dev libswscale-dev

# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_dynamic_libs

# Force ffpyplayer backend on Linux
import os
os.environ.setdefault("KIVY_AUDIO", "ffpyplayer")

a = Analysis(
    ['../src/main.py'],
    pathex=['.'],
    binaries=collect_dynamic_libs('kivy'),
    datas=[
        ("../src/component/*.py","component"),
        ("../src/controller/*.py","controller"),
        ("../src/l18n/*.py","l18n"),
        ("../src/template/*.kv","template"),
    ],
    hiddenimports=['kivy.core.audio'],
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
