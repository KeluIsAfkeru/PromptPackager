@echo off
echo Installing dependencies...
pip install -r requirements.txt

echo Building executable...
pyinstaller --noconfirm --onefile --windowed --name "PromptPackager" --collect-all customtkinter --icon=NONE main.py

echo Build complete. Check the "dist" folder.
pause