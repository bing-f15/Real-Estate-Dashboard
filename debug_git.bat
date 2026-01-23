@echo off
echo --- Git Connection Debugger ---
echo.

:: Check if git is recognized
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Git is not recognized as a command. 
    echo Please make sure you installed Git from git-scm.com and RESTARTED your computer or terminal.
    goto end
)

echo [OK] Git is installed.

:: Check status
echo.
echo Checking repository status...
git status >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Initializing new repository...
    git init
)

:: Add files
echo Adding files...
git add .

:: Commit
echo Committing...
git commit -m "Update dashboard" >nul 2>&1

:: Set branch
git branch -M main

:: Remote setup
echo Setting remote...
:: We use remove then add to avoid "remote origin already exists" errors
git remote remove origin >nul 2>&1
git remote add origin https://github.com/bing-f15/real-estate-dashboard.git

:: Try to push
echo.
echo --- ATTEMPTING PUSH ---
echo (A window may pop up asking you to log in to GitHub)
echo.
git push -u origin main --force

if %errorlevel% equ 0 (
    echo.
    echo [SUCCESS] Your code has been pushed to GitHub!
) else (
    echo.
    echo [FAILED] Push failed. 
    echo.
    echo Common reasons:
    echo 1. You haven't created the repository "real-estate-dashboard" on YOUR GitHub account (bing-f15) yet.
    echo 2. Your password/token is incorrect.
    echo 3. The repository name is different.
)

:end
echo.
pause
