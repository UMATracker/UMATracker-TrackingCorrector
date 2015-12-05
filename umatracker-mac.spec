import os


datas = [('./data', 'data'),]

binaries = [(r'/usr/local/Cellar/ffms2/2.21/lib/libffms2.dylib', 'lib'), ]

a = Analysis(['./main.py'],
            pathex=['./'],
            binaries=binaries,
            datas=datas,
            hiddenimports=[],
            hookspath=None,
            runtime_hooks=None,
            excludes=None,
            win_no_prefer_redirects=None,
            win_private_assemblies=None,
            cipher=None)

pyz = PYZ(a.pure, cipher=None)

exe = EXE(pyz,
        a.scripts,
        a.binaries,
        a.zipfiles,
        a.datas,
        a.binaries,
        name='UMATracker-TrackingCorrector',
        debug=True,
        strip=None,
        upx=True,
        console=True, icon='./icon/icon.icns')

coll = COLLECT(exe,
        a.binaries,
        a.zipfiles,
        a.datas,
        strip=None,
        upx=True,
        name=os.path.join('dist', 'UMATracker'))

app = BUNDLE(coll,
        name=os.path.join('dist', 'UMATracker-TrackingCorrector.app'),
        appname="UMATracker-TrackingCorrector",
        version = '0.1', icon='./icon/icon.icns'
        )
