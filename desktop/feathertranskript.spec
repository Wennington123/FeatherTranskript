# -*- mode: python ; coding: utf-8 -*-
import os
import sys

from PyInstaller.utils.hooks import collect_all

datas = [(os.path.join(SPECPATH, "assets"), "assets")]
binaries = []
hiddenimports = []

for package in ("faster_whisper", "ctranslate2", "onnxruntime", "tokenizers", "av", "huggingface_hub"):
    pkg_datas, pkg_binaries, pkg_hidden = collect_all(package)
    datas += pkg_datas
    binaries += pkg_binaries
    hiddenimports += pkg_hidden

a = Analysis(
    [os.path.join(SPECPATH, "app.py")],
    pathex=[SPECPATH],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

if sys.platform == "win32":
    splash = Splash(
        os.path.join(SPECPATH, "assets", "feathertlogo.png"),
        binaries=a.binaries,
        datas=a.datas,
    )
    exe = EXE(
        pyz,
        a.scripts,
        splash,
        splash.binaries,
        a.binaries,
        a.datas,
        [],
        name="FeatherTranskript",
        console=False,
        icon=os.path.join(SPECPATH, "build", "icon.ico"),
    )
else:
    exe = EXE(
        pyz,
        a.scripts,
        [],
        exclude_binaries=True,
        name="FeatherTranskript",
        console=False,
    )
    coll = COLLECT(
        exe,
        a.binaries,
        a.datas,
        strip=False,
        upx=False,
        name="FeatherTranskript",
    )
