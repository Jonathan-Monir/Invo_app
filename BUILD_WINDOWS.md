# Building the INVO Windows executable

This produces a Windows app folder (`dist\INVO\`) containing `INVO.exe` and all its
dependencies. PyInstaller cannot cross-compile, so **run these steps on a Windows PC.**

## Prerequisites

- Windows 10/11.
- **Python 3.10–3.12** from <https://www.python.org/downloads/> — during install,
  tick **"Add python.exe to PATH"**. (The standard installer includes `tkinter`.)
- This project's files copied onto the Windows machine (including `setups.db` and the
  `images\` folder).

## Quick build (recommended)

From the project root, double-click **`build_windows.bat`** (or run it in a Command
Prompt). It will:

1. create a build virtual environment in `.venv\`,
2. install the build dependencies from `requirements-build.txt`,
3. clean any previous `build\` / `dist\`,
4. run `pyinstaller --noconfirm INVO.spec`,
5. copy `images\` and `setups.db` **next to the exe** in `dist\INVO\`.

When it finishes you'll have:

```
dist\INVO\
├── INVO.exe          <- double-click to run
├── setups.db         <- your saved setups (writable, persists)
├── images\           <- logo / background
├── output\           <- created on first export
└── _internal\        <- bundled Python + libraries (don't touch)
```

## Manual build (if you prefer not to use the .bat)

```bat
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements-build.txt
pyinstaller --noconfirm INVO.spec
xcopy /e /i /y images dist\INVO\images
copy /y setups.db dist\INVO\setups.db
```

## Distributing the app

Zip the **entire `dist\INVO\` folder** and send that. The user unzips it anywhere and
double-clicks `INVO.exe`. `setups.db` travels with it, so all saved setups are included,
and new setups / exported files are written next to the exe.

> Keep the folder together — `INVO.exe` needs the `_internal\` folder and the
> `images\` / `setups.db` files beside it. A lone `INVO.exe` will not run.

## Notes

- **Writable data lives next to the exe.** `resource_path()` and the app's working
  directory both resolve to the folder containing `INVO.exe`, so `setups.db`, `images\`,
  and `output\` are found and writable regardless of where the app is launched from.
- **login.py / login2.py are not part of the exe.** They use `mysql.connector` /
  `geocoder` and are standalone scripts unrelated to the `main_app.py` entry point, so
  those packages are intentionally excluded from the build.

## Troubleshooting

- **Windows SmartScreen / antivirus warning.** The exe is unsigned, so Windows may show
  "Windows protected your PC". Click **More info → Run anyway**. (Code-signing requires a
  paid certificate; out of scope here.)
- **The window flashes and closes immediately.** Build a debug version to see the error:
  open `INVO.spec`, set `console=False` to `console=True`, rerun the build, and launch
  `INVO.exe` from a Command Prompt so the traceback stays visible. Switch it back to
  `False` for the final build.
- **`Failed to execute script 'main_app'`.** Usually a missing dependency. Check
  `build\INVO\warn-INVO.txt` for `missing module named ...` lines and add the module to
  `hiddenimports` in `INVO.spec` (or `--collect-all <package>`), then rebuild.
- **`pip` can't find a wheel for pandas/numpy.** Use Python 3.10–3.12; the newest
  releases sometimes lack prebuilt Windows wheels on day one.
