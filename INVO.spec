# -*- mode: python ; coding: utf-8 -*-
#
# PyInstaller spec for the INVO app (onedir build).
# Build with:  pyinstaller --noconfirm INVO.spec
#
# Notes:
#  * Entry point is main_app.py.
#  * tkcalendar pulls in Babel locale data; pandastable ships data files -- both
#    are collected explicitly because PyInstaller's static analysis can miss them.
#  * pandas / numpy / PIL / openpyxl are handled by PyInstaller's built-in hooks.
#  * The app's own data (images/, setups.db) is NOT bundled here; the build script
#    copies it NEXT TO the exe so setups.db and output/ stay writable at runtime
#    (see build_windows.bat). resource_path() resolves against the exe directory.

from PyInstaller.utils.hooks import collect_all

datas = []
binaries = []
hiddenimports = ["babel.numbers", "babel.dates"]

for pkg in ("tkcalendar", "babel", "pandastable"):
    pkg_datas, pkg_binaries, pkg_hidden = collect_all(pkg)
    datas += pkg_datas
    binaries += pkg_binaries
    hiddenimports += pkg_hidden


a = Analysis(
    ['main_app.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    # These are only used by the standalone login.py / login2.py scripts, which
    # are NOT part of the main_app entry point. Excluding them avoids dragging in
    # mysql-connector / geocoder (not needed and not necessarily installed).
    excludes=['login', 'login2', 'database', 'mysql', 'mysql.connector', 'geocoder'],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='INVO',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,            # GUI app -> no console window. Set True to debug startup errors.
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='images/logo.ico',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='INVO',
)
