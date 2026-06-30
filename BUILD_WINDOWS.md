# Building the INVO Windows executable

This produces a **single** `INVO.exe` (onefile build) that bundles Python and all
libraries inside itself. You ship just `INVO.exe` plus `images\` and `setups.db` —
there is **no `_internal\` folder** to send. PyInstaller cannot cross-compile, so
**run these steps on a Windows PC.**

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
4. run `pyinstaller --noconfirm INVO.spec` (produces `dist\INVO.exe`),
5. stage the deliverable in `package\`: `INVO.exe` + `images\` + `setups.db`.

When it finishes you'll have:

```
package\
├── INVO.exe          <- single self-contained executable (double-click to run)
├── setups.db         <- your saved setups (writable, persists)
├── images\           <- logo / background
└── output\           <- created next to the exe on first export
```

## Manual build (if you prefer not to use the .bat)

```bat
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements-build.txt
pyinstaller --noconfirm INVO.spec
mkdir package
copy /y dist\INVO.exe package\INVO.exe
xcopy /e /i /y images package\images
copy /y setups.db package\setups.db
```

## Distributing the app

Zip the **contents of `package\`** (`INVO.exe`, `images\`, `setups.db`) and send that.
The recipient unzips them into one folder and double-clicks `INVO.exe`. Those three
items just need to sit together in the same folder.

> The single `INVO.exe` contains Python and every library, so there's no `_internal\`
> folder anymore. It still needs `images\` and `setups.db` beside it (the app reads the
> images and writes the database/output there).

## Notes

- **Onefile vs onedir.** This is a onefile build: one `INVO.exe`. On launch it
  self-extracts its bundled libraries to a temp folder, so the **first start can take a
  few seconds** (and antivirus may scan it). That's normal. If you ever prefer faster
  startup at the cost of shipping a whole folder, switch back to a onedir spec.
- **Writable data lives next to the exe.** `resource_path()` and the app's working
  directory both resolve to the folder containing `INVO.exe` (works in onefile mode via
  `sys.executable`), so `setups.db`, `images\`, and `output\` are found and writable
  regardless of where the app is launched from.
- **login.py / login2.py are not part of the exe.** They use `mysql.connector` /
  `geocoder` and are standalone scripts unrelated to the `main_app.py` entry point, so
  those packages are intentionally excluded from the build.

## Troubleshooting

- **`python3xx.dll is missing` / app won't start on another PC.** That's the symptom of
  shipping only part of a *onedir* build. This spec is *onefile*, which fixes it — make
  sure you're sending the `package\INVO.exe` produced by this build, not an old folder
  build, and that `images\` + `setups.db` are in the same folder.
- **Windows SmartScreen / antivirus warning.** The exe is unsigned, so Windows may show
  "Windows protected your PC". Click **More info → Run anyway**. (Code-signing requires a
  paid certificate; out of scope here.) Onefile exes are flagged a little more often than
  folder builds.
- **The window flashes and closes immediately.** Build a debug version to see the error:
  open `INVO.spec`, set `console=False` to `console=True`, rerun the build, and launch
  `INVO.exe` from a Command Prompt so the traceback stays visible. Switch it back to
  `False` for the final build.
- **`Failed to execute script 'main_app'`.** Usually a missing dependency. Check
  `build\INVO\warn-INVO.txt` for `missing module named ...` lines and add the module to
  `hiddenimports` in `INVO.spec` (or `--collect-all <package>`), then rebuild.
- **`pip` can't find a wheel for pandas/numpy.** Use Python 3.10–3.12; the newest
  releases sometimes lack prebuilt Windows wheels on day one.
