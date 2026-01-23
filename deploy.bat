@echo off
echo Initializing Git repo and pushing to GitHub...
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote remove origin
git remote add origin https://github.com/bing-f15/real-estate-dashboard.git
git push -u origin main
echo.
echo If there were no errors, your code is now on GitHub!
pause
