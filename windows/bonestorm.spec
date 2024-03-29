# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

import os
import sys

a = Analysis([os.environ["START"]],
             binaries=[],
             pathex=[os.environ["ROOT"]],
             datas=[("../font", "font"),
                    ("../variants", "variants"),
                    ("../img", "img")],
             hiddenimports=["pygame"],
             hookspath=[],
             runtime_hooks=[],
             excludes=["pytest", "numpy"],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='bonestorm',
          icon='../img/bone.ico',
          debug=False,
          bootloader_ignore_signals=False,
          strip=True,
          upx=False,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False)
