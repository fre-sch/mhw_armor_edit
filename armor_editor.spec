# -*- mode: python -*-

block_cipher = None


a = Analysis(['src\\mhw_armor_edit\\armor_editor.py'],
             pathex=['D:\\Users\\frederik\\Documents\\_Workspaces\\Python\\mhw_armor_edit'],
             binaries=[],
             datas=[
                ("./src/mhw_armor_edit/assets/*.json", "mhw_armor_edit.assets"),
             ],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='MHW-Armor-Editor',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='MHW-Armor-Editor')
