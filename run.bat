@echo off
echo ==============================
echo    TestSmith AI Launcher
echo ==============================
echo.

if "%1"=="" (
    echo Usage: run.bat [command]
    echo.
    echo Commands:
    echo   test "your test instruction"  - Run a single test
    echo   file filename.txt            - Run tests from a file
    echo   eval                         - Run evaluation suite
    echo   install                      - Install dependencies
    echo.
    pause
    goto :end
)

if "%1"=="install" (
    echo Installing dependencies...
    pip install -r requirements.txt
    pause
    goto :end
)

if "%1"=="eval" (
    python main.py --eval
    pause
    goto :end
)

if "%1"=="file" (
    if "%2"=="" (
        echo Please provide a filename
        pause
        goto :end
    )
    python main.py --file "%2"
    pause
    goto :end
)

if "%1"=="test" (
    :: This handles the test command better
    set "instruction="
    setlocal enabledelayedexpansion
    set args=%*
    set args=!args:~5!
    python main.py "!args!"
    pause
    goto :end
)

echo Unknown command: %1
pause
:end