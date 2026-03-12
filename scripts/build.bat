@echo off
echo === Wave Blender Build ===
echo.

cd /d "%~dp0\.."

echo [1/3] Installing dependencies...
pip install -r requirements.txt
pip install pyinstaller

echo.
echo [2/3] Building executable...
pyinstaller --onefile --windowed --name "WaveBlender" --collect-data imageio_ffmpeg main.py

echo.
echo [3/3] Build complete!
if exist "dist\WaveBlender.exe" (
    echo Output: dist\WaveBlender.exe
) else (
    echo ERROR: Build failed. Check the output above for errors.
)
echo.
pause
