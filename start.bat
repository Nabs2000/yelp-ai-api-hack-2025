@echo off
REM Moving Assistant - Quick Start Script (Windows)

echo.
echo Starting Moving Assistant...
echo.

REM Check if .env file exists
if not exist "backend\.env" (
    echo Backend .env file not found!
    echo Creating from .env.example...
    copy "backend\.env.example" "backend\.env"
    echo Created backend\.env
    echo Please edit backend\.env with your API keys before continuing!
    echo.
    pause
    exit /b 1
)

REM Check if frontend .env.local exists
if not exist "frontend\.env.local" (
    echo Creating frontend\.env.local...
    copy "frontend\.env.example" "frontend\.env.local"
    echo Created frontend\.env.local
)

REM Check for Docker
docker --version >nul 2>&1
if errorlevel 1 (
    echo Docker is not installed!
    echo Please install Docker from https://www.docker.com/get-started
    pause
    exit /b 1
)

echo Building and starting containers...
echo.

REM Start containers
docker-compose up --build -d

echo.
echo Moving Assistant is starting!
echo.
echo Services:
echo    Frontend: http://localhost
echo    Backend:  http://localhost:8000
echo    API Docs: http://localhost:8000/docs
echo.
echo Useful commands:
echo    View logs:    docker-compose logs -f
echo    Stop:         docker-compose down
echo    Restart:      docker-compose restart
echo.
echo Waiting for services to be ready...
timeout /t 10 /nobreak >nul

echo.
echo Done! Open http://localhost in your browser
echo.
pause
