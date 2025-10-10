@echo off
REM ===============================================================
REM  AI MANAGEMENT TEAM – ENVIRONMENT SETUP (Windows)
REM  Version: 1.0
REM  Maintainer: Founder (Rob)
REM  Date: 2025-10-08
REM
REM  Purpose:
REM      Initialize a consistent development environment for
REM      the AI Management-Team project under Windows.
REM      Creates folder structure, virtual environment,
REM      installs dependencies, and sets up configuration files.
REM ===============================================================

setlocal enabledelayedexpansion

set PYTHON=python
set VENV_DIR=.venv
set REQUIREMENTS_FILE=requirements.txt

echo.
echo ===============================================================
echo 🚀 Setting up AI Management Team development environment...
echo ===============================================================

REM Step 1️⃣ — Create folder hierarchy
for %%D in (
    src
    src\agents
    src\utils
    memory
    logs
    data\project_proposals
    data\market_data
    data\reports
    docs\system\archive
    config
    dashboards\api
    dashboards\ui
    dashboards\static
    tests
    scripts
) do (
    if not exist %%D (
        mkdir %%D
    )
)
echo 📁 Directory structure created.

REM Step 2️⃣ — Create Python virtual environment
if not exist "%VENV_DIR%" (
    echo 🐍 Creating Python virtual environment in %VENV_DIR% ...
    %PYTHON% -m venv %VENV_DIR%
) else (
    echo 🔁 Virtual environment already exists, skipping creation.
)

REM Step 3️⃣ — Activate virtual environment
call %VENV_DIR%\Scripts\activate
if errorlevel 1 (
    echo ⚠️ Could not activate virtual environment. Please activate manually:
    echo     %VENV_DIR%\Scripts\activate
) else (
    echo ✅ Virtual environment activated.
)

REM Step 4️⃣ — Install dependencies
if exist "%REQUIREMENTS_FILE%" (
    echo 📦 Installing dependencies from %REQUIREMENTS_FILE% ...
    pip install --upgrade pip
    pip install -r %REQUIREMENTS_FILE%
) else (
    echo ⚠️ No requirements.txt found — creating a default one.
    (
        echo requests
        echo pandas
        echo numpy
        echo pyyaml
        echo python-dotenv
        echo slack_sdk
        echo chromadb
        echo fastapi
    ) > requirements.txt
    pip install -r requirements.txt
)
echo ✅ Dependencies installed.

REM Step 5️⃣ — Create .env file template
if not exist "config\.env" (
    echo 🧾 Creating .env template...
    (
        echo # ENVIRONMENT VARIABLES
        echo SLACK_WEBHOOK_URL=
        echo CLAUDE_API_KEY=
        echo PROJECT_NAME=AI_Management_Team
    ) > config\.env
) else (
    echo 🔁 .env already exists, skipping.
)

REM Step 6️⃣ — Create .gitignore
if not exist ".gitignore" (
    echo ⚙️ Creating .gitignore ...
    (
        echo __pycache__/
        echo *.pyc
        echo *.pyo
        echo *.pyd
        echo *.log
        echo .env
        echo .venv/
        echo .envrc
        echo memory/*.json
        echo logs/
        echo .DS_Store
        echo Thumbs.db
    ) > .gitignore
)
echo ✅ .gitignore ready.

REM Step 7️⃣ — Create README.md placeholder
if not exist "README.md" (
    echo 🧩 Creating project README.md ...
    (
        echo # AI Management Team – Claude Code Project
        echo Initialized via setup_environment.bat
        echo See /docs/system/ for governance, orchestration, and decision documentation.
    ) > README.md
)
echo ✅ README.md created.

REM Step 8️⃣ — Summary
echo.
echo ===============================================================
echo 🎉 Environment setup complete!
echo ---------------------------------------------------------------
echo → To activate your environment:
echo    %VENV_DIR%\Scripts\activate
echo → To initialize documentation:
echo    python scripts\init_management_team.py
echo ---------------------------------------------------------------
echo 🧠 Tip: After adding new dependencies, run:
echo    pip freeze > requirements.txt
echo ===============================================================
echo.

endlocal
pause

