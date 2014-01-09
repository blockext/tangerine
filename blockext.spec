# -*- mode: python -*-
a = Analysis(['installer.py'],
             pathex=['C:\\Users\\Borg\\Dropbox\\blockext\\installer'],
             hiddenimports=['distutils.command.build'],
             hookspath=None,
             runtime_hooks=None)
for name in ["index.html"]:
    a.datas.append((name, name, 'DATA'))
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='blockext.exe',
          debug=True,
          strip=None,
          upx=True,
          console=True )
