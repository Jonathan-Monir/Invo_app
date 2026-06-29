@echo off
REM ==========================================================================
REM  Build the INVO Windows executable with PyInstaller.
REM  Run this from the project root on a Windows machine:  build_windows.bat
REM  Recommended: Python 3.10 - 3.12 from python.org (includes tkinter).
REM ==========================================================================

setlocal

REM --- 1) Create a build virtual environment (first run only) ---------------
if not exist .venv (
    echo Creating virtual environment...
    python -m venv .venv
    if errorlevel 1 (
        echo ERROR: could not create venv. Is Python on your PATH?
        pause
        exit /b 1
    )
)
call .venv\Scripts\activate.bat

REM --- 2) Install build dependencies ----------------------------------------
python -m pip install --upgrade pip
python -m pip install -r requirements-build.txt
if errorlevel 1 (
    echo ERROR: dependency installation failed.
    pause
    exit /b 1
)

REM --- 3) Clean previous build output ----------------------------------------
if exist build rmdir /s /q build
if exist dist  rmdir /s /q dist

REM --- 4) Build (onedir) using the spec --------------------------------------
pyinstaller --noconfirm INVO.spec
if errorlevel 1 (
    echo ERROR: PyInstaller build failed.
    pause
    exit /b 1
)

REM --- 5) Ship writable data + assets NEXT TO the exe ------------------------
REM These are resolved at runtime relative to INVO.exe (see resource_path).
xcopy /e /i /y images "dist\INVO\images" >nul
copy /y setups.db "dist\INVO\setups.db" >nul

echo.
echo ============================================================
echo  Build complete.
echo  App folder : dist\INVO\
echo  Run        : dist\INVO\INVO.exe  (double-click)
echo  Distribute : zip the whole  dist\INVO  folder and send it.
echo ============================================================
pause
endlocal
