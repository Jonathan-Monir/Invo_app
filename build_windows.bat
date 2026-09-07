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

REM --- 4) Build (onefile) using the spec ------------------------------------
pyinstaller --noconfirm INVO.spec
if errorlevel 1 (
    echo ERROR: PyInstaller build failed.
    pause
    exit /b 1
)

REM --- 5) Stage the single exe with its external data -----------------------
REM Onefile output is dist\INVO.exe (one file). images\ and setups.db ship
REM NEXT TO it; they are resolved at runtime relative to INVO.exe.
if exist package rmdir /s /q package
mkdir package
copy /y dist\INVO.exe "package\INVO.exe" >nul
xcopy /e /i /y images "package\images" >nul
copy /y setups.db "package\setups.db" >nul

echo.
echo ============================================================
echo  Build complete.
echo  App folder : package\   (INVO.exe + images\ + setups.db)
echo  Run        : package\INVO.exe  (double-click)
echo  Distribute : zip the contents of  package\  and send it.
echo               Your father just needs INVO.exe, images\ and
echo               setups.db together in one folder -- no _internal.
echo ============================================================
pause
endlocal
