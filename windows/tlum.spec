# Build Windows application:
# > cd windows
# > python -m PyInstaller tlum.spec
# > mkdir dist/assets
# > xcopy "./../assets/*" "./dist/assets/" /E /I /Y
# > cp AppxManifest.xml dist
# > choco install windows-sdk-10.0 -y
# # > winget install "MSIX Packaging Tool" --disable-interactivity
# > makeappx pack /d "dist" /p "tlum.msix"
# # For the case of not being recognized, use:
# # > $SdkPath = Get-ChildItem "C:\Program Files (x86)\Windows Kits\10\bin\" -Directory |
#       Sort-Object Name -Descending |
#       Select-Object -First 1
#     $MakeAppx = Join-Path $SdkPath.FullName "x64\makeappx.exe"
# # It would be something like:
# # &"C:/Program Files (x86)/Windows Kits/10/bin/10.0.22621.0/x64/makeappx.exe" pack /d "dist" /p "tlum.msix"

# -*- mode: python ; coding: utf-8 -*-
from kivy_deps import sdl2, glew, angle, gstreamer
from PyInstaller.utils.hooks import collect_dynamic_libs

a = Analysis(
    ['..\\src\\main.py'],
    pathex=['.'],
    binaries=collect_dynamic_libs('kivy'),
    datas=[
        ("..\\src\\component\\*.py","component"),
        ("..\\src\\l18n\\*.py","l18n"),
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
