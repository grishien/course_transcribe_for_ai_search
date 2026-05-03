@echo off
echo Creating virtual environment...
python -m venv .venv

echo Activating...
call .venv\Scripts\activate

echo Installing dependencies...
pip install openai-whisper

echo.
echo Done! Now run run.bat to start transcription.
pause