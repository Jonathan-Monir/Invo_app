# -*- mode: python ; coding: utf-8 -*-
#
# PyInstaller spec for the INVO app (ONEFILE build).
# Build with:  pyinstaller --noconfirm INVO.spec
#
# Onefile = everything (Python, python3xx.dll, all libraries) is packed INSIDE a
# single INVO.exe, which self-extracts to a temp folder at runtime. You only ship
# INVO.exe plus the external data the app writes to (setups.db) and reads
# (images/). There is NO _internal/ folder to send.
#
# Notes:
#  * Entry point is main_app.py.
#  * tkcalendar pulls in Babel locale data; pandastable ships data files -- both
#    are collected explicitly because PyInstaller's static analysis can miss them.
#  * pandas / numpy / PIL / openpyxl are handled by PyInstaller's built-in hooks.
#  * images/ and setups.db are NOT bundled inside the exe; they ship NEXT TO it so
#    setups.db and output/ stay writable. resource_path() resolves against the exe
#    directory (os.path.dirname(sys.executable)), which works in onefile mode too.

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

# Onefile: fold the binaries and datas INTO the EXE (no separate COLLECT step).
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='INVO',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    runtime_tmpdir=None,
    console=False,            # GUI app -> no console window. Set True to debug startup errors.
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='images/logo.ico',
)
