@echo off
setlocal

cd /d %~dp0\..

echo === CURRENT DIR ===
cd

set VENV_PY=%CD%\.venv\Scripts\python.exe

if not exist "%VENV_PY%" (
    echo ERROR: .venv が見つかりません
    pause
    exit /b 1
)

echo === USING PYTHON ===
"%VENV_PY%" -c "import sys; print(sys.executable)"

echo === PYINSTALLER CHECK ===
"%VENV_PY%" -m PyInstaller --version
if errorlevel 1 (
    echo ERROR: PyInstaller が .venv に入っていません
    pause
    exit /b 1
)

rmdir /s /q build 2>nul
rmdir /s /q dist 2>nul

echo === BUILD START ===
"%VENV_PY%" -m PyInstaller ^
  --noconfirm ^
  --windowed ^
  --name amedas_qt_final ^
  --add-data "master\stations.csv;master" ^
  --add-data "sample\sample_jma_sunshine.csv;sample" ^
  --add-data "sample\batch_settings.csv;sample" ^
  --add-data "docs\manual.md;docs" ^
  --add-data "docs\exe_build_guide.md;docs" ^
  main.py

if errorlevel 1 (
    echo ERROR: Build failed
    pause
    exit /b 1
)

if exist dist\amedas_qt_final (
    mkdir dist\amedas_qt_final\input 2>nul
    mkdir dist\amedas_qt_final\output 2>nul
    mkdir dist\amedas_qt_final\logs 2>nul
)

echo === BUILD END ===
echo Build complete.
pause