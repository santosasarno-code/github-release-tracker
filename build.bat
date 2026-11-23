@echo off
setlocal
cd /d "%~dp0"
title Build GitHub Release Tracker

echo ============================================================
echo  GitHub Release Tracker - build the portable .exe
echo ============================================================
echo.

rem --- 1. Python ---------------------------------------------------------
where py >nul 2>&1
if %errorlevel%==0 (set "PY=py -3") else (set "PY=python")
%PY% --version
if errorlevel 1 (
  echo.
  echo [X] Python was not found. Install Python 3.10 or newer from python.org
  echo     and tick "Add python.exe to PATH" in the installer.
  goto :fail
)

rem --- 2. tkinter (the app's window toolkit) -------------------------------
%PY% -c "import tkinter" >nul 2>&1
if errorlevel 1 (
  echo.
  echo [X] This Python has no tkinter. Run the Python installer again, choose
  echo     Modify, and tick "tcl/tk and IDLE".
  goto :fail
)

rem --- 3. The version number in the source ---------------------------------
set "VER="
for /f "usebackq delims=" %%V in (`%PY% tools\release_info.py version`) do set "VER=%%V"
if not defined VER (
  echo.
  echo [X] Could not read APP_VERSION from github_release_tracker.py ^(see the message above^).
  goto :fail
)
echo App version in the source: %VER%  ^(release tag will be v%VER%^)
echo.

rem --- 4. The source must at least compile --------------------------------
%PY% -m py_compile github_release_tracker.py
if errorlevel 1 (
  echo.
  echo [X] github_release_tracker.py has an error. Fix it and run this again.
  goto :fail
)

rem --- 5. PyInstaller ----------------------------------------------------
echo Installing / updating PyInstaller ^(needs internet^)...
%PY% -m pip install --upgrade pyinstaller
if errorlevel 1 (
  echo.
  echo [X] Could not install PyInstaller. Check your internet connection.
  goto :fail
)

rem --- 6. Build ----------------------------------------------------------
set "ICON="
if exist icon.ico (set "ICON=--icon icon.ico") else (echo [!] icon.ico not found - building without the app icon.)
echo.
echo Building GitHubReleaseTracker.exe ^(single file, no console window^)...
%PY% -m PyInstaller --noconfirm --clean --onefile --windowed %ICON% --name GitHubReleaseTracker github_release_tracker.py
if errorlevel 1 (
  echo.
  echo [X] Build failed. See the messages above.
  goto :fail
)
if not exist dist\GitHubReleaseTracker.exe (
  echo.
  echo [X] The build finished but dist\GitHubReleaseTracker.exe is missing.
  goto :fail
)

rem --- 7. Release notes with the SHA-256 -----------------------------------
echo.
%PY% tools\release_info.py notes dist\GitHubReleaseTracker.exe
if errorlevel 1 (
  echo.
  echo [!] The exe was built, but the release notes file could not be written.
)

echo.
echo ============================================================
echo  DONE: version %VER%
echo ============================================================
echo  Your portable app:   %~dp0dist\GitHubReleaseTracker.exe
echo  Release notes text:  %~dp0dist\release-notes-v%VER%.md
echo.
echo  Next ^(details in RELEASING.md^):
echo    1. Run the exe once and check the title says v%VER%.
echo    2. Upload the changed files to GitHub.
echo    3. Create a release with the tag  v%VER%  ^(exactly this^), attach the exe,
echo       and paste the release notes text into the description.
echo.
pause
exit /b 0

:fail
echo.
echo Build stopped.
pause
exit /b 1
