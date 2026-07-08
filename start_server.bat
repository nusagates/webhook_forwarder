@echo off
echo =========================================
echo    Starting Webhook Forwarder (SaaS)
echo =========================================
echo.
echo Opening Backend server (FastAPI) in a new window...
start "Backend" cmd /c "uv run uvicorn main:app --reload --port 8000"

echo Opening Frontend server (React) in a new window...
start "Frontend" cmd /c "cd frontend & npm run dev"

echo.
echo Done! Please open your browser at:
echo http://localhost:5173
echo.
pause
