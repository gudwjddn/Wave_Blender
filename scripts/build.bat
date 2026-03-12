@echo off
echo === Wave Blender Build ===
echo.

cd /d "%~dp0\.."

echo [1/4] Installing dependencies...
python -m pip install -r requirements.txt
python -m pip install pyinstaller pillow

echo.
echo [2/4] Converting icon...
if exist "icon.jpg" (
    python -c "from PIL import Image; img = Image.open('icon.jpg'); img.save('icon.ico', format='ICO', sizes=[(256,256),(128,128),(64,64),(48,48),(32,32),(16,16)])"
    if exist "icon.ico" (
        echo Icon converted successfully.
        set ICON_ARG=--icon icon.ico
    ) else (
        echo WARNING: Icon conversion failed, building without icon.
        set ICON_ARG=
    )
) else (
    echo WARNING: icon.jpg not found, building without icon.
    set ICON_ARG=
)

echo.
echo [3/4] Building executable...
python -m PyInstaller --onefile --windowed --name "WaveBlender" --collect-data imageio_ffmpeg %ICON_ARG% main.py

echo.
echo [4/4] Cleanup ^& result...
if exist "icon.ico" del "icon.ico"
if exist "dist\WaveBlender.exe" (
    echo Output: dist\WaveBlender.exe
) else (
    echo ERROR: Build failed. Check the output above for errors.
)
echo.
pause
