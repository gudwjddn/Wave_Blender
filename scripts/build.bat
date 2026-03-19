@echo off
echo === Wave Blender Build ===
echo.

cd /d "%~dp0\.."

echo [1/3] Installing dependencies...
python -m pip install -r requirements.txt
python -m pip install pyinstaller pillow

echo.
echo [2/3] Building executable...
set ICON_SRC=
if exist "icon.png" (
    set ICON_SRC=icon.png
) else if exist "assets\icon.png" (
    set ICON_SRC=assets/icon.png
)

set ICON_FLAG=
set ADDDATA_FLAG=
if not "%ICON_SRC%"=="" (
    python -c "from PIL import Image; img=Image.open('%ICON_SRC%'); img.save('icon.ico',format='ICO',sizes=[(256,256),(128,128),(64,64),(48,48),(32,32),(16,16)])"
    if exist "icon.ico" (
        echo Icon ready.
        set ICON_FLAG=--icon "%CD%\icon.ico"
        set ADDDATA_FLAG=--add-data "%CD%\icon.ico;assets"
    ) else (
        echo WARNING: Icon conversion failed, building without icon.
    )
) else (
    echo No icon found, building without icon.
)
python -m PyInstaller --onefile --windowed --clean --name "WaveBlender" --collect-data imageio_ffmpeg %ICON_FLAG% %ADDDATA_FLAG% main.py

echo.
echo [3/3] Cleanup ^& result...
if exist "icon.ico" del "icon.ico"
if exist "dist\WaveBlender.exe" (
    echo Output: dist\WaveBlender.exe
) else (
    echo ERROR: Build failed. Check the output above for errors.
)
echo.
pause
